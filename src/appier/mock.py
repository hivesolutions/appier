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

from . import util
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

class MockResponse(MockObject):

    def read(self):
        return self.data

    def readline(self):
        return self.read()

    def close(self):
        pass

    def getcode(self):
        return self.code

    def info(self):
        return self.headers

class MockApp(object):

    def get(self, *args, **kwargs):
        return self.method("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.method("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.method("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.method("DELETE", *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.method("PATCH", *args, **kwargs)

    def options(self, *args, **kwargs):
        return self.method("OPTIONS", *args, **kwargs)

    def method(
        self,
        method,
        location,
        query = "",
        data = b"",
        scheme = "http",
        address = "127.0.0.1",
        headers = {}
    ):
        # creates the dictionary that is going to hold the (initial)
        # response structure and the "encapsulates" the provided data
        # payload around a bytes io buffer (provides file interface)
        response = dict()
        input = legacy.BytesIO(data)

        # verifies if the location contains a query part (question mark)
        # and if that's the case splits the location in the two parts
        if "?" in location: location, query = location.split("?", 1)

        # builds the map that is going to be used as the basis for the
        # construction of the request, this map should be compliant with
        # the WSGI standard and expectancy
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

        # iterates over the complete set of provided header value to set
        # them with the proper HTTP_ prefix in the environment map
        for name, value in headers: environ["HTTP_" + name.upper()] = value

        def start_response(code, headers):
            # splits the provided code string into its component
            # verifying defaulting the status of the code to an
            # empty string in case none is defined (only code)
            code_s = code.split(" ", 1)
            if len(code_s) == 1: code, status = code_s[0], ""
            else: code, status = code_s

            # converts the code into the integer representation
            # so that its type is coherent with specification
            code = int(code)

            # updates the various fields of the response dictionary
            # including: code, status and headers, this structure is
            # going to be used latter in the building of the mock object
            response["code"] = code
            response["status"] = status
            response["headers"] = dict(headers)
            response["headers_l"] = headers

        # runs the application call providing it with the environment
        # dictionary and the start response callable and then joins the
        # resulting data buffer, sets it in the response dictionary and
        # encapsulates that same dictionary around a mock object, note
        # that the application execution is performed under the request
        # "safe" context that replaces the current application's context
        # in a proper way so that at the end of the call it's properly
        # restored as expected by a possible control flow
        with util.ctx_request(self): result = self.application(environ, start_response)
        response["data"] = b"".join(result)
        return MockResponse(**response)
