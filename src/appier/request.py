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

import util
import exceptions

CODE_STRINGS = {
    200 : "OK",
    500 : "Internal Error"
}
""" Dictionary associating the error code as integers
with the official descriptive message for it """

class Request(object):

    ALIAS = ("token",)
    SESSIONS = {}

    def __init__(self, method, path, params = {}, data_j = {}, environ = {}):
        self.method = method
        self.path = path
        self.params = params
        self.data_j = data_j
        self.environ = environ
        self.code = 200
        self.content_type = None
        self.session = {}
        self.cookies = {}
        self.in_headers = {}
        self.out_headers = {}
        self.warnings = []
        self._params = None

    def warning(self, message):
        message_t = type(message)

        if message_t in types.StringTypes:
            message = dict(message = message)
        elif not message_t == types.DictType:
            raise RuntimeError("Invalid message type '%s'", message_t)

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
        self.session = Request.SESSIONS.get(sid, {})

        if not self.session and create:
            sid = util.gen_token()
            self.session = dict(sid = sid)
            Request.SESSIONS[sid] = self.session

        return self.session

    def get_warnings(self):
        return self.warnings

    def get_headers(self):
        return self.out_headers.items()

    def get_code_s(self):
        code_s = CODE_STRINGS.get(self.code, "Unknown")
        code_s = str(self.code) + " " + code_s
        return code_s

    def _resolve_p(self, params):
        secret = self.session.get("secret", None)
        if not secret: return params

        raise exceptions.AppierException("not implemented")
