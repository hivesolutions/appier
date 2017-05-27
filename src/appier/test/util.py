#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2017 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import unittest

import appier

class UtilTest(unittest.TestCase):

    def test_obfuscate(self):
        result = appier.obfuscate("hello world")
        self.assertEqual(result, "hel********")

        result = appier.obfuscate("hello world", display_l = 6)
        self.assertEqual(result, "hello *****")

        result = appier.obfuscate("hello world", display_l = 100)
        self.assertEqual(result, "hello world")

        result = appier.obfuscate("hello world", display_l = 6, token = "-")
        self.assertEqual(result, "hello -----")

        result = appier.obfuscate(appier.legacy.u("你好世界"), display_l = 3)
        self.assertEqual(result, appier.legacy.u("你好世*"))

    def test_email_parts(self):
        name, email = appier.email_parts("João Magalhães <joamag@hive.pt>")
        self.assertEqual(type(name), str)
        self.assertEqual(type(email), str)
        self.assertEqual(name, "João Magalhães")
        self.assertEqual(email, "joamag@hive.pt")

        name, email = appier.email_parts(appier.legacy.u("João Magalhães <joamag@hive.pt>"))
        self.assertEqual(type(name), appier.legacy.UNICODE)
        self.assertEqual(type(email), appier.legacy.UNICODE)
        self.assertEqual(name, appier.legacy.u("João Magalhães"))
        self.assertEqual(email, appier.legacy.u("joamag@hive.pt"))

        name, email = appier.email_parts(appier.legacy.u("你好世界 <hello@hive.pt>"))
        self.assertEqual(type(name), appier.legacy.UNICODE)
        self.assertEqual(type(email), appier.legacy.UNICODE)
        self.assertEqual(name, appier.legacy.u("你好世界"))
        self.assertEqual(email, appier.legacy.u("hello@hive.pt"))

    def test_email_mime(self):
        result = appier.email_mime("João Magalhães <joamag@hive.pt>")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "=?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>")

        result = appier.email_mime(appier.legacy.u("João Magalhães <joamag@hive.pt>"))
        self.assertEqual(type(result), appier.legacy.UNICODE)
        self.assertEqual(result, appier.legacy.u("=?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>"))

    def test_date_to_timestamp(self):
        result = appier.date_to_timestamp("29/06/1984")
        self.assertEqual(type(result), int)
        self.assertEqual(int(result), 457315200)

        result = appier.date_to_timestamp("29/06/0000")
        self.assertEqual(result, None)

        result = appier.date_to_timestamp("1984-06-29", format = "%Y-%m-%d")
        self.assertEqual(result, 457315200)

        result = appier.date_to_timestamp("1984-13-29", format = "%Y-%m-%d")
        self.assertEqual(result, None)

    def test_camel_to_underscore(self):
        result = appier.camel_to_underscore("HelloWorld")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "hello_world")

        result = appier.camel_to_underscore("HELLOWorld")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "hello_world")

        result = appier.camel_to_underscore("HELLOWorldHELLOWorld")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "hello_world_hello_world")

    def test_camel_to_readable(self):
        result = appier.camel_to_readable("HelloWorld")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World")

        result = appier.camel_to_readable("HelloWorld", lower = True)
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello world")

        result = appier.camel_to_readable("HelloWorld", lower = True, capitalize = True)
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World")

        result = appier.camel_to_readable("HELLOWorld")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "HELLO World")

        result = appier.camel_to_readable("HELLOWorld", lower = True)
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello world")

        result = appier.camel_to_readable(
            "HELLOWorld",
            lower = True,
            capitalize = True
        )
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World")

        result = appier.camel_to_readable("HELLOWorldHELLOWorld")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "HELLO World HELLO World")

        result = appier.camel_to_readable(
            "HELLOWorldHELLOWorld",
            lower = True
        )
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello world hello world")

        result = appier.camel_to_readable(
            "HELLOWorldHELLOWorld",
            lower = True,
            capitalize = True
        )
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World Hello World")

    def test_underscore_to_readable(self):
        result = appier.underscore_to_readable("hello_world")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello world")

        result = appier.underscore_to_readable("hello_world", capitalize = True)
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World")

        result = appier.underscore_to_readable("hello_world_hello_world")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello world hello world")

        result = appier.underscore_to_readable("hello_world_hello_world", capitalize = True)
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World Hello World")

    def test_is_content_type(self):
        result = appier.is_content_type("text/plain", "text/plain")
        self.assertEqual(result, True)

        result = appier.is_content_type("text/plain", ("text/plain",))
        self.assertEqual(result, True)

        result = appier.is_content_type("text/plain", "text/html")
        self.assertEqual(result, False)

        result = appier.is_content_type("text/plain", ("text/html",))
        self.assertEqual(result, False)

        result = appier.is_content_type("text/plain", ("text/plain", "text/html"))
        self.assertEqual(result, True)

        result = appier.is_content_type("text/*", "text/plain")
        self.assertEqual(result, True)

        result = appier.is_content_type("text/*", "text/json")
        self.assertEqual(result, True)

    def test_parse_content_type(self):
        result = appier.parse_content_type("text/plain")
        self.assertEqual(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ["text/plain"])
        self.assertEqual(result[1], dict())

        result = appier.parse_content_type("text/plain+json")
        self.assertEqual(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ["text/plain", "text/json"])
        self.assertEqual(result[1], dict())

        result = appier.parse_content_type("text/plain+json; charset=utf-8")
        self.assertEqual(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ["text/plain", "text/json"])
        self.assertEqual(result[1], dict(charset = "utf-8"))

        result = appier.parse_content_type("text/plain+json   ; charset=utf-8")
        self.assertEqual(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ["text/plain", "text/json"])
        self.assertEqual(result[1], dict(charset = "utf-8"))

        result = appier.parse_content_type("text/plain+json; charset=utf-8; boundary=hello;")
        self.assertEqual(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ["text/plain", "text/json"])
        self.assertEqual(result[1], dict(charset = "utf-8", boundary = "hello"))

        result = appier.parse_content_type("")
        self.assertEqual(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [])
        self.assertEqual(result[1], dict())

        result = appier.parse_content_type("text")
        self.assertEqual(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [])
        self.assertEqual(result[1], dict())

        result = appier.parse_content_type("text/plain+json; charset")
        self.assertEqual(type(result), tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ["text/plain", "text/json"])
        self.assertEqual(result[1], dict())

    def test_check_login(self):
        request = appier.Request("GET", "/", session_c = appier.MemorySession)

        request.session["tokens"] = ["*"]
        result = appier.check_login(None, token = "admin", request = request)
        self.assertEqual(result, True)
        self.assertEqual(request.session["tokens"], {"*" : True})

        request.session["tokens"] = []
        result = appier.check_login(None, token = "admin", request = request)
        self.assertEqual(result, False)
        self.assertEqual(request.session["tokens"], {})

        request.session["tokens"] = ["admin"]
        result = appier.check_login(None, token = "admin", request = request)
        self.assertEqual(result, True)
        self.assertEqual(request.session["tokens"], {"admin" : True})

        request.session["tokens"] = ["admin.read"]
        result = appier.check_login(None, token = "admin", request = request)
        self.assertEqual(result, False)
        result = appier.check_login(None, token = "admin.read", request = request)
        self.assertEqual(result, True)
        self.assertEqual(request.session["tokens"], {
            "admin" : {
                "read" : True
            }
        })

        request.session["tokens"] = ["admin.*"]
        result = appier.check_login(None, token = "admin.read", request = request)
        self.assertEqual(result, True)
        self.assertEqual(request.session["tokens"], {
            "admin" : {
                "*" : True
            }
        })

        request.session["tokens"] = ["admin", "admin.write"]
        result = appier.check_login(None, token = "admin.read", request = request)
        self.assertEqual(result, False)
        self.assertEqual(request.session["tokens"], {
            "admin" : {
                "_" : True,
                "write" : True
            }
        })

        request.session["tokens"] = ["admin.write", "admin.*"]
        result = appier.check_login(None, token = "admin.read", request = request)
        self.assertEqual(result, True)
        self.assertEqual(request.session["tokens"], {
            "admin" : {
                "write" : True,
                "*" : True
            }
        })

        del request.session["tokens"]
        result = appier.check_login(None, token = "admin.read", request = request)
        self.assertEqual(result, False)
        self.assertEqual("tokens" in request.session, False)

    def test_check_tokens(self):
        result = appier.check_tokens(None, ("admin", "user"), tokens_m = {"*" : True})
        self.assertEqual(result, True)

        result = appier.check_tokens(None, ("admin", "user"), tokens_m = {})
        self.assertEqual(result, False)

        result = appier.check_tokens(None, ("admin", "user"), tokens_m = {"admin" : True})
        self.assertEqual(result, False)

    def test_check_token(self):
        result = appier.check_token(None, "admin", tokens_m = {"*" : True})
        self.assertEqual(result, True)

        result = appier.check_token(None, "admin", tokens_m = {})
        self.assertEqual(result, False)

        result = appier.check_token(None, "admin", tokens_m = {"admin" : True})
        self.assertEqual(result, True)

        result = appier.check_token(None, "admin.read", tokens_m = {
            "admin" : {
                "read" : True
            }
        })
        self.assertEqual(result, True)

        result = appier.check_token(None, "admin", tokens_m = {
            "admin" : {
                "read" : True
            }
        })
        self.assertEqual(result, False)

        result = appier.check_token(None, "admin.read", tokens_m = {
            "admin" : {
                "*" : True
            }
        })
        self.assertEqual(result, True)

        result = appier.check_token(None, None, tokens_m = {})
        self.assertEqual(result, True)

    def test_to_tokens_m(self):
        result = appier.to_tokens_m(["admin"])
        self.assertEqual(result, {"admin" : True})

        result = appier.to_tokens_m(["admin", "admin.read"])
        self.assertEqual(result, {
            "admin" : {
                "_" : True,
                "read" : True
            }
        })

        result = appier.to_tokens_m(["admin.read", "admin"])
        self.assertEqual(result, {
            "admin" : {
                "_" : True,
                "read" : True
            }
        })

        result = appier.to_tokens_m(["admin", "admin.*"])
        self.assertEqual(result, {
            "admin" : {
                "_" : True,
                "*" : True
            }
        })

    def test_dict_merge(self):
        first = dict(a = "hello", b = "world")
        second = dict(a = "hello_new", b = "world_new", c = "other")

        result = appier.dict_merge(first, second)
        self.assertEqual(id(result) in (id(first), (id(second))), False)
        self.assertEqual(result["a"], "hello_new")
        self.assertEqual(result["b"], "world_new")
        self.assertEqual(result["c"], "other")

        result = appier.dict_merge(first, second, override = False)
        self.assertEqual(id(result) in (id(first), (id(second))), False)
        self.assertEqual(result["a"], "hello")
        self.assertEqual(result["b"], "world")
        self.assertEqual(result["c"], "other")
