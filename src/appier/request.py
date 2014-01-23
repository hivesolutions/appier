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

import json
import types
import urlparse

import util
import session
import exceptions

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
        method,
        path,
        prefix = "/",
        params = {},
        data_j = {},
        environ = {},
        session_c = session.FileSession
    ):
        self.method = method
        self.path = path
        self.prefix = prefix
        self.params = params
        self.data_j = data_j
        self.environ = environ
        self.session_c = session_c
        self.code = 200
        self.location = prefix + path.lstrip("/")
        self.content_type = None
        self.data = None
        self.session = session.MockSession(self)
        self.set_cookie = None
        self.args = {}
        self.cookies = {}
        self.in_headers = {}
        self.out_headers = {}
        self.warnings = []
        self.properties = {}
        self._params = None

    def flush(self):
        self.session.flush()

    def warning(self, message):
        message_t = type(message)

        if message_t in types.StringTypes:
            message = dict(message = message)
        elif not message_t == types.DictType:
            raise exceptions.OperationalError(
                message = "Invalid message type '%s'" % message_t
            )

        self.warnings.append(message)

    def get_params(self):
        if self._params: return self._params
        self._params = {}
        for key, value in self.params.iteritems(): self._params[key] = value[0]
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

    def set_json(self, data_j):
        self.data_j = data_j

    def set_code(self, code):
        self.code = code

    def extend_args(self, args):
        for key, value in args.iteritems():
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

    def resolve_params(self):
        self.params = self._resolve_p(self.params)

    def load_data(self):
        # initializes the various structure associated with the data loading
        # and/or parsing, so that the request is correctly populated
        self.data_j = None
        self.post = {}
        self.files = {}

        # verifies if the current data attribute contains a valid value in case
        # it does not returns immediately as there's nothing to be loaded
        if not self.data: return

        # tries to retrieve the current content type value set in the environment
        # then splits it around the separator to retrieve the mime type
        content_type = self.environ.get("HTTP_CONTENT_TYPE", "application/json")
        content_type_s = content_type.split(";")
        mime_type = content_type_s[0]

        if mime_type == "application/json":
            try: self.data_j = json.loads(self.data) if self.data else None
            except: pass
        elif mime_type == "application/x-www-form-urlencoded":
            post = urlparse.parse_qs(
                self.data,
                keep_blank_values = True
            ) if self.data else {}
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

    def load_session(self):
        self.load_cookies()
        self.set_alias()
        self.set_session()

    def load_headers(self):
        for key, value in self.environ.iteritems():
            if not key.startswith("HTTP_"): continue
            key = key[5:]
            parts = key.split("_")
            parts = [part.title() for part in parts]
            key_s = "-".join(parts)
            self.in_headers[key_s] = value

    def load_cookies(self):
        cookie_s = self.environ.get("HTTP_COOKIE", "")

        cookies = [cookie.strip() for cookie in cookie_s.split(";")]
        for cookie in cookies:
            if not "=" in cookie: cookie += "="
            name, value = cookie.split("=", 1)
            self.cookies[name] = value

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

        # tries to retrieve the session reference for the
        # provided sid (session id) in case there's an exception
        # defaults to unset session so that a new gets created
        try: session = self.session_c.get_s(sid)
        except: session = None

        # in case no valid session exists a new one must be created
        # so that the user may be able to interact with the system
        # with some kind of memory/persistence otherwise sets the
        # loaded session in the current request (to be used)
        if session: self.session = session
        elif create: self.session = self.session_c.new()

    def get_warnings(self):
        return self.warnings

    def get_set_cookie(self):
        return self.set_cookie

    def get_headers(self):
        return self.out_headers.items()

    def get_code_s(self):
        code_s = CODE_STRINGS.get(self.code, "Unknown")
        code_s = str(self.code) + " " + code_s
        return code_s

    def get_encoding(self):
        return "utf-8"

    def is_mobile(self):
        user_agent = self.get_header("User-Agent", None)
        return util.is_mobile(user_agent)

    def _resolve_p(self, params):
        secret = self.session.get("secret", None)
        if not secret: return params

        raise exceptions.AppierException(message = "Not implemented")
