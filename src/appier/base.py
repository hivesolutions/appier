#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2018 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import re
import sys
import imp
import time
import json
import uuid
import atexit
import locale
import signal
import socket
import inspect
import datetime
import itertools
import mimetypes
import threading
import traceback

import logging.handlers

from . import bus
from . import log
from . import git
from . import http
from . import meta
from . import util
from . import data
from . import smtp
from . import mock
from . import cache
from . import extra
from . import model
from . import config
from . import legacy
from . import defines
from . import session
from . import request
from . import compress
from . import settings
from . import observer
from . import execution
from . import controller
from . import structures
from . import exceptions
from . import preferences
from . import asynchronous

APP = None
""" The global reference to the application object this
should be a singleton object and so no multiple instances
of an app may exist in the same process """

LEVEL = None
""" The global reference to the (parsed/processed) debug
level that is going to be used for some core assumptions
in situations where no app is created (eg: api clients) """

NAME = "appier"
""" The name to be used to describe the framework while working
on its own environment, this is just a descriptive value """

VERSION = "1.17.31"
""" The version of the framework that is currently installed
this value may be used for debugging/diagnostic purposes """

PLATFORM = "%s %d.%d.%d.%s %s" % (
    sys.subversion[0] if hasattr(sys, "subversion") else "CPython",
    sys.version_info[0],
    sys.version_info[1],
    sys.version_info[2],
    sys.version_info[3],
    sys.platform
)
""" Extra system information containing some of the details
of the technical platform that is running the system, this
string should be exposed carefully to avoid extra information
from being exposed to outside agents """

IDENTIFIER_SHORT = "%s/%s" % (NAME, VERSION)
""" The short version of the current environment's identifier
meant to be used in production like environment as it hides some
of the critical and internal information of the system """

IDENTIFIER_LONG = "%s/%s (%s)" % (NAME, VERSION, PLATFORM)
""" Longest version of the system identifier, to be used in the
development like environment as it shows critical information
about the system internals that may expose the system """

IDENTIFIER = IDENTIFIER_LONG if config._is_devel() else IDENTIFIER_SHORT
""" The identifier that may be used to identify an user agent
or service running under the current platform, this string
should comply with the typical structure for such values,
by default this value is set with the short version of the
identifier (less information) but this may be changed at
runtime if the current verbosity level is changed """

API_VERSION = 1
""" The incremental version number that may be used to
check on the level of compatibility for the api """

BUFFER_SIZE = 32768
""" The size of the buffer so be used while sending data using
the static file serving approach (important for performance) """

MAX_LOG_SIZE = 524288
""" The maximum amount of bytes for a log file created by
the rotating file handler, after this value is reached a
new file is created for the buffering of the results """

MAX_LOG_COUNT = 5
""" The maximum number of files stores as backups for the
rotating file handler, note that these values are stored
just for extra debugging purposes """

RUNNING = "running"
""" The running state for the app, indicating that the
complete api set is being served correctly """

STOPPED = "stopped"
""" The stopped state for the app, indicating that some
of the api components may be down """

CACHE_CONTROL = "private, no-cache, no-store, must-revalidate"
""" The default/fallback value that is going to be used in the
"Cache-Control" header for the dynamic requests, should be restrictive
in terms of re-validation of content """

ALLOW_ORIGIN = "*"
""" The default value to be used in the "Access-Control-Allow-Origin"
header value, this should not be too restrictive """

ALLOW_HEADERS = "*, X-Requested-With"
""" The default value to be used in the "Access-Control-Allow-Headers"
header value, this should not be too restrictive """

ALLOW_METHODS = "GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS"
""" The default value to be used in the "Access-Control-Allow-Methods"
header value, this should not be too restrictive """

CONTENT_SECURITY = "default-src * ws://* wss://* data: blob:; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline';"
""" The default value to be used in the "Content-Security-Policy"
header value, this should not be too restrictive """

FRAME_OPTIONS = "SAMEORIGIN"
""" The value to be as the default/original for the "X-Frame-Options"
header, this should ensure that the same origin is always used when
trying to embed a dynamic content into a web page """

XSS_PROTECTION = "1; mode=block"
""" Value to be used as the original one for the "X-XSS-Protection"
header value, should provide a way of preventing XSS attach under the
internet explorer browser """

CONTENT_OPTIONS = "nosniff"
""" Default "X-Content-Type-Options" header value to be used to prevent
the sniffing of content type values, ensuring that the browser sticks to
value of content type provided by the server """

OCTET_TYPE = "application/octet-stream"
""" The mime/content type to be used for octet stream based message payloads
so that the legacy byte oriented value is readable """

REPLACE_REGEX = re.compile("(?<!\(\?P)\<((\w+)(\([\"'].*?[\"']\))?:)?(\w+)\>")
""" The regular expression to be used in the replacement
of the capture groups for the urls, this regex will capture
any named group not changed until this stage (eg: int,
string, regex, etc.) """

INT_REGEX = re.compile("\<int:(\w+)\>")
""" The regular expression to be used in the replacement
of the integer type based groups for the urls """

REGEX_REGEX = re.compile("\<regex\([\"'](.*?)[\"']\):(\w+)\>")
""" Regular expression that is going to be used for the
replacement of regular expression types with the proper
group in the final URL based route regex """

SLUGIER_REGEX_1 = re.compile(r"[^\w]+", re.UNICODE)
""" The first regular expression that is going to be used
by the slugier sub system to replace some of its values """

SLUGIER_REGEX_2 = re.compile(r"[-]+", re.UNICODE)
""" The second regular expression that is going to be used
by the slugier sub system to replace some of its values """

CSS_ABS_REGEX = re.compile(b"url\((?!(http:\/\/|https:\/\/|\/\/|\/))([^\)]+)\)")
""" The regular expression that is going to be used to capture
the relative CSS URL values, so that they may be converted into
absolute ones for proper inlining, note that the regex is defined
as a negation of the absolute URL values """

BODYLESS_METHODS = (
    "GET",
    "HEAD",
    "OPTIONS",
    "DELETE"
)
""" The sequence that defines the complete set of
HTTP methods that are considered to be bodyless,
meaning that no contents should be expected under
it's body, content length should be zero """

ESCAPE_EXTENSIONS = (
    ".xml",
    ".html",
    ".xhtml",
    ".liquid",
    ".xml.tpl",
    ".html.tpl",
    ".xhtml.tpl"
)
""" The sequence containing the various extensions
for which the autoescape mode will be enabled  by
default as expected by the end developer """

TYPES_R = dict(
    int = int,
    str = legacy.UNICODE,
    regex = legacy.UNICODE
)
""" Map that resolves a data type from the string representation
to the proper type value to be used in casting """

EXCLUDED_NAMES = (
    "server",
    "host",
    "port",
    "ssl",
    "key_file",
    "cer_file"
)
""" The sequence that contains the names that are considered
excluded from the auto parsing of parameters """

EMPTY_METHODS = (
    "HEAD",
)
""" Sequence containing the complete set of HTTP methods, that
should have an empty body as defined by HTTP specification """

BASE_HEADERS = (
    ("X-Powered-By", IDENTIFIER),
)
""" The sequence containing the headers considered to be basic
and that are going to be applied to all of the requests received
by the appier framework (water marking each of the requests) """

REQUEST_LOCK = threading.RLock()
""" The lock to be used in the application handling of request
so that no two request get handled at the same time for the current
app instance, as that would create some serious problems """

CASTERS = {
    list : lambda v: [y for y in itertools.chain(*[x.split(",") for x in v])],
    bool : lambda v: v if isinstance(v, bool) else\
        not v in ("", "0", "false", "False")
}
""" The map associating the various data types with a proper custom
caster to be used for special data types (more complex) under some
of the simple casting operations """

CASTER_MULTIPLE = {
    list : True,
    "list" : True
}
""" Map that associates the various data type values with the proper
value for the multiple (fields) for the (get) field operation, this
way it's possible to defined a pre-defined multiple value taking into
account the target data type """

class App(
    legacy.with_meta(
        meta.Indexed,
        observer.Observable,
        compress.Compress,
        mock.MockApp
    )
):
    """
    The base application object that should be inherited
    from all the application in the appier environment.
    This object is responsible for the starting of all the
    structures and for the routing of the request.
    It should also be compliant with the WSGI specification.
    """

    _BASE_ROUTES = []
    """ Set of routes meant to be enable in a static
    environment using for instance decorators this is
    required because at the time of application loading
    there's no application instance available """

    _ERROR_HANDLERS = {}
    """ The dictionary associating the error object (may be
    both an integer code or an exception class) with the
    proper method that is going to be used to handle that
    error when it is raised """

    _CUSTOM_HANDLERS = {}
    """ Map that associates the various custom key values and
    the tuples that describe the various handlers associated
    with such actions (this is considered a generic value) """

    def __init__(
        self,
        name = None,
        locales = ("en_us",),
        parts = (),
        level = None,
        handlers = None,
        service = True,
        safe = False,
        lazy = False,
        payload = False,
        cache_s = 604800,
        cache_c = cache.MemoryCache,
        preferences_c = preferences.MemoryPreferences,
        bus_c = bus.MemoryBus,
        session_c = session.FileSession
    ):
        observer.Observable.__init__(self)
        compress.Compress.__init__(self)
        self.name = name or self.__class__.__name__
        self.name_b = self.name
        self.name_i = self.name
        self.locales = locales
        self.parts = parts
        self.service = service
        self.safe = safe
        self.lazy = lazy
        self.payload = payload
        self.cache_s = cache_s
        self.cache_c = cache_c
        self.preferences_c = preferences_c
        self.bus_c = bus_c
        self.session_c = session_c
        self.description = self._description()
        self.logo_url = None
        self.logo_square_url = None
        self.copyright = None
        self.copyright_year = None
        self.copyright_url = None
        self.server = None
        self.server_version = None
        self.host = None
        self.port = None
        self.ssl = False
        self.local_url = None
        self.adapter = data.MongoAdapter()
        self.manager = asynchronous.QueueManager(self)
        self.routes_v = None
        self.pid = None
        self.tid = None
        self.type = "default"
        self.status = STOPPED
        self.start_time = None
        self.start_date = None
        self.touch_time = None
        self.sort_headers = False
        self.secure_headers = True
        self.uid = str(uuid.uuid4())
        self.puid = self.uid
        self.random = str(uuid.uuid4())
        self.secret = self.random
        self.hostname = socket.gethostname()
        self.cache = datetime.timedelta(seconds = cache_s)
        self.cache_control = CACHE_CONTROL
        self.allow_origin = ALLOW_ORIGIN
        self.allow_headers = ALLOW_HEADERS
        self.allow_methods = ALLOW_METHODS
        self.content_security = CONTENT_SECURITY
        self.frame_options = FRAME_OPTIONS
        self.xss_protection = XSS_PROTECTION
        self.content_options = CONTENT_OPTIONS
        self.login_route = "base.login"
        self.part_routes = []
        self.context = {}
        self.models = {}
        self.models_l = []
        self.controllers = {}
        self.controllers_l = []
        self.names = {}
        self.libraries = {}
        self.lib_loaders = {}
        self.parts_l = []
        self.parts_m = {}
        self._loaded = False
        self._resolved = False
        self._locale_d = locales[0]
        self._server = None
        self._user_routes = None
        self._core_routes = None
        self._own = self
        self._peers = {}
        self.__routes = []
        self.load(level = level, handlers = handlers)

    def __getattr__(self, name):
        if not name in ("session",):
            raise AttributeError("'%s' not found" % name)

        if not hasattr(self, "request"):
            raise AttributeError("'%s' not found" % name)

        if not hasattr(self.request, name):
            raise AttributeError("'%s' not found" % name)

        return getattr(self.request, name)

    @property
    def request(self):
        if not self.safe: return self._request
        if self.is_main(): return self._request
        return self.mock

    @property
    def locale(self):
        if not self.request: return None
        return self.request.locale

    @property
    def mock(self):
        return self._mock

    @property
    def own(self):
        if not self.safe: return self._own
        if self.is_main(): return self._own
        return self

    @property
    def crypt_secret(self):
        if not self.secret: return None
        if self.secret == self.random: return None
        return self.secret

    @property
    def server_full(self):
        if not self.server_version: return self.server
        return self.server + "/" + str(self.server_version)

    @staticmethod
    def load_g():
        logging.basicConfig(format = log.LOGGING_FORMAT)

    @staticmethod
    def unload_g():
        pass

    @staticmethod
    def add_route(*args, **kwargs):
        route = App.norm_route(*args, **kwargs)
        App._BASE_ROUTES.append(route)

    @staticmethod
    def add_error(error, method, scope = None, json = False, opts = None, context = None):
        error_handlers = App._ERROR_HANDLERS.get(error, [])
        error_handlers.append([method, scope, json, opts, context])
        App._ERROR_HANDLERS[error] = error_handlers
        if APP and APP._resolved: APP._add_error(
            error,
            method,
            scope = scope,
            json = json,
            opts = opts,
            context = context
        )

    @staticmethod
    def remove_error(error, method, scope = None, json = False, opts = None, context = None):
        error_handlers = App._ERROR_HANDLERS[error]
        error_handlers.remove([method, scope, json, opts, context])
        if APP and APP._resolved: APP._remove_error(
            error,
            method,
            scope = scope,
            json = json,
            opts = opts,
            context = context
        )

    @staticmethod
    def add_exception(exception, method, scope = None, json = False, opts = None, context = None):
        error_handlers = App._ERROR_HANDLERS.get(exception, [])
        error_handlers.append([method, scope, json, opts, context])
        App._ERROR_HANDLERS[exception] = error_handlers
        if APP and APP._resolved: APP._add_exception(
            exception,
            method,
            scope = scope,
            json = json,
            opts = opts,
            context = context
        )

    @staticmethod
    def remove_exception(exception, method, scope = None, json = False, opts = None, context = None):
        error_handlers = App._ERROR_HANDLERS[exception]
        error_handlers.remove([method, scope, json, opts, context])
        if APP and APP._resolved: APP._remove_exception(
            exception,
            method,
            scope = scope,
            json = json,
            opts = opts,
            context = context
        )

    @staticmethod
    def add_custom(key, method, opts = None, context = None):
        custom_handlers = App._CUSTOM_HANDLERS.get(key, [])
        custom_handlers.append([method, opts, context])
        App._CUSTOM_HANDLERS[key] = custom_handlers
        if is_loaded(): APP._add_custom(key, method, opts = opts, context = context)

    @staticmethod
    def remove_custom(key, method, opts = None, context = None):
        custom_handlers = App._CUSTOM_HANDLERS[key]
        custom_handlers.remove([method, opts, context])
        if is_loaded(): APP._remove_custom(key, method, opts = opts, context = context)

    @staticmethod
    def norm_route(
        method,
        expression,
        function,
        asynchronous = False,
        json = False,
        opts = None,
        context = None
    ):
        # creates the list that will hold the various parameters (type and
        # name tuples) and the map that will map the name of the argument
        # to the string representing the original expression of it so that
        # it may be latter used for reference (as specified in definition)
        param_t = []
        names_t = {}

        # retrieves the data type of the provided method and in case it
        # references a string type converts it into a simple tuple otherwise
        # uses it directly, then creates the options dictionary with the
        # series of values that are going to be used as options in the route
        method_t = type(method)
        method = (method,) if method_t in legacy.STRINGS else method
        opts = dict(opts) if opts else dict()
        opts.update(
            base = expression,
            param_t = param_t,
            names_t = names_t,
            json = opts.get("json", json),
            asynchronous = opts.get("asynchronous", asynchronous),
        )

        # creates a new match based iterator to try to find all the parameter
        # references in the provided expression so that meta information may
        # be created on them to be used latter in replacements
        iterator = REPLACE_REGEX.finditer(expression)
        for match in iterator:
            # retrieves the group information on the various groups and unpacks
            # them creating the param tuple from the resolved type and the name
            # of the parameter (to be used in parameter passing casting)
            _type_s, type_t, extras, name = match.groups()
            type_r = TYPES_R.get(type_t, str)
            param = (type_r, name)

            # creates the target (replacement) expression taking into account if
            # the type values has been provided or not, note that for expression
            # with type the extras value is used in case it exists
            if type_t: target = "<" + type_t + (extras or "") + ":" + name + ">"
            else: target = "<" + name + ">"

            # adds the parameter to the list of parameter tuples and then sets the
            # target replacement association (name to target string)
            param_t.append(param)
            names_t[name] = target

        # runs the regex based replacement chain that should translate
        # the expression from a simplified domain into a regex based domain
        # that may be correctly compiled into the rest environment then
        # creates the route list, compiling the expression and returns it
        # to the caller method so that it may be used in the current environment
        expression = "^" + expression + "$"
        expression = INT_REGEX.sub(r"(?P[\1>[\\d]+)", expression)
        expression = REGEX_REGEX.sub(r"(?P[\2>\1)", expression)
        expression = REPLACE_REGEX.sub(r"(?P[\4>[\\@\\+\\:\\.\\s\\w-]+)", expression)
        expression = expression.replace("?P[", "?P<")
        return [method, re.compile(expression, re.UNICODE), function, context, opts]

    def load(self, *args, **kwargs):
        if self._loaded: return
        level = kwargs.get("level", None)
        handlers = kwargs.get("handlers", None)
        self._set_global()
        self._load_paths()
        self._load_config()
        self._load_logging(level)
        self._load_settings()
        self._load_handlers(handlers)
        self._load_cache()
        self._load_preferences()
        self._load_bus()
        self._load_session()
        self._load_adapter()
        self._load_manager()
        self._load_execution()
        self._load_request()
        self._load_context()
        self._load_templating()
        self._load_imaging()
        self._load_slugification()
        self._load_bundles()
        self._load_controllers()
        self._load_models()
        self._load_parts()
        self._load_libraries()
        self._load_patches()
        self._load_supervisor()
        self._set_config()
        self._set_variables()
        self._loaded = True

    def unload(self, *args, **kwargs):
        if not self._loaded: return
        self._unload_supervisor()
        self._unload_parts()
        self._unload_models()
        self._unload_execution()
        self._unload_bus()
        self._unload_preferences()
        self._unload_cache()
        self._unload_logging()
        self._loaded = False

    def start(self, refresh = True):
        if self.status == RUNNING: return
        self._print_welcome()
        self.pid = os.getpid()
        self.tid = threading.current_thread().ident
        self.start_time = time.time()
        self.start_date = datetime.datetime.utcnow()
        self.touch_time = "t=%d" % self.start_time
        self._start_controllers()
        self._start_models()
        self._start_supervisor()
        if refresh: self.refresh()
        if self.manager: self.manager.start()
        self.status = RUNNING
        self.trigger("start")

    def stop(self, refresh = True):
        if self.status == STOPPED: return
        self._print_bye()
        self.pid = None
        self.tid = None
        self._stop_controllers()
        self._stop_models()
        self._stop_supervisor()
        if refresh: self.refresh()
        if self.manager: self.manager.stop()
        self.status = STOPPED
        self.trigger("stop")

    def refresh(self):
        self._set_url()

    def info_dict(self):
        return dict(
            name = self.name,
            instance = self.instance,
            service = self.service,
            type = self.type,
            server = self.server,
            server_version = self.server_version,
            server_full = self.server_full,
            host = self.host,
            port = self.port,
            ssl = self.ssl,
            status = self.status,
            uptime = self.get_uptime_s(),
            routes = len(self._routes()),
            configs = len(config.CONFIGS),
            parts = self.get_parts(simple = True),
            libraries = self.get_libraries(map = True),
            platform = PLATFORM,
            identifier = IDENTIFIER,
            appier = VERSION,
            api_version = API_VERSION,
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def fork(self):
        """
        Called upon process forking should be able to restore the child
        process state to a situation where no issue arises.

        This method should be called from within the child process.
        """

        # in case unique identifier regeneration is required a new one is
        # generated for the new child process (proper unique identification)
        self.puid = self.uid
        self.uid = str(uuid.uuid4())

        # verifies if there's an already started manager and adapter and
        # if that's the case resets their state (avoids parent process issues)
        if self.manager: self.manager.restart()
        if self.adapter: self.adapter.reset()

        # if there's a common bus handler it must be reloaded for the current
        # instance as there may be issues with the fork operation
        if self.bus_d: self.bus_d.reload()

        # forces the refreshing of the peers as new ones may have been created
        # this is done by triggering an update peers request
        self.trigger_bus("update_peers")

    def loop(self, callable = lambda: time.sleep(60)):
        # prints a small information message about the event loop that is
        # just going t be started
        self.logger.info("Starting event loop ...")

        # creates the proper handler function that is going to be used in
        # case of signal throwing operation (as expected)
        handler = lambda s, f: sys.exit(0)

        # registers for the proper signal handler so that the system exit
        # exception is raised upon signal trigger
        signint_old = signal.signal(signal.SIGINT, handler)
        sigterm_old = signal.signal(signal.SIGTERM, handler)

        # runs the start operation, effectively starting the infra-structure
        # for the main event loop (as expected)
        self.start()

        # loops continuously over the callable function, waiting
        # for an interruption that will break the loop
        while True:
            try: callable()
            except (KeyboardInterrupt, SystemExit): break

        # restores the old signal handler so that everything remains the same
        # as it's expected by interface (proper base handlers)
        signal.signal(signal.SIGINT, signint_old)
        signal.signal(signal.SIGTERM, sigterm_old)

        # runs the "final" stop operation that will restore the data structures
        # back to the "original"/expected state
        self.stop()

    def serve(
        self,
        server = "legacy",
        host = "127.0.0.1",
        port = 8080,
        ipv6 = False,
        ssl = False,
        key_file = None,
        cer_file = None,
        backlog = socket.SOMAXCONN,
        threaded = False,
        conf = True,
        **kwargs
    ):
        server = config.conf("SERVER", server) if conf else server
        host = config.conf("HOST", host) if conf else host
        port = config.conf("PORT", port, cast = int) if conf else port
        ipv6 = config.conf("IPV6", ipv6, cast = bool) if conf else cer_file
        ssl = config.conf("SSL", ssl, cast = bool) if conf else ssl
        key_file = config.conf("KEY_FILE", key_file) if conf else key_file
        cer_file = config.conf("CER_FILE", cer_file) if conf else cer_file
        backlog = config.conf("BACKLOG", backlog, cast = int) if conf else backlog
        servers = config.conf_prefix("SERVER_") if conf else dict()
        for name, value in servers.items():
            name_s = name.lower()[7:]
            if name_s in EXCLUDED_NAMES: continue
            kwargs[name_s] = value
        kwargs["handlers"] = self.handlers
        kwargs["level"] = self.level
        self.logger.info("Starting '%s' with '%s' ..." % (self.name, server))
        self.server = server
        self.host = host
        self.port = port
        self.ssl = ssl
        self.start()
        method = getattr(self, "serve_" + server)
        names = method.__code__.co_varnames
        if "ipv6" in names: kwargs["ipv6"] = ipv6
        if "ssl" in names: kwargs["ssl"] = ssl
        if "key_file" in names: kwargs["key_file"] = key_file
        if "cer_file" in names: kwargs["cer_file"] = cer_file
        if "backlog" in names: kwargs["backlog"] = backlog
        if threaded: util.BaseThread(
            target = self.serve_final,
            args = (server, method, host, port, kwargs),
            daemon = True,
            name = "Server"
        ).start()
        else: self.serve_final(server, method, host, port, kwargs)

    def serve_final(self, server, method, host, port, kwargs):
        try: return_value = method(host = host, port = port, **kwargs)
        except BaseException as exception:
            lines = traceback.format_exc().splitlines()
            self.logger.critical("Unhandled exception received: %s" % legacy.UNICODE(exception))
            for line in lines: self.logger.warning(line)
            raise
        self.stop()
        self.logger.info("Stopped '%s'' in '%s' ..." % (self.name, server))
        return return_value

    def serve_legacy(self, host, port, **kwargs):
        """
        Starts the serving process for the application using the python's
        legacy WSGI server implementation, this server is considered unstable
        and should only be used for development/testing purposes.

        :type host: String
        :param host: The host name of IP address to bind the server
        to, this value should be represented as a string.
        :type port: int
        :param port: The tcp port for the bind operation of the
        server (listening operation).
        """

        import wsgiref.simple_server
        httpd = wsgiref.simple_server.make_server(host, port, self.application)
        httpd.serve_forever()

    def serve_netius(
        self,
        host,
        port,
        ipv6 = False,
        ssl = False,
        key_file = None,
        cer_file = None,
        backlog = socket.SOMAXCONN,
        **kwargs
    ):
        """
        Starts serving the current application using the hive solutions
        python based web server netius HTPP, this is supposed to be used
        with care as the server is still under development.

        For more information on the netius HTTP servers please refer
        to the https://github.com/hivesolutions/netius site.

        :type host: String
        :param host: The host name of IP address to bind the server
        to, this value should be represented as a string.
        :type port: int
        :param port: The tcp port for the bind operation of the
        server (listening operation).
        :type ipv6: bool
        :param ipv6: If the server should be started under the IPv6 mode
        meaning that a socket is opened for that protocol, instead of the
        typical IPv4 version.
        :type ssl: bool
        :param ssl: If the ssl framework for encryption should be used
        in the creation of the server socket.
        :type key_file: String
        :param key_file: The path to the file containing the private key
        that is going to be used in the SSL communication.
        :type cer_file: String
        :param cer_file: The path to the certificate file to be used in
        the ssl based communication.
        :type backlog: int
        :param backlog: Size of the backlog structure that is going to be
        used to store connections pending to be accepted, the larger the
        value is the bigger is the capacity of the server to accept many
        connections in a short time span.
        """

        util.ensure_pip("netius")
        import netius.servers
        self.server_version = netius.VERSION
        self._server = netius.servers.WSGIServer(self.application, **kwargs)
        self._server.bind("child", lambda s: self.fork())
        self._server.serve(
            host = host,
            port = port,
            ipv6 = ipv6,
            ssl = ssl,
            key_file = key_file,
            cer_file = cer_file,
            backlog = backlog
        )

    def serve_waitress(self, host, port, **kwargs):
        """
        Starts the serving of the current application using the
        python based waitress server in the provided host and
        port as requested.

        For more information on the waitress HTTP server please
        refer to https://pypi.python.org/pypi/waitress.

        :type host: String
        :param host: The host name of IP address to bind the server
        to, this value should be represented as a string.
        :type port: int
        :param port: The tcp port for the bind operation of the
        server (listening operation).
        """

        waitress = util.import_pip("waitress")
        waitress.serve(self.application, host = host, port = port)

    def serve_tornado(self, host, port, ssl = False, key_file = None, cer_file = None, **kwargs):
        util.ensure_pip("tornado")
        import tornado.wsgi
        import tornado.httpserver

        self.server_version = tornado.version

        ssl_options = ssl and dict(
            keyfile = key_file,
            certfile = cer_file
        ) or None

        container = tornado.wsgi.WSGIContainer(self.application)
        self._server = tornado.httpserver.HTTPServer(container, ssl_options = ssl_options)
        self._server.listen(port, address = host)
        instance = tornado.ioloop.IOLoop.instance()
        instance.start()

    def serve_cherry(self, host, port, **kwargs):
        util.ensure_pip("cherrypy")
        try:
            import cherrypy.wsgiserver
            WSGIServer = cherrypy.wsgiserver.CherryPyWSGIServer
            self.server_version = cherrypy.__version__
        except:
            import cheroot.wsgi
            WSGIServer = cheroot.wsgi.Server
            self.server_version = cheroot.__version__

        self._server = WSGIServer(
            (host, port),
            self.application
        )
        try: self._server.start()
        except (KeyboardInterrupt, SystemExit): self._server.stop()

    def serve_gunicorn(self, host, port, workers = 1, **kwargs):
        util.ensure_pip("gunicorn")
        import gunicorn.app.base

        self.server_version = gunicorn.__version__

        class GunicornApplication(gunicorn.app.base.BaseApplication):

            def __init__(self, application, options = None):
                self.application = application
                self.options = options or {}
                gunicorn.app.base.BaseApplication.__init__(self)

            def load_config(self):
                for key, value in legacy.iteritems(self.options):
                    self.cfg.set(key, value)

            def load(self):
                return self.application

        options = dict(
            bind = "%s:%d" % (host, port),
            workers = workers
        )
        self._server = GunicornApplication(self.application, options)
        self._server.run()

    def load_jinja(self, **kwargs):
        try: import jinja2
        except: self.jinja = None; return

        has_async = hasattr(jinja2, "asyncfilters")

        use_cache = not self.is_devel()
        use_cache = config.conf("TEMPLATE_CACHE", use_cache, cast = bool)

        loader = jinja2.FileSystemLoader(self.templates_path)
        auto_reload = False if use_cache else True
        bytecode_cache = jinja2.FileSystemBytecodeCache() if use_cache else None

        self.jinja = jinja2.Environment(
            loader = loader,
            auto_reload = auto_reload,
            bytecode_cache = bytecode_cache,
            extensions = ("jinja2.ext.do",),
            **kwargs
        )

        self.jinja_cache = dict()

        if has_async: self.jinja_async = jinja2.Environment(
            loader = loader,
            auto_reload = auto_reload,
            bytecode_cache = bytecode_cache,
            extensions = ("jinja2.ext.do",),
            enable_async = True,
            **kwargs
        )
        else: self.jinja_async = self.jinja

        self.add_filter(self.to_locale_jinja, "locale", type = "context")
        self.add_filter(self.nl_to_br_jinja, "nl_to_br", type = "eval")
        self.add_filter(self.sp_to_nbsp_jinja, "sp_to_nbsp", type = "eval")

        self.add_filter(self.echo, "echo")
        self.add_filter(self.echo, "handle")
        self.add_filter(self.unset, "unset")
        self.add_filter(self.dumps, "dumps")
        self.add_filter(self.loads, "loads")
        self.add_filter(self.typeof, "type")
        self.add_filter(self.strip, "strip")
        self.add_filter(self.sentence, "sentence")

        self.add_filter(self.script_tag_jinja, "script_tag", type = "eval")
        self.add_filter(self.css_tag_jinja, "css_tag", type = "eval")
        self.add_filter(self.css_tag_jinja, "stylesheet_tag", type = "eval")
        self.add_filter(self.asset_url, "asset_url")

        for name, value in self.context.items(): self.add_global(value, name)

    def add_filter(self, method, name = None, type = None):
        """
        Adds a filter to the current context in the various template
        handlers that support this kind of operation.

        Note that a call to this method may not have any behavior in
        case the handler does not support filters.

        :type method: Method
        :param method: The method that is going to be added as the
        filter handler, by default the method name is used as the name
        for the filter.
        :type name: String
        :param name: The optional name to be used as the filter name
        this is the name to be used in the template.
        :type type: String
        :param type: The type of filter to be added (eg: context, eval
        environ, etc.), if this value is not provided the default
        standard value is going to be used.
        """

        name = name or method.__name__
        function = method.__func__ if hasattr(method, "__func__") else method
        if type == "context": function.contextfilter = True
        if type == "eval": function.evalcontextfilter = True
        if type == "environ": function.environmentfilter = True
        if self.jinja: self.jinja.filters[name] = method
        if self.jinja: self.jinja_async.filters[name] = method

    def remove_filter(self, name):
        if self.jinja and name in self.jinja.filters: del self.jinja.filters[name]
        if self.jinja and name in self.jinja_async.filters: del self.jinja_async.filters[name]

    def add_global(self, symbol, name):
        if self.jinja: self.add_global_jinja(symbol, name)

    def remove_global(self, name):
        if self.jinja: self.remove_global_jinja(name)

    def add_global_jinja(self, symbol, name, targets = None):
        targets = targets or (self.jinja, self.jinja_async)
        for target in targets:
            _globals = getattr(target, "globals")
            _globals[name] = symbol

    def remove_global_jinja(self, name, targets = None):
        targets = targets or (self.jinja, self.jinja_async)
        for target in targets:
            _globals = getattr(target, "globals")
            if not name in _globals: continue
            del _globals[name]

    def load_pil(self):
        try: import PIL.Image
        except: self.pil = None; return
        self.pil = PIL
        self._pil_image = PIL.Image

    def load_pyslugify(self):
        try: import slugify
        except: self.pyslugify = None; return
        self.pyslugify = slugify

    def load_slugier(self):
        self.slugier = True

    def close(self):
        pass

    def routes(self):
        return []

    def all_routes(self):
        return self._BASE_ROUTES + self.user_routes() + self.core_routes()

    def user_routes(self):
        if self._user_routes: return self._user_routes
        routes = self.routes() + self.__routes
        self._user_routes = [App.norm_route(*route) for route in routes]
        return self._user_routes

    def core_routes(self):
        if self._core_routes: return self._core_routes
        self.base_routes = [
            (("GET",), "/static/.*", self.static),
            (("GET",), "/appier/static/.*", self.static_res),
            (("GET",), "/<str:part>/static/.*", self.static_part)
        ]
        self.extra_routes = [
            (("GET",), "/", self.info),
            (("GET",), "/favicon.ico", self.icon),
            (("GET",), "/info", self.info),
            (("GET",), "/version", self.version),
            (("GET",), "/log", self.logging),
            (("GET",), "/debug", self.debug),
            (("GET", "POST"), "/login", self.login),
            (("GET", "POST"), "/logout", self.logout)
        ] if self.service else []
        core_routes = self.part_routes + self.base_routes + self.extra_routes
        self._core_routes = [App.norm_route(*route) for route in core_routes]
        return self._core_routes

    def clear_routes(self):
        """
        Clears the current routes cache (used for route acceleration)
        so that the base structures are re-created on the next request.

        Notice that because re-building the routing cache implies computation
        calling of this method should be reduced to the absolute minimum.
        """

        self.routes_v = None
        self._user_routes = None
        self._core_routes = None

    def application(self, environ, start_response):
        self.prepare()
        try: return self.application_l(environ, start_response)
        finally: self.restore()

    def prepare(self):
        """
        Method responsible for the preparation of the application state
        into the typical structure expected at the start of the handling
        of request received from the top level server infra-structure.
        """

        REQUEST_LOCK.acquire()

    def restore(self):
        """
        Method responsible for the restoring of the application state
        back to normal after the handling of an application request.

        This method should be called safely using the finally keyword
        and the execution of it should avoid the raising of an exception
        so that the application behavior remains static.
        """

        self._request.close()
        self._request = self._mock
        self._own = self
        REQUEST_LOCK.release()

    def application_l(self, environ, start_response):
        # runs a series of assertions to make sure that the integrity
        # of the system is guaranteed (otherwise corruption may occur)
        util.verify(self._request == self._mock)

        # unpacks the various fields provided by the WSGI layer
        # in order to use them in the current request handling
        method = environ["REQUEST_METHOD"]
        path = environ["PATH_INFO"]
        query = environ["QUERY_STRING"]
        script_name = environ["SCRIPT_NAME"]
        content_length = environ.get("CONTENT_LENGTH")
        address = environ.get("REMOTE_ADDR")
        protocol = environ.get("SERVER_PROTOCOL")
        input = environ.get("wsgi.input")
        scheme = environ.get("wsgi.url_scheme")

        # in case the current executing environment is python 3
        # compliant a set of extra operations must be applied to
        # both the path and the script name so that they are
        # properly encoded under the current environment
        if legacy.PYTHON_3: path = legacy.bytes(path).decode("utf-8")
        if legacy.PYTHON_3: script_name = legacy.bytes(script_name).decode("utf-8")

        # converts the received content length (string value) into
        # the appropriate integer representation so that it's possible
        # to use it in the reading of the provided input stream
        content_length_i = int(content_length) if content_length else -1

        # creates the proper prefix value for the request from
        # the script name field and taking into account that this
        # value may be an empty or invalid value
        prefix = script_name if script_name.endswith("/") else script_name + "/"

        # creates the initial request object to be used in the
        # handling of the data has been received not that this
        # request object is still transient as it does not have
        # either the params and the JSON data set in it
        self._request = request.Request(
            owner = self,
            method = method,
            path = path,
            prefix = prefix,
            query = query,
            scheme = scheme,
            address = address,
            protocol = protocol,
            environ = environ,
            session_c = self.session_c
        )

        # sets the original (unset) context for the request handling
        # note that the original (own) context is considered to be the
        # current instance as it's the base for the context retrieval
        self._own = self

        # parses the provided query string creating a map of
        # parameters that will be used in the request handling
        # and then sets it in the request
        params = legacy.parse_qs(query, keep_blank_values = True)
        params = util.decode_params(params)
        self.request.set_params(params)

        # reads the data from the input stream file and then tries
        # to load the data appropriately handling all normal cases
        # (eg JSON, form data, etc.)
        data = None if method in BODYLESS_METHODS else input.read(content_length_i)
        self.request.set_data(data)
        self.request.load_base()
        self.request.load_locale(self.locales)

        # resolves the secret based params so that their content
        # is correctly decrypted according to the currently set secret
        self.request.resolve_params()

        # runs the query (safe) resolution process, so that the unsafe
        # parameters are "correctly" removed from it (as expected)
        self.request.resolve_query_s()

        # sets the global (operative system) locale for according to the
        # current value of the request, this value should be set while
        # the request is being handled after that it should be restored
        # back to the original (unset) value
        self._set_locale()

        # calls the before request handler method, indicating that the
        # request is going to be handled in the next few logic steps
        self.before_request()

        try:
            # handles the currently defined request and in case there's an
            # exception triggered by the underlying action methods, handles
            # it with the proper error handler so that a proper result value
            # is returned indicating the exception
            result = self.handle()

            # "extracts" the data type for the result value coming from the handle
            # method, in case the value is a generator extracts the first value from
            # it so that it may be used  for length evaluation (protocol definition)
            # at this stage it's possible to have an exception raised for a non
            # existent file or any other pre validation based problem
            is_generator, result = asynchronous.ensure_generator(result)
            if is_generator: first = next(result)
            else: first = None

            # tries to determine if the first element of the generator (if existent)
            # is valid and if that's not the case tries to find a fallback
            is_valid = first == None or isinstance(first, legacy.INTEGERS)
            if not is_valid:
                if hasattr(result, "restore"): result.restore(first); first = -1
                else: raise exceptions.OperationalError(
                    message = "No message size defined for generator"
                )
        except BaseException as exception:
            # resets the values associated with the generator based strategy so
            # that the error/exception is handled in the proper (non generator)
            # way and no interference exists for such situation, otherwise some
            # compatibility problems would occur
            is_generator = False
            first = None

            # calls the exception request handler method, indicating that the request
            # has been affected by an exception, useful for handling operations
            self.exception_request(exception)

            # verifies if the current error to be handled is a soft one (not severe)
            # meaning that it's expected under some circumstances, for that kind of
            # situations a less verbose logging operation should be performed
            is_soft = isinstance(exception, (exceptions.NotFoundError,))

            # handles the raised exception with the proper behavior so that the
            # resulting value represents the exception with either a map or a
            # string based value (properly encoded with the default encoding)
            result = self.handle_error(exception)
            if is_soft: self.log_warning(exception)
            else: self.log_error(exception)

            # triggers the on error event indicating that an exception has occurred
            # there are some exceptions that are considered soft and such value is
            # passed as part of the event to the lower layers
            self.trigger("exception", exception, is_soft = is_soft)
        finally:
            # calls the finally request handler method, indicating that the request
            # has finished the current try context, useful for cleanup operations
            self.finally_request()

        # in case the current method required empty responses/result the result
        # is "forced" to be empty so that no specification is
        if method in EMPTY_METHODS: result = ""

        # re-retrieves the data type for the result value, this is required
        # as it may have been changed by an exception handling, failing to do
        # this would create series handling problems (stalled connection)
        result_t = type(result)

        # verifies that the type of the result is a dictionary and if
        # that's the case verifies if it's considered to be empty, for
        # such situations the single result value is set with success
        is_map = result_t == dict
        is_list = result_t in (list, tuple)
        if is_map and not result: result["result"] = "success"

        # retrieves the complete set of warning "posted" during the handling
        # of the current request and in case there's at least one warning message
        # contained in it sets the warnings in the result
        warnings = self.request.get_warnings()
        if is_map and warnings: result["warnings"] = warnings

        # retrieves any pending set cookie directive from the request and
        # uses it to update the set cookie header if it exists
        set_cookie = self.request.get_set_cookie()
        if set_cookie: self.request.set_header("Set-Cookie", set_cookie)

        # verifies if the current response is meant to be serialized as a JSON message
        # this is the case for both the map type of response and the list type type
        # of response as both of them represent a JSON message to be serialized
        is_json = is_map or is_list

        # retrieves the name of the encoding that is going to be used in case the
        # the resulting data need to be converted from unicode
        encoding = self.request.get_encoding()

        # dumps the result using the JSON serializer and retrieves the resulting
        # string value from it as the final message to be sent to the client, then
        # validates that the value is a string value in case it's not casts it as
        # a string using the default "serializer" structure
        result_s = json.dumps(result) if is_json else result
        result_t = type(result_s)
        if result_t == legacy.UNICODE: result_s = result_s.encode(encoding)
        elif not result_t == legacy.BYTES: result_s = legacy.bytes(str(result_s))

        # calculates the final size of the resulting message in bytes so that
        # it may be used in the content length header, note that a different
        # approach is taken when the returned value is a generator, where it's
        # expected that the first yield result is the total size of the message
        result_l = first if is_generator else len(result_s)
        is_empty = self.request.is_empty() and result_l == 0

        # tries to determine if the length of the payload to be sent should be
        # set as part of the headers for the response
        set_length = not is_empty and not result_l in (None, -1)

        # sets the "target" content type taking into account the if the value is
        # set and if the current structure is a map or not
        default_content_type = is_json and "application/json" or "text/plain"
        self.request.default_content_type(default_content_type)

        # sets the default cache control in the request in case none has been
        # defined, this fallback value should be as restrictive as possible,
        # enforcing the re-validation of the server data
        self.request.default_cache_control(self.cache_control)

        # updates the request information with the length that has just been
        # calculated, this allows the request object to know the amount of data
        # that is going to be directly returned via the HTTP server
        self.request.result_l = result_l

        # calls the after request handler that is meant to defined the end of the
        # processing of the request, this creates an extension point for final
        # modifications on the request/response to be sent to the client
        self.after_request()

        # retrieves the (output) headers defined in the current request and extends
        # them with the current content type (JSON) then calls starts the response
        # method so that the initial header is set to the client
        content_type = self.request.get_content_type() or "text/plain"
        cache_control = self.request.get_cache_control()
        code_s = self.request.get_code_s()
        self.request.set_headers_l(BASE_HEADERS)
        self.request.set_header("Content-Type", content_type)
        if cache_control: self.request.set_header("Cache-Control", cache_control)
        if set_length: self.request.set_header("Content-Length", str(result_l))
        if self.secure_headers and self.allow_origin:
            self.request.ensure_header("Access-Control-Allow-Origin", self.allow_origin)
        if self.secure_headers and self.allow_headers:
            self.request.ensure_header("Access-Control-Allow-Headers", self.allow_headers)
        if self.secure_headers and self.allow_methods:
            self.request.ensure_header("Access-Control-Allow-Methods", self.allow_methods)
        if self.secure_headers and self.content_security:
            self.request.ensure_header("Content-Security-Policy", self.content_security)
        if self.secure_headers and self.frame_options:
            self.request.ensure_header("X-Frame-Options", self.frame_options)
        if self.secure_headers and self.xss_protection:
            self.request.ensure_header("X-XSS-Protection", self.xss_protection)
        if self.secure_headers and self.content_options:
            self.request.ensure_header("X-Content-Type-Option", self.content_options)
        headers = self.request.get_headers() or []
        if self.sort_headers: headers.sort()
        start_response(code_s, headers)

        # determines the proper result value to be returned to the WSGI infra-structure
        # in case the current result object is a generator it's returned to the caller
        # method, otherwise a the proper set of chunks is "yield" for the result string
        result = result if is_generator else self.chunks(result_s)
        return result

    def handle(self):
        # in case the request is considered to be already handled (by the middleware)
        # the result is considered to be the one cached in the request, otherwise runs
        # the "typical" routing process that should use the loaded routes to retrieve
        # actions methods that are then used to handle the request
        if self.request.handled: result = self.request.result
        else: result = self.route()

        # returns the result defaulting to an empty map in case no value was
        # returned from the handling method (fallback strategy) note that this
        # strategy is only applied in case the request is considered to be a
        # success one otherwise an empty result is returned instead
        default = {} if self.request.is_success() else ""
        result = default if result == None else result
        return result

    def handle_error(self, exception):
        # retrieves the reference to the class associated with the current instance
        # so that class level operations may be performed
        cls = self.__class__

        # tries to ensure that the UID value of the exception is set,
        # notice that under some extreme occasions it may not be possible
        # to ensure such behaviour (eg: native code based exception)
        if not hasattr(exception, "uid"):
            try: exception.uid = uuid.uuid4()
            except: pass

        # formats the various lines contained in the exception and then tries
        # to retrieve the most information possible about the exception so that
        # the returned map is the most verbose as possible (as expected)
        lines = traceback.format_exc().splitlines()
        lines = cls._lines(lines)
        message = hasattr(exception, "message") and\
            exception.message or str(exception)
        code = hasattr(exception, "code") and\
            exception.code or 500
        headers = hasattr(exception, "headers") and\
            exception.headers or None
        errors = hasattr(exception, "errors") and\
            exception.errors or None
        uid = hasattr(exception, "uid") and\
            exception.uid or None
        session = self.request.session
        sid = session and session.sid
        scope = self.request.context.__class__

        # "saves" both the exception in handling and the stack trace lines in the
        # current request, so that it may be used latter to print exception information
        # for instance for logging purposes (extremely useful)
        self.request.exception = exception
        self.request.stacktrace = lines

        # sets the proper error code for the request, this value has been extracted
        # from the current exception or the default one is used, this must be done
        # to avoid any miss setting of the status code for the current request
        self.request.set_code(code)

        # sets the complete set of (extra) headers defined in the exceptions, these
        # headers may be used to explain the kind of problem that has just been
        # "raised" by the current exception object in handling
        self.request.set_headers(headers)

        # runs the on error processor in the base application object and in case
        # a value is returned by a possible handler it is used as the response
        # for the current request (instead of the normal handler)
        result = self.call_error(exception, code = code, scope = scope, json = True)
        if result: return result

        # creates the resulting dictionary object that contains the various items
        # that are meant to describe the error/exception that has just been raised
        result = dict(
            result = "error",
            name = exception.__class__.__name__,
            message = message,
            code = code,
            traceback = lines,
            uid = uid,
            session = sid
        )
        if errors: result["errors"] = errors
        if not settings.DEBUG: del result["traceback"]

        # returns the resulting map to the caller method so that it may be used
        # to serialize the response in the upper layers (proper handling)
        return result

    def log_error(self, exception, message = None):
        # tries to retrieve the proper template message that is going to be
        # used as the basis for the logging process
        message = message or "Problem handling request: %s"

        # formats the various lines contained in the exception so that the may
        # be logged in the currently defined logger object
        lines = traceback.format_exc().splitlines()

        # print a logging message about the error that has just been "logged"
        # for the current request handling (logging also the traceback lines)
        self.logger.error(message % str(exception))
        for line in lines: self.logger.warning(line)

    def log_warning(self, exception, message = None):
        # tries to retrieve the proper template message that is going to be
        # used as the basis for the logging process
        message = message or "Problem handling request: %s"

        # formats the various lines contained in the exception so that the may
        # be logged in the currently defined logger object
        lines = traceback.format_exc().splitlines()

        # print a logging message about the error that has just been "logged"
        # for the current request handling (logging also the traceback lines)
        # note that is a softer logging with less severity
        self.logger.warning(message % str(exception))
        for line in lines: self.logger.info(line)

    def call_error(self, exception, code = None, scope = None, json = False):
        # retrieves the top level class for the exception for which
        # the error handler is meant to be called
        cls = exception.__class__

        # iterates over the complete set of bases classes for the
        # exception class trying to find the best match for an error
        # handler for the current exception (most concrete first)
        for base in self._bases(cls):
            handler = self._error_handler(base, scope = scope, json = json)
            if handler: break

        # tries (one more time) to retrieve a proper error handler
        # taking into account the exception's error code
        handler = self._error_handler(
            code,
            scope = scope,
            json = json,
            default = handler
        )
        if not handler: return None

        # unpacks the error handler into a tuple containing the method
        # to be called, the scope, the (is) JSON handler flag the global
        # options dictionary/map and the context, notice that the local
        # own variable is changed to the method's context if required and
        # then restored back to original one if required
        method, _scope, _json, _opts, _context = handler
        has_context = hasattr(method, "__self__")
        context = method.__self__ if has_context else self
        _own, self._own = self._own, context
        try:
            if method: result = method(exception)
            if not result == False: return result
        except BaseException as exception:
            self.log_warning(exception)
            return None
        finally:
            self._own = _own
        return None

    def route(self):
        """
        Runs the routing process for the current request to the proper
        action method, this method is responsible for the selective
        handling of the synchronous and asynchronous request.

        It should also be able to route multiple request, but only for
        the asynchronous type of handling.

        :rtype: Object
        :return: The returning value from the action function that was
        used in the handling of the current request.
        """

        # retrieves the currently defined set of routes, this should be
        # handled using a lazy loading strategy, where only the first call
        # will trigger a loading process, the following ones are cached
        routes = self._routes()

        # unpacks the various element from the request, this values are
        # going to be used along the routing process
        method = self.request.method
        path = self.request.path
        params = self.request.params
        data_j = self.request.data_j

        # runs the unquoting of the path as this is required for a proper
        # routing of the request (extra values must be correctly processed)
        # note that the value is converted into an unicode string suing the
        # proper encoding as defined by the HTTP standard
        path_u = util.unquote(path)

        # retrieves both the callback and the mid parameters these values
        # are going to be used in case the request is handled asynchronously
        callback = params.get("callback", None)
        mid = params.get("mid", None)

        # retrieves the mid (message identifier) and the callback URL from
        # the provided list of parameters in case they are defined, these
        # values are going to be used latter in case these is considered to
        # an asynchronous request that should have a callback request
        mid = mid[0] if mid else None
        callback = callback[0] if callback else None

        # iterates over the complete set of routing items that are
        # going to be verified for matching (complete regex collision)
        # and runs the match operation, handling the request with the
        # proper action method associated
        for route in routes:
            # unpacks the current item into the HTTP method, regex and
            # action method and then tries to match the current path
            # against the current regex in case there's a valid match and
            # the current method is valid in the current item continues
            # the current logic (method handing)
            methods_i, regex_i, method_i = route[:3]
            match = regex_i.match(path_u)
            if not method in methods_i or not match: continue

            # verifies if there's a definition of an options map for the current
            # routes in case there's not defines an empty one (fallback)
            item_l = len(route)
            opts_i = route[3] if item_l > 3 else {}

            # tries to retrieve the payload attribute for the current item in case
            # a JSON data value is defined otherwise default to single value (simple
            # message handling)
            if data_j: payload = data_j["payload"] if "payload" in data_j else [data_j]
            else: payload = [data_j]

            # retrieves the number of messages to be processed in the current context
            # this value will have the same number as the callbacks calls for the async
            # type of message processing (as defined under specification)
            mcount = len(payload)

            # sets the initial (default) return value from the action method as unset,
            # this value should be overriden by the various actions methods
            return_v = None

            # updates the value of the JSON (serializable) request taking into account
            # the value of the JSON option for the request to be handled, this value
            # will be used in the serialization of errors so that the error gets properly
            # serialized even in template based events (forced serialization)
            self.request.json = opts_i.get("json", False)

            # tries to retrieve the parameters tuple from the options in the item in
            # case it does not exists defaults to an empty list (as defined in spec)
            param_t = opts_i.get("param_t", [])

            # iterates over all the items in the payload to handle them in sequence
            # as defined in the payload list (first come, first served)
            for payload_i in payload:
                # retrieves the method specification for both the "unnamed" arguments and
                # the named ones (keyword based) so that they may be used to send the correct
                # parameters to the action methods
                method_a = legacy.getargspec(method_i)[0]
                method_kw = legacy.getargspec(method_i)[2]

                # retrieves the various matching groups for the regex and uses them as the first
                # arguments to be sent to the method then adds the JSON data to it, after that
                # the keyword arguments are "calculated" using the provided "get" parameters but
                # filtering the ones that are not defined in the method signature
                groups = match.groups()
                groups = [value_t(value) for value, (value_t, _value_n) in zip(groups, param_t)]
                args = list(groups) + ([] if payload_i == None or not self.payload else [payload_i])
                kwargs = dict([(key, value[0]) for key, value in params.items() if key in method_a or method_kw])

                # in case the current route is meant to be as handled asynchronously
                # runs the logic so that the return is immediate and the handling is
                # deferred to a different thread execution logic
                is_async = opts_i.get("asynchronous", False)
                if is_async:
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
                    has_context = hasattr(method_i, "__self__")
                    context = method_i.__self__ if has_context else self
                    self._own = context
                    self.request.context = context
                    self.request.method_i = method_i
                    self.trigger("before_route", method_i, args, kwargs)
                    return_v = method_i(*args, **kwargs)
                    self.trigger("after_route", method_i, args, kwargs)

            # returns the currently defined return value, for situations where
            # multiple call have been handled this value may contain only the
            # result from the last call
            return return_v

        # raises a runtime error as if the control flow as reached this place
        # no regular expression/method association has been matched
        raise exceptions.NotFoundError(
            message = "Request %s '%s' not handled" % (method, path_u)
        )

    def run_async(self, method, callback, mid = None, args = [], kwargs = {}):
        # generates a new token to be used as the message identifier in case
        # the mid was not passed to the method (generated on client side)
        # this identifier should represent a request uniquely (nonce value)
        mid = mid or util.gen_token()

        def async_method(*args, **kwargs):
            # triggers the before route event indicating the fact that the
            # the method for route is going to be called (with provided arguments)
            self.trigger("before_route", method, args, kwargs)

            # calls the proper method reference (base object) with the provided
            # arguments and keyword based arguments, in case an exception occurs
            # while handling the request the error should be properly serialized
            # suing the proper error handler method for the exception
            try: result = method(*args, **kwargs)
            except BaseException as exception:
                result = self.handle_error(exception)
                self.trigger("exception", exception)

            # calls the after route event that indicates that the call to the route
            # method has just been completed (with provided arguments)
            self.trigger("after_route", method, args, kwargs)

            # verifies if a result dictionary has been created and creates a new
            # one in case it has not, then verifies if the result value is set
            # in the result if not sets it as success (fallback value)
            result = result or dict()
            if not "result" in result: result["result"] = "success"

            try:
                # in case the callback URL is defined sends a post request to
                # the callback URL containing the result as the JSON based payload
                # this value should with the result for the operation
                callback and http.post(callback, data_j = result, params = {
                    "mid" : mid
                })
            except legacy.HTTPError as error:
                data = error.read()
                try:
                    data_s = json.loads(data)
                    message = data_s.get("message", "")
                    lines = data_s.get("traceback", [])
                except:
                    message = data
                    lines = []

                # logs the information about the callback call error, this should
                # include both the main message description but also the complete
                # set of traceback lines for the handling
                self.logger.warning("Async callback (remote) error: %s" % message)
                for line in lines: self.logger.info(line)

        # in case no queueing manager is defined it's not possible to queue
        # the current request and so an error must be raised indicating the
        # problem that has just occurred (as expected)
        if not self.manager:
            raise exceptions.OperationalError(message = "No queue manager defined")

        # adds the current async method and request to the queue manager this
        # method will be called latter, notice that the mid is passed to the
        # manager as this is required for a proper insertion of work
        self.manager.add(
            async_method,
            args = args,
            kwargs = kwargs,
            mid = mid,
            request = self.request
        )
        return mid

    def before_request(self):
        # sets the start time for the handling of the request as
        # the current one, this may be used latter to calculate
        # the duration of the request handling process
        if not self.request.stime: self.request.stime = time.time()

        # runs the "sslify" operation that ensures that proper ssl
        # is defined for the current request, redirecting the request
        # if that's required (no secure connection established)
        self._sslify()

        # retrieves the complete set of custom handlers associated
        # with the before request operation and call the associated
        # method for each of them to run the operation
        handlers = self.custom_handlers("before_request")
        for handler in handlers: handler()

        # triggers the event that indicates the starting of the request
        # handling, allows proper decoupling of modules
        self.trigger("before_request")

    def after_request(self):
        # runs the annotate async operation that verifies if the proper
        # async header is defined and o that situations runs a series
        # of manipulation strategies on the request headers
        self._annotate_async()

        # retrieves the complete set of custom handlers associated
        # with the after request operation and call the associated
        # method for each of them to run the operation
        handlers = self.custom_handlers("after_request")
        for handler in handlers: handler()

        # triggers the event that indicates the ending of the request
        # handling, allows proper decoupling of modules
        self.trigger("after_request")

    def finally_request(self):
        # sets the end time for the handling of the request as
        # the current one, this may be used latter to calculate
        # the duration of the request handling process
        if not self.request.etime: self.request.etime = time.time()

        # performs the flush operation in the request so that all the
        # stream oriented operations are completely performed, this
        # should include things like session flushing (into cookie)
        self.request.flush()

        # resets the locale so that the value gets restored to the original
        # value as it is expected by the current systems behavior, note that
        # this is only done in case the safe flag is active (would create some
        # serious performance problems otherwise)
        if self.safe: self._reset_locale()

        # retrieves the complete set of custom handlers associated
        # with the finally request operation and call the associated
        # method for each of them to run the operation
        handlers = self.custom_handlers("finally_request")
        for handler in handlers: handler()

        # triggers the event that indicates the finally of the request
        # handling, allows proper decoupling of modules
        self.trigger("finally_request")

    def exception_request(self, exception):
        # sets the end time for the handling of the request as
        # the current one, this may be used latter to calculate
        # the duration of the request handling process
        if not self.request.etime: self.request.etime = time.time()

        # retrieves the complete set of custom handlers associated
        # with the exception request operation and call the associated
        # method for each of them to run the operation
        handlers = self.custom_handlers("exception_request")
        for handler in handlers: handler()

        # triggers the event that indicates the exception of the request
        # handling, allows proper decoupling of modules
        self.trigger("exception_request", exception)

    def warning(self, message):
        self.request.warning(message)

    def redirect(self, url, code = 303, params = None, **kwargs):
        # in case there are no explicit parameters provided then the
        # named arguments should be used instead
        if params == None: params = kwargs

        # tries to encode the provided set of parameters into a
        # simpler query string to be added to the redirection URL
        query = http._urlencode(params)
        if query: url += ("&" if "?" in url else "?") + query

        # sets both the (redirection) code and the new location URL
        # values in the current request (response) object
        self.request.code = code
        self.request.set_header("Location", url)

    def delay(self, method, args = [], kwargs = {}):
        """
        Delays the execution of the provided method to be performed
        by the current (execution) manager entity set in the app instance.

        Typically the execution is going to be performed on a separate
        thread from the main one (avoid stalled behaviour), but concrete
        details depend on the (execution) manager implementation.

        :type method: function
        :param method: The function/method that is going to be executed
        using the currently set (execution) manager.
        :type args: List
        :param args: The (unnamed) arguments to be passed to the function
        upon its execution.
        :type kwargs: Dictionary
        :param kwargs: The named arguments to be used in function execution.
        """

        self.manager.add(method, args = args, kwargs = kwargs)

    def schedule(
        self,
        method,
        args = [],
        kwargs = {},
        timeout = 0,
        *_args,
        **_kwargs
    ):
        """
        Schedules the execution of the provided method with the
        arguments and named arguments after the requested timeout.

        This execution is going to be performed after the request
        number of seconds (timeout).

        Preferably the execution is going to be performed on the
        main thread (under an outside event loop manager).

        :type method: function
        :param method: The function/method that is going to be executed
        after the specified amount of seconds on the execution thread.
        :type args: List
        :param args: The (unnamed) arguments to be passed to the function
        upon its execution.
        :type kwargs: Dictionary
        :param kwargs: The named arguments to be used in function execution.
        :type timeout: float
        :param timeout: The requested number of seconds to be used as
        the delay for the function execution.
        :rtype: Handle
        :return: The handle to the scheduled execution, may allow cancellation.
        """

        # creates the simplified (no arguments) callable by creating a clojure
        # based lambda expression, so that the interface to execution is simpler
        callable = lambda: method(*args, **kwargs)

        # determines if the delay operation (on event loop) is present on the
        # the server and if so runs it under the delay execution, otherwise
        # runs it through the legacy (thread) base execution
        has_delay = hasattr(self._server, "delay")
        if has_delay: return self._server.delay(
            callable,
            timeout = timeout,
            *_args, **_kwargs
        )
        else: return self.schedule_legacy(
            callable,
            timeout = timeout,
            *_args, **_kwargs
        )

    def schedule_legacy(self, callable, timeout = 0, safe = False):
        def callable_t():
            time.sleep(timeout)
            callable()

        # tries to retrieve the appropriate normalized timeout value
        # and if the value is zero runs the callable immediately, no
        # need to create a full thread to call the new callable
        timeout = max(0, timeout)
        if timeout == 0: return callable()

        # creates the thread to be used for the callable calling and
        # starts it for asynchronous calling of the callable, notice
        # that that the thread is marked as daemon (avoiding problems
        # with the exist of the current process)
        thread = threading.Thread(target = callable_t, name = "ScheduleLegacy")
        thread.daemon = True
        thread.start()

    def chunks(self, data, size = 32768):
        for index in range(0, len(data), size):
            yield data[index:index + size]

    def email(
        self,
        template,
        sender = None,
        receivers = [],
        cc = [],
        bcc = [],
        subject = "",
        plain_template = None,
        host = None,
        port = None,
        username = None,
        password = None,
        stls = False,
        encoding = "utf-8",
        convert = True,
        headers = {},
        renderer = None,
        html_handler = None,
        plain_handler = None,
        **kwargs
    ):
        # tries to retrieve the URL based definition of the SMTP
        # settings so that they may be used for configuration
        url = config.conf("SMTP_URL", None)
        url_p = legacy.urlparse(url) if url else None
        if url_p:
            host_p, port_p, user_p, password_p, stls_p =\
            url_p.hostname,\
            url_p.port,\
            url_p.username,\
            url_p.password,\
            url_p.scheme == "smtps"
        else:
            host_p, port_p, user_p, password_p, stls_p =\
            None, None, None, None, None

        # runs the defaulting operation for port definition
        # that haven't been set (should follow SMTP defaults)
        if port_p == None: port_p = 25

        # retrieves the complete set of SMTP definitions taking
        # into account the multiple configuration, note that if
        # parameters are passed to the method these take precedence
        # over the configuration based values
        host = host or config.conf("SMTP_HOST", host_p)
        port = port or config.conf("SMTP_PORT", port_p, cast = int)
        username = username or config.conf("SMTP_USER", user_p)
        password = password or config.conf("SMTP_PASSWORD", password_p)
        stls = password or stls or config.conf("SMTP_STARTTLS", stls_p, cast = int)
        stls = True if stls else False

        locale = config.conf("EMAIL_LOCALE", None)
        if locale and not "locale" in kwargs: kwargs["locale"] = locale

        # verifies if the renderer callable is defined and if that's
        # not the case sets the default one (simple template renderer)
        if renderer == None: renderer = self.template

        sender_base = util.email_base(sender)
        receivers_base = util.email_base(receivers)
        cc_base = util.email_base(cc)
        bcc_base = util.email_base(bcc)

        receivers_total = receivers_base + cc_base + bcc_base

        sender_mime = util.email_mime(sender)
        receivers_mime = util.email_mime(receivers)
        cc_mime = util.email_mime(cc)

        parameters = dict(kwargs)
        parameters.update(
            sender = sender,
            receivers = receivers,
            cc = cc,
            bcc = bcc,
            subject = subject,
        )

        html = renderer(template, detached = True, **parameters)
        if plain_template: plain = renderer(plain_template, detached = True, **parameters)
        elif convert: plain = util.html_to_text(html)
        else: plain = legacy.UNICODE("Email rendered using HTML")

        if html_handler: html = html_handler(html)
        if plain_handler: plain = html_handler(plain)

        html = html.encode(encoding)
        plain = plain.encode(encoding)

        mime = smtp.multipart()
        mime["Subject"] = subject
        mime["From"] = sender_mime
        mime["To"] = ", ".join(receivers_mime) if receivers_mime else "undisclosed-recipients:"
        if cc_mime: mime["Cc"] = ", ".join(cc_mime)

        for key, value in headers.items(): mime[key] = value

        plain_part = smtp.plain(plain, encoding = encoding)
        html_part = smtp.html(html, encoding = encoding)
        mime.attach(plain_part)
        mime.attach(html_part)

        smtp.message(
            sender_base,
            receivers_total,
            mime,
            host = host,
            port = port,
            username = username,
            password = password,
            stls = stls
        )

    def html(self, data, content_type = "text/html"):
        self.request.set_content_type(content_type)
        return data

    def json(
        self,
        structure,
        content_type = "application/json",
        encoding = "utf-8",
        sort_keys = False,
        indent = None,
        separators = None,
        **kwargs
    ):
        data = json.dumps(
            structure,
            sort_keys = sort_keys,
            indent = indent,
            separators = separators,
            **kwargs
        )
        data = legacy.bytes(data, encoding = encoding, force = True)
        self.request.set_content_type(content_type)
        return data

    def slugify(self, word):
        """
        Runs the "slugification" process on the provided word,
        this process should reduce the provided word/sentence
        to a simple (ascii compatible) string separated by dash
        characters instead of spaces.

        The final slug value meant to be used for semantic URL
        values.

        :type word: String
        :param word: The word or sentence that is going to be
        "slugified" and reduced.
        :rtype: String
        :return: The final "slugified" version of the provided word,
        this value is typically called the slug.
        :see: http://en.wikipedia.org/wiki/Semantic_URL
        """

        # sets the initial result value as invalid so that in
        # case no proper slugification method is found that is
        # properly detected and an exception is raised
        result = None

        # verifies if the python slugify method is available and
        # if that's the case runs such slugification process
        if result == None and self.pyslugify:
            result = self.slugify_pyslugify(word)

        # check if the (legacy) slugier operation is available
        # and runs that method in case no method has not been
        # run already (avoiding duplicated execution)
        if result == None and self.slugier:
            result = self.slugify_slugier(word)

        # in case no slug value has been returned by any of the
        # slugification methods an exception is raised indicating
        # that no engined for slug operation has been found
        if result == None: raise exceptions.OperationalError(
            message = "No valid slugification engine found"
        )

        # returns the final slug value as the result of the
        # slugification process (to the caller method)
        return result

    def slugify_pyslugify(self, word):
        return self.pyslugify.slugify(word)

    def slugify_slugier(self, word):
        cls = self.__class__
        word = legacy.u(word, encoding = "utf-8", force = True)
        slug = cls._simplify(word)
        slug = SLUGIER_REGEX_1.sub("-", slug)
        slug = slug.strip("-")
        slug = SLUGIER_REGEX_2.sub("-", slug)
        slug = legacy.bytes(slug, encoding = "utf-8", force = True)
        slug = legacy.quote(slug)
        slug = slug.lower()
        slug = legacy.str(slug)
        return slug

    def template(
        self,
        template,
        content_type = "text/html",
        templates_path = None,
        cache = True,
        detached = False,
        locale = None,
        asynchronous = False,
        **kwargs
    ):
        # calculates the proper templates path defaulting to the current
        # instances template path in case no custom value was passed
        templates_path = templates_path or self.templates_path

        # sets the initial value for the result, this value should
        # always contain an utf-8 based string value containing the
        # results of the template engine execution
        result = None

        # determines if the provided template value is a template instance
        # if that's the case some of the assumptions for file path values
        # are ignored and a different path is taken
        is_template = isinstance(template, Template)

        # "resolves" the provided template path, taking into account
        # things like localization, at the end of this method execution
        # the template path should be the best match according to the
        # current framework's rules and definitions
        if not is_template: template = self.template_resolve(
            template,
            templates_path = templates_path,
            locale = locale
        )

        # runs the template args method to export a series of symbols
        # of the current context to the template so that they may be
        # used inside the template as it they were the proper instance
        self.template_args(kwargs)

        # verifies if the target locale for the template has been defined
        # and if thtat's the case updates the keyword based arguments for
        # the current template render to include that value
        if locale: kwargs["_locale"] = locale

        # runs a series of template engine validation to detect the one
        # that should be used for the current context, returning the result
        # for each of them inside the result variable
        if result == None and self.jinja:
            result = self.template_jinja(
                template,
                templates_path = templates_path,
                cache = cache,
                locale = locale,
                asynchronous = asynchronous,
                **kwargs
            )

        # in case no result value is defined (no template engine ran) an
        # exception must be raised indicating this problem
        if result == None: raise exceptions.OperationalError(
            message = "No valid template engine found"
        )

        # in case there's no request currently defined or the template is
        # being rendered in a detached environment (eg: email rendering)
        # no extra operations are required and the result value is returned
        # immediately to the caller method (for processing)
        if not self.request or detached: return result

        # updates the content type vale of the request with the content type
        # defined as parameter for the template running and then returns the
        # resulting (string buffer) value to the caller method
        self.request.set_content_type(content_type)
        return result

    def template_async(self, *args, **kwargs):
        # ensures that the asynchronous support is enabled in the keyword based
        # arguments and then runs a "normal" call to the template method pipelining
        # the provide arguments and keyword arguments
        kwargs["asynchronous"] = True
        return self.template(*args, **kwargs)

    def template_jinja(
        self,
        template,
        templates_path = None,
        cache = True,
        locale = None,
        asynchronous = False,
        **kwargs
    ):
        import jinja2

        # tries to retrieve the proper jinja instance taking into account
        # if the asynchronous mode is enabled or not, this is required to
        # avoid unwanted behaviour in the underlying render method
        jinja = self.jinja_async if asynchronous else self.jinja

        # retrieves the reference to the cache instance currently in use
        # by the main jinja instance to be restored latter if necessary
        _cache = jinja.cache

        # retrieves the file extension for the template to be used in determining
        # the proper autoescape feature enabling value
        extension = self._extension(template)

        if isinstance(templates_path, (list, tuple)): search_path = list(templates_path)
        else: search_path = [templates_path]
        for part in self.parts: search_path.append(part.templates_path)

        # in case cache is requested for the current render operation
        # we'll try to find the correct cache instance taking into account
        # the current context (search path) as for each different sequence
        # of search paths a new cache instance must be used to avoid template
        # key name collision (jinja is not very smart on cache handling),
        # notice that the size used in the creation of the new cache instances is
        # the same as the base "original" jinja environment cache instance capacity
        if cache:
            search_path_t = tuple(search_path)
            cache_i = self.jinja_cache.get(search_path_t, None)
            if cache_i == None:
                cache_i = jinja2.environment.create_cache(_cache.capacity)
                self.jinja_cache[search_path_t] = cache_i

        jinja.autoescape = self._extension_in(extension, ESCAPE_EXTENSIONS)
        jinja.cache = cache_i if cache else None
        jinja.is_async = asynchronous

        try:
            jinja.loader.searchpath = search_path
            jinja.locale = locale
            is_template = isinstance(template, Template)
            if is_template:
                builder = lambda: jinja.from_string(template)
                template = template.get_template("jinja", builder)
            template = jinja.get_template(template)
            if asynchronous: return template.render_async(kwargs)
            else: return template.render(kwargs)
        finally:
            jinja.cache = _cache

    def template_args(self, kwargs, safe = False):
        import appier

        # creates the base dictionary that is going to be used to
        # expose the base/initial symbols to the template engine
        # these values are considered critical for execution
        base = dict(
            appier = appier,
            owner = self,
            own = self.own,
            request = self.request,
            session = self.request.session,
            location = self.request.location,
            location_f = self.request.location_f,
            config = config
        )

        # iterates over both the base and the context values to set
        # their complete set of values in the current named arguments
        # note that if the value is already set and the safe flag is
        # unset no overwrite operation exists (allows inheritance of values)
        for key, value in itertools.chain(
            legacy.iteritems(base),
            legacy.iteritems(self.context)
        ):
            if not safe and key in kwargs: continue
            kwargs[key] = value

    def template_resolve(self, template, templates_path = None, locale = None):
        """
        Resolves the provided template path, using the currently
        defined locale. It tries to find the best match for the
        template file falling back to the default (provided) template
        path in case the best one could not be found.

        An optional templates path value may be used to change
        the default path to be used in the resolution of the template.

        :type template: String
        :param template: Path to the template file that is going to
        be "resolved" trying to find the best locale match.
        :type templates_path: String/List
        :param templates_path: The path to the directory containing the
        template files to be used in the resolution, this value may be
        a sequence of paths instead of a single one.
        :type locale: String
        :param locale: The default locale that is going to be used for the
        loading of the template, in case this value is not defined the
        current request in usage is going to be used to determine locale.
        :rtype: String
        :return: The resolved version of the template file taking into
        account the existence or not of the best locale template.
        """

        # verifies if the templates path value is not a sequence and if
        # that the case the value is encapsulated in a list so that the
        # sequence interface is respected as expected by the method's logic
        is_sequence = type(templates_path) in (list, tuple)
        if not is_sequence: templates_path = [templates_path]

        # tries to define the proper value for the locale that is going to be
        # used as the preference for the resolution of the template and then
        # tries to retrieve the language value from it
        locale = locale or (self.request.locale if hasattr(self.request, "locale") else None)
        language = locale.split("_", 1)[0] if locale else None

        # splits the provided template name into the base and the name values
        # and then splits the name into the base file name and the extension
        # part so that it's possible to re-construct the name with the proper
        # locale naming part included in the name
        base, name = os.path.split(template)
        fname, extension = name.split(".", 1)

        # sets the fallback name as the "original" template path, because
        # that's the default and expected behavior for the template engine
        fallback = template

        # iterates over the complete set of locale values eligible for the
        # resolution (this also takes into account the base language)
        for _locale in (locale, language):
            # in case the current value in iteration is not valid (not set
            # or empty) then the current iteration is not required
            if not _locale: continue

            # creates the base file name for the target (locale based) template
            # and then joins the file name with the proper base path to create
            # the "full" target file name
            target = fname + "." + _locale + "." + extension
            target = base + "/" + target if base else target

            # "joins" the target path and the templates (base) path to create
            # the full path to the target template, then verifies if it exists
            # and in case it does sets it as the template name
            for _templates_path in templates_path:
                target_f = os.path.join(_templates_path, target)
                if not os.path.exists(target_f): continue
                return target

        # runs the same operation for the fallback template name and verifies
        # for its existence in case it exists uses it as the resolved value
        for _templates_path in templates_path:
            fallback_f = os.path.join(_templates_path, fallback)
            if not os.path.exists(fallback_f): continue
            return fallback

        # retrieves the current list of locales for he application and removes
        # any previously "visited" locale value (redundant) so that the list
        # represents the non visited locales by order of preference
        locales = list(self.locales)
        if locale in locales: locales.remove(locale)

        # iterates over the complete list of locales trying to find the any
        # possible existing template that is compatible with the specification
        # note that the order of iteration should be associated with priority
        for locale in locales:
            target = fname + "." + locale + "." + extension
            target = base + "/" + target if base else target
            for _templates_path in templates_path:
                target_f = os.path.join(_templates_path, target)
                if not os.path.exists(target_f): continue
                return target

        # returns the fallback value as the last option available, note that
        # for this situation the resolution process is considered failed
        return fallback

    def send_static(self, path, static_path = None, cache = False):
        return self.static(
            resource_path = path,
            static_path = static_path,
            cache = cache
        )

    def send_file(
        self,
        contents,
        name = None,
        content_type = None,
        etag = None,
        cache = False
    ):
        _etag = self.request.get_header("If-None-Match", None)
        not_modified = etag == _etag and not etag == None
        disposition = "filename=\"%s\"" % name if name else None
        type, _encoding = mimetypes.guess_type(name or "", strict = False)
        content_type = content_type or type or OCTET_TYPE
        if cache: target_s, cache_s = self._cache()
        if content_type: self.content_type(content_type)
        if not_modified: self.request.set_code(304); return ""
        if etag: self.request.set_header("Etag", etag)
        if cache: self.request.set_header("Expires", target_s)
        if cache: self.request.set_header("Cache-Control", cache_s)
        else: self.request.set_header("Cache-Control", "no-cache, must-revalidate")
        if disposition: self.request.set_header("Content-Disposition", disposition)
        return contents

    def send_path(
        self,
        file_path,
        url_path = None,
        name = None,
        content_type = OCTET_TYPE,
        cache = False,
        ranges = True,
        compress = None
    ):
        # defaults the URL path value to the provided file path, this is
        # just a fallback behavior and should be avoided whenever possible
        # to be able to provide the best experience on error messages
        url_path = url_path or file_path or name

        # in case the current operative system is windows based an extra
        # prefix must be pre-pended to the file path so that extra long
        # file names are properly handled (avoiding possible issues)
        if os.name == "nt" and not file_path.startswith("\\\\?\\"):
            file_path = "\\\\?\\" + file_path

        # verifies if the resource exists and in case it does not raises
        # an exception about the problem (going to be serialized)
        if not os.path.exists(file_path):
            raise exceptions.NotFoundError(
                message = "Resource '%s' does not exist" % url_path
            )

        # checks if the path refers a directory and in case it does raises
        # an exception because no directories are valid for static serving
        if os.path.isdir(file_path):
            raise exceptions.NotFoundError(
                message = "Resource '%s' refers a directory" % url_path
            )

        # tries to use the current mime sub system to guess the mime type
        # for the file to be returned in the request and then uses this type
        # to update the request object content type value, note that in case
        # there's a compress operation to be used the proper type is resolved
        type, _encoding = mimetypes.guess_type(
            url_path, strict = True
        )
        if compress:
            has_type = hasattr(self, "type_" + compress)
            type = getattr(self, "type_" + compress)() if has_type else type
        self.request.content_type = type

        # retrieves the last modified timestamp for the file path and
        # uses it to create the etag for the resource to be served
        modified = os.path.getmtime(file_path)
        etag = "appier-%.2f" % modified

        # retrieves the provided etag for verification and checks if the
        # etag remains the same if that's the case the file has not been
        # modified and the response should indicate exactly that
        _etag = self.request.get_header("If-None-Match", None)
        not_modified = etag == _etag

        # in case the file has not been modified a not modified response
        # must be returned inside the response to the client
        if not_modified: self.request.set_code(304); yield 0; return

        # tries to use the current mime sub system to guess the mime type
        # for the file to be returned in the request
        file_type, _encoding = mimetypes.guess_type(
            url_path, strict = True
        )

        # runs the defaulting operation of the file type so that there's
        # always a file type associated with the file path based serving
        # even if not was guessed using the default strategy
        file_type = file_type or content_type

        # tries to determine the proper (content) disposition value for
        # situations where the "target" name is provided
        disposition = "filename=\"%s\"" % name if name else None

        # retrieves the value of the range header value and updates the
        # is partial flag value with the proper boolean value in case the
        # header exists or not (as expected by specification)
        range_s = self.request.get_header("Range", None)
        is_partial = True if range_s else False

        # retrieves the size of the resource file in bytes, this value is
        # going to be used in the computation of the range values, note that
        # this retrieval takes into account the compressor to be used
        if compress: file_size, file = self.compress(file_path, method = compress)
        else: file_size = os.path.getsize(file_path); file = None

        # updates the current request in handling so that the proper file
        # content type is set in with (notifies the user agent for display)
        self.request.content_type = file_type

        # convert the current string based representation of the range
        # into a tuple based presentation otherwise creates the default
        # tuple containing the initial position and the final one
        if is_partial:
            range_s = range_s[6:]
            start_s, end_s = range_s.split("-", 1)
            start = int(start_s) if start_s else 0
            end = int(end_s) if end_s else file_size - 1
            range = (start, end)
        else: range = (0, file_size - 1)

        # creates the string that will represent the content range that is
        # going to be returned to the client in the current request
        content_range_s = "bytes %d-%d/%d" % (range[0], range[1], file_size)

        # in case the cache model is enabled retrieves both the target string
        # value (date in locale format) and the cache string value that defines
        # the proper cache control (including timeout) to be applied
        if cache: target_s, cache_s = self._cache()

        # sets the complete set of headers expected for the current request
        # this is done before the field yielding operation so that the may
        # be correctly sent as the first part of the message sending
        self.request.set_header("Etag", etag)
        if cache: self.request.set_header("Expires", target_s)
        if cache: self.request.set_header("Cache-Control", cache_s)
        else: self.request.set_header("Cache-Control", "no-cache, must-revalidate")
        if is_partial: self.request.set_header("Content-Range", content_range_s)
        if not is_partial and ranges: self.request.set_header("Accept-Ranges", "bytes")
        if disposition: self.request.set_header("Content-Disposition", disposition)

        # in case the current request is a partial request the status code
        # must be set to the appropriate one (partial content)
        if is_partial: self.request.set_code(206)

        # calculates the real data size of the chunk that is going to be
        # sent to the client this must use the normal range approach then
        # yields this result because its going to be used by the upper layer
        # of the framework to "know" the correct content length to be sent
        data_size = range[1] - range[0] + 1
        yield data_size

        # opens the file for binary reading this is going to be used for the
        # complete reading of the contents, suing a generator based approach
        # this way static file serving may be fast and memory efficient
        if file == None: file = open(file_path, "rb")

        try:
            # seeks the file to the initial target position so that the reading
            # starts on the requested starting point as expected
            file.seek(range[0])

            # iterates continuously reading a series of chunks from the
            # the file until no value is returned (end of file) this chunks
            # are going to be yield to the parent method to be sent in a
            # recursive fashion (avoid memory problems)
            while True:
                if not data_size: break
                size = data_size if BUFFER_SIZE > data_size else BUFFER_SIZE
                data = file.read(size)
                if not data: break
                data_l = len(data)
                data_size -= data_l
                yield data
        finally:
            # in case there's an exception in the middle of the reading the
            # file must be correctly, in order to avoid extra leak problems
            file.close()

    def send_url(self, url, name = None, content_type = None, params = None, **kwargs):
        params = params or kwargs or dict()
        if name: self.content_disposition("filename=\"%s\"" % name)
        if content_type: self.content_type(content_type)
        return http.get(url, params = params)

    def send_url_g(self, url, name = None, content_type = None, params = None, **kwargs):
        params = params or kwargs or dict()
        if name: self.content_disposition("filename=\"%s\"" % name)
        if content_type: self.content_type(content_type)
        for value in asynchronous.header_a(): yield value
        yield http.get(url, params = params)

    def send_url_a(self, url, name = None, content_type = None, params = None, **kwargs):
        params = params or kwargs or dict()
        if name: self.content_disposition("filename=\"%s\"" % name)
        if content_type: self.content_type(content_type)
        for value in asynchronous.header_a(): yield value
        for value in extra.get_a(url, params = params):
            yield value
            yield value.result()

    def encoding(self, encoding):
        self.request.set_encoding(encoding)

    def content_type(self, content_type):
        self.request.set_content_type(str(content_type))

    def content_disposition(self, disposition):
        self.request.set_header("Content-Disposition", disposition)

    def content_cache(self):
        target_s, cache_s = self._cache()
        self.request.set_header("Expires", target_s)
        self.request.set_header("Cache-Control", cache_s)

    def custom_handlers(self, key):
        """
        Retrieves the complete set of methods considered as handlers
        of the operation described in the key.

        Most of these methods should have been registered using a decorator
        and so a proper runtime resolution os the method should be required.

        :type key: String
        :param key: The key to be used in the custom handler retrieval.
        :rtype: List
        :return: The complete set of the methods registered as handlers for
        the custom operation described by the provided key.
        """

        # ensures proper pre computation of the routes, this is required
        # to be able to access the custom handlers in a safe manner, with
        # the complete resolution of methods and functions
        self._routes()

        # retrieves the complete set of handlers for the requested key and
        # then computes the method for each as the first element of the list
        handlers = self._CUSTOM_HANDLERS.get(key, [])
        methods = [handler[0] for handler in handlers]
        return methods

    def models_c(self, models = None, sort = True):
        """
        Retrieves the complete set of valid model classes
        currently loaded in the application environment,
        or the the models classes present in the provided
        models module in case it's provided.

        A model class is considered to be a class that is
        inside the models module and that inherits from the
        base model class.

        :type models: Module
        :param models: The module containing the various models
        that are going to be instantiated and returned, if this
        value is not present the base models module is used.
        :type sort: bool
        :param sort: If the loaded set o models should be sorted
        at the end of the loading so that their sequence remains
        the same and the data models is represents in a normal way.
        :rtype: List
        :return: The complete set of model classes that are
        currently loaded in the application environment.
        """

        # defaults the provided models value taking into account
        # also the provided value, in case the value is not provided
        # the module currently set in the application is used instead
        models = models or self.models_i

        # creates the list that will hold the various model
        # class discovered through module analysis
        models_c = []

        # iterates over the complete set of items in the models
        # modules to find the ones that inherit from the base
        # model class for those are the real models
        for _name, value in models.__dict__.items():
            # verifies if the current value in iteration inherits
            # from the top level model in case it does not continues
            # the loop as there's nothing to be done
            try: is_valid = issubclass(value, model.Model)
            except: is_valid = False
            if not is_valid: continue

            # adds the current value in iteration as a new class
            # to the list that hold the various model classes
            models_c.append(value)

        # in case the sort flag is set the loaded models are sorted
        # so that their order remains the same across loadings, this
        # creates a coherent view over the data model
        if sort: models_c.sort()

        # returns the list containing the various model classes
        # to the caller method as expected by definition
        return models_c

    def resolve(self, identifier = "_id", counters = True):
        """
        Resolves the current set of model classes meaning that
        a list of tuples representing the class name and the
        identifier attribute name will be returned. This value
        may than be used to represent the model for instance in
        exporting/importing operations.

        In case the counters boolean flag is set the counters model
        will also be included so that the counters may be restored.

        :type identifier: String
        :param identifier: The name of the attribute that may be
        used to uniquely identify any of the model values.
        :type counters: bool
        :param counters: If the counters "model" should also be
        included in the resolution, so that they may be restored.
        :rtype: List
        :return: A list containing a sequence of tuples with the
        name of the model (short name) and the name of the identifier
        attribute for each of these models.
        """

        # creates the list that will hold the definition of the current
        # model classes with a sequence of name and identifier values
        entities = []

        # retrieves the complete set of model classes registered
        # for the current application and for each of them retrieves
        # the name of it and creates a tuple with the name and the
        # identifier attribute name adding then the tuple to the
        # list of entities tuples (resolution list)
        for model_c in self.models_r:
            name = model_c._name()
            tuple = (name, identifier)
            entities.append(tuple)

        # in case the counters flag is defined the counters tuple containing
        # the counters table name and identifier is added to the entities list
        if counters: entities.append(("counters", identifier))

        # returns the resolution list to the caller method as requested
        # by the call to this method
        return entities

    def fields(self):
        return dict((key, values[0]) for key, values in self.request.args.items())

    def field(
        self,
        name,
        default = None,
        cast = None,
        multiple = None,
        front = True,
        strip = False,
        mandatory = False,
        not_empty = False,
        validation = None,
        message = None
    ):
        return self.get_field(
            name,
            default = default,
            cast = cast,
            multiple = multiple,
            front = front,
            strip = strip,
            mandatory = mandatory,
            not_empty = not_empty,
            validation = validation,
            message = message
        )

    def get_field(
        self,
        name,
        default = None,
        cast = None,
        multiple = None,
        front = True,
        strip = False,
        mandatory = False,
        not_empty = False,
        validation = None,
        message = None
    ):
        value = default
        args = self.request.args
        exists = name in args
        if mandatory and not exists: raise exceptions.OperationalError(
            message = message or "Mandatory field '%s' not found in request" % name,
            code = 400
        )
        if multiple == None: multiple = CASTER_MULTIPLE.get(cast, False)
        if exists: value = args[name] if multiple else args[name][0 if front else -1]
        empty = value == "" if exists else False
        if not_empty and empty: raise exceptions.OperationalError(
            message = message or "Not empty field '%s' is empty in request" % name,
            code = 400
        )
        for validator in validation or []:
            is_sequence = isinstance(validator, (list, tuple))
            if is_sequence: validator, args = validator[0], validator[1:]
            else: args = []
            validator = validator(name, *args)
            object = dict()
            if exists: object[name] = value
            validator(object, None)
        if strip: value = value.strip()
        if cast: cast = CASTERS.get(cast, cast)
        if cast and not value in (None, ""): value = cast(value)
        return value

    def set_field(self, name, value):
        self.request.args[name] = [value]

    def get_fields(self, name, default = None, cast = None, mandatory = False):
        values = default
        args = self.request.args
        exists = name in args
        if mandatory and not exists: raise exceptions.OperationalError(
            message = "Mandatory field '%s' not found in request" % name
        )
        if exists: values = args[name]
        _values = []
        for value in values:
            if cast and not value in (None, ""): value = cast(value)
            _values.append(value)
        return _values

    def set_fields(self, name, values):
        self.request.args[name] = values

    def get_cache_d(self):
        return self.cache_d

    def get_preferences_d(self):
        return self.preferences_d

    def get_bus_d(self):
        return self.bus_d

    def get_request(self):
        return self.request

    def get_session(self):
        return self.request.session

    def get_logger(self):
        return self.logger

    def get_cache(self, key, default = None):
        try: return self.cache_d.get_item(key)
        except KeyError: return default

    def set_cache(self, key, value, expires = None, timeout = None):
        self.cache_d.set_item(key, value, expires = expires, timeout = timeout)

    def try_cache(self, key, flag, default = None):
        if not key in self.cache_d: return default
        _flag, value = self.cache_d[key]
        if not _flag == flag: return default
        return value

    def flag_cache(self, key, flag, value):
        self.set_cache(key, (flag, value))

    def flush_cache(self):
        self.cache_d.flush()

    def get_preference(self, key, default = None):
        return self.preferences_d.get(key, default = default)

    def set_preference(self, key, value):
        self.preferences_d.set(key, value)

    def flush_preferences(self):
        self.preferences_d.flush()

    def bind_bus(self, name, method):
        self.bus_d.bind(name, method)

    def unbind_bus(self, name, method = None):
        self.bus_d.unbind(name, method = None)

    def trigger_bus(self, name, *args, **kwargs):
        self.bus_d.trigger(name, *args, **kwargs)

    def get_uptime(self):
        current_date = datetime.datetime.utcnow()
        delta = current_date - (self.start_date if self.start_time else current_date)
        return delta

    def get_uptime_s(self, count = 2):
        uptime = self.get_uptime()
        uptime_s = self._format_delta(uptime)
        return uptime_s

    def get_model(self, name, raise_e = False):
        model = self.models.get(name, None)
        if not model and raise_e:
            raise exceptions.NotFoundError(
                message = "Model not found '%s'" % name
            )
        return model

    def get_controller(self, name, own = False, raise_e = False):
        controller = self.controllers.get(name, None)
        if not controller and raise_e:
            raise exceptions.NotFoundError(
                message = "Controller not found '%s'" % name
            )
        if own and controller: self._own = controller
        return controller

    def get_part(self, name, own = False, raise_e = False):
        part_m = self.parts_m.get(name, None)
        if not part_m and raise_e:
            raise exceptions.NotFoundError(
                message = "Part not found '%s'" % name
            )
        if not part_m: return None
        part = part_m.get("part", None)
        if own and part: self._own = part
        return part

    def get_bundle(self, name = None, context = None, split = True):
        if name == None: name = self.request.locale
        if context: bundles = self.bundles_context.get(context, {})
        else: bundles = self.bundles
        bundle = bundles.get(name, None)
        if bundle: return bundle
        if split and name:
            base = name.split("_", 1)[0]
            bundle = bundles.get(base, None)
            if bundle: return bundle
        name = self._best_locale(name)
        return bundles.get(name, None)

    def get_adapter(self):
        return self.adapter

    def get_manager(self):
        return self.manager

    def get_parts(self, update = True, simple = False, sort = True):
        parts = list(self.parts_l)
        if sort: parts.sort(key = lambda v: v["name"])
        if simple: parts = [value["name"] for value in parts]
        return parts

    def get_libraries(self, update = True, map = False, sort = True):
        if update: self._update_libraries()
        if map: return self.libraries
        libraries = legacy.items(self.libraries)
        if sort: libraries.sort()
        return libraries

    def is_loaded(self):
        return self._loaded

    def is_parent(self):
        return os.getpid() == self.pid

    def is_child(self):
        return not self.is_parent()

    def is_main(self):
        return threading.current_thread().ident == self.tid

    def is_devel(self):
        if not self.level: return False
        return self.level < logging.INFO

    def serialize(self, value):
        if value in legacy.STRINGS: return value
        return json.dumps(value)

    def echo(self, value):
        return value

    def unset(self, value, default = "", empty = False, extra = ()):
        if empty and extra: extra = tuple(list(extra) + [""])
        elif empty and not extra: extra = ("",)
        if self.is_unset(value, extra = extra): return default
        return value

    def dumps(self, value, ensure_ascii = False):
        return json.dumps(value, ensure_ascii = ensure_ascii)

    def loads(self, value):
        return json.loads(value)

    def typeof(self, value):
        return type(value)

    def strip(self, value):
        value = re.sub(" +", " ", value)
        value = value.replace("\r\n", " ")
        value = value.replace("\r", " ")
        value = value.replace("\n", " ")
        return value

    def sentence(self, value):
        value = self.strip(value)
        if not value.endswith("."): value += "."
        return value

    def url_for(
        self,
        type,
        filename = None,
        query = None,
        params = None,
        absolute = False,
        touch = True,
        session = False,
        compress = None,
        base_url = None,
        *args,
        **kwargs
    ):
        result = self._url_for(
            type,
            filename = filename,
            query = query,
            params = params,
            touch = touch,
            session = session,
            compress = compress,
            *args,
            **kwargs
        )
        if result == None: raise exceptions.AppierException(
            message = "Cannot resolve path for '%s'" % type
        )
        if absolute:
            base_url = base_url if base_url else self.base_url()
            if base_url: result = base_url + result
        return result

    def asset_url(self, filename):
        return self.url_for("static", "assets/" + filename)

    def base_url(self):
        return config.conf("BASE_URL", self.local_url)

    def dump_url(
        self,
        url,
        type = None,
        escape = True,
        encoding = "utf-8",
        timeout = 3600,
        force = False
    ):
        if self.request.partial and not force: return ""

        is_absolute = url.startswith(("http://", "https://", "//"))
        is_relative = not is_absolute

        if url.startswith("//"):
            prefix = "http" if self.ssl else "https"
            url = prefix + ":" + url

        key = url
        if type: key += ":" + type
        if encoding: key += ":" + encoding

        # tries to retrieve the data contents with the provided key from
        # the cache and in case that fails runs the remote/local retrieval
        # process that may block the current processing
        data = self.get_cache(key)
        if not data:
            # runs the proper retrieval process taking into account if the
            # URL is relative (local retrieval) or if it's a remote process
            # and the HTTP client should be executed in a sync fashion , note
            # that both responses are compliant with the typical python interface
            # for HTTP responses (from urllib)
            if is_relative: response = self.get(url)
            else: _data, response = http.get(url, handle = True)

            # reads the response payload contents and then unpacks the response
            # gathering the headers dictionary structure
            data = response.read()
            headers = response.info()

            # retrieves the cache control header and parses it creating a dictionary
            # of key to value fields so that it's possible to try to retrieve the
            # max age value to use it to defined the proper timeout
            cache_control = headers.get("Cache-Control", None)
            cache_l = [value.strip() for value in cache_control.split(",")]
            cache_t = []
            for cache_e in cache_l:
                parts = cache_e.split("=", 1)
                parts = parts if len(parts) > 1 else (parts[0], None)
                cache_t.append(parts)
            cache_d = dict(cache_t)
            max_age = cache_d.get("max-age", None)
            if max_age: timeout = int(max_age)

            # in case the type of the resource is css an extra replace operation
            # on the urls must be performed so that the base URL is added to all
            # the resources, this is required so that relative urls are fixed
            if type == "css":
                base, _name = url.rsplit("/", 1)
                base = legacy.bytes(base)
                data = CSS_ABS_REGEX.sub(b"url(" + base + b"/\\2)", data)

            # stores the data that was retrieved in the current's app cache structure
            # with the timeout that was retrieve either from the cache control header
            # or the value coming from the default parameter value in call
            self.set_cache(key, data, timeout = timeout)

        if encoding and legacy.is_bytes(data): data = data.decode(encoding)
        if escape: data = self.escape_template(data)

        return data

    def inline(self, filename):
        resource_path = os.path.join(self.static_path, filename)
        file = open(resource_path, "rb")
        try: data = file.read()
        finally: file.close()
        return data

    def touch(self, url):
        return url + "?" + self.touch_time

    def acl(self, token):
        return util.check_login(self, token = token, request = self.request)

    def to_locale(
        self,
        value,
        locale = None,
        context = None,
        default = None,
        fallback = True
    ):
        value_t = type(value)
        is_sequence = value_t in (list, tuple)
        if is_sequence:
            return self.serialize([
                self.to_locale(
                    value,
                    locale = locale,
                    context = context,
                    default = default,
                    fallback = fallback
                ) for value in value
            ])
        locale = locale or self.request.locale
        if locale:
            bundle = self.get_bundle(locale, context = context) or {}
            result = bundle.get(value, None)
            if not result == None: return result
            language = locale.split("_", 1)[0]
            bundle = self.get_bundle(language, context = context) or {}
            result = bundle.get(value, None)
            if not result == None: return result
        if fallback:
            return self.to_locale(
                value,
                locale = self._locale_d,
                context = context,
                default = default,
                fallback = False
            )
        return value if default == None else default

    def has_locale(self, value, locale = None, context = None):
        locale = locale or self.request.locale
        bundle = self.get_bundle(locale, context = context) or {}
        return value in bundle

    def quote(self, value, encoding = "utf-8"):
        value = legacy.bytes(value, encoding = encoding, force = True)
        value = legacy.quote(value)
        value = legacy.UNICODE(value)
        return value

    def unquote(self, value, encoding = "utf-8"):
        value = str(value)
        value = legacy.unquote(value)
        value = legacy.u(value, encoding = encoding, force = True)
        return value

    def nl_to_br(self, value):
        return value.replace("\n", "<br/>\n")

    def sp_to_nbsp(self, value):
        return value.replace(" ", "&nbsp;")

    def is_unset(self, value, extra = ()):
        return self.is_unset_jinja(value, extra = extra)

    def is_unset_jinja(self, value, extra = ()):
        import jinja2
        if isinstance(value, jinja2.Undefined): return True
        if value in (None,): return True
        if value in extra: return True
        return False

    def escape_template(self, value):
        return self.escape_jinja(value)

    def escape_jinja(self, value):
        import jinja2
        return jinja2.Markup(value)

    def escape_jinja_f(self, callable, eval_ctx, value, *args, **kwargs):
        import jinja2
        if eval_ctx.autoescape: value = legacy.UNICODE(jinja2.escape(value))
        value = callable(value, *args, **kwargs)
        if eval_ctx.autoescape: value = jinja2.Markup(value)
        return value

    def to_locale_jinja(self, ctx, value, locale = None, context = None):
        locale = locale or ctx.environment.locale
        return self.to_locale(value, locale = locale, context = context)

    def nl_to_br_jinja(self, eval_ctx, value):
        return self.escape_jinja_f(self.nl_to_br, eval_ctx, value)

    def sp_to_nbsp_jinja(self, eval_ctx, value):
        return self.escape_jinja_f(self.sp_to_nbsp, eval_ctx, value)

    def script_tag(self, value):
        return "<script type=\"text/javascript\" src=\"%s\"></script>" % value

    def script_tag_jinja(self, eval_ctx, value):
        return self.escape_jinja_f(self.script_tag, eval_ctx, value)

    def css_tag(self, value):
        return "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\" />" % value

    def css_tag_jinja(self, eval_ctx, value):
        return self.escape_jinja_f(self.css_tag, eval_ctx, value)

    def date_time(self, value, format = "%d/%m/%Y"):
        """
        Formats the provided as a date string according to the
        provided date format.

        Assumes that the provided value represents a float string
        and that may be used as the based timestamp for conversion.

        :type value: String
        :param value: The base timestamp value string that is going
        to be used for the conversion of the date string.
        :type format: String
        :param format: The format string that is going to be used
        when formatting the date time value.
        :rtype: String
        :return: The resulting date time string that may be used
        to represent the provided value.
        """

        # tries to convert the provided string value into a float
        # in case it fails the proper string value is returned
        # immediately as a fallback procedure
        try: value_f = float(value)
        except: return value

        # creates the date time structure from the provided float
        # value and then formats the date time according to the
        # provided format and returns the resulting string
        date_time_s = datetime.datetime.utcfromtimestamp(value_f)
        date_time_s = date_time_s.strftime(format)
        is_unicode = legacy.is_unicode(date_time_s)
        return date_time_s if is_unicode else date_time_s.decode("utf-8")

    def static(
        self,
        data = {},
        resource_path = None,
        static_path = None,
        cache = True,
        ranges = False,
        compress = None,
        prefix_l = 8
    ):
        # retrieves the proper static path to be used in the resolution
        # of the current static resource that is being requested
        static_path = static_path or self.static_path

        # retrieves the remaining part of the path excluding the static
        # prefix and uses it to build the complete path of the file and
        # then normalizes it as defined in the specification
        resource_path_o = resource_path or self.request.path[prefix_l:]
        resource_path_f = os.path.join(static_path, resource_path_o)
        resource_path_f = os.path.abspath(resource_path_f)
        resource_path_f = os.path.normpath(resource_path_f)

        # verifies if the provided path starts with the contents of the
        # static path in case it does not it's a security issue and a proper
        # exception must be raised indicating the issue
        is_sub = resource_path_f.startswith(static_path)
        if not is_sub: raise exceptions.SecurityError(
            message = "Invalid or malformed path",
            code = 401
        )

        # runs the send (file) operation for the static file, this should
        # raise exception for error situations or return a generator object
        # for the sending of the file in case of success, the cache flag should
        # control the server side caching using etag values
        return self.send_path(
            resource_path_f,
            url_path = resource_path_o,
            cache = cache,
            ranges = ranges,
            compress = compress
        )

    def static_res(self, data = {}):
        static_path = os.path.join(self.res_path, "static")
        return self.static(
            data = data,
            static_path = static_path,
            prefix_l = 15
        )

    def static_part(self, part, data = {}):
        # tries to retrieve the part structure to be able
        # to resolve the static file and in case no resolution
        # is possible raises a not found error
        part_s = self.get_part(part)
        if not part_s: raise exceptions.NotFoundError(
            message = "Part not found '%s'" % part,
        )

        # sends the static information taking into account the
        # provided data and the base static path of the part
        # notice that the prefix length is dynamically calculated
        # taking into account the size of the part string
        return self.static(
            data = data,
            static_path = part_s.static_path,
            prefix_l = len(part) + 9
        )

    def icon(self, data = {}):
        pass

    def info(self, data = {}):
        return self.json(
            self.info_dict(),
            sort_keys = True
        )

    def version(self, data = {}):
        return self.json(
            dict(
                api_version = API_VERSION
            ),
            sort_keys = True
        )

    @util.private
    def logging(self, data = {}, count = None, level = None):
        if not settings.DEBUG:
            raise exceptions.OperationalError(message = "Not in DEBUG mode")
        count = int(count) if count else 100
        level = level if level else None
        return dict(
            messages = self.handler_memory.get_latest(
                count = count,
                level = level
            )
        )

    @util.private
    def debug(self, data = {}):
        if not settings.DEBUG:
            raise exceptions.OperationalError(message = "Not in DEBUG mode")
        return dict(
            info = self.info(data),
            manager = self.manager.info()
        )

    def login(self, data = {}):
        params = self.request.get_params()
        secret = self.request.params.get("secret", (None,))[0]
        self.auth(**params)

        self.request.session.ensure()
        sid = self.request.session.sid

        self.on_login(sid, secret, **params)

        return dict(
            token = sid
        )

    def logout(self, data = {}):
        self.on_logout()

    def auth(self, username, password, **kwargs):
        is_valid = username == settings.USERNAME and password == settings.PASSWORD
        if not is_valid: raise exceptions.AppierException(
            message = "Invalid credentials provided",
            code = 403
        )

    def on_login(self, sid, secret, username = "undefined", **kwargs):
        self.request.session["username"] = username
        if secret: self.request.session["secret"] = secret

    def on_logout(self):
        if not self.request.session: return
        if "username" in self.request.session:
            del self.request.session["username"]

    @classmethod
    def _level(cls, level):
        """
        Converts the provided logging level value into the best
        representation of it, so that it may be used to update
        a logger's level of representation.

        This method takes into account the current interpreter
        version so that no problem occur.

        :type level: String/int
        :param level: The level value that is meant to be converted
        into the best representation possible.
        :rtype: int
        :return: The best representation of the level so that it may
        be used freely for the setting of logging levels under the
        current running interpreter.
        """

        level_t = type(level)
        if level_t == int: return level
        if level == None: return level
        if level == "SILENT": return log.SILENT
        if hasattr(logging, "_checkLevel"):
            return logging._checkLevel(level)
        return logging.getLevelName(level)

    @classmethod
    def _simplify(cls, value):
        value = value.lower()
        for origin, target in defines.SLUG_PERMUTATIONS:
            origin = legacy.u(origin)
            value = value.replace(origin, target)
        return value

    @classmethod
    def _lines(cls, lines):
        return [line.decode("utf-8", "ignore") if legacy.is_bytes(line) else\
            line for line in lines]

    @classmethod
    def _format_extended(
        cls,
        exception,
        offset = 8,
        encoding = "utf-8",
        template = "File \"%s\", line %d, in %s"
    ):
        # ensure that the provided template is properly converted
        # into an unicode string proper unicode output expected
        template = legacy.u(template)

        # creates the list that is going to hold the complete set
        # of formatted item from the stack
        formatted = []

        # tries to extract the stack trace of the current exception
        # from all the available strategies, note that using the
        # execution info should be always considered a fallback
        stacktrace = exception.__traceback__ if\
            hasattr(exception, "__traceback__") else None
        stacktrace = stacktrace if stacktrace else sys.exc_info()[2]
        stack = traceback.extract_tb(stacktrace)

        # iterates over the complete set of items in the stack that
        # has been extracted from the traceback values, so that a proper
        # set of structured line may be constructed from it
        for item in stack:
            # creates the list that is going to be populated with the
            # complete target lines for the current stack item in iteration
            lines = []

            # unpacks the stack item tuple into its components that are
            # going to be processed for structure
            path, lineno, context, line = item

            # runs the decoding operation in the context and line
            # values so that they can properly be placed as an unicode
            # strings in any context (if required)
            context = context.decode(encoding, "ignore") if\
                legacy.is_bytes(context) else context
            line = line.decode(encoding, "ignore") if\
                legacy.is_bytes(line) else line

            # opens the current file in stack trace and reads the complete
            # contents from it so that the target lines may be read
            file = open(path, "rb")
            try: contents = file.read()
            finally: file.close()

            # decodes the complete file using the most used encoding (blind
            # guess) and ignoring possible parsing errors
            contents_d = contents.decode(encoding, "ignore")

            # generates a new random identifier for the current stack item
            # this is going to be used to identify it univocally
            id = str(uuid.uuid4())

            # normalizes the currently extracted path by ensuring that it's
            # absolute and the running the normalization process on it
            path = os.path.abspath(path)
            path = os.path.normpath(path)

            # tries to find the proper eol (end of line) character by trying
            # to find one between two different strategies
            eol = b"\n" if contents.find(b"\n") else b"\r"

            # splits the contents data around the newline character so that
            # we can access the complete set of lines from the file
            contents_l = contents.split(eol)

            # calculates the zero based index range of lines that are going
            # to be used for the gathering (avoids overflow)
            start = max(lineno - (offset + 1), 0)
            end = min(lineno + offset, len(contents_l)) - 1

            # iterates over the "calculated" range to be able to compile the
            # complete set of line maps that describe each line
            for index in legacy.xrange(start, end + 1):
                _line = contents_l[index]
                _line = _line.rstrip()
                _line = _line.decode(encoding, "ignore") if legacy.is_bytes(_line) else _line
                _lineno = index + 1
                is_target = _lineno == lineno
                lines.append(
                    dict(
                        line = _line,
                        lineno = _lineno,
                        is_target = is_target
                    )
                )

            # creates the "contiguous" buffer of lines, that may be used to
            # directly print the complete set of lines in the structure
            lines_b = legacy.u("\n").join((line["line"] for line in lines))

            # runs the template for the path, so that it's possible to better
            # understand the origin of the path execution
            path_f = template % (path, lineno, context)

            # creates the dictionary that contains the complete set of information
            # about the current line in the stack and then runs the pipeline of
            # operation in it to properly process it
            item_d = dict(
                id = id,
                path = path,
                path_f = path_f,
                line = line,
                lineno = lineno,
                context = context,
                start = start,
                end = end,
                contents = contents,
                contents_d = contents_d,
                lines = lines,
                lines_b = lines_b
            )
            cls._extended_handle(item_d)

            # adds the newly created formatted item to the list of formatted
            # items to be returned at the end of the method execution
            formatted.append(item_d)

        # returns the "final" set of formatted stack items that may be
        # used to better "understand" the current "stack trace"
        return formatted

    @classmethod
    def _extended_handle(cls, item_d):
        cls._extended_path(item_d)
        cls._extended_git(item_d)

    @classmethod
    def _extended_path(cls, line_d):
        # determines if the extended git functionality is currently
        # enabled and if that's not the case returns immediately
        enabled = config.conf("EXTENDED_PATH", True, cast = bool)
        if not enabled: return

        # populates the line dictionary with the canonical URL associated
        # with the file for the current line in processing
        path = line_d["path"]
        path_url = "file:///%s" % path
        line_d["path_url"] = path_url

    @classmethod
    def _extended_git(cls, line_d):
        # determines if the extended git functionality is currently
        # enabled and if that's not the case returns immediately
        enabled = config.conf("EXTENDED_GIT", False, cast = bool)
        if not enabled: return

        # retrieves the required information from the line of the stack
        # and then retrieves the directory path from the current line path
        path, lineno = line_d["path"], line_d["lineno"]
        directory_path = os.path.dirname(path)

        # retrieves the reference to the top level repository
        # directory that is going to be used to "calculate"
        # the relative path inside the repository
        repo_path = git.Git.get_repo_path(path = directory_path)
        if not repo_path: return

        # calculates the relative path
        relative_path = os.path.relpath(path, repo_path)
        relative_path = relative_path.replace("\\", "/")

        # in case the relative path refers a top directory
        # then this file is not considered as part of the
        # repository (belongs to different top level directory)
        if relative_path.startswith("../"): return

        file_name = os.path.basename(path)

        origin = git.Git.get_origin(path = directory_path)
        branch = git.Git.get_branch(path = directory_path)
        origin_d = git.Git.parse_origin(origin)

        hostname = origin_d["hostname"]
        url_path = origin_d["path"]

        if hostname == "bitbucket.org":
            line_d["git_service"] = "bitbucket.org"
            line_d["git_url"] = "https://bitbucket.org%s/src/%s/%s#%s-%d" %\
                (url_path, branch, relative_path, file_name, lineno)

        if hostname == "github.com":
            line_d["git_service"] = "github.com"
            line_d["git_url"] = "https://github.com%s/blob/%s/%s#L%d" %\
            (url_path, branch, relative_path, lineno)

    def _load_paths(self):
        # retrieves a series of abstract references to be used
        # for the resolution of the various required paths
        cls = self.__class__
        module_name = cls.__module__
        module = sys.modules[module_name]
        is_abstract = cls == App

        # retrieves and sets the complete set of path values
        # that are going to be used through the application
        self.appier_path = os.path.dirname(__file__)
        self.base_path = os.path.dirname(module.__file__)
        self.base_path = os.path.abspath(self.base_path)
        self.base_path = os.path.normpath(self.base_path)
        self.root_path = os.path.join(self.base_path, "..")
        self.root_path = os.path.abspath(self.root_path)
        self.root_path = os.path.normpath(self.root_path)
        self.res_path = os.path.join(self.appier_path, "res")
        self.static_path = os.path.join(self.base_path, "static")
        self.controllers_path = os.path.join(self.base_path, "controllers")
        self.models_path = os.path.join(self.base_path, "models")
        self.templates_path = os.path.join(self.base_path, "templates")
        self.bundles_path = os.path.join(self.base_path, "bundles")

        # verifies if the current execution is abstract app level
        # and if that's the case returns immediately as no path
        # changing is meant to occur (not required)
        if is_abstract: return

        # changes the base system path so that both the base and the
        # root path are present and defined as the priority (first entry)
        sys.path = [path for path in sys.path if not path in\
            (self.base_path, self.root_path)]
        sys.path.insert(0, self.base_path)
        sys.path.insert(0, self.root_path)

    def _load_config(self, apply = True):
        # tries to determine if there's an instance value defined for the
        # current execution environment as this value may be used to load
        # more concrete configuration files
        instance = config.conf("INSTANCE", None)
        instance = config.conf("PROFILE", instance)

        # extracts both the normalized naming for the current instance and
        # the class name for the same (to be used for config file loading)
        name = util.camel_to_underscore(self.name)
        class_name = util.camel_to_underscore(self.__class__.__name__)

        # constructs the base list to be used for the file loading using
        # the base (appier) config naming and the app naming ones
        names = [
            config.FILE_NAME,
            config.FILE_TEMPLATE % name,
            config.FILE_TEMPLATE % class_name
        ]

        # in case there's an instance naming defined extends the names list
        # with the more concrete files for the current instance
        if instance: names.extend([
            config.FILE_TEMPLATE % instance,
            config.FILE_TEMPLATE % (name + "." + instance),
            config.FILE_TEMPLATE % (class_name + "." + instance)
        ])

        # converts the names list into a tuple (immutable) and then runs the
        # load operation on the configuration file for the current base path
        # note that the home based paths are also going to be used
        names = tuple(names)
        config.load(names = names, path = self.base_path)

        # in case the apply flag is set applies the current configuration
        # effectively setting some of the value in the instance
        if apply: self._apply_config()

    def _load_logging(
        self,
        level = None,
        set_default = True,
        format_base = log.LOGGING_FORMAT,
        format_tid = log.LOGGING_FORMAT_TID
    ):
        level_s = config.conf("LEVEL", None)
        format = config.conf("LOGGING_FORMAT", None)
        self.level = level
        self.level = self.level or self._level(level_s)
        self.level = self.level or logging.INFO
        self.formatter = log.ThreadFormatter(format or format_base)
        self.formatter.set_tid(format or format_tid)
        self.logger = logging.getLogger(self.name)
        self.logger.parent = None
        self.logger.setLevel(self.level)
        if not set_default: return

        # retrieves the reference to the default logger (global)
        # and set the level of it to the defined one, so that even
        # the modules that use the global logger are coherent
        logger = logging.getLogger()
        logger.setLevel(self.level)

    def _unload_logging(self):
        # in case no logger is currently defined it's not possible
        # to run the unloading process for it, returns immediately
        if not self.logger: return

        # iterates over the complete set of handlers registered
        # for the logging and tries to remove them from the
        # current logger (unregistration process)
        for handler in self.handlers:
            if not handler: continue
            if not handler in self.logger.handlers: continue
            self.logger.removeHandler(handler)

        # unsets the various logging related attributes from the
        # current instance, this way no more access to logging is
        # allow or possible (note that no further unload is possible)
        self.level = None
        self.formatter = None
        self.logger = None

    def _load_dummy_logging(self, level = None):
        level_s = config.conf("LEVEL", None)
        self.level = level
        self.level = self.level or self._level(level_s)
        self.level = self.level or logging.INFO
        self.logger = log.DummyLogger()

    def _load_settings(self):
        settings.DEBUG = config.conf("DEBUG", settings.DEBUG, cast = bool)
        settings.USERNAME = config.conf("USERNAME", settings.USERNAME)
        settings.PASSWORD = config.conf("USERNAME", settings.PASSWORD)
        settings.DEBUG = settings.DEBUG or self.is_devel()

    def _load_handlers(self, handlers = None, set_default = True):
        # retrieves a series of configuration values that are going to
        # be used in the control of certain logging features
        file_log = config.conf("FILE_LOG", False, cast = bool)
        stream_log = config.conf("STREAM_LOG", True, cast = bool)
        memory_log = config.conf("MEMORY_LOG", True, cast = bool)
        syslog_host = config.conf("SYSLOG_HOST", None)
        syslog_port = config.conf("SYSLOG_PORT", None, cast = int)
        syslog_proto = config.conf("SYSLOG_PROTO", "udp")
        syslog_kwargs = dict(socktype = socket.SOCK_STREAM) if\
            syslog_proto in ("tcp",) else dict()
        syslog_log = True if syslog_host else False

        # tries to determine the default syslog port in case no port
        # is defined and syslog logging is enabled
        if not syslog_port and syslog_log:
            syslog_port = log.SYSLOG_PORTS.get(syslog_proto)

        # retrieves the reference to the default logger that is going to be
        # used to set the handlers in case the set default flag is set
        default_logger = logging.getLogger()

        # creates the various logging file names and then uses them to
        # try to construct the full file path version of them taking into
        # account the current operative system in use
        info_name = self.name + ".log"
        error_name = self.name + ".err"
        info_path = info_name if os.name == "nt" else "/var/log/" + info_name
        error_path = error_name if os.name == "nt" else "/var/log/" + error_name

        # "computes" the correct log levels that are going to be used in the
        # logging of certain handlers (most permissive option)
        info_level = self.level if self.level > logging.INFO else logging.INFO
        error_level = self.level if self.level > logging.ERROR else logging.ERROR

        # verifies if the current used has access ("write") permissions to the
        # currently defined file paths, otherwise default to the base name
        if file_log and not self._has_access(info_path, type = "a"): info_path = info_name
        if file_log and not self._has_access(error_path, type = "a"): error_path = error_name

        # creates both of the rotating file handlers that are going to be used
        # in the file logging of the current appier infra-structure note that
        # this logging handlers are only created in case the file log flag is
        # active so that no extra logging is used if not required
        try: self.handler_info = logging.handlers.RotatingFileHandler(
            info_path,
            maxBytes = MAX_LOG_SIZE,
            backupCount = MAX_LOG_COUNT
        ) if file_log else None
        except: self.handler_info = None
        try: self.handler_error = logging.handlers.RotatingFileHandler(
            error_path,
            maxBytes = MAX_LOG_SIZE,
            backupCount = MAX_LOG_COUNT
        ) if file_log else None
        except: self.handler_error = None

        # creates the complete set of handlers that are  required or the
        # current configuration and the "joins" them under the handlers
        # list that my be used to retrieve the set of handlers
        self.handler_stream = logging.StreamHandler() if stream_log else None
        self.handler_syslog = logging.handlers.SysLogHandler(
            (syslog_host, syslog_port), **syslog_kwargs
        ) if syslog_log else None
        self.handler_memory = log.MemoryHandler() if memory_log else None
        self.handlers = handlers or (
            self.handler_info,
            self.handler_error,
            self.handler_stream,
            self.handler_syslog,
            self.handler_memory
        )

        # runs the "cleanup" operation on the handlers so that only the
        # ones that are considered valid are going to be set, this will
        # also convert the possible handlers tuple into a list so that
        # it may be changed at any time during runtime
        self.handlers = [handler for handler in self.handlers if handler]

        # updates the various handler configuration and then adds all
        # of them to the current logger with the appropriate formatter
        if self.handler_info:
            self.handler_info.setLevel(info_level)
            self.handler_info.setFormatter(self.formatter)
        if self.handler_error:
            self.handler_error.setLevel(error_level)
            self.handler_error.setFormatter(self.formatter)
        if self.handler_stream:
            self.handler_stream.setLevel(self.level)
            self.handler_stream.setFormatter(self.formatter)
        if self.handler_syslog:
            formatter = log.BaseFormatter(
                log.LOGGIGN_SYSLOG % self.name_i,
                datefmt = "%Y-%m-%dT%H:%M:%S.000000+00:00",
                wrap = True
            )
            self.handler_syslog.setLevel(self.level)
            self.handler_syslog.setFormatter(formatter)
        if self.handler_memory:
            self.handler_memory.setLevel(self.level)
            self.handler_memory.setFormatter(self.formatter)

        # runs the extra logging step for the current state, meaning that
        # some more handlers may be created according to the logging config
        self._extra_logging(self.level, self.formatter)

        # iterates over the complete set of handlers defined in the default
        # logger to remove them, as new ones are going to be created, this
        # operation is only performed in case the set default flag is set
        for handler in list(default_logger.handlers) if set_default else []:
            default_logger.removeHandler(handler)

        # iterates over the complete set of handlers currently registered
        # to add them to the current logger infra-structure so that they
        # are used when logging functions are called
        for handler in self.handlers:
            if not handler: continue
            self.logger.addHandler(handler)
            if not set_default: continue
            default_logger.addHandler(handler)

    def _load_cache(self):
        # tries to retrieve the value of the cache configuration and in
        # defaulting to an invalid value in case it's not defined
        cache_s = config.conf("CACHE", None)

        # runs the normalization process for the cache name string and
        # tries to retrieve the appropriate class reference for the cache
        # and uses it to create the instance that is going to be used
        if cache_s: cache_s = cache_s.capitalize() + "Cache"
        if cache_s and hasattr(cache, cache_s):
            self.cache_c = getattr(cache, cache_s)
        self.cache_d = self.cache_c(owner = self)

    def _unload_cache(self):
        # verifies if the cache instance is defined if that's not the case
        # returns the control flow immediately, nothing to be done
        if not self.cache_d: return

        # runs the unloading process for the cache instance (should release
        # it) and then unsets the current instance (not going to be used anymore)
        self.cache_d.unload()
        self.cache_d = None

    def _load_preferences(self):
        # tries to retrieve the value of the preferences configuration and in
        # defaulting to an invalid value in case it's not defined
        preferences_s = config.conf("PREFERENCES", None)

        # runs the normalization process for the preferences name string and
        # tries to retrieve the appropriate class reference for the preferences
        # and uses it to create the instance that is going to be used
        if preferences_s: preferences_s = preferences_s.capitalize() + "Preferences"
        if preferences_s and hasattr(preferences, preferences_s):
            self.preferences_c = getattr(preferences, preferences_s)
        self.preferences_d = self.preferences_c(owner = self)

    def _unload_preferences(self):
        # verifies if the preferences instance is defined if that's not the case
        # returns the control flow immediately, nothing to be done
        if not self.preferences_d: return

        # runs the unloading process for the preferences instance (should release
        # it) and then unsets the current instance (not going to be used anymore)
        self.preferences_d.unload()
        self.preferences_d = None

    def _load_bus(self):
        # tries to retrieve the value of the bus configuration and in
        # defaulting to an invalid value in case it's not defined
        bus_s = config.conf("BUS", None)

        # runs the normalization process for the bus name string and
        # tries to retrieve the appropriate class reference for the bus
        # and uses it to create the instance that is going to be used
        if bus_s: bus_s = bus_s.capitalize() + "Bus"
        if bus_s and hasattr(bus, bus_s):
            self.bus_c = getattr(bus, bus_s)
        self.bus_d = self.bus_c(owner = self)

    def _unload_bus(self):
        # verifies if the bus instance is defined if that's not the case
        # returns the control flow immediately, nothing to be done
        if not self.bus_d: return

        # runs the unloading process for the bus instance (should release
        # it) and then unsets the current instance (not going to be used anymore)
        self.bus_d.unload()
        self.bus_d = None

    def _load_session(self):
        # tries to retrieve the value of the session configuration and in
        # case it's not defined returns to the caller immediately
        session_s = config.conf("SESSION", None)
        if not session_s: return

        # runs the normalization process for the session name string and
        # tries to retrieve the appropriate class reference for the session
        # from the session module, in case it's not found ignores it so that
        # the default session class is used instead
        session_s = session_s.capitalize() + "Session"
        if not hasattr(session, session_s): return
        self.session_c = getattr(session, session_s)

    def _load_adapter(self):
        # tries to retrieve the value of the adapter configuration and in
        # case it's not defined returns to the caller immediately
        adapter_s = config.conf("ADAPTER", None)
        if not adapter_s: return

        # converts the naming of the adapter into a capital case one and
        # then tries to retrieve the associated class for proper instantiation
        # in case the class is not found returns immediately
        adapter_s = adapter_s.capitalize() + "Adapter"
        if not hasattr(data, adapter_s): return
        self.adapter = getattr(data, adapter_s)()

    def _load_manager(self):
        # tries to retrieve the value of the manager configuration and in
        # case it's not defined returns to the caller immediately
        manager_s = config.conf("MANAGER", None)
        if not manager_s: return

        # converts the naming of the manager into a capital case one and
        # then tries to retrieve the associated class for proper instantiation
        # in case the class is not found returns immediately
        manager_s = manager_s.capitalize() + "Manager"
        if not hasattr(asynchronous, manager_s): return
        self.manager = getattr(asynchronous, manager_s)(self)

    def _load_execution(self):
        # creates the thread that it's going to be used to
        # execute the various background tasks and starts
        # it, providing the mechanism for execution
        execution.background_t = execution.ExecutionThread()
        background_t = execution.background_t
        background_t.start()

    def _unload_execution(self):
        # stop the execution thread so that it's possible to
        # the process to return the calling
        background_t = execution.background_t
        background_t and background_t.stop()

    def _load_request(self):
        # creates a new mock request and sets it under the currently running
        # application so that it may switch on and off for the handling of
        # the various requests for the application, note that this is always
        # going to be the request to be used while working outside of the
        # typical web context (as defined for the specification)
        locale = self._base_locale()
        self._mock = request.MockRequest(
            locale = locale,
            session_c = self.session_c
        )
        self._request = self._mock

    def _load_context(self):
        self.context["echo"] = self.echo
        self.context["dumps"] = self.dumps
        self.context["loads"] = self.loads
        self.context["typeof"] = self.typeof
        self.context["strip"] = self.strip
        self.context["sentence"] = self.sentence
        self.context["url_for"] = self.url_for
        self.context["asset_url"] = self.asset_url
        self.context["dump_url"] = self.dump_url
        self.context["inline"] = self.inline
        self.context["touch"] = self.touch
        self.context["acl"] = self.acl
        self.context["to_locale"] = self.to_locale
        self.context["quote"] = self.quote
        self.context["unquote"] = self.unquote
        self.context["nl_to_br"] = self.nl_to_br
        self.context["sp_to_nbsp"] = self.sp_to_nbsp
        self.context["script_tag"] = self.script_tag
        self.context["css_tag"] = self.css_tag
        self.context["date_time"] = self.date_time
        self.context["field"] = self.field
        self.context["zip"] = zip
        self.context["time"] = time
        self.context["datetime"] = datetime

    def _load_templating(self):
        self.load_jinja()

    def _load_imaging(self):
        self.load_pil()

    def _load_slugification(self):
        self.load_pyslugify()
        self.load_slugier()

    def _load_bundles(self, bundles_path = None, method = None):
        # defaults the current bundles path in case it has not been
        # provided, the default value to be used is going to be the
        # bundles path of the application (default loading)
        bundles_path = bundles_path or self.bundles_path

        # defaults the "register" method value with the default register
        # method to be used by the bundles
        method = method or self._register_bundle

        # creates the base dictionary that will handle all the loaded
        # bundle information and sets it in the current application
        # object reference so that may be used latter on
        bundles = self.bundles if hasattr(self, "bundles") else dict()
        self.bundles = bundles

        # creates the dictionary that is going to be used in the loading
        # of the context specific values, can be used to provide an extra
        # layer of context to a certain localization, gives a sense of
        # ownership to the provided set of locale strings
        bundles_context = self.bundles_context if\
            hasattr(self, "bundles_context") else dict()
        self.bundles_context = bundles_context

        # verifies if the current path to the bundle files exists in case
        # it does not returns immediately as there's no bundle to be loaded
        if not os.path.exists(bundles_path): return

        # list the bundles directory files and iterates over each of the
        # files to load its own contents into the bundles "registry"
        paths = os.listdir(bundles_path)
        for path in paths:
            # joins the current (base) bundles path with the current path
            # in iteration to create the full path to the file and opens
            # it trying to read its JSON based contents
            path_f = os.path.join(bundles_path, path)
            file = open(path_f, "rb")
            try: data = file.read(); data = data.decode("utf-8")
            except: continue
            finally: file.close()
            try: data_j = json.loads(data)
            except: continue

            # unpacks the current path in iteration into the base name,
            # locale string and file extension to be used in the registration
            # of the data in the bundles registry
            try: _base, locale, _extension = path.split(".", 2)
            except: continue

            # registers the new bundle information under the current system
            # this should extend the current registry with new information so
            # that it becomes available to the possible end-user usage
            method(data_j, locale)

    def _unload_bundles(self, bundles_path = None):
        return self._load_bundles(
            bundles_path = bundles_path,
            method = self._unregister_bundle
        )

    def _load_controllers(self):
        # tries to import the controllers module and in case it
        # fails (no module is returned) returns the control flow
        # to the caller function immediately (nothing to be done)
        controllers = self._import("controllers")
        if not controllers: return

        # iterate over all the items in the controller module
        # trying to find the complete set of controller classes
        # to set them in the controllers map
        for key, value in controllers.__dict__.items():
            # in case the current value in iteration is not a class
            # continues the iteration loop, nothing to be done for
            # non class value in iteration
            is_class = type(value) in (type, meta.Indexed)
            if not is_class: continue

            # verifies if the current value inherits from the base
            # controller class and in case it does not continues the
            # iteration cycle as there's nothing to be done
            is_controller = issubclass(value, controller.Controller)
            if not is_controller: continue

            # creates a new controller instance providing the current
            # app instance as the owner of it and then sets the
            # resulting instance in the controllers map and list
            _controller = value(self)
            self.controllers[key] = _controller
            self.controllers_l.append(_controller)

    def _load_models(self):
        # sets the various default values for the models structures,
        # this is required to avoid any problems with latter loading
        # as the variables must be defined up in the process
        self.models_r = list()
        self.models_d = dict()

        # runs the importing of the models module/package and in case
        # no models are found returns immediately as there's nothing
        # remaining to be done for the loading of the models
        self.models_i = self._import("models")
        if not self.models_i: return

        # retrieves the complete set of model classes from the loaded
        # modules/packages, these are going to be used in registration
        models_c = self.models_c(models = self.models_i)

        # sets the initial version of the model classes that are being
        # used under the current application, this sequence may change
        # with the loading of additional parts and other structures,
        # these models are considered to be "registered" for application
        self.models_r = list(models_c)
        self.models_d = structures.OrderedDict()
        self.models_d[self.name_b] = models_c

        # runs the named base registration of the models so that they may
        # directly accessed using a key to value based access latter on
        self._register_models(models_c)

    def _unload_models(self):
        for model_c in self.models_r: model_c.teardown()

    def _load_parts(self):
        # tries to retrieve the possible dynamic list of parts to be
        # loaded (dynamically), these parts should have their base
        # module defined as the package in pip and then the tail should
        # be the variable full name from the base module
        parts = config.conf("PARTS", [], cast = list)

        # "resets" the sequence that is going to be used to store
        # the map information for the various parts to be loaded
        self.parts_l = []
        self.parts_m = dict()

        # converts the current sequence of parts (may be a tuple)
        # into a list so that it may be changed properly
        self.parts = list(self.parts)

        # iterates over the complete set of dynamic (string based) parts
        # to be loaded and dynamically imports them adding the loaded classes
        # to the list of parts for the current instance
        for part in parts:
            # splits the part string name into the head (module/package name)
            # and the tail to be used in full path discovery, then tries to
            # run the import pip operation in the package to import it, in case
            # the import fails continues the loop (nothing to be done)
            head, tail = part.split(".", 1)
            module = util.import_pip(head)
            if not module: continue

            # sets the loaded module as the reference attribute to be used in
            # the start of the recursion and then runs iterations on the various
            # attributes of the full attribute path value
            value = module
            for name in tail.split("."):
                value = getattr(value, name)

            # adds the "final" resolved attribute to the list of part classes as
            # this attribute should represent the part class
            self.parts.append(value)

        # creates the list that will hold the final set of parts
        # properly instantiated an initialized
        parts = []

        # iterates over the complete set of parts, that may
        # be either classes (require instantiation) or instances
        # to register the current manager (pre-setup operation)
        for part in self.parts:
            # verifies if the current part in is a class or an instance
            # and acts accordingly for each case (instantiating if required)
            is_class = inspect.isclass(part)
            if is_class: part = part(owner = self)
            else: part.register(self)

            # retrieves the base name for the part according to its
            # canonical definition (simplified name)
            name = part.name()

            # adds the "loaded" part to the list of parts and then sets
            # the part in the current application using its name, this
            # should provide the primary way to interact with the part
            parts.append(part)
            setattr(self, name + "_part", part)

            # creates the dictionary that contains the information on the
            # the part this is going to be used as the based unit for latter
            # usage at runtime retrieval (required), notice that it is started
            # with the reference to the part instance (runtime usage)
            part_m = dict(part.info())
            part_m["part"] = part

            # retrieves the "common" names that are going to be given to
            # the part, to be used as the reference for latter retrieval
            name = part_m["name"]
            class_name = part_m["class_name"]

            # adds the part map information to the parts list and then sets
            # that same information in the map of parts with name key index
            self.parts_l.append(part_m)
            self.parts_m[name] = part_m
            self.parts_m[class_name] = part_m

        # updates the list of parts registered in the application
        # with the list that contains them properly initialized, so
        # that all of them are guaranteed to be part instance (not classes)
        self.parts = parts

        # iterates (again) over the complete set of parts to properly load
        # all of their components
        for part in self.parts:
            # runs the concrete implementation of the part loader so that
            # the part is properly loaded according to the specification
            self._load_part(part)

    def _unload_parts(self):
        # iterates over the complete set of parts currently registered
        # and runs the unload operation on each of them
        for part in self.parts: self._unload_part(part)

    def _load_libraries(self):
        self._update_libraries()

    def _load_patches(self):
        import email.charset
        patch_json = config.conf("PATH_JSON", True, cast = bool)
        patch_email = config.conf("PATH_EMAIL", True, cast = bool)
        if patch_json: json._default_encoder = util.JSONEncoder()
        if patch_email: email.charset.add_charset(
            "utf-8",
            header_enc = email.charset.QP,
            body_enc = email.charset.BASE64,
            output_charset = "utf-8"
        )

    def _load_supervisor(self):
        # runs the initial bind operations for both the update and the
        # (new) peer events responsible for the global status consistency
        self.bind_bus("update_peers", self._on_update_peers)
        self.bind_bus("peer", self._on_peer)
        self.bind_bus("peer-%s" % self.uid, self._on_self)

    def _unload_supervisor(self):
        # runs the unbind operation for the global events related with the
        # peer updating operations (no longer needed)
        self.unbind_bus("update_peers", self._on_update_peers)
        self.unbind_bus("peer", self._on_peer)
        self.unbind_bus("peer-%s" % self.uid, self._on_self)

    def _add_handlers(self, logger):
        for handler in self.handlers:
            if not handler: continue
            logger.addHandler(handler)

    def _load_part(self, part):
        # retrieves the various characteristics of the part and uses
        # them to start some of its features (eg: routes and models)
        # this should be the main way of providing base extension
        name = part.name()
        routes = part.routes()
        models = part.models()

        # extends the currently defined routes for parts with the routes
        # that have just been retrieved for the current part, this should
        # enable the access to the new part routes, notice that the routes
        # cache is invalidated/cleared to avoid possible route errors
        self.part_routes.extend(routes)
        self.clear_routes()

        # retrieves the complete set of models classes for the part
        # using the models module as reference and then runs the register
        # operation for each of them, after that extends the currently
        # "registered" model classes with the ones that were just loaded
        models_c = self.models_c(models = models) if models else []
        if models_c: self.models_r.extend(models_c)
        if models_c: self.models_d[name] = models_c
        self._register_models(models_c)

        # runs the loading process for the bundles associated with the
        # current part that is going to be loaded (adding the bundles)
        # note that these bundles will be treated equally to the others
        self._load_bundles(bundles_path = part.bundles_path)

        # loads the part, this should initialize the part structure
        # and make its service available through the application
        part.load()

    def _unload_part(self, part):
        # retrieves the various characteristics of the part and uses
        # them to start some of its features (eg: routes and models)
        # this should be the main way of providing base extension
        name = part.name()
        routes = part.routes()
        models = part.models()

        # runs the "concrete" part unloading process this should properly
        # disabled the installed structures of the part
        part.unload()

        # runs the unloading process for the bundles associated with the
        # current part that is going to be loaded (removing the bundles)
        # note that these bundles will be treated equally to the others
        self._unload_bundles(bundles_path = part.bundles_path)

        # retrieves the complete set of models classes for the part
        # using the models module as reference and then runs the unregister
        # operation for each of them, after that reduces the currently
        # "registered" model classes with the ones that were just loaded
        models_c = self.models_c(models = models) if models else []
        for model_c in models_c: model_c.teardown()
        if models_c: self.models_r.extend(models_c)
        if models_c: self.models_d[name] = models_c
        self._unregister_models(models_c)

        # reduces the currently defined routes for parts with the routes
        # that have just been retrieved for the current part, this should
        # disable the access to the part routes, notice that the routes
        # cache is invalidated/cleared to avoid possible route errors
        for route in routes: self.part_routes.remove(route)
        self.clear_routes()

    def _register_model(self, model_c):
        name = model_c._name()
        cls_name = model_c.__name__
        und_name = model_c._under()
        sng_name = model_c._under(plural = False)
        if name in self.models: raise exceptions.OperationalError(
            message = "Duplicated model '%s' in registry" % name
        )
        if cls_name in self.models: raise exceptions.OperationalError(
            message = "Duplicated model '%s' in registry" % cls_name
        )
        if und_name in self.models: raise exceptions.OperationalError(
            message = "Duplicated model '%s' in registry" % und_name
        )
        if sng_name in self.models: raise exceptions.OperationalError(
            message = "Duplicated model '%s' in registry" % sng_name
        )
        self.models[name] = model_c
        self.models[cls_name] = model_c
        self.models[und_name] = model_c
        self.models[sng_name] = model_c
        self.models_l.append(model_c)

    def _unregister_model(self, model_c):
        name = model_c._name()
        cls_name = model_c.__name__
        und_name = model_c._under()
        sng_name = model_c._under(plural = False)
        if name in self.models: del self.models[name]
        if cls_name in self.models: del self.models[cls_name]
        if und_name in self.models: del self.models[und_name]
        if sng_name in self.models: del self.models[sng_name]
        self.models_l.remove(model_c)

    def _register_models(self, models_c):
        for model_c in models_c: self._register_model(model_c)

    def _unregister_models(self, models_c):
        for model_c in models_c: self._unregister_model(model_c)

    def _register_models_m(self, models, name = None):
        """
        Registers a module containing a series of models classes
        into the current models registry.

        This should be considered the primary method to be called
        for bulk models registration.

        :type models: Module
        :param models: The module that "contains" a series of model
        classes.
        :type name: String
        :param name: The name to be used to identify the modules
        models under a directory (default to app name).
        """

        name = name or self.name
        models_c = self.models_c(models = models) if models else []
        if models_c: self.models_r.extend(models_c)
        if models_c: self.models_d[name] = models_c
        self._register_models(models_c)

    def _register_bundle(self, extra, locale, context = None):
        # retrieves a possible existing map for the current locale in the
        # registry and updates such map with the loaded data, then re-updates
        # the reference to the locale in the current bundle registry
        bundle = self.bundles.get(locale, {})
        bundle.update(extra)
        self.bundles[locale] = bundle

        # in case the context is defined then there should be an
        # extra registration operation for such context
        if context:
            bundle_context = self.bundles_context.get(context, {})
            bundle_context_l = bundle_context.get(locale, {})
            bundle_context_l.update(extra)
            bundle_context[locale] = bundle_context_l
            self.bundles_context[context] = bundle_context

    def _unregister_bundle(self, extra, locale, context = None, strict = False):
        bundle = self.bundles[locale]
        for key in extra:
            if not strict and not key in bundle: continue
            del bundle[key]
        if not bundle: del self.bundles[locale]

        if context:
            bundle_context = self.bundles_context[context]
            bundle_context_l = bundle_context[locale]
            for key in extra:
                if not strict and not key in bundle_context_l: continue
                del bundle_context_l[key]
            if not bundle_context_l: del bundle_context[locale]
            if not bundle_context: del self.bundles_context[context]

    def _print_welcome(self):
        self.logger.info("Booting %s %s (%s) ..." % (NAME, VERSION, PLATFORM))
        for file_path in config.CONFIG_F:
            self.logger.info("Using '%s'" % file_path)
        self.logger.info("Using '%s', '%s' and '%s'" % (
            self.session_c.__name__,
            self.adapter.__class__.__name__,
            self.manager.__class__.__name__
        ))

    def _print_bye(self):
        self.logger.info("Finishing %s %s (%s) ..." % (NAME, VERSION, PLATFORM))

    def _start_controllers(self):
        for model in self.controllers_l:
            model.register(lazy = self.lazy)

    def _stop_controllers(self):
        for model in self.controllers_l:
            model.unregister(lazy = self.lazy)

    def _start_models(self):
        for model in self.models_l:
            model.register(lazy = self.lazy)

    def _stop_models(self):
        for model in self.models_l:
            model.unregister(lazy = self.lazy)

    def _start_supervisor(self):
        # retrieves the global supervisor interval value and uses
        # it as the base timeout on the supervisor by starting the
        # first update operation
        interval = config.conf("SUPERVISOR_INTERVAL", 60.0, cast = float)
        self._schedule_peers(timeout = interval)

    def _stop_supervisor(self):
        pass

    def _add_route(self, *args, **kwargs):
        self.__routes.append(args)
        self.clear_routes()

    def _remove_route(self, *args, **kwargs):
        self.__routes.remove(args)
        self.clear_routes()

    def _add_error(self, error, function, scope = None, json = False, opts = None, context = None):
        method, _name = self._resolve(function, context_s = context)
        handlers = self._ERROR_HANDLERS[error]
        if not [method, scope, json, opts, context] in handlers:
            handlers.append([method, scope, json, opts, context])

    def _remove_error(self, error, function, scope = None, json = False, opts = None, context = None):
        method, _name = self._resolve(function, context_s = context)
        handlers = self._ERROR_HANDLERS[error]
        handlers.remove([method, scope, json, opts, context])

    def _add_exception(self, exception, function, scope = None, json = False, opts = None, context = None):
        method, _name = self._resolve(function, context_s = context)
        handlers = self._ERROR_HANDLERS[exception]
        if not [method, scope, json, opts, context] in handlers:
            handlers.append([method, scope, json, opts, context])

    def _remove_exception(self, exception, function, scope = None, json = False, opts = None, context = None):
        method, _name = self._resolve(function, context_s = context)
        handlers = self._ERROR_HANDLERS[exception]
        handlers.remove([method, scope, json, opts, context])

    def _add_custom(self, key, function, opts = None, context = None):
        method, _name = self._resolve(function, context_s = context)
        handlers = self._CUSTOM_HANDLERS[key]
        if not [method, opts, context] in handlers:
            handlers.append([method, opts, context])

    def _remove_custom(self, key, function, opts = None, context = None):
        method, _name = self._resolve(function, context_s = context)
        handlers = self._CUSTOM_HANDLERS[key]
        handlers.remove([method, opts, context])

    def _set_config(self):
        config.conf_s("APPIER_NAME", self.name)
        config.conf_s("APPIER_INSTANCE", self.instance)
        config.conf_s("APPIER_BASE_PATH", self.base_path)

    def _set_global(self):
        global APP
        APP = self

    def _set_variables(self):
        self.description = self._description()

    def _apply_config(self):
        """
        Applies a series of configuration related values to the current
        instance should be able to normalized many of its values.

        Some of the values are constructed by appending multiple values.
        """

        self.instance = config.conf("INSTANCE", None)
        self.instance = config.conf("PROFILE", self.instance)
        self.name = config.conf("NAME", self.name)
        self.logo_url = config.conf("LOGO_URL", self.logo_url)
        self.logo_square_url = config.conf("LOGO_SQUARE_URL", self.logo_square_url)
        self.copyright = config.conf("COPYRIGHT", self.copyright)
        self.copyright_year = config.conf("COPYRIGHT_YEAR", self.copyright_year)
        self.copyright_url = config.conf("COPYRIGHT_URL", self.copyright_url)
        self.force_ssl = config.conf("FORCE_SSL", False, cast = bool)
        self.force_host = config.conf("FORCE_HOST", None)
        self.secret = config.conf("SECRET", self.secret)
        self.name_b = self.name
        self.name_i = self.name + "-" + self.instance if self.instance else self.name
        self.name = self.name_i

    def _update_libraries(self):
        """
        Runs the update/flush operation for the libraries meaning
        that it will run the various loaders for the libraries that
        will populate the key to value association in the libraries
        map valuable as debugging information.
        """

        self.libraries = dict()
        for name, module in legacy.items(sys.modules):
            lib_loader = self.lib_loaders.get(name, None)
            if not lib_loader: continue
            try: result = lib_loader(module)
            except: continue
            self.libraries.update(dict(result))

    def _extra_logging(self, level, formatter):
        """
        Loads the complete set of logging handlers defined in the
        current logging value, should be a map of definitions.

        This handlers will latter be used for piping the various
        logging messages to certain output channels.

        The creation of the handler is done using a special keyword
        arguments strategy so that python and configuration files
        are properly set as compatible.

        :type level: String/int
        :param level: The base severity level for which the new handler
        will be configured in case no extra level definition is set.
        :type formatter: Formatter
        :param formatter: The logging formatter instance to be set in
        the handler for formatting messages to the output.
        """

        # verifies if the logging attribute of the current instance is
        # defined and in case it's not returns immediately, otherwise
        # starts by converting the currently defined set of handlers into
        # a list so that it may be correctly manipulated (add handlers)
        logging = config.conf("LOGGING", None)
        if not logging: return
        self.handlers = list(self.handlers)

        # iterates over the complete set of handler configuration in the
        # logging to create the associated handler instances
        for _config in logging:
            # gathers the base information on the current handler configuration
            # running also the appropriate transformation on the level
            name = _config.get("name", None)
            _level = _config.get("level", level)
            _level = self._level(_level)

            # "clones" the configuration dictionary and then removes the base
            # values so that they do not interfere with the building
            _config = dict(_config)
            if "level" in _config: del _config["level"]
            if "name" in _config: del _config["name"]

            # retrieves the proper building, skipping the current loop in case
            # it does not exits and then builds the new handler instance, setting
            # the proper level and formatter and then adding it to the set
            if not hasattr(log, name + "_handler"): continue
            builder = getattr(log, name + "_handler")
            handler = builder(**_config)
            handler.setLevel(_level)
            handler.setFormatter(formatter)
            self.handlers.append(handler)

        # restores the handlers structure back to the "original" tuple form
        # so that no expected data types are violated
        self.handlers = tuple(self.handlers)

    def _set_url(self):
        """"
        Updates the various URL values that are part of the application
        so that they represent the most up-to-date strings taking into
        account the defined server configuration.

        Note that the server configuration may change during the runtime,
        thus requiring a refresh on the URL values.
        """

        port = self.port or 8080
        prefix = "https://" if self.ssl else "http://"
        default_port = (self.ssl and port == 443) or (not self.ssl and port == 80)
        self.local_url = prefix + "localhost"
        if not default_port: self.local_url += ":%d" % port

    def _schedule_peers(self, timeout = 60.0):
        """
        Runs the scheduling of the peers discovery operation for
        the current tick and at the end of its execution schedules
        a new one according to the provided timeout.

        :type timeout: float
        :param timeout: The number of seconds until the next peers
        scheduling operation should be performed.
        """

        if not self.get_bus_d(): return
        self._refresh_peers(timeout = timeout * 2)
        self.trigger_bus("update_peers")
        self.schedule(
            self._schedule_peers,
            timeout = timeout,
            kwargs = dict(timeout = timeout)
        )

    def _refresh_peers(self, timeout = 120.0):
        """
        Runs the house keeping operation on the peers structure so
        that for instance old peers are removed once a certain timeout
        threshold is reached.

        It should be considered a garbage collection operation.

        :type timeout: float
        :param timeout: The maximum number of seconds waiting for a "ping"
        operation from a peer until it should be considered expired.
        """

        current = time.time()
        target = current - timeout
        for uid, peer in legacy.items(self._peers):
            if peer["ping"] > target: continue
            del self._peers[uid]

    def _send_peer(self):
        """
        "Sends" the information on the current peer (instance) to the
        shared bus, so that the other peers in the mesh are notified
        about the existence of the current instance/process.
        """

        if not self.get_bus_d(): return
        self.trigger_bus(
            "peer",
            data = dict(
                uid = self.uid,
                name = self.name,
                name_b = self.name_b,
                name_i = self.name_i,
                instance = self.instance,
                hostname = self.hostname,
                info_dict = self.info_dict()
            )
        )

    def _on_update_peers(self):
        """
        Callback method triggered when a request for an update operation
        about the peers on the bus is performed.

        Should send the information on the current peer to the bus.
        """

        self._send_peer()

    def _on_peer(self, data = None):
        """
        Callback method to be called when the information regarding
        a new peer is received on the currently (shared) bus.

        :type data: Dictionary
        :param data: The map containing the detailed information on the
        peer (it must have been sent on the "wire").
        """

        if not data: return
        uid = data.get("uid", None)
        if not uid: return
        if uid == self.uid: return
        peer = self._peers.get("uid", None)
        if not peer: peer = dict()
        peer["data"] = data
        peer["ping"] = time.time()
        self._peers[uid] = peer

    def _on_self(self, data = None):
        """
        Callback method to be called when a new request specifically
        targeted for this peer is performed on the shared bus.

        :type data: Dictionary
        :param data: The map containing the details on the request that
        has been performed.
        """

        if not data: return

    def _base_locale(self, fallback = "en_us"):
        """
        Retrieves the locale considered to to be the base one for
        the current application, this should be the best locale to
        be used when no reference exists to choose the best one from
        the end user configuration.

        This method should always be called for the retrieval of
        locales outside of the request environment.

        :type fallback: String
        :param fallback: The fallback value to be used when there's no
        loaded configuration about locales for the application.
        :rtype: String
        :return: The best base locale for the current environment taking
        no input from the end user.
        """

        locale = config.conf("LOCALE", None)
        if locale in self.locales: return locale
        if self.locales: return self.locales[0]
        return fallback

    def _set_locale(self):
        # normalizes the current locale string by converting the
        # last part of the locale string to an uppercase representation
        # and then re-joining the various components of it
        values = self.request.locale.split("_", 1)
        if len(values) > 1: values[1] = values[1].upper()
        locale_n = "_".join(values)
        locale_n = str(locale_n)

        # in case the current operative system is windows based an
        # extra locale conversion operation must be performed, after
        # than the proper setting of the os locale is done with the
        # fallback for exception being silent (non critical)
        if os.name == "nt": locale_n = defines.WINDOWS_LOCALE.get(locale_n, "")
        else: locale_n += ".utf8"
        try: locale.setlocale(locale.LC_ALL, locale_n)
        except: pass

    def _reset_locale(self):
        locale.setlocale(locale.LC_ALL, "")

    def _sslify(self):
        """
        Runs the sslify process on the current request, meaning that if the
        current request is handled using a plain encoding (HTTP) a redirection
        is going to be set in the request for a secure version of the URL (HTTPS).

        The re-writing of the request implies that no "typical" action function
        based handling is going to occur as the request is going to be marked
        as handled, avoiding normal handling.
        """

        if not self.force_ssl and not self.force_host: return

        scheme = self.request.scheme
        host = self.request.in_headers.get("Host", None)

        if not host: return

        scheme_t = "https" if self.force_ssl else scheme
        host_t = self.force_host if self.force_host else host

        is_valid = scheme == scheme_t and host == host_t
        if is_valid: return

        url = scheme_t + "://" + host_t + self.request.location
        query = http._urlencode(self.request.params)
        if query: url += "?" + query

        self.redirect(url)
        self.request.handle()

    def _annotate_async(self):
        """
        Verifies if the current request in handling is a redirection one
        and if it's considered to be an asynchronous one. For such situations
        annotates (marks) it with a special response code so that it may
        be properly handled by the client side.
        """

        # verifies if the current response contains the location header
        # meaning that a redirection will occur, and if that's not the
        # case this function returns immediately to avoid problems
        if not "Location" in self.request.out_headers: return

        # checks if the current request is "marked" as asynchronous, for
        # such cases a special redirection process is applied to avoid the
        # typical problems with automated redirection using "ajax"
        is_async = True if self.request.asynchronous else False
        is_async = True if self.field("async") else is_async
        if is_async: self.request.code = 280

    def _routes(self):
        if self.routes_v: return self.routes_v
        self._proutes()
        self._pcore()
        self.routes_v = self.all_routes()
        return self.routes_v

    def _proutes(self):
        """
        Processes the currently defined static routes taking
        the current instance as base for the function resolution.

        Note that some extra handler processing may occur for the
        resolution of the handlers for certain operations.

        Usage of this method may require some knowledge of the
        internal routing system as some of the operations are
        specific and detailed.
        """

        # in case the (static routes) resolved flag is already set
        # returns the control flow immediately, no processing pending
        if self._resolved: return

        self._BASE_ROUTES = []
        self._ERROR_HANDLERS = {}
        self._CUSTOM_HANDLERS = {}

        # iterates over the complete set of base routes (for the app)
        # registered using a static global operation (eg: decorator)
        for route in App._BASE_ROUTES:
            route = list(route)

            function, context_s = route[2], route[3]

            # runs the concrete method resolution with the aid of the context
            # and re-sets the method in the route list
            method, name = self._resolve(function, context_s = context_s)
            self.names[name] = route
            route[2] = method

            # removes the unnecessary context reference as the method has been
            # already resolve (no more need for it)
            del route[3]

            # tries to retrieve the options dictionary from the route list
            # and then sets the (function) name in it (notice that the dictionary
            # is cloned to avoid reference issues)
            opts = route[3]
            opts = dict(opts)
            opts["name"] = name
            route[3] = opts

            # in case the CORS execution mode is enabled for this route
            # some extra operations will have to be performed, including
            # the creation of an "extra" OPTIONS route
            cors = opts.get("cors", False)
            if cors:
                self._BASE_ROUTES.append([
                    ("OPTIONS",),
                    route[1],
                    lambda *args, **kwargs: b"",
                    dict(
                        name = "private.cors",
                        base = opts["base"],
                        param_t = opts.get("param_t", []),
                        names_t = opts.get("names_t", {}),
                        json = opts.get("json", False)
                    )
                ])

            # adds the processed static route to the list of base routes,
            # these are considered to be the most important routes, as they
            # are the recommended way for the developer to register static routes
            self._BASE_ROUTES.append(route)

        self._no_duplicates(self._BASE_ROUTES)

        for name, handlers in legacy.iteritems(App._ERROR_HANDLERS):
            _handlers = []

            for handler in handlers:
                # creates a copy of the handler so that the original value
                # remains intact (as expected)
                handler = list(handler)

                # retrieves both the function (not resolved) and the context
                # from the handler, to be used in the registration
                function, context_s = handler[0], handler[4]

                # runs the resolution process over the associated function
                # to be able to retrieve the concrete method and updates
                # the first element of the handler with the (resolved) method
                method, _name = self._resolve(function, context_s = context_s)
                handler[0] = method

                # adds the final handler list to the list of handled candidate
                # to be error handlers for the current error value
                _handlers.append(handler)

            self._no_duplicates(_handlers)
            self._ERROR_HANDLERS[name] = _handlers

        for name, handlers in legacy.iteritems(App._CUSTOM_HANDLERS):
            _handlers = []

            for handler in handlers:
                # creates a copy of the handler so that the original value
                # remains intact (as expected)
                handler = list(handler)

                # retrieves both the function (not resolved) and the context
                # from the handler, to be used in the registration
                function, context_s = handler[0], handler[2]

                # runs the resolution process over the associated function
                # to be able to retrieve the concrete method and updates
                # the first element of the handler with the (resolved) method
                method, _name = self._resolve(function, context_s = context_s)
                handler[0] = method

                # adds the final handler list to the list of handled candidate
                # to be exception handlers for the current exception value
                _handlers.append(handler)

            self._no_duplicates(_handlers)
            self._CUSTOM_HANDLERS[name] = _handlers

        self._resolved = True

    def _pcore(self, routes = None):
        """
        Runs the processing of the user and core routes so that the proper
        context is used for it's handling, this is required in order to have
        the controllers referenced at runtime.

        It's possible to override the default set of routes that is going
        to be processed by passing the extra routes parameter.

        :type routes: List
        :param routes: The sequence containing the complete set of routes
        that is going to be processed.
        """

        # retrieves the complete set of routes that are going to be processed
        # (either the routes passed as parameters) or the basic routes both
        # from the user and the core ones
        routes = routes or (self.user_routes() + self.core_routes())

        # iterates over each of the routes to be able to process it accordingly
        # notice that this is considered to be an expensive operation and its
        # execution should be minimized
        for route in routes:
            # verifies if the route has already been processed
            # (smaller size than expected) and if that's the case
            # skips the current iteration (nothing to be done)
            is_processed = len(route) < 5
            if is_processed: continue

            function = route[2]

            _method, name = self._resolve(function)
            self.names[name] = route

            del route[3]

            opts = route[3]
            opts["name"] = name

    def _resolve(self, function, context_s = None):
        function_name = function.__name__

        has_class = hasattr(function, "__self__") and function.__self__
        if has_class: context_s = function.__self__.__class__.__name__

        # tries to resolve the "object" context for the method taking
        # into account the class association the context string or as
        # a fallback the current running application object
        if has_class: context = function.__self__
        elif context_s: context = self.controllers.get(context_s, self)
        else: context = self

        if context_s: name = util.base_name_m(context_s) + "." + function_name
        else: name = function_name

        has_method = hasattr(context, function_name)
        if has_method: method = getattr(context, function_name)
        else: method = function

        return method, name

    def _error_handler(self, error_c, scope = None, json = False, default = None):
        handler = default
        handlers = self._ERROR_HANDLERS.get(error_c, None)
        if not handlers: return handler
        handlers = sorted(handlers, reverse = True, key = lambda v: 1 if v[1] else 0)
        for _handler in handlers:
            if not _handler: continue
            if _handler[1] and not scope == _handler[1]: continue
            if not json == _handler[2]: continue
            handler = _handler
            break
        return handler

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

    def _description(self):
        """
        Resolves the proper description for the current application taking
        into account that some major transformations must be done on the
        current name so that it becomes a proper description.

        Note that in case no transformation is required the original name
        value is returned immediately as the description.

        :rtype: String
        :return: The transformed version of the current name so that it
        may be used as description.
        """

        return util.camel_to_readable(self.name_b, capitalize = True)

    def _has_access(self, path, type = "w"):
        """
        Verifies if the provided path is accessible by the
        current used logged in to the system.

        Note that this method may left some garbage in case
        the file that is being verified does not exists.

        :type path: String
        :param path: The path to the file that is going to be verified
        for the provided permission types.
        :type type: String
        :param type: The type of permissions for which the file has
        going to be verifies (default to write permissions).
        :rtype: bool
        :return: If the file in the provided path is accessible
        by the currently logged in user.
        """

        has_access = True
        try: file = open(path, type)
        except: has_access = False
        else: file.close()
        return has_access

    def _has_templating(self):
        """
        Verifies if the currently loaded system contains at least one
        templating engine loading, this is relevant to make runtime
        decisions on how to render some of the information.

        :rtype: bool
        :return: If at least one template engine is loading in the
        currently running infra-structure.
        """

        if self.jinja: return True
        return False

    def _import(self, name):
        # tries to search for the requested module making sure that the
        # correct files exist in the current file system, in case they do
        # fails gracefully with no problems
        try: file, _path, _description = imp.find_module(name)
        except ImportError: return None

        # in case a file is returned from the find module call it must be
        # closes in order to avoid any leaking of memory descriptors
        if file: file.close()

        # tries to import the requested module (relative to the currently)
        # executing path and in case there's an error raises the error to
        # the upper levels so that it is correctly processed, then returns
        # the module value to the caller method
        module = __import__(name)
        return module

    def _url_for(
        self,
        reference,
        filename = None,
        query = None,
        params = None,
        touch = True,
        session = False,
        compress = None,
        *args,
        **kwargs
    ):
        """
        Tries to resolve the URL for the provided type string (static or
        dynamic), filename and other dynamic arguments.

        This method is the inner protected method that returns invalid
        in case no resolution is possible and should not be used directly.

        The optional touch flag may be used to control if the URL for static
        resources should be returned with the optional timestamp flag appended.
        This option provides a way of invalidating the client side cache for
        every re-start of the application infra-structure.

        Example values for type include (static, controller.method, etc.).

        :type reference: String
        :param reference: The reference string that is going to be used in
        the resolution of the urls (should conform with the standard).
        :type filename: String
        :param filename: The name (path) of the (static) file (relative to static
        base path) for the static file URL to be retrieved.
        :type query: String
        :param query: The "base" query string to be used in case provided, otherwise
        only the params and keyword based arguments will be used in construction of
        the final query string to be applied to the URL.
        :type params: Dictionary
        :param params: The parameters for the URL construction to be used, in case
        they are not provided the keyword based arguments are used instead.
        :type touch: bool
        :param touch: If the URL should be "touched" in the sense that the
        start timestamp of the current instance should be appended as a get
        attribute to the full URL value of a static resource.
        :type session: String
        :param session: If the special session parameter (sid) should be included
        in the generated URL for special session handling situations.
        :type compress: String
        :param compress: The string describing the compression method/strategy
        that is going to be used to compress the static resource. This should
        be a "free" plain string value.
        :rtype: String
        :return: The URL that has been resolved with the provided arguments, in
        case no resolution was possible an invalid (unset) value is returned.
        """

        if session: sid = self._sid()
        else: sid = None

        params = kwargs if params == None else params

        prefix = self.request.prefix
        if reference == "static":
            location = prefix + "static/" + filename
            query = self._query_for(touch = touch, compress = compress, sid = sid)
            return util.quote(location) + query
        elif reference == "appier":
            location = prefix + "appier/static/" + filename
            query = self._query_for(touch = touch, compress = compress, sid = sid)
            return util.quote(location) + query
        elif reference + "_part" in self.__dict__:
            location = prefix + reference + "/static/" + filename
            query = self._query_for(touch = touch, compress = compress, sid = sid)
            return util.quote(location) + query
        elif reference == "location":
            location = self.request.location
            return location
        elif reference == "location_f":
            location_f = self.request.location_f
            return location_f
        else:
            self._routes()

            route = self.names.get(reference, None)
            if not route: return route

            if sid: params["sid"] = sid

            route_l = len(route)
            opts = route[3] if route_l > 3 else {}

            base = opts.get("base", route[1].pattern)
            names_t = opts.get("names_t", {})

            base = base.rstrip("$")
            base = base.lstrip("^/")

            query = [query] if query else []

            for key, value in params.items():
                if value == None: continue
                value_t = type(value)
                replacer = names_t.get(key, None)
                if replacer:
                    is_string = value_t in legacy.STRINGS
                    if not is_string: value = str(value)
                    base = base.replace(replacer, value)
                else:
                    key_q = util.quote(key)
                    if not value_t in (list, tuple): value = [value]
                    for _value in value:
                        _value_t = type(_value)
                        _is_string = _value_t in legacy.STRINGS
                        if not _is_string: _value = str(_value)
                        value_q = util.quote(_value)
                        param = key_q + "=" + value_q
                        query.append(param)

            location = prefix + base
            location = util.quote(location)

            query_s = "&".join(query)

            return location + "?" + query_s if query_s else location

    def _query_for(self, touch = True, compress = None, sid = None):
        # creates the list that is going to hold the various elements
        # that are going to be part of the final query string
        query = []

        # validates the various options and adds the corresponding items
        # to the query components list (to be able to construct the query)
        if touch and self.touch_time: query.append(self.touch_time)
        if compress: query.append("compress=%s" % compress)
        if sid: query.append("sid=%s" % sid)

        # constructs the query string value taking into account the list
        # of elements that compose query, in case the query string is not
        # empty the additional query indicator character is prepended
        query_s = "&".join(query)
        if query_s: query_s = "?" + query_s

        # returns the "final" query string to the caller method, this value
        # should be safe to use for URL construction
        return query_s

    def _cache(self, cache = None):
        # tries to determine the proper amount of time to be applied to the cache
        # defaulting to the currently set global value in case none is provided
        cache = cache or self.cache

        # retrieves the current date value and increments the cache overflow value
        # to it so that the proper expire value is set, then formats the date as
        # a string based value in order to be set in the headers
        current = datetime.datetime.utcnow()
        target = current + cache
        with util.ctx_locale(): target_s = target.strftime("%a, %d %b %Y %H:%M:%S GMT")

        # creates the cache string that will be used to populate the cache control
        # header in case there's a valid cache value for the current request
        cache_s = "public, max-age=%d" % self.cache_s

        # returns the tuple that contains the definition for both the target cache
        # data and the cache header string value with proper invalidation
        return target_s, cache_s

    def _extension(self, file_path):
        _head, tail = os.path.split(file_path)
        tail_s = tail.split(".", 1)
        if len(tail_s) > 1: return "." + tail_s[1]
        return None

    def _extension_in(self, extension, sequence):
        if not extension: return False
        for item in sequence:
            valid = extension.endswith(item)
            if not valid: continue
            return True
        return False

    def _best_locale(self, locale):
        if not locale: return locale
        for _locale in self.locales:
            is_valid = _locale.startswith(locale)
            if not is_valid: continue
            return _locale
        return locale

    def _bases(self, cls):
        yield cls
        for direct_base in cls.__bases__:
            for base in self._bases(direct_base):
                yield base

    def _sid(self):
        session = self.request.session
        sid = session and session.sid
        return sid

    def _no_duplicates(self, items):
        visited = []
        removal = []

        for item in items:
            exists = item in visited
            if exists: removal.append(item)
            else: visited.append(item)

        for handler in removal: items.remove(handler)

class APIApp(App):
    pass

class WebApp(App):

    def __init__(
        self,
        service = False,
        *args,
        **kwargs
    ):
        App.__init__(
            self,
            service = service,
            *args,
            **kwargs
        )
        decorator = util.route("/", "GET")
        decorator(self.handle_holder)
        decorator = util.error_handler(403)
        decorator(self.to_login)

    def handle_holder(self):
        templates_path = os.path.join(self.res_path, "templates")
        return self.template(
            "holder.html.tpl",
            templates_path = templates_path
        )

    def handle_error(self, exception):
        # retrieves the reference to the class associated with the current instance
        # so that class level operations may be performed
        cls = self.__class__

        # in case the current request is of type JSON (serializable) or if
        # there's no template support available this exception should not
        # be handled using the template based strategy but using the
        # (base) serialized based strategy instead
        if self.request.json: return App.handle_error(self, exception)
        if not self._has_templating(): return App.handle_error(self, exception)

        # tries to ensure that the UID value of the exception is set,
        # notice that under some extreme occasions it may not be possible
        # to ensure such behaviour (eg: native code based exception)
        if not hasattr(exception, "uid"):
            try: exception.uid = uuid.uuid4()
            except: pass

        # formats the various lines contained in the exception and then tries
        # to retrieve the most information possible about the exception so that
        # the returned map is the most verbose as possible (as expected)
        lines = traceback.format_exc().splitlines()
        lines = cls._lines(lines)
        message = hasattr(exception, "message") and\
            exception.message or str(exception)
        code = hasattr(exception, "code") and\
            exception.code or 500
        headers = hasattr(exception, "headers") and\
            exception.headers or None
        errors = hasattr(exception, "errors") and\
            exception.errors or None
        uid = hasattr(exception, "uid") and\
            exception.uid or None
        session = self.request.session
        sid = session and session.sid
        scope = self.request.context.__class__

        # "saves" both the exception in handling and the stack trace lines in the
        # current request, so that it may be used latter to print exception information
        # for instance for logging purposes (extremely useful)
        self.request.exception = exception
        self.request.stacktrace = lines

        # determines the kind of information that is going to be sent as the
        # extended version of the lines (defaulting to empty list), this take
        # into account if the current setup is running under debug mode or not
        extended = cls._format_extended(exception) if settings.DEBUG else []

        # in case the current running mode does not have the debugging features
        # enabled the lines value should be set as empty to avoid extra information
        # from being provided to the end user (as expected by specification)
        lines = lines if settings.DEBUG else []

        # sets the proper error code for the request, this value has been extracted
        # from the current exception or the default one is used, this must be done
        # to avoid any miss setting of the status code for the current request
        self.request.set_code(code)

        # sets the complete set of (extra) headers defined in the exceptions, these
        # headers may be used to explain the kind of problem that has just been
        # "raised" by the current exception object in handling
        self.request.set_headers(headers)

        # run the on error processor in the base application object and in case
        # a value is returned by a possible handler it is used as the response
        # for the current request (instead of the normal handler)
        result = self.call_error(exception, code = code, scope = scope)
        if result: return result

        # computes the various exception class related attributes, as part of these
        # attributes the complete (full) name of the exception should be included
        name = exception.__class__.__name__
        module = inspect.getmodule(exception)
        base_name = module.__name__ if module else None
        full_name = base_name + "." + name if base_name else name

        # calculates the path to the (base) resources related templates path, this is
        # going to be used instead of the (default) application related path
        templates_path = os.path.join(self.res_path, "templates")

        # renders the proper error template for the error with the complete set of
        # calculated attributes so that they may be displayed in the template
        return self.template(
            "error.html.tpl",
            templates_path = templates_path,
            exception = exception,
            name = name,
            full_name = full_name,
            lines = lines,
            extended = extended,
            message = message,
            code = code,
            errors = errors,
            uid = uid,
            session = session,
            sid = sid
        )

    def to_login(self, error):
        if self.request.json: return
        login_route = self._to_login_route(error)
        return self.redirect(
            self.url_for(
                login_route,
                next = self.request.location_f,
                error = error.message
            )
        )

    def _to_login_route(self, error):
        # tries to extract keyword based arguments from the provided
        # error and in case there's none defaults the value as a simple
        # empty dictionary for compatibility with the execution
        kwargs = error.kwargs if hasattr(error, "kwargs") else dict()

        # creates the full custom login route from the context and verifies
        # that such route is registered under the current object if so
        # returns such route as the login route (expected)
        context = kwargs.get("context", None)
        context_route = "login_route_" + context if context else None
        has_context = hasattr(self, context_route) if context_route else False
        if has_context: return getattr(self, context_route)

        # creates the full custom login route from the token and verifies
        # that such route is registered under the current object if so
        # returns such route as the login route (expected)
        token = kwargs.get("token", None)
        token_route = "login_route_" + token if token else None
        has_token = hasattr(self, token_route) if token_route else False
        if has_token: return getattr(self, token_route)

        # retrieves the "default" login route value to the caller method
        # this should be used if no other strategy was available (fallback)
        return self.login_route

class Template(legacy.UNICODE):

    def get_template(self, name, builder = None):
        if hasattr(self, name): return getattr(self, name)
        if not builder: return None
        template = builder()
        setattr(self, name, template)
        return template

def get_app():
    return APP

def get_name():
    return APP and APP.name

def get_base_path():
    return APP and APP.base_path

def get_cache():
    return APP and APP.get_cache_d()

def get_preferences():
    return APP and APP.get_preferences_d()

def get_bus():
    return APP and APP.get_bus_d()

def get_request():
    return APP and APP.get_request()

def get_session():
    return APP and APP.get_session()

def get_model(name, raise_e = False):
    return APP and APP.get_model(name, raise_e = raise_e)

def get_controller(name, raise_e = False):
    return APP and APP.get_controller(name, raise_e =raise_e)

def get_part(name, raise_e = False):
    return APP and APP.get_part(name, raise_e = raise_e)

def get_adapter():
    return APP and APP.get_adapter()

def get_manager():
    return APP and APP.get_manager()

def get_logger():
    return APP and APP.get_logger()

def get_level():
    global LEVEL
    if LEVEL: return LEVEL
    level_s = config.conf("LEVEL", None)
    LEVEL = App._level(level_s) if level_s else logging.INFO
    return LEVEL

def is_loaded():
    return APP.is_loaded() if APP else False

def is_devel():
    if not APP: return get_level() < logging.INFO
    return APP.is_devel()

def is_safe():
    return APP.safe if APP else False

def to_locale(value, *args, **kwargs):
    if not APP: value
    return APP and APP.to_locale(value, *args, **kwargs)

def on_exit(function):
    app = get_app()
    if app: app.bind("stop", function, oneshot = True)
    else: atexit.register(function)
