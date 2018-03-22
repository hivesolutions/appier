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

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.app = appier.App()

    def tearDown(self):
        self.app.unload()

    def test_locale(self):
        self.app.locales = ("en_us", "pt_pt", "es_es")
        self.app._register_bundle(dict(hello = "Hello"), "en_us")
        self.app._register_bundle(dict(hello = "Olá"), "pt_pt")
        self.app._register_bundle(dict(hello = "Bonjour"), "fr")

        result = self.app.to_locale("hello")
        self.assertEqual(result, "Hello")

        result = self.app.to_locale("hello", locale = "en_us")
        self.assertEqual(result, "Hello")

        result = self.app.to_locale("hello", locale = "en-us")
        self.assertEqual(result, "Hello")

        result = self.app.to_locale("hello", locale = "pt_pt")
        self.assertEqual(result, "Olá")

        result = self.app.to_locale("hello", locale = "pt-pt")
        self.assertNotEqual(result, "Olá")
        self.assertEqual(result, "Hello")

        result = self.app.to_locale("hello", locale = "fr_fr")
        self.assertEqual(result, "Bonjour")

        result = self.app.to_locale("hello", locale = "fr")
        self.assertEqual(result, "Bonjour")

        result = self.app.to_locale("hello", locale = "es_es")
        self.assertNotEqual(result, "Hola")
        self.assertEqual(result, "Hello")

        result = self.app.has_locale("hello", locale = "pt_pt")
        self.assertEqual(result, True)

        result = self.app.has_locale("Hello", locale = "pt_pt")
        self.assertEqual(result, False)

        result = self.app.has_locale("hello", locale = "fr_fr")
        self.assertEqual(result, True)

        result = self.app.has_locale("hello", locale = "fr")
        self.assertEqual(result, True)

        result = self.app.has_locale("Hello", locale = "fr")
        self.assertEqual(result, False)

        result = self.app.has_locale("hello", locale = "es_es")
        self.assertEqual(result, False)

        result = self.app.has_locale("Hello", locale = "es_es")
        self.assertEqual(result, False)

        self.app._register_bundle(dict(hello = "Hola"), "es_es")

        result = self.app.to_locale("hello", locale = "es_es")
        self.assertEqual(result, "Hola")

        result = self.app.to_locale("hello", locale = "en")
        self.assertEqual(result, "Hello")

        result = self.app.to_locale("hello", locale = "pt")
        self.assertEqual(result, "Olá")

        result = self.app.to_locale("hello", locale = "es")
        self.assertEqual(result, "Hola")

        result = self.app.to_locale("bye")
        self.assertEqual(result, "bye")

        result = self.app.to_locale("bye", locale = "cn")
        self.assertEqual(result, "bye")

        self.app._register_bundle(dict(bye = "Bye"), "en_us")

        result = self.app.to_locale("bye")
        self.assertEqual(result, "Bye")

        result = self.app.to_locale("bye", locale = "en_us")
        self.assertEqual(result, "Bye")

        result = self.app.to_locale("bye", locale = "pt_pt")
        self.assertEqual(result, "Bye")

        result = self.app.to_locale("bye", locale = "pt_pt", fallback = False)
        self.assertEqual(result, "bye")

        result = self.app.has_locale("bye", locale = "en_us")
        self.assertEqual(result, True)

        result = self.app.has_locale("Bye", locale = "en_us")
        self.assertEqual(result, False)

        result = self.app.has_locale("bye", locale = "pt_pt")
        self.assertEqual(result, False)

        result = self.app.has_locale("Bye", locale = "pt_pt")
        self.assertEqual(result, False)

    def test_field(self):
        request = appier.Request("GET", "/")
        request.set_params(
            dict(
                name = ["john doe"],
                message = [""],
                valid_email = ["john@doe.com"],
                invalid_email = ["john"],
                valid_length = ["1234"],
                invalid_length = ["12345"]
            ),
        )
        self.app._request = request

        value = self.app.field("name")
        self.assertEqual(value, "john doe")

        value = self.app.field("message", mandatory = True)
        self.assertEqual(value, "")

        value = self.app.field(
            "valid_email",
            mandatory = True,
            not_empty = True,
            validation = (appier.is_email,)
        )
        self.assertEqual(value, "john@doe.com")

        value = self.app.field(
            "valid_length",
            mandatory = True,
            not_empty = True,
            validation = ((appier.string_lt, 5),)
        )
        self.assertEqual(value, "1234")

        self.assertRaises(
            appier.OperationalError,
            lambda: self.app.field("other", mandatory = True)
        )

        self.assertRaises(
            appier.OperationalError,
            lambda: self.app.field("message", mandatory = True, not_empty = True)
        )

        self.assertRaises(
            appier.ValidationInternalError,
            lambda: self.app.field(
                "invalid_email",
                mandatory = True,
                not_empty = True,
                validation = (appier.is_email,)
            )
        )

        self.assertRaises(
            appier.ValidationInternalError,
            lambda: self.app.field(
                "invalid_length",
                mandatory = True,
                not_empty = True,
                validation = ((appier.string_lt, 5),)
            )
        )

    def test_slugify(self):
        result = self.app.slugify("hello world")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "hello-world")

        result = self.app.slugify("olá mundo")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "ola-mundo")

    def test_pyslugify(self):
        if not self.app.pyslugify:
            if not hasattr(self, "skipTest"): return
            self.skipTest("No python-slugify engine present")

        result = self.app.slugify_pyslugify("hello world")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "hello-world")

        result = self.app.slugify_pyslugify("olá mundo")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "ola-mundo")

        result = self.app.slugify_pyslugify("你好世界")
        self.assertEqual(result, "ni-hao-shi-jie")

        result = self.app.slugify_pyslugify(appier.legacy.bytes("你好世界", encoding = "utf-8"))
        self.assertEqual(type(result), str)
        self.assertEqual(result, "ni-hao-shi-jie")

    def test_slugier(self):
        if not self.app.slugier:
            if not hasattr(self, "skipTest"): return
            self.skipTest("No slugier engine present")

        result = self.app.slugify_slugier("hello world")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "hello-world")

        result = self.app.slugify_slugier("olá mundo")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "ola-mundo")

        result = self.app.slugify_slugier("你好世界")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "%e4%bd%a0%e5%a5%bd%e4%b8%96%e7%95%8c")

        result = self.app.slugify_slugier(appier.legacy.bytes("你好世界", encoding = "utf-8"))
        self.assertEqual(type(result), str)
        self.assertEqual(result, "%e4%bd%a0%e5%a5%bd%e4%b8%96%e7%95%8c")

    def test_url_for(self):
        result = self.app.url_for("app.login")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "/login")

        result = self.app.url_for("app.login", query = "query_string")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "/login?query_string")

        result = self.app.url_for("app.login", params = dict(query = "query_string"))
        self.assertEqual(type(result), str)
        self.assertEqual(result, "/login?query=query_string")

        result = self.app.url_for("static", filename = "hello.txt")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "/static/hello.txt")

        result = self.app.url_for("static", filename = "hello.txt", compress = "gzip")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "/static/hello.txt?compress=gzip")

    def test_filters(self):
        if not self.app.jinja:
            if not hasattr(self, "skipTest"): return
            self.skipTest("No Jinja2 template engine present")

        template = appier.Template("{{ message|locale }}")
        result = self.app.template(template, message = "hello")
        self.assertEqual(result, "hello")

        template = appier.Template("{{ message|nl_to_br }}")
        result = self.app.template(template, message = "hello\n")
        self.assertEqual(result, "hello<br/>\n")

        template = appier.Template("{{ message|sp_to_nbsp }}")
        result = self.app.template(template, message = "hello world")
        self.assertEqual(result, "hello&nbsp;world")

    def test_locale_filter(self):
        if not self.app.jinja:
            if not hasattr(self, "skipTest"): return
            self.skipTest("No Jinja2 template engine present")

        self.app._register_bundle({
            "hello" : appier.legacy.u("olá"),
            "world" : appier.legacy.u("mundo"),
        }, "pt_pt")

        template = appier.Template("{{ message|locale }}")
        result = self.app.template(template, locale = "pt_pt", message = "hello")
        self.assertEqual(result, appier.legacy.u("olá"))
        result = self.app.template(template, locale = "en_us", message = "hello")
        self.assertEqual(result, appier.legacy.u("hello"))

        template = appier.Template("{{ 'hello'|locale }}")
        result = self.app.template(template, locale = "pt_pt")
        self.assertEqual(result, appier.legacy.u("olá"))
        result = self.app.template(template, locale = "en_us")
        self.assertEqual(result, appier.legacy.u("hello"))
