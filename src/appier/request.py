#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2015 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import json
import time
import base64
import datetime

from . import util
from . import config
from . import legacy
from . import session
from . import exceptions

CODE_STRINGS = {
    100 : "Continue",
    101 : "Switching Protocols",
    200 : "OK",
    201 : "Created",
    202 : "Accepted",
    203 : "Non-Authoritative Information",
    204 : "No Content",
    205 : "Reset Content",
    206 : "Partial Content",
    207 : "Multi-Status",
    301 : "Moved permanently",
    302 : "Found",
    303 : "See Other",
    304 : "Not Modified",
    305 : "Use Proxy",
    306 : "(Unused)",
    307 : "Temporary Redirect",
    400 : "Bad Request",
    401 : "Unauthorized",
    402 : "Payment Required",
    403 : "Forbidden",
    404 : "Not Found",
    405 : "Method Not Allowed",
    406 : "Not Acceptable",
    407 : "Proxy Authentication Required",
    408 : "Request Timeout",
    409 : "Conflict",
    410 : "Gone",
    411 : "Length Required",
    412 : "Precondition Failed",
    413 : "Request Entity Too Large",
    414 : "Request-URI Too Long",
    415 : "Unsupported Media Type",
    416 : "Requested Range Not Satisfiable",
    417 : "Expectation Failed",
    500 : "Internal Server Error",
    501 : "Not Implemented",
    502 : "Bad Gateway",
    503 : "Service Unavailable",
    504 : "Gateway Timeout",
    505 : "HTTP Version Not Supported"
}
""" Dictionary associating the error code as integers
with the official descriptive message for it """

class Request(object):
    """
    Request class that acts as a proxy for the both
    the input and output of an http request.

    Other responsibilities should include indirect
    session management and serialization.
    """

    ALIAS = ("session_id", "_sid")
    """ The list of strings that are considered to represent
    and alias to the session identifier name, this values may
    be changed in case the app required loading of the session
    using a different attribute name """

    def __init__(
        self,
        owner = None,
        method = "GET",
        path = "/",
        prefix = "/",
        query = "",
        scheme = None,
        params = {},
        data_j = {},
        environ = {},
        session_c = session.FileSession
    ):
        self.owner = owner
        self.method = method
        self.path = path
        self.prefix = prefix
        self.query = query
        self.scheme = scheme
        self.params = params
        self.data_j = data_j
        self.environ = environ
        self.session_c = session_c
        self.handled = False
        self.json = False
        self.code = 200
        self.location = prefix + util.quote(path).lstrip("/")
        self.content_type = None
        self.authorization = None
        self.data = None
        self.result = None
        self.session = session.MockSession(self)
        self.set_cookie = None
        self.args = {}
        self.cookies = {}
        self.in_headers = {}
        self.out_headers = {}
        self.warnings = []
        self.properties = {}
        self._params = None

    def handle(self, code = None, result = ""):
        """
        Handles the current request, setting the response code
        and the resulting data that is going to be returned to
        the current client.

        This method should not be called directly by any of the
        action functions but only by the internal appier structures
        or any other extra middleware handler. Because of that
        this method should be considered internal and must be
        used with extreme care.

        If this method is called the request is considered to be
        handled and the "typical" action function based handling
        is going to be skipped.

        :type code: int
        :param code: The status code that is going to be set for
        the response associated with the current request.
        :type result: Object
        :param result: Value that is returned to the handling
        infra-structure as the result of the handling, proper data
        types may vary and the include: strings, dictionaries or
        generator objects.
        """

        self.handled = True
        self.code = self.code if self.code else 200
        self.code = code if code else self.code
        self.result = result

    def flush(self):
        """
        Flushes the current request information meaning that the
        current request information is updated so that it's state
        is persisted into the current client's information.

        This method should always be called at the end of the request
        handling workflow.
        """

        self.session.flush(self)

    def warning(self, message):
        message_t = type(message)

        if message_t in legacy.STRINGS:
            message = dict(message = message)
        elif not message_t == dict:
            raise exceptions.OperationalError(
                message = "Invalid message type '%s'" % message_t
            )

        self.warnings.append(message)

    def get_params(self):
        if self._params: return self._params
        self._params = {}
        for key, value in self.params.items(): self._params[key] = value[0]
        return self._params

    def get_param(self, name, default = None):
        if not name in self.params: return default
        value = self.params[name]
        return value[0] if value else default

    def set_params(self, params):
        self.params = params
        self.extend_args(params)

    def set_post(self, post):
        self.post = post
        self.extend_args(post)

    def set_files(self, files):
        self.files = files
        self.extend_args(files)

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_json(self):
        return self.data_j

    def set_json(self, data_j):
        self.data_j = data_j

    def set_code(self, code):
        self.code = code

    def extend_args(self, args):
        for key, value in args.items():
            _value = self.args.get(key, [])
            _value.extend(value)
            self.args[key] = _value

    def get_content_type(self):
        return self.content_type

    def set_content_type(self, content_type):
        self.content_type = content_type

    def default_content_type(self, default):
        if self.content_type: return
        self.content_type = default

    def get_header(self, name, default = None):
        return self.in_headers.get(name, default)

    def set_header(self, name, value):
        self.out_headers[name] = str(value)

    def set_headers(self, headers):
        if not headers: return
        for name, value in headers.items():
            self.set_header(name, value)

    def resolve_params(self):
        self.params = self._resolve_p(self.params)

    def load_data(self):
        # initializes the various structures associated with the data loading
        # and/or parsing, so that the request is correctly populated
        self.data_j = None
        self.post = {}
        self.files = {}

        # verifies if the current data attribute contains a valid value in case
        # it does not returns immediately as there's nothing to be loaded
        if not self.data: return

        # tries to retrieve the current content type value set in the environment
        # then splits it around the separator to retrieve the mime type
        content_type = self.environ.get("CONTENT_TYPE", "application/json")
        content_type = self.environ.get("HTTP_CONTENT_TYPE", content_type)
        content_type_s = content_type.split(";")
        mime_type = content_type_s[0]

        if mime_type == "application/json":
            data = self.data.decode("utf-8") if self.data else None
            try: self.data_j = json.loads(data) if data else None
            except: pass
        elif mime_type == "application/x-www-form-urlencoded":
            data = legacy.str(self.data) if self.data else None
            post = legacy.parse_qs(
                data,
                keep_blank_values = True
            ) if self.data else {}
            post = util.decode_params(post)
            self.set_post(post)
        elif mime_type == "multipart/form-data":
            boundary = content_type_s[1]
            post, files = util.parse_multipart(self.data, boundary)
            self.set_post(post)
            self.set_files(files)

    def load_form(self):
        self.params_s = util.load_form(self.params)
        self.post_s = util.load_form(self.post)
        self.files_s = util.load_form(self.files)

    def load_authorization(self):
        # tries to decode the provided authorization header into it's own
        # components of username and password, in case the structure of the
        # provided string is not compliant an exception is raised
        authorization = self.environ.get("HTTP_AUTHORIZATION", None)
        if not authorization: return
        parts = authorization.split(" ", 1)
        if not len(parts) == 2: raise exceptions.OperationalError(
            message = "Invalid authorization header"
        )
        _method, value = parts
        value = base64.b64decode(value)
        value = legacy.str(value)
        parts = value.split(":", 1)
        if not len(parts) == 2: raise exceptions.OperationalError(
            message = "Invalid authorization header"
        )
        self.authorization = tuple(parts)

    def load_session(self):
        self.load_cookies()
        self.set_alias()
        self.set_session()

    def load_headers(self):
        for key, value in self.environ.items():
            if not key.startswith("HTTP_"): continue
            key = key[5:]
            parts = key.split("_")
            parts = [part.title() for part in parts]
            key_s = "-".join(parts)
            self.in_headers[key_s] = value

    def load_cookies(self):
        cookie_s = self.environ.get("HTTP_COOKIE", "")
        self.cookies = util.parse_cookie(cookie_s)

    def locale_s(self, value = None):
        value = value or self.locale
        return value.replace("_", "-").lower()

    def locale_b(self, value = None):
        value = value or self.locale
        return value.replace("-", "_").lower()

    def load_locale(self, available, fallback = "en_us"):
        # tries to gather the best locale value using the currently
        # available strategies and in case the retrieved local is part
        # of the valid locales for the app returns the locale, otherwise
        # returns the fallback value instead
        locale = self.get_locale(fallback = fallback)
        locale = self.locale_b(locale)
        if locale in available: self.locale = locale
        else: self.locale = fallback

    def get_locale(self, fallback = "en_us"):
        # tries to retrieve the locale value from the provided url
        # parameters (this is the highest priority) and in case it
        # exists returns this locale immediately
        locale = self.params.get("locale", None)
        if locale: return locale[0]

        # uses the currently loaded session to try to gather the locale
        # value from it and in case it's valid and exists returns it
        locale = self.session.get("locale", None)
        if locale: return locale

        # gathers the complete set of language values set in the accept
        # language header and in case there's at least one value returned
        # returns the first of these values as the locale
        langs = self.get_langs()
        if langs: return langs[0]

        # defines the locale as the global wide appier configuration and
        # tries to retrieve the value of it in case it's valid uses it
        locale = config.conf("LOCALE", None)
        if locale: return locale

        # in case this code entry is reached all the strategies for locale
        # retrieval have failed and so the fallback value is returned
        return fallback

    def get_langs(self):
        # gathers the value of the accept language header and in case
        # it's not defined returns immediately as no language can be
        # determined using the currently provided headers
        accept_language = self.in_headers.get("Accept-Language", None)
        if not accept_language: return ()

        # starts the list that is going to be used to store the various
        # languages "recovered" from the accept language header, note that
        # the order of these languages should be from the most relevant to
        # the least relevant as defined in http specification
        langs = []

        # splits the accept language header into the various components of
        # it and then iterates over each of them splitting each of the
        # components into the proper language string and priority
        parts = accept_language.split(",")
        for part in parts:
            values = part.split(";", 1)
            value_l = len(values)
            if value_l == 1: lang, = values
            else: lang, _priority = values
            lang = lang.replace("-", "_")
            lang = lang.lower()
            langs.append(lang)

        # returns the complete list of languages that have been extracted
        # from the accept language header these list may be empty in case
        # the header was not parsed correctly or there's no contents in it
        return langs

    def set_alias(self):
        for alias in Request.ALIAS:
            if not alias in self.params: continue
            self.params["sid"] = self.params[alias]

        for alias in Request.ALIAS:
            if not alias in self.post: continue
            self.post["sid"] = self.post[alias]

        for alias in Request.ALIAS:
            if not alias in self.args: continue
            self.args["sid"] = self.args[alias]

    def set_session(self, create = False):
        # tries to retrieves the session id (sid) from all the
        # possible sources so that something may be used in the
        # identification of the current request
        sid = self.cookies.get("sid", None)
        sid = self.post.get("sid", (None,))[0] or sid
        sid = self.params.get("sid", (None,))[0] or sid

        # in case the data type of the currently provided session
        # identifier is not unicode based converts it into a string
        # so that it may be used to correctly retrieve the associated
        # session object from the underlying session class repository
        sid = str(sid) if type(sid) == legacy.UNICODE else sid

        # tries to retrieve the session reference for the
        # provided sid (session id) in case there's an exception
        # defaults to unset session so that a new gets created
        try: session = self.session_c.get_s(sid, request = self)
        except: session = None

        # in case no valid session exists a new one must be created
        # so that the user may be able to interact with the system
        # with some kind of memory/persistence otherwise sets the
        # loaded session in the current request (to be used)
        if session: self.session = session
        elif create: self.session = self.session_c.new()

    def get_session(self):
        return self.session

    def get_warnings(self):
        return self.warnings

    def get_set_cookie(self, lang = "en", path = "/", delta = 31536000):
        base = self.set_cookie
        if not base: return base
        expires = time.time() + delta
        expires_d = datetime.datetime.fromtimestamp(expires)
        expires_s = expires_d.strftime("%a, %m %b %Y %H:%M:%S GMT")
        set_cookie = "%s;lang=%s;path=%s;expires=%s;" % (base, lang, path, expires_s)
        return set_cookie

    def get_headers(self):
        headers = self.out_headers.items()
        return legacy.eager(headers)

    def get_code_s(self):
        code_s = CODE_STRINGS.get(self.code, "Unknown")
        code_s = str(self.code) + " " + code_s
        return code_s

    def get_encoding(self):
        return "utf-8"

    def is_mobile(self):
        user_agent = self.get_header("User-Agent", None)
        return util.is_mobile(user_agent)

    def is_success(self):
        return self.code == 200

    def _resolve_p(self, params):
        secret = self.session.get("secret", None)
        if not secret: return params

        raise exceptions.AppierException(message = "Not implemented")

class MockRequest(Request):
    """
    Mock request class, that is meant to be used for situations
    where no web oriented request is possible to be retried or
    the logic being running outside of web request.
    """

    def __init__(self, locale = "en_us"):
        Request.__init__(self, "NONE", "/")
        self.locale = locale
        self.files_s = dict()
        self.post_s = dict()
        self.params_s = dict()
