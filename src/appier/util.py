#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid
import hashlib
import inspect

import exceptions

def gen_token():
    token_s = str(uuid.uuid4())
    token = hashlib.sha256(token_s).hexdigest()
    return token

def private(function):
    def _private(self, *args, **kwargs):
        is_auth = self.request.session and "username" in self.request.session
        if not is_auth: raise exceptions.AppierException(
            "Method '%s' requires authentication" % function.__name__,
            error_code = 403
        )

        sanitize(function, kwargs)
        return function(self, *args, **kwargs)
    return _private

def sanitize(function, kwargs):
    removal = []
    method_a = inspect.getargspec(function)[0]
    for name in kwargs:
        if name in method_a: continue
        removal.append(name)
    for name in removal: del kwargs[name]
