#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2012 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Appier Framework. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import os
import re
import json
import types
import logging
import urllib2
import inspect
import urlparse
import datetime
import traceback

import log
import http
import util
import request
import settings
import exceptions

API_VERSION = 1
""" The incremental version number that may be used to
check on the level of compatibility for the api """

RUNNING = "running"
""" The running state for the app, indicating that the
complete api set is being served correctly """

STOPPED = "stopped"
""" The stopped state for the app, indicating that some
of the api components may be down """

REPLACE_REGEX = re.compile("\<(\w+)\>")
""" The regular expression to be used in the replacement
of the capture groups for the urls """

class App(object):
    """
    The base application object that should be inherited
    from all the application in the appier environment.
    This object is responsible for the starting of all the
    structures and for the routing of the request.
    It should also be compliant with the WSGI specification.
    """

    _BASE_ROUTES = []
    """ Set of routes meant to be enable in a static
    environment using for instance decorators """

    def __init__(self, name = None):
        self.name = name or self.__class__.__name__
        self.handler = log.MemoryHandler()
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)
        self.server = None
        self.host = None
        self.port = None
        self.ssl = False
        self.manager = None
        self.routes_v = None
        self.type = "unset"
        self.status = STOPPED
        self.start_date = None
        self._load_paths(2)
        self._load_templating()

    @staticmethod
    def load():
        logging.basicConfig(format = log.LOGGING_FORMAT)

    @staticmethod
    def add_route(method, expression, function):
        method_t = type(method)
        method = (method,) if method_t in types.StringTypes else method
        expression = "^" + expression + "$"
        expression = REPLACE_REGEX.sub(r"(?P<\1>[a-zA-Z0-9_-]+)", expression)
        route = [method, re.compile(expression), function]
        App._BASE_ROUTES.append(route)

    def start(self):
        if self.status == RUNNING: return

        self.start_date = datetime.datetime.utcnow()
        if self.manager: self.manager.start()
        self.status = RUNNING

    def stop(self):
        if self.status == STOPPED: return

        self.status = STOPPED

    def serve(self, server = "waitress", host = "127.0.0.1", port = 8080, ssl = False, key_file = None, cer_file = None):
        self.logger.info("Starting '%s' with '%s'..." % (self.name, server))
        self.server = server; self.host = host; self.port = port; self.ssl = ssl
        self.start()
        method = getattr(self, "serve_" + server)
        kwargs = dict()
        names = method.func_code.co_varnames
        if "ssl" in names: kwargs["ssl"] = port
        if "key_file" in names: kwargs["key_file"] = key_file
        if "cer_file" in names: kwargs["cer_file"] = cer_file
        return_value = method(host = host, port = port, **kwargs)
        self.stop()
        self.logger.info("Stopped '%s'' in '%s' ..." % (self.name, server))
        return return_value

    def serve_waitress(self, host, port):
        """
        Starts the serving of the current application using the
        python based waitress server in the provided host and
        port as requested.

        For more information on the waitress http server please
        refer to https://pypi.python.org/pypi/waitress.

        @type host: String
        @param host: The host name of ip address to bind the server
        to, this value should be represented as a string.
        @type port: int
        @param port: The tcp port for the bind operation of the
        server (listening operation).
        """

        import waitress
        waitress.serve(self.application, host = host, port = port)

    def serve_tornado(self, host, port, ssl = False, key_file = None, cer_file = None):
        import tornado.wsgi
        import tornado.httpserver

        ssl_options = ssl and dict(
            keyfile = key_file,
            certfile = cer_file
        ) or None

        container = tornado.wsgi.WSGIContainer(self.application)
        server = tornado.httpserver.HTTPServer(container, ssl_options = ssl_options)
        server.listen(port, address = host)
        instance = tornado.ioloop.IOLoop.instance()
        instance.start()

    def serve_cherry(self, host, port):
        import cherrypy.wsgiserver

        server = cherrypy.wsgiserver.CherryPyWSGIServer(
            (host, port),
            self.application
        )
        try: server.start()
        except KeyboardInterrupt: server.stop()

    def load_jinja(self):
        try: import jinja2
        except: self.jinja = None; return

        loader = jinja2.FileSystemLoader(self.templates_path)
        self.jinja = jinja2.Environment(loader = loader)

    def close(self):
        pass

    def routes(self):
        return App._BASE_ROUTES + [
            (("GET",), re.compile("^/$"), self.info),
            (("GET",), re.compile("^/favicon.ico$"), self.icon),
            (("GET",), re.compile("^/info$"), self.info),
            (("GET",), re.compile("^/version$"), self.version),
            (("GET",), re.compile("^/log$"), self.logging),
            (("GET",), re.compile("^/debug$"), self.debug),
            (("GET", "POST"), re.compile("^/login$"), self.login),
            (("GET", "POST"), re.compile("^/logout$"), self.logout)
        ]

    def application(self, environ, start_response):
        # unpacks the various fields provided by the wsgi layer
        # in order to use them in the current request handling
        method = environ["REQUEST_METHOD"]
        path = environ["PATH_INFO"]
        query = environ["QUERY_STRING"]
        input = environ.get("wsgi.input")

        # creates the initial request object to be used in the
        # handling of the data has been received not that this
        # request object is still transient as it does not have
        # either the params and the json data set in it
        self.request = request.Request(method, path, environ = environ)

        # parses the provided query string creating a map of
        # parameters that will be used in the request handling
        # and then sets it in the request
        params = urlparse.parse_qs(query)
        self.request.set_params(params)

        # reads the data from the input stream file and then tries
        # to load a json object from it to be set in the request
        data = input.read()
        data_j = json.loads(data) if data else None
        self.request.set_json(data_j)
        self.request.load_session()

        # resolves the secret based params so that their content
        # is correctly decrypted according to the currently set secret
        self.request.resolve_params()

        # handles the currently defined request and in case there's an
        # exception triggered by the underlying action methods, handles
        # it and serializes its contents into a dictionary
        try: result = self.handle()
        except BaseException, exception:
            is_map = True
            lines = traceback.format_exc().splitlines()
            code = hasattr(exception, "error_code") and\
                exception.error_code or 500
            result = {
                "result" : "error",
                "name" : exception.__class__.__name__,
                "message" : str(exception),
                "code" : code,
                "traceback" : lines
            }
            self.request.set_code(code)
            if not settings.DEBUG: del result["traceback"]

            self.logger.error("Problem handling request: %s" % str(exception))
            for line in lines: self.logger.warning(line)
        else:
            is_map = type(result) == types.DictType
            if is_map and not "result" in result: result["result"] = "success"

        # retrieves the complete set of warning "posted" during the handling
        # of the current request and in case thre's at least one warning message
        # contained in it sets the warnings in the result
        warnings = self.request.get_warnings()
        if warnings: result["warnings"] = warnings

        # dumps the result using the json serializer and retrieves the resulting
        # sting value from it as the final message to be sent
        result_s = json.dumps(result) if is_map else result

        # sets the "target" content type taking into account the if the value is
        # set and if the current structure is a map or not
        default_content_type = is_map and "application/json" or "text/plain"
        self.request.default_content_type(default_content_type)

        # retrieves the (output) headers defined in the current request and extends
        # them with the current content type (json) then starts the response and
        # returns the result string to the caller wsgi infra-structure
        headers = self.request.get_headers() or []
        content_type = self.request.get_content_type() or "text/plain"
        code_s = self.request.get_code_s()
        headers.extend([("Content-Type", content_type)])
        start_response(code_s, headers)
        return (result_s)

    def handle(self):
        # retrieves the current registered routes, should perform a loading only
        # on the first execution and then runs the routing process using the
        # currently set request object, retrieving the result
        routes = self._routes()
        result = self.route(routes)

        # returns the result defaulting to an empty man in case no value was
        # returns from the handling method
        result = result or {}
        return result

    def route(self, items):
        # unpacks the various element from the request, this values are
        # going to be used along the routing process
        method = self.request.method
        path = self.request.path
        params = self.request.params
        data_j = self.request.data_j

        # retrieves both the callback and the mid parameters and uses them
        # to verify if the request is of type asynchronous
        callback = params.get("callback", None)
        mid = params.get("mid", None)
        is_async = callback and True or False

        # retrieves the mid (message identifier) and the callback url from
        # the provided list of parameters in case they are defined
        mid = mid[0] if mid else None
        callback = callback[0] if callback else None

        # iterates over the complete set of routing items that are
        # going to be verified for matching (complete regex collision)
        # and runs the match operation, handling the request with the
        # proper action method associated
        for item in items:
            # unpacks the current item into the http method, regex and
            # action method and then tries to match the current path
            # against the current regex in case there's a valid match and
            # the current method is valid in the current item continues
            # the current logic (method handing)
            methods_i, regex_i, method_i = item[:3]
            match = regex_i.match(path)
            if not method in methods_i or not match: continue

            # verifies if there's a definition of an options map for the current
            # routes in case there's not defines an empty one (fallback)
            item_l = len(item)
            opts_i = item[3] if item_l > 3 else {}

            # tries to retrieve the payload attribute for the current item in case
            # a json data value is defined otherwise default to single value (simple
            # message handling)
            if data_j: payload = data_j["payload"] if "payload" in data_j else [data_j]
            else: payload = [data_j]

            # retrieves the number of messages to be processed in the current context
            # this value will have the same number as the callbacks calls for the async
            # type of message processing
            mcount = len(payload)

            # sets the initial (default) return value from the action method as unset,
            # this value should be overriden by the various actions methods
            return_v = None

            # iterates over all the items in the payload to handle them in sequence
            # as defined in the payload list (first come, first served)
            for payload_i in payload:
                # retrieves the method specification for both the "unnamed" arguments and
                # the named ones (keyword based) so that they may be used to send the correct
                # parameters to the action methods
                method_a = inspect.getargspec(method_i)[0]
                method_kw = inspect.getargspec(method_i)[2]

                # retrieves the various matching groups for the regex and uses them as the first
                # arguments to be sent to the method then adds the json data to it, afters that
                # the keyword arguments are "calculated" using the provided "get" parameters but
                # filtering the ones that are not defined in the method signature
                groups = match.groups()
                args = list(groups) + ([payload_i] if not payload_i == None else [])
                kwargs = dict([(key, value[0]) for key, value in params.items() if key in method_a or method_kw])

                # in case the current route is meant to be as handled asynchronously
                # runs the logic so that the return is immediate and the handling is
                # deferred to a different thread execution logic
                if is_async:
                    force_async = opts_i.get("async", False)
                    if not settings.DEBUG and not force_async: raise RuntimeError(
                        "Async call not allowed for '%s'" % path
                    )
                    mid = self.run_async(
                        method_i,
                        callback,
                        mid = mid,
                        args = args,
                        kwargs = kwargs
                    )
                    return_v = dict(
                        result = "async",
                        mid = mid,
                        mcount = mcount
                    )

                # otherwise the request is synchronous and should be handled immediately
                # in the current workflow logic, thread execution may block for a while
                else:
                    force_async = opts_i.get("async", False)
                    if not settings.DEBUG and force_async: raise RuntimeError(
                        "Sync call not allowed for '%s'" % path
                    )
                    return_v = method_i(*args, **kwargs)

            # returns the currently defined return value, for situations where
            # multiple call have been handled this value may contain only the
            # result from the last call
            return return_v

        # raises a runtime error as if the control flow as reached this place
        # no regular expression/method association has been matched
        raise RuntimeError("Request %s '%s' not handled" % (method, path))

    def run_async(self, method, callback, mid = None, args = [], kwargs = {}):
        mid = mid or util.gen_token()
        def async_method(*args, **kwargs):
            try: result = method(*args, **kwargs)
            except BaseException, exception:
                lines = traceback.format_exc().splitlines()
                code = hasattr(exception, "error_code") and\
                    exception.error_code or 500
                result = {
                    "result" : "error",
                    "name" : exception.__class__.__name__,
                    "message" : str(exception),
                    "code" : code,
                    "traceback" : lines
                }
                if not settings.DEBUG: del result["traceback"]

                self.logger.warning("Problem handling async request: %s" % str(exception))
                for line in lines: self.logger.info(line)
            else:
                result = result or {}
                if not "result" in result: result["result"] = "success"

            try:
                http.post(callback, data_j = result, params = {
                    "mid" : mid
                })
            except urllib2.HTTPError, error:
                data = error.read()
                try:
                    data_s = json.loads(data)
                    message = data_s.get("message", "")
                    lines = data_s.get("traceback", [])
                except:
                    message = data
                    lines = []

                self.logger.warning("Assync callback (remote) error: %s" % (message))
                for line in lines: self.logger.info(line)

        if not self.manager:
            raise RuntimeError("No queue manager defined")

        is_private = method.__name__ == "_private"
        is_auth = self.request.session and "username" in self.request.session
        if is_private and not is_auth: raise exceptions.AppierException(
            "Method requires authentication",
            error_code = 403
        )

        self.manager.add(async_method, args, kwargs)
        return mid

    def warning(self, message):
        self.request.warning(message)

    def template(self, name, **kwargs):
        if self.jinja: return self.template_jinja(name, **kwargs)
        raise exceptions.OperationalError(
            message = "no valid template engine found"
        )

    def template_jinja(self, name, **kwargs):
        template = self.jinja.get_template(name)
        return template.render(**kwargs)

    def get_logger(self):
        return self.logger

    def get_uptime(self):
        current_date = datetime.datetime.utcnow()
        delta = current_date - self.start_date
        return delta

    def get_uptime_s(self, count = 2):
        uptime = self.get_uptime()
        uptime_s = self._format_delta(uptime)
        return uptime_s

    def icon(self, data = {}):
        pass

    def info(self, data = {}):
        return dict(
            name = self.name,
            type = self.type,
            server = self.server,
            host = self.host,
            port = self.port,
            ssl = self.ssl,
            status = self.status,
            uptime = self.get_uptime_s(),
            api_version = API_VERSION,
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def version(self, data = {}):
        return dict(
            api_version = API_VERSION
        )

    @util.private
    def logging(self, data = {}, count = None):
        if not settings.DEBUG: raise RuntimeError("Not in DEBUG mode")
        count = int(count) if count else 100
        return dict(
            messages = self.handler.get_latest(count = count)
        )

    @util.private
    def debug(self, data = {}):
        if not settings.DEBUG: raise RuntimeError("Not in DEBUG mode")
        return dict(
            info = self.info(data),
            manager = self.manager.info()
        )

    def login(self, data = {}):
        params = self.request.get_params()
        secret = self.request.params.get("secret", (None,))[0]
        self.auth(**params)

        self.request.set_session(create = True)
        sid = self.request.session["sid"]
        self.request.set_header("Set-Cookie", "sid=%s" % sid)

        self.on_login(sid, secret, **params)

        return dict(
            token = sid
        )

    def logout(self, data = {}):
        self.on_logout()

    def auth(self, username, password, **kwargs):
        is_valid = username == settings.USERNAME and password == settings.PASSWORD
        if not is_valid: raise RuntimeError("Invalid credentials provided")

    def on_login(self, sid, secret, username = "undefined", **kwargs):
        self.request.session["username"] = username
        if secret: self.request.session["secret"] = secret

    def on_logout(self):
        if not self.request.session: return
        del self.request.session["username"]

    def _load_paths(self, offset = 1):
        element = inspect.stack()[offset]
        module = inspect.getmodule(element[0])
        self.base_path = os.path.dirname(module.__file__)
        self.base_path = os.path.normpath(self.base_path)
        self.templates_path = os.path.join(self.base_path, "templates")

    def _load_templating(self):
        self.load_jinja()

    def _routes(self):
        if self.routes_v: return self.routes_v
        self._proutes()
        self.routes_v = self.routes()
        return self.routes_v

    def _proutes(self):
        """
        Processes the currently defined static routes taking
        the current instance as base for the function resolution.

        Usage of this method may require some knowledge of the
        internal routing system.
        """

        for route in App._BASE_ROUTES:
            function = route[2]
            function_name = function.__name__
            method = getattr(self, function_name)
            route[2] = method

    def _format_delta(self, time_delta, count = 2):
        days = time_delta.days
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        delta_s = ""
        if days > 0:
            delta_s += "%dd " % days
            count -= 1
        if count == 0: return delta_s.strip()
        if hours > 0:
            delta_s += "%dh " % hours
            count -= 1
        if count == 0: return delta_s.strip()
        if minutes > 0:
            delta_s += "%dm " % minutes
            count -= 1
        if count == 0: return delta_s.strip()
        delta_s += "%ds" % seconds
        return delta_s.strip()
