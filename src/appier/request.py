#!/usr/bin/python
# -*- coding: utf-8 -*-

import types

import util
import exceptions

class Request(object):

    ALIAS = ("token",)
    SESSIONS = {}

    def __init__(self, method, path, params = {}, data_j = {}, environ = {}):
        self.method = method
        self.path = path
        self.params = params
        self.data_j = data_j
        self.environ = environ
        self.session = {}
        self.cookies = {}
        self.in_headers = {}
        self.out_headers = {}
        self.warnings = []

    def warning(self, message):
        message_t = type(message)

        if message_t in types.StringTypes:
            message = dict(message = message)
        elif not message_t == types.DictType:
            raise RuntimeError("Invalid message type '%s'", message_t)

        self.warnings.append(message)

    def get_param(self, name, default = None):
        if not name in self.params: return default
        value = self.params[name]
        return value[0] if value else default

    def set_params(self, params):
        self.params = params

    def set_json(self, data_j):
        self.data_j = data_j

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

    def _resolve_p(self, params):
        secret = self.session.get("secret", None)
        if not secret: return params

        raise exceptions.AppierException("not implemented")
