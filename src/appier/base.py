#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import types
import logging
import urllib2
import inspect
import urlparse
import datetime
import traceback

import http
import util
import request
import settings
import exceptions

API_VERSION = 1
""" The incremental version number that may be used to
check on the level of compatibility for the api """

RUNNING = "running"
""" The running state for the bot, indicating that the
complete api set is being served correctly """

STOPPED = "stopped"
""" The stopped state for the bot, indicating that some
of the api components may be down """

LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
""" The format to be used for the logging operation in
the bot, these operations are going to be handled by
multiple stream handlers """

class MemoryHandler(logging.Handler):

    MAX_LENGTH = 1000

    def __init__(self, level = logging.NOTSET):
        logging.Handler.__init__(self, level = level)
        self.messages = []

        formatter = logging.Formatter(LOGGING_FORMAT)
        self.setFormatter(formatter)

    def emit(self, record):
        message = self.format(record)
        self.messages.insert(0, message)
        messages_l = len(self.messages)
        if messages_l > MemoryHandler.MAX_LENGTH:
            self.messages.pop()

    def get_latest(self, count = 100):
        return self.messages[:count]

class App(object):

    _BASE_ROUTES = []
    """ Set of routes meant to be enable in a static
    environment using for instance decorators """

    def __init__(self, name = None):
        self.name = name or self.__class__.__name__
        self.handler = MemoryHandler()
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.handler)
        self.manager = None
        self.routes_v = None
        self.type = "unset"
        self.status = STOPPED
        self.start_date = None

    @staticmethod
    def load():
        base_dir = (os.path.normpath(os.path.dirname(__file__) or ".") + "/../..")
        if not base_dir in sys.path: sys.path.insert(0, base_dir)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cleermob.settings")
        logging.basicConfig(format = LOGGING_FORMAT)

    @staticmethod
    def add_route(method, expression, function):
        method_t = type(method)
        method = (method,) if method_t in types.StringTypes else method
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

    def serve(self, server = "waitress", host = "127.0.0.1", port = 8080):
        self.logger.info("Starting '%s' with '%s'..." % (self.name, server))
        self.start()
        method = getattr(self, "serve_" + server)
        return_value = method(host = host, port = port)
        self.stop()
        self.logger.info("Stopped '%s'' in '%s' ..." % (self.name, server))
        return return_value

    def serve_waitress(self, host, port):
        import waitress
        waitress.serve(self.application, host = host, port = port)

    def serve_tornado(self, host, port):
        import tornado.wsgi
        import tornado.httpserver

        container = tornado.wsgi.WSGIContainer(self.application)
        server = tornado.httpserver.HTTPServer(container)
        server.listen(port, address = host)
        instance = tornado.ioloop.IOLoop.instance()
        instance.start()

    def close(self):
        pass

    def routes(self):
        return App._BASE_ROUTES + [
            (("GET",), re.compile("^/$"), self.info),
            (("GET",), re.compile("^/favicon.ico$"), self.icon),
            (("GET",), re.compile("^/api/info$"), self.info),
            (("GET",), re.compile("^/api/version$"), self.version),
            (("GET",), re.compile("^/api/log$"), self.logging),
            (("GET",), re.compile("^/api/debug$"), self.debug),
            (("GET", "POST"), re.compile("^/api/login$"), self.login),
            (("GET", "POST"), re.compile("^/api/logout$"), self.logout)
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

        # assumes that there's success in the handling of the request
        # only in case an exception is raises the request is considered
        # to be in an error state
        success = True

        # handles the currently defined request and in case there's an
        # exception triggered by the underlying action methods, handles
        # it and serializes its contents into a dictionary
        try: result = self.handle()
        except BaseException, exception:
            success = False
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

            self.logger.error("Problem handling request: %s" % str(exception))
            for line in lines: self.logger.warning(line)
        else:
            if not "result" in result: result["result"] = "success"

        # retrieves the complete set of warning "posted" during the handling
        # of the current request and in case thre's at least one warning message
        # contained in it sets the warnings in the result
        warnings = self.request.get_warnings()
        if warnings: result["warnings"] = warnings

        # dumps the result using the json serializer and retrieves the resulting
        # sting value from it as the final message to be sent
        result_s = json.dumps(result)

        # retrieves the (output) headers defined in the current request and extends
        # them with the current content type (json) then starts the response and
        # returns the result string to the caller wsgi infra-structure
        headers = self.request.get_headers() or []
        headers.extend([("Content-Type", "application/json")])
        start_response(success and "200 OK" or "500 Error", headers)
        return (result_s)

    def handle(self):
        routes = self._routes()
        result = self.route(routes)

        result = result or {}
        return result

    def route(self, items):
        method = self.request.method
        path = self.request.path
        params = self.request.params
        data_j = self.request.data_j

        callback = params.get("callback", None)
        mid = params.get("mid", None)
        is_async = callback and True or False

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
        username = self.request.params.get("username", (None,))[0]
        password = self.request.params.get("password", (None,))[0]
        secret = self.request.params.get("secret", (None,))[0]
        self.auth(username, password)

        self.request.set_session(create = True)
        self.request.session["username"] = username
        if secret: self.request.session["secret"] = secret

        sid = self.request.session["sid"]
        self.request.set_header("Set-Cookie", "sid=%s" % sid)
        return dict(
            token = sid
        )

    def logout(self, data = {}):
        if not self.request.session: return
        del self.request.session["username"]

    def auth(self, username, password):
        is_valid = username == settings.USERNAME and password == settings.PASSWORD
        if not is_valid: raise RuntimeError("Invalid credentials provided")

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
