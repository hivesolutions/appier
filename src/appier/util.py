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

CONTEXT = None
""" The current context that is going to be used for new
routes that are going to be registered with decorators """

def gen_token():
    token_s = str(uuid.uuid4())
    token = hashlib.sha256(token_s).hexdigest()
    return token

def camel_to_underscore(camel):
    values = []
    camel_l = len(camel)

    for index in xrange(camel_l):
        char = camel[index]
        is_upper = char.isupper()

        if is_upper and not index == 0: values.append("_")
        values.append(char)

    return "".join(values).lower()

def base_name(name, suffix = "_controller"):
    """
    Retrieves the base name of a class name that contains
    a suffix (eg: controller) the resulting value is the
    underscore version of the name without the suffix.

    This method provides an easy way to expose class names
    in external environments.

    @type name: String
    @param name: The name from which the base name will be
    extracted and treated.
    @type suffix: String
    @param suffix: The optional suffix value that if sent will
    be removed from the last part of the name string.
    @rtype: String
    @return: The resulting base name for the provided name, treated
    and with the suffix removed (in case it exists).
    """

    name = camel_to_underscore(name)
    if name.endswith(suffix): name = name[:-11]
    return name

def private(function):

    def _private(self, *args, **kwargs):
        is_auth = "username" in self.request.session
        if not is_auth: raise exceptions.AppierException(
            message = "Method '%s' requires authentication" % function.__name__,
            error_code = 403
        )

        sanitize(function, kwargs)
        return function(self, *args, **kwargs)

    return _private

def controller(controller):

    def decorator(function, *args, **kwargs):
        global CONTEXT
        CONTEXT = controller
        return function

    return decorator

def route(url, method = "GET"):

    def decorator(function, *args, **kwargs):
        base.App.add_route(method, url, function, context = CONTEXT)
        return function

    return decorator

def sanitize(function, kwargs):
    removal = []
    method_a = inspect.getargspec(function)[0]
    for name in kwargs:
        if name in method_a: continue
        removal.append(name)
    for name in removal: del kwargs[name]
