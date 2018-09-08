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

class UtilTest(unittest.TestCase):

    def test_is_mobile(self):
        result = appier.is_mobile("Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19")
        self.assertEqual(result, True)

        result = appier.is_mobile("Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
        self.assertEqual(result, True)

        result = appier.is_mobile("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12")
        self.assertEqual(result, False)

        result = appier.is_mobile("Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30")
        self.assertEqual(result, False)

        result = appier.is_mobile("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36")
        self.assertEqual(result, False)

        result = appier.is_mobile("Mozilla/5.0 (iPad; CPU OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1")
        self.assertEqual(result, False)

        result = appier.is_mobile("")
        self.assertEqual(result, False)

        result = appier.is_mobile(None)
        self.assertEqual(result, False)

    def test_is_tablet(self):
        result = appier.is_tablet("Mozilla/5.0 (iPad; CPU OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1")
        self.assertEqual(result, True)

        result = appier.is_tablet("Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B329")
        self.assertEqual(result, True)

        result = appier.is_tablet("Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19")
        self.assertEqual(result, True)

        result = appier.is_tablet("Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
        self.assertEqual(result, True)

        result = appier.is_tablet("Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30")
        self.assertEqual(result, True)

        result = appier.is_tablet("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12")
        self.assertEqual(result, False)

        result = appier.is_tablet("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36")
        self.assertEqual(result, False)

        result = appier.is_tablet("")
        self.assertEqual(result, False)

        result = appier.is_tablet(None)
        self.assertEqual(result, False)

    def test_is_browser(self):
        result = appier.is_browser("Mozilla/5.0 (iPad; CPU OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1")
        self.assertEqual(result, True)

        result = appier.is_browser("Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B329")
        self.assertEqual(result, True)

        result = appier.is_browser("Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19")
        self.assertEqual(result, True)

        result = appier.is_browser("Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
        self.assertEqual(result, True)

        result = appier.is_browser("Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30")
        self.assertEqual(result, True)

        result = appier.is_browser("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12")
        self.assertEqual(result, True)

        result = appier.is_browser("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36")
        self.assertEqual(result, True)

        result = appier.is_browser("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136")
        self.assertEqual(result, True)

        result = appier.is_browser("DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)")
        self.assertEqual(result, False)

        result = appier.is_browser("netius/1.1.10")
        self.assertEqual(result, False)

        result = appier.is_browser("")
        self.assertEqual(result, False)

    def test_is_bot(self):
        result = appier.is_bot("Mozilla/5.0 (iPad; CPU OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1")
        self.assertEqual(result, False)

        result = appier.is_bot("Mozilla/5.0 (iPad; CPU OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B329")
        self.assertEqual(result, False)

        result = appier.is_bot("Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19")
        self.assertEqual(result, False)

        result = appier.is_bot("Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1")
        self.assertEqual(result, False)

        result = appier.is_bot("Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30")
        self.assertEqual(result, False)

        result = appier.is_bot("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12")
        self.assertEqual(result, False)

        result = appier.is_bot("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36")
        self.assertEqual(result, False)

        result = appier.is_bot("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136")
        self.assertEqual(result, False)

        result = appier.is_bot("DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)")
        self.assertEqual(result, True)

        result = appier.is_bot("netius/1.1.10")
        self.assertEqual(result, False)

        result = appier.is_bot("")
        self.assertEqual(result, False)

        result = appier.is_bot(None)
        self.assertEqual(result, False)

    def test_browser_info(self):
        result = appier.browser_info("Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136")
        self.assertEqual(result, dict(
            name = "Edge",
            version = "12.10136",
            version_f = 12.10136,
            version_i = 12,
            interactive = True,
            bot = False,
            os = "Windows"
        ))

        result = appier.browser_info("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36")
        self.assertEqual(result, dict(
            name = "Chrome",
            version = "62.0.3202.75",
            version_f = 62.0,
            version_i = 62,
            interactive = True,
            bot = False,
            os = "Windows"
        ))

        result = appier.browser_info("Mozilla/5.0 (iPad; CPU OS 9_3_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13F69 Safari/601.1")
        self.assertEqual(result, dict(
            name = "Safari",
            version = "601.1",
            version_f = 601.1,
            version_i = 601,
            interactive = True,
            bot = False,
            os = "Mac"
        ))

        result = appier.browser_info("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0")
        self.assertEqual(result, dict(
            name = "Firefox",
            version = "56.0",
            version_f = 56.0,
            version_i = 56,
            interactive = True,
            bot = False,
            os = "Windows"
        ))

        result = appier.browser_info("Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)")
        self.assertEqual(result, dict(
            name = "Explorer",
            version = "8.0",
            version_f = 8.0,
            version_i = 8,
            interactive = True,
            bot = False,
            os = "Windows"
        ))

        result = appier.browser_info("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")
        self.assertEqual(result, dict(
            name = "Googlebot",
            version = "2.1",
            version_f = 2.1,
            version_i = 2,
            interactive = False,
            bot = True
        ))

        result = appier.browser_info("Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)")
        self.assertEqual(result, dict(
            name = "Bingbot",
            version = "2.0",
            version_f = 2.0,
            version_i = 2,
            interactive = False,
            bot = True
        ))

        result = appier.browser_info("DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)")
        self.assertEqual(result, dict(
            name = "DuckDuckBot",
            version = "1.0",
            version_f = 1.0,
            version_i = 1,
            interactive = False,
            bot = True
        ))

        result = appier.browser_info("netius/1.1.10")
        self.assertEqual(result, dict(
            name = "netius",
            version = "1.1.10",
            version_f = 1.1,
            version_i = 1,
            interactive = False,
            bot = False
        ))

        result = appier.browser_info("APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)")
        self.assertEqual(result, None)

        result = appier.browser_info(None)
        self.assertEqual(result, None)

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

        name, email = appier.email_parts(appier.legacy.u(" joamag@hive.pt "))
        self.assertEqual(type(name), appier.legacy.UNICODE)
        self.assertEqual(type(email), appier.legacy.UNICODE)
        self.assertEqual(name, appier.legacy.u("joamag@hive.pt"))
        self.assertEqual(email, appier.legacy.u("joamag@hive.pt"))

    def test_email_mime(self):
        result = appier.email_mime("João Magalhães <joamag@hive.pt>")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "=?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>")

        result = appier.email_mime(appier.legacy.u("João Magalhães <joamag@hive.pt>"))
        self.assertEqual(type(result), appier.legacy.UNICODE)
        self.assertEqual(result, appier.legacy.u("=?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>"))

        result = appier.email_mime(appier.legacy.u(" joamag@hive.pt "))
        self.assertEqual(type(result), appier.legacy.UNICODE)
        self.assertEqual(result, appier.legacy.u("joamag@hive.pt <joamag@hive.pt>"))

        result = appier.email_mime([
            appier.legacy.u("João Magalhães <joamag@hive.pt>"),
            appier.legacy.u(" joamag@hive.pt "),
            None
        ])
        self.assertEqual(type(result), list)
        self.assertEqual(result, [
            appier.legacy.u("=?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>"),
            appier.legacy.u("joamag@hive.pt <joamag@hive.pt>")
        ])

    def test_email_base(self):
        result = appier.email_base("João Magalhães <joamag@hive.pt>")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "joamag@hive.pt")

        result = appier.email_base(appier.legacy.u("João Magalhães <joamag@hive.pt>"))
        self.assertEqual(type(result), appier.legacy.UNICODE)
        self.assertEqual(result, appier.legacy.u("joamag@hive.pt"))

        result = appier.email_base(appier.legacy.u(" joamag@hive.pt "))
        self.assertEqual(type(result), appier.legacy.UNICODE)
        self.assertEqual(result, appier.legacy.u("joamag@hive.pt"))

        result = appier.email_base([
            appier.legacy.u("joamag@hive.pt"),
            appier.legacy.u("joamag@hive.pt"),
            None
        ])
        self.assertEqual(type(result), list)
        self.assertEqual(result, [
            appier.legacy.u("joamag@hive.pt"),
            appier.legacy.u("joamag@hive.pt")
        ])

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

    def test_gather_errors(self):
        def raiser(): raise appier.OperationalError(message = "hello")
        struct = appier.lazy_dict(
            first = appier.lazy(lambda: raiser()),
            second = appier.lazy(lambda: 2),
        )

        errors = appier.gather_errors(struct)
        self.assertEqual(errors, dict(first = ["hello"]))

        struct.__getitem__("first", force = True)._value = 1

        errors = appier.gather_errors(struct)
        self.assertEqual(errors, dict(first = ["hello"]))

        struct.__getitem__("first", force = True)._value = 1

        errors = appier.gather_errors(struct, resolve = False)
        self.assertEqual(errors, dict())

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

        result = appier.underscore_to_readable("hello_world_")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello world")

        result = appier.underscore_to_readable("hello_world_", capitalize = True)
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World")

        result = appier.underscore_to_readable("__hello_world__")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello world")

        result = appier.underscore_to_readable("__hello_world__", capitalize = True)
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World")

        result = appier.underscore_to_readable("__hello___world__")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello world")

        result = appier.underscore_to_readable("__hello___world__", capitalize = True)
        self.assertEqual(type(result), str)
        self.assertEqual(result, "Hello World")

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

        first = dict(a = dict(a = "hello", b = "world", d = "other", m = dict(a = "hello")))
        second = dict(a = dict(a = "hello_new", b = "world_new", c = "other", m = dict(b = "world")))

        result = appier.dict_merge(first, second)
        self.assertEqual(id(result) in (id(first), (id(second))), False)
        self.assertEqual(result["a"], dict(
            a = "hello_new",
            b = "world_new",
            c = "other",
            m = dict(b = "world")
        ))

        result = appier.dict_merge(first, second, recursive = True)
        self.assertEqual(id(result) in (id(first), (id(second))), False)
        self.assertEqual(result["a"], dict(
            a = "hello_new",
            b = "world_new",
            c = "other",
            d = "other",
            m = dict(
                a = "hello",
                b = "world"
            )
        ))

    def test_verify(self):
        result = appier.verify(1 == 1)
        self.assertEqual(result, None)

        result = appier.verify("hello" == "hello")
        self.assertEqual(result, None)

        self.assertRaises(appier.AssertionError, lambda: appier.verify(1 == 2))

        self.assertRaises(
            appier.OperationalError,
            lambda: appier.verify(1 == 2, exception = appier.OperationalError)
        )

    def test_verify_equal(self):
        result = appier.verify_equal(1, 1)
        self.assertEqual(result, None)

        result = appier.verify_equal("hello", "hello")
        self.assertEqual(result, None)

        self.assertRaises(appier.AssertionError, lambda: appier.verify_equal(1, 2))

        self.assertRaises(
            appier.OperationalError,
            lambda: appier.verify_equal(1, 2, exception = appier.OperationalError)
        )

    def test_verify_not_equal(self):
        result = appier.verify_not_equal(1, 2)
        self.assertEqual(result, None)

        result = appier.verify_not_equal("hello", "world")
        self.assertEqual(result, None)

        self.assertRaises(appier.AssertionError, lambda: appier.verify_not_equal(1, 1))

        self.assertRaises(
            appier.OperationalError,
            lambda: appier.verify_not_equal(1, 1, exception = appier.OperationalError)
        )

class FileTupleTest(unittest.TestCase):

    def test_basic(self):
        file = appier.FileTuple.from_data(
            b"hello world",
            name = "hello",
            mime = "text/plain"
        )

        self.assertEqual(file.read(), b"hello world")
        self.assertEqual(file.name, "hello")
        self.assertEqual(file.mime, "text/plain")
        self.assertEqual(file.data, b"hello world")

    def test_interface(self):
        file = appier.FileTuple.from_data(
            b"hello world",
            name = "hello",
            mime = "text/plain"
        )

        self.assertEqual(file.read(), b"hello world")
        self.assertEqual(file.tell(), 11)

        file.seek(0)

        self.assertEqual(file.tell(), 0)

        self.assertEqual(file.read(5), b"hello")
        self.assertEqual(file.tell(), 5)
