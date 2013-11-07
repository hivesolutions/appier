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

import types

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
        self.content_type = None
        self.session = session.MockSession(self)
        self.set_cookie = None
        self.cookies = {}
        self.in_headers = {}
        self.out_headers = {}
        self.warnings = []
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

    def set_json(self, data_j):
        self.data_j = data_j

    def set_code(self, code):
        self.code = code

    def get_content_type(self):
        return self.content_type

    def default_content_type(self, default):
        if self.content_type: return
        self.content_type = default

    def set_header(self, name, value):
        self.out_headers[name] = value

    def resolve_params(self):
        self.params = self._resolve_p(self.params)

    def load_session(self):
        self.load_cookies()
        self.set_alias()
        self.set_session()

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

    def set_session(self, create = False):
        sid = self.cookies.get("sid", None)
        sid = self.params.get("sid", (None,))[0] or sid
        session = self.session_c.get_s(sid)

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

    def _resolve_p(self, params):
        secret = self.session.get("secret", None)
        if not secret: return params

        raise exceptions.AppierException(message = "Not implemented")
