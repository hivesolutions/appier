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

import uuid
import hashlib
import inspect

import base
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

def route(url, method = "GET"):

    def decorator(function, *args, **kwargs):
        base.App.add_route(method, url, function)
        return function

    return decorator

def sanitize(function, kwargs):
    removal = []
    method_a = inspect.getargspec(function)[0]
    for name in kwargs:
        if name in method_a: continue
        removal.append(name)
    for name in removal: del kwargs[name]
