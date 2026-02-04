#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2024 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import io
import asyncio
import unittest

import appier


class ASGITest(unittest.TestCase):
    def setUp(self):
        self.app = appier.App()

    def tearDown(self):
        self.app.unload()

    def test_build_environ(self):
        """
        The `_build_environ` method should correctly convert an ASGI
        scope dictionary into a WSGI-compatible environ dictionary
        with all the expected keys properly populated.
        """

        scope = dict(
            type="http",
            method="GET",
            path="/hello",
            query_string=b"name=world",
            http_version="1.1",
            root_path="",
            scheme="https",
            server=("example.com", 443),
            client=("10.0.0.1", 54321),
            headers=[
                (b"host", b"example.com"),
                (b"content-type", b"application/json"),
                (b"content-length", b"13"),
                (b"x-custom-header", b"custom-value"),
            ],
        )

        async def _test():
            body = io.BytesIO(b'{"key":"val"}')

            async def sender(data):
                pass

            environ = await self.app._build_environ(scope, body, sender)
            return environ

        environ = _run_async(_test())

        self.assertEqual(environ["REQUEST_METHOD"], "GET")
        self.assertEqual(environ["PATH_INFO"], "/hello")
        self.assertEqual(environ["QUERY_STRING"], "name=world")
        self.assertEqual(environ["SCRIPT_NAME"], "")
        self.assertEqual(environ["SERVER_PROTOCOL"], "HTTP/1.1")
        self.assertEqual(environ["SERVER_NAME"], "example.com")
        self.assertEqual(environ["SERVER_PORT"], "443")
        self.assertEqual(environ["REMOTE_ADDR"], "10.0.0.1")
        self.assertEqual(environ["wsgi.url_scheme"], "https")
        self.assertEqual(environ["CONTENT_TYPE"], "application/json")
        self.assertEqual(environ["CONTENT_LENGTH"], "13")
        self.assertEqual(environ["HTTP_HOST"], "example.com")
        self.assertEqual(environ["HTTP_X_CUSTOM_HEADER"], "custom-value")

    def test_build_environ_defaults(self):
        """
        When the scope dictionary does not include server or client
        information, the `_build_environ` method should provide sensible
        default values for SERVER_NAME and SERVER_PORT and omit REMOTE_ADDR.
        """

        scope = dict(
            type="http",
            method="POST",
            path="/submit",
            query_string=b"",
            http_version="1.0",
            headers=[],
        )

        async def _test():
            body = io.BytesIO(b"")

            async def sender(data):
                pass

            environ = await self.app._build_environ(scope, body, sender)
            return environ

        environ = _run_async(_test())

        self.assertEqual(environ["REQUEST_METHOD"], "POST")
        self.assertEqual(environ["PATH_INFO"], "/submit")
        self.assertEqual(environ["QUERY_STRING"], "")
        self.assertEqual(environ["SERVER_NAME"], "localhost")
        self.assertEqual(environ["SERVER_PORT"], "80")
        self.assertEqual(environ["SERVER_PROTOCOL"], "HTTP/1.0")
        self.assertNotIn("REMOTE_ADDR", environ)

    def test_build_environ_duplicate_headers(self):
        """
        When multiple headers with the same name are present in the
        ASGI scope, they should be joined with a comma separator in
        the resulting environ dictionary as per the CGI specification.
        """

        scope = dict(
            type="http",
            method="GET",
            path="/",
            query_string=b"",
            http_version="1.1",
            headers=[
                (b"x-forwarded-for", b"1.1.1.1"),
                (b"x-forwarded-for", b"2.2.2.2"),
            ],
        )

        async def _test():
            body = io.BytesIO(b"")

            async def sender(data):
                pass

            environ = await self.app._build_environ(scope, body, sender)
            return environ

        environ = _run_async(_test())

        self.assertEqual(environ["HTTP_X_FORWARDED_FOR"], "1.1.1.1,2.2.2.2")

    def test_build_body(self):
        """
        The `_build_body` method should read the full request body from
        the receive callable and return a seeked-to-zero file-like
        object containing all the received bytes.
        """

        async def _test():
            receive = await _build_receive(b"hello world")
            body = await self.app._build_body(receive)
            data = body.read()
            body.close()
            return data

        result = _run_async(_test())
        self.assertEqual(result, b"hello world")

    def test_build_body_chunked(self):
        """
        The `_build_body` method should properly concatenate multiple
        chunks received from the ASGI receive callable into a single
        contiguous body in the resulting file-like object.
        """

        async def _test():
            receive = await _build_receive_chunked([b"hello", b" ", b"world"])
            body = await self.app._build_body(receive)
            data = body.read()
            body.close()
            return data

        result = _run_async(_test())
        self.assertEqual(result, b"hello world")

    def test_build_body_empty(self):
        """
        The `_build_body` method should handle an empty request body
        gracefully, returning a file-like object that reads as an
        empty bytes sequence.
        """

        async def _test():
            receive = await _build_receive(b"")
            body = await self.app._build_body(receive)
            data = body.read()
            body.close()
            return data

        result = _run_async(_test())
        self.assertEqual(result, b"")

    def test_build_start_response(self):
        """
        The `_build_start_response` method should return a callable
        that, when invoked with a status string and headers list,
        creates an asyncio task that sends the HTTP response start
        event through the ASGI send callable.
        """

        async def _test():
            send = _MockSend()
            ctx = dict(start_task=None, encoding="utf-8")
            start_response = await self.app._build_start_response(ctx, send)

            start_response("200 OK", [("Content-Type", "text/plain")])

            self.assertNotEqual(ctx["start_task"], None)

            await ctx["start_task"]

            start = send.get_start()
            self.assertNotEqual(start, None)
            self.assertEqual(start["status"], 200)

            headers = send.get_headers()
            self.assertEqual(headers["content-type"], "text/plain")

        _run_async(_test())

    def test_build_start_response_idempotent(self):
        """
        The `start_response` callable returned by `_build_start_response`
        should be idempotent, ignoring subsequent calls once the
        initial response start has been triggered.
        """

        async def _test():
            send = _MockSend()
            ctx = dict(start_task=None, encoding="utf-8")
            start_response = await self.app._build_start_response(ctx, send)

            start_response("200 OK", [("Content-Type", "text/plain")])
            start_response("500 Internal Server Error", [("Content-Type", "text/html")])

            await ctx["start_task"]

            start = send.get_start()
            self.assertEqual(start["status"], 200)

            start_events = [
                e for e in send.events if e["type"] == "http.response.start"
            ]
            self.assertEqual(len(start_events), 1)

        _run_async(_test())

    def test_build_sender(self):
        """
        The sender callable returned by `_build_sender` should send
        body chunks through the ASGI send callable after ensuring
        that the response start has been sent first.
        """

        async def _test():
            send = _MockSend()
            ctx = dict(start_task=None, encoding="utf-8")
            start_response = await self.app._build_start_response(ctx, send)

            start_response("200 OK", [("Content-Type", "text/plain")])
            await ctx["start_task"]

            sender = await self.app._build_sender(ctx, send, start_response)
            await sender(b"hello")

            body = send.get_body()
            self.assertEqual(body, b"hello")

        _run_async(_test())

    def test_build_sender_string(self):
        """
        The sender callable should handle string data by encoding
        it to bytes using the encoding specified in the context
        dictionary before sending it through the ASGI send callable.
        """

        async def _test():
            send = _MockSend()
            ctx = dict(start_task=None, encoding="utf-8")
            start_response = await self.app._build_start_response(ctx, send)

            start_response("200 OK", [("Content-Type", "text/plain")])
            await ctx["start_task"]

            sender = await self.app._build_sender(ctx, send, start_response)
            await sender("olá mundo")

            body = send.get_body()
            self.assertEqual(body, "olá mundo".encode("utf-8"))

        _run_async(_test())

    def test_application_asgi_invalid_scope(self):
        """
        The `application_asgi` method should raise an `OperationalError`
        when it receives a scope with an unsupported type value, as
        the framework should not silently ignore unknown protocols.
        """

        scope = dict(type="websocket")

        async def _test():
            receive = await _build_receive(b"")
            send = _MockSend()
            await self.app.application_asgi(scope, receive, send)

        self.assertRaises(appier.OperationalError, lambda: _run_async(_test()))

    def test_lifespan_startup(self):
        """
        The `asgi_lifespan` method should handle the startup event
        by starting the application and sending the startup complete
        event back through the ASGI send callable.
        """

        async def _test():
            send = _MockSend()
            events = [dict(type="lifespan.startup"), dict(type="lifespan.shutdown")]
            events_iter = iter(events)

            async def receive():
                return next(events_iter)

            scope = dict(type="lifespan")
            await self.app.asgi_lifespan(scope, receive, send)

            types = [e["type"] for e in send.events]
            self.assertIn("lifespan.startup.complete", types)
            self.assertIn("lifespan.shutdown.complete", types)

        _run_async(_test())

    def test_lifespan_startup_order(self):
        """
        The `asgi_lifespan` method should process startup before
        shutdown and send the completion events in the correct
        sequential order matching the received lifecycle events.
        """

        async def _test():
            send = _MockSend()
            events = [dict(type="lifespan.startup"), dict(type="lifespan.shutdown")]
            events_iter = iter(events)

            async def receive():
                return next(events_iter)

            scope = dict(type="lifespan")
            await self.app.asgi_lifespan(scope, receive, send)

            self.assertEqual(len(send.events), 2)
            self.assertEqual(send.events[0]["type"], "lifespan.startup.complete")
            self.assertEqual(send.events[1]["type"], "lifespan.shutdown.complete")

        _run_async(_test())

    def test_lifespan_startup_failed(self):
        """
        The `asgi_lifespan` method should send a `lifespan.startup.failed`
        event with a message when the application startup raises an
        exception, as required by the ASGI lifespan specification.
        """

        _original_start = self.app.start

        def _failing_start(*args, **kwargs):
            raise RuntimeError("startup error")

        self.app.start = _failing_start

        async def _test():
            send = _MockSend()
            events = [dict(type="lifespan.startup"), dict(type="lifespan.shutdown")]
            events_iter = iter(events)

            async def receive():
                return next(events_iter)

            scope = dict(type="lifespan")
            await self.app.asgi_lifespan(scope, receive, send)

            types = [e["type"] for e in send.events]
            self.assertIn("lifespan.startup.failed", types)

            failed = [e for e in send.events if e["type"] == "lifespan.startup.failed"]
            self.assertEqual(len(failed), 1)
            self.assertIn("message", failed[0])
            self.assertIn("startup error", failed[0]["message"])

        try:
            _run_async(_test())
        finally:
            self.app.start = _original_start

    def test_lifespan_shutdown_failed(self):
        """
        The `asgi_lifespan` method should send a `lifespan.shutdown.failed`
        event with a message when the application shutdown raises an
        exception, as required by the ASGI lifespan specification.
        """

        _original_stop = self.app.stop

        def _failing_stop(*args, **kwargs):
            raise RuntimeError("shutdown error")

        self.app.stop = _failing_stop

        async def _test():
            send = _MockSend()
            events = [dict(type="lifespan.startup"), dict(type="lifespan.shutdown")]
            events_iter = iter(events)

            async def receive():
                return next(events_iter)

            scope = dict(type="lifespan")

            # ensure the app is marked as started so it attempts stop
            if not self.app.is_started():
                self.app.start()

            await self.app.asgi_lifespan(scope, receive, send)

            types = [e["type"] for e in send.events]
            self.assertIn("lifespan.shutdown.failed", types)

            failed = [e for e in send.events if e["type"] == "lifespan.shutdown.failed"]
            self.assertEqual(len(failed), 1)
            self.assertIn("message", failed[0])
            self.assertIn("shutdown error", failed[0]["message"])

        try:
            _run_async(_test())
        finally:
            self.app.stop = _original_stop

    def test_build_environ_query_latin1(self):
        """
        The `_build_environ` method should decode the query string using
        latin1 encoding as required by PEP 3333 (WSGI), allowing non-ASCII
        bytes that may appear in percent-encoded or raw query parameters.
        """

        scope = dict(
            type="http",
            method="GET",
            path="/search",
            query_string=b"key=caf\xe9",
            http_version="1.1",
            headers=[],
        )

        async def _test():
            body = io.BytesIO(b"")

            async def sender(data):
                pass

            environ = await self.app._build_environ(scope, body, sender)
            return environ

        environ = _run_async(_test())

        self.assertEqual(environ["QUERY_STRING"], "key=caf\xe9")


class _MockSend(object):
    """
    Mock ASGI send callable that records all the events
    sent through it, allowing assertions on the response
    start and body events after a request is processed.
    """

    def __init__(self):
        self.events = []

    async def __call__(self, event):
        self.events.append(event)

    def get_start(self):
        for event in self.events:
            if event["type"] == "http.response.start":
                return event
        return None

    def get_body(self):
        body = b""
        for event in self.events:
            if event["type"] == "http.response.body":
                body += event.get("body", b"")
        return body

    def get_headers(self):
        start = self.get_start()
        if not start:
            return {}
        headers = {}
        for name, value in start.get("headers", []):
            headers[name.decode("latin1")] = value.decode("latin1")
        return headers


def _run_async(coro):
    """
    Helper function that runs a coroutine synchronously using
    a new event loop, required for running async test methods
    from within a synchronous unittest test case.
    """

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _build_receive(body=b""):
    """
    Builds a mock ASGI receive callable that yields
    a single HTTP request message containing the provided
    body bytes, simulating a complete request body.
    """

    messages = [dict(type="http.request", body=body, more_body=False)]
    messages_iter = iter(messages)

    async def receive():
        return next(messages_iter)

    return receive


async def _build_receive_chunked(chunks):
    """
    Builds a mock ASGI receive callable that yields
    multiple HTTP request messages to simulate chunked
    transfer of the request body.
    """

    messages = []
    for index, chunk in enumerate(chunks):
        is_last = index == len(chunks) - 1
        messages.append(dict(type="http.request", body=chunk, more_body=not is_last))
    messages_iter = iter(messages)

    async def receive():
        return next(messages_iter)

    return receive
