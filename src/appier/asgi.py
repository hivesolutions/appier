#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import io
import asyncio
import inspect
import tempfile

from . import util
from . import legacy
from . import exceptions

class ASGIApp(object):

    @classmethod
    async def asgi_entry(cls, scope, receive, send):
        if hasattr(cls, "_asgi") and cls._asgi:
            return await cls._asgi.app_asgi(scope, receive, send)
        cls._asgi = cls()
        return await cls._asgi.app_asgi(scope, receive, send)

    def serve_uvicorn(self, host, port, **kwargs):
        import uvicorn
        reload = kwargs.get("reload", False)
        app_asgi = build_asgi_i(self)
        uvicorn.run(app_asgi, host = host, port = port, reload=reload)

    async def app_asgi(self, *args, **kwargs):
        return await self.application_asgi(*args, **kwargs)

    async def application_asgi(self, scope, receive, send):
        """
        ASGI version of the application entrypoint, should define
        the proper asynchronous workflow for an HTTP request handling.

        :type scope: Dictionary
        :param scope: The connection scope, a dictionary that contains
        at least a type key specifying the protocol that is incoming.
        :type receive: Coroutine
        :param receive: An awaitable callable that will yield a new
        event dictionary when one is available.
        :type send: Coroutine
        :param send: an awaitable callable taking a single event dictionary
        as a positional argument that will return once the send has been
        completed or the connection has been closed.
        :see: https://channels.readthedocs.io/en/latest/asgi.html
        """

        scope_type = scope.get("type", None)
        scope_method = getattr(self, "asgi_" + scope_type, None)
        if not scope_method:
            raise exceptions.OperationalError(
                message = "Unexpected scope type '%s'" % scope_type
            )

        return await scope_method(scope, receive, send)

    async def asgi_lifespan(self, scope, receive, send):
        running = True

        while running:
            event = await receive()

            if event["type"] == "lifespan.startup":
                self.start()
                await send(dict(type = "lifespan.startup.complete"))

            elif event["type"] == "lifespan.shutdown":
                self.stop()
                await send(dict(type = "lifespan.shutdown.complete"))
                running = False

    async def asgi_http(self, scope, receive, send):
        try:
            # creates the context dictionary so that this new "pseudo" request
            # can have its own context for futures placement
            ctx = dict(start_task = None)

            # runs the asynchronous building of the intermediate structures
            # to get to the final WSGI compliant environment dictionary
            start_response = await self._build_start_response(ctx, send)
            sender = await self._build_sender(ctx, send, start_response)
            body = await self._build_body(receive)
            environ = await self._build_environ(scope, body, sender)

            self.prepare()
            try:
                result = self.application_l(environ, start_response, ensure_gen = False)
                self.set_request_ctx()
            finally:
                self.restore()

            # verifies if the resulting value is an awaitable and if
            # that's the case waits for it's "real" result value (async)
            if inspect.isawaitable(result): result = await result

            # waits for the start (code and headers) send operation to be
            # completed (async) so that we can proceed with body sending
            await ctx["start_task"]

            # iterates over the complete set of chunks in the response
            # iterator to send each of them to the client side
            for chunk in (result if result else [b""]):
                if asyncio.iscoroutine(chunk):
                    await chunk
                elif asyncio.isfuture(chunk):
                    await chunk
                elif isinstance(chunk, int):
                    continue
                else:
                    if legacy.is_string(chunk):
                        chunk = chunk.encode("utf-8")
                    await send({
                        "type" : "http.response.body",
                        "body" : chunk
                    })
        finally:
            self.unset_request_ctx()

    async def _build_start_response(self, ctx, send):
        def start_response(status, headers):
            if ctx["start_task"]: return
            code = status.split(" ", 1)[0]
            code = int(code)
            headers = [
                (name.lower().encode("ascii"), value.encode("ascii"))
                for name, value in headers
            ]
            send_coro = send({
                "type" : "http.response.start",
                "status" : code,
                "headers" : headers
            })
            ctx["start_task"] = asyncio.create_task(send_coro)
        return start_response

    async def _build_sender(self, ctx, send, start_response):
        async def sender(data):
            if not ctx["start_task"]:
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", "text/plain")
                    ]
                )
                await ctx["start_task"]
            return await send({
                "type" : "http.response.body",
                "body" : data,
                "more_body" : True
            })
        return sender

    async def _build_body(self, receive):
        with tempfile.SpooledTemporaryFile(max_size = 65536) as body:
            while True:
                message = await receive()
                util.verify(message["type"] == "http.request")
                body.write(message.get("body", b""))
                if not message.get("more_body"): break
            body.seek(0)
        return body

    async def _build_environ(self, scope, body, sender):
        """
        Builds a scope and request body into a WSGI environ object.

        :type scope: Dictionary
        :param scope: The scope dictionary from ASGI.
        :type: body: File
        :param body: The body callable to be used for the reading
        of the input.
        :type sender: Function
        :param sender: The sender function responsible for the sending
        of data to the client side (reponse).
        :rtype: Dictionary
        :return: The WSGI compatible environ dictionary converted
        from ASGI and ready to be used by WSGI apps.
        """

        environ = {
            "REQUEST_METHOD": scope["method"],
            "SCRIPT_NAME": scope.get("root_path", ""),
            "PATH_INFO": scope["path"],
            "QUERY_STRING": scope["query_string"].decode("ascii"),
            "SERVER_PROTOCOL": "HTTP/%s" % scope["http_version"],
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": scope.get("scheme", "http"),
            "wsgi.input": body,
            "wsgi.output": sender,
            "wsgi.errors": io.BytesIO(),
            "wsgi.multithread": True,
            "wsgi.multiprocess": True,
            "wsgi.run_once": False,
        }

        if "server" in scope:
            environ["SERVER_NAME"] = scope["server"][0]
            environ["SERVER_PORT"] = str(scope["server"][1])
        else:
            environ["SERVER_NAME"] = "localhost"
            environ["SERVER_PORT"] = "80"

        if "client" in scope:
            environ["REMOTE_ADDR"] = scope["client"][0]

        for name, value in scope.get("headers", []):
            name = name.decode("latin1")
            if name == "content-length":
                corrected_name = "CONTENT_LENGTH"
            elif name == "content-type":
                corrected_name = "CONTENT_TYPE"
            else:
                corrected_name = "HTTP_%s" % name.upper().replace("-", "_")

            value = value.decode("latin1")
            if corrected_name in environ:
                value = environ[corrected_name] + "," + value
            environ[corrected_name] = value

        return environ

def build_asgi(app_cls):
    async def app_asgi(scope, receive, send):
        return await app_cls.asgi_entry(scope, receive, send)
    return app_asgi

def build_asgi_i(app):
    async def app_asgi(scope, receive, send):
        return await app.app_asgi(scope, receive, send)
    return app_asgi
