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

import unittest

import appier

class RequestTest(unittest.TestCase):

    def test_mock(self):
        request = appier.Request(
            "GET",
            "/",
            address = "127.0.0.1",
            session_c = appier.FileSession
        )
        request.load_session()

        sid = request.session.sid

        self.assertEqual(request.session.__class__, appier.MockSession)
        self.assertEqual(request.session.sid, sid)
        self.assertEqual(request.session.address, "127.0.0.1")

        request.session["first"] = 1

        self.assertNotEqual(request.set_cookie, None)

        self.assertEqual(request.session["first"], 1)
        self.assertEqual(request.session.__class__, appier.FileSession)
        self.assertEqual(request.session.sid, sid)
        self.assertEqual(request.session.address, "127.0.0.1")

        appier.FileSession.close()

    def test_query_s(self):
        request = appier.Request(
            "GET",
            "/",
            query = "x-message=hello&message=world"
        )
        request.resolve_query_s()

        self.assertEqual(request.query, "x-message=hello&message=world")
        self.assertEqual(request.query_s, "message=world")
        self.assertEqual(request.location, "/")
        self.assertEqual(request.location_f, "/?message=world")

    def test_get_address(self):
        request = appier.Request("GET", "/", address = "127.0.0.1")

        self.assertEqual(request.get_address(), "127.0.0.1")

        request.in_headers["X-Forwarded-For"] = "1.1.1.1, 1.1.1.2, 1.1.1.3"
        self.assertEqual(request.get_address(), "1.1.1.1")

        request.in_headers["X-Client-Ip"] = "2.2.2.2"
        self.assertEqual(request.get_address(), "2.2.2.2")

        request.in_headers["X-Real-Ip"] = "3.3.3.3"
        self.assertEqual(request.get_address(), "3.3.3.3")

        result = request.get_address(resolve = False)
        self.assertEqual(result, "127.0.0.1")

        request = appier.Request("GET", "/", address = "::ffff:127.0.0.1")

        self.assertEqual(request.get_address(), "127.0.0.1")

        result = request.get_address(cleanup = False)
        self.assertEqual(result, "::ffff:127.0.0.1")

    def test_get_host(self):
        request = appier.Request(
            "GET",
            "/",
            address = "127.0.0.1",
            environ = dict(
                SERVER_NAME = "local.com",
                SERVER_PORT = "80"
            )
        )

        self.assertEqual(request.get_host(), "local.com:80")

        request = appier.Request(
            "GET",
            "/",
            address = "127.0.0.1",
            environ = dict(
                SERVER_NAME = "local.com",
                SERVER_PORT = "80",
                HTTP_HOST = "forward.example.com",
                HTTP_X_FORWARDED_HOST = "example.com"
            )
        )
        request.load_headers()

        self.assertEqual(request.get_host(), "example.com")
        self.assertEqual(request.get_host(resolve = False), "forward.example.com")

    def test_get_url(self):
        request = appier.Request(
            "GET",
            "/",
            scheme = "http",
            address = "127.0.0.1",
            environ = dict(
                SERVER_NAME = "local.com",
                SERVER_PORT = "80"
            )
        )

        self.assertEqual(request.get_url(), "http://local.com:80/")

        request = appier.Request(
            "GET",
            "/",
            query = "hello=world&world=hello",
            scheme = "http",
            address = "127.0.0.1",
            environ = dict(
                SERVER_NAME = "local.com",
                SERVER_PORT = "80",
                HTTP_HOST = "forward.example.com",
                HTTP_X_FORWARDED_HOST = "example.com"
            )
        )
        request.load_headers()

        self.assertEqual(request.get_url(), "http://example.com/?hello=world&world=hello")
        self.assertEqual(request.get_url(resolve = False), "http://forward.example.com/?hello=world&world=hello")

    def test_get_header(self):
        request = appier.Request(
            "GET",
            "/",
            environ = dict(
                HTTP_CONTENT_TYPE = "text/plain",
                HTTP_X_REAL_IP = "1.1.1.1"
            )
        )
        request.load_headers()

        self.assertEqual(request.get_header("Content-Type"), "text/plain")
        self.assertEqual(request.get_header("content-type"), "text/plain")
        self.assertEqual(request.get_header("CONTENT-TYPE"), "text/plain")
        self.assertEqual(request.get_header("Content-TYPE"), "text/plain")
        self.assertEqual(request.get_header("Content_Type"), None)
        self.assertEqual(request.get_header("CONTENT_TYPE"), None)
        self.assertEqual(request.get_header("Content-Type", normalize = False), "text/plain")
        self.assertEqual(request.get_header("content-type", normalize = False), None)
        self.assertEqual(request.get_header("CONTENT-TYPE", normalize = False), None)

        self.assertEqual(request.get_header("X-Real-IP"), "1.1.1.1")
        self.assertEqual(request.get_header("X-Real-Ip"), "1.1.1.1")
        self.assertEqual(request.get_header("x-real-ip"), "1.1.1.1")
        self.assertEqual(request.get_header("X-REAL-IP"), "1.1.1.1")
        self.assertEqual(request.get_header("X-Real-IP"), "1.1.1.1")
        self.assertEqual(request.get_header("X_Real_Ip"), None)
        self.assertEqual(request.get_header("X_REAL_IP"), None)
        self.assertEqual(request.get_header("X-Real-Ip", normalize = False), "1.1.1.1")
        self.assertEqual(request.get_header("X-Real-IP", normalize = False), None)
        self.assertEqual(request.get_header("x-real-ip", normalize = False), None)
        self.assertEqual(request.get_header("X-REAL-IP", normalize = False), None)

    def test_data(self):
        request = appier.Request("GET", "/")
        request.set_data(appier.legacy.bytes("hello world", encoding = "utf-8"))

        self.assertEqual(type(request.get_data()), bytes)
        self.assertEqual(request.get_data(), appier.legacy.bytes("hello world", encoding = "utf-8"))
        self.assertEqual(type(request.get_encoded()), appier.legacy.UNICODE)
        self.assertEqual(request.get_encoded(), appier.legacy.u("hello world"))

        request = appier.Request("GET", "/")
        request.set_data(appier.legacy.bytes("你好世界", encoding = "utf-8"))

        self.assertEqual(type(request.get_data()), bytes)
        self.assertEqual(request.get_data(), appier.legacy.bytes("你好世界", encoding = "utf-8"))
        self.assertEqual(type(request.get_encoded()), appier.legacy.UNICODE)
        self.assertEqual(request.get_encoded(), appier.legacy.u("你好世界"))
        self.assertEqual(type(request.get_encoded(encoding = "ascii")), bytes)
        self.assertEqual(request.get_data(), appier.legacy.bytes("你好世界", encoding = "utf-8"))
        self.assertRaises(
            UnicodeDecodeError,
            lambda: request.get_encoded(encoding = "ascii", safe = False)
        )
