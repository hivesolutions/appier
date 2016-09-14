#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2016 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import legacy

class MockObject(object):

    def __init__(self, *args, **kwargs):
        self.model = kwargs

    def __getattribute__(self, name):
        try:
            model = object.__getattribute__(self, "model")
            if name in model: return model[name]
        except AttributeError: pass
        return object.__getattribute__(self, name)

    def __getitem__(self, key):
        return self.model.__getitem__(key)

    def __setitem__(self, key, value):
        self.model.__setitem__(key, value)

    def __delitem__(self, key):
        self.model.__delitem__(key)

class MockApp(object):

    def get(self, *args, **kwargs):
        return self.method("GET", *args, **kwargs)

    def method(
        self,
        method,
        location,
        query = "",
        data = b"",
        scheme = "http",
        address = "127.0.0.1"
    ):
        response = dict()
        input = legacy.BytesIO(data)
        environ = {
            "REQUEST_METHOD" : method,
            "PATH_INFO" : location,
            "QUERY_STRING" : query,
            "SCRIPT_NAME" : location,
            "CONTENT_LENGTH" : len(data),
            "REMOTE_ADDR" : address,
            "wsgi.input" : input,
            "wsgi.url_scheme" : scheme
        }

        def start_response(code, headers):
            response["code"] = code
            response["headers"] = dict(headers)
            response["headers_l"] = headers

        result = self.application(environ, start_response)
        response["data"] = b"".join(result)
        return MockObject(**response)
