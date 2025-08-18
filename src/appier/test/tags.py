#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2024 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import unittest

import appier


class TagsTest(unittest.TestCase):
    def setUp(self):
        self.app = appier.App()

    def tearDown(self):
        self.app.unload()

    def test_script_tag(self):
        if not self.app.jinja:
            if not hasattr(self, "skipTest"):
                return
            self.skipTest("No Jinja2 template engine present")

        template = appier.Template("{{ value|script_tag }}")
        result = self.app.template(template, value="/static/app.js")
        self.assertEqual(
            result, '<script type="text/javascript" src="/static/app.js"></script>'
        )

        template = appier.Template("{{ '/static/app.js'|script_tag }}")
        result = self.app.template(template)
        self.assertEqual(
            result, '<script type="text/javascript" src="/static/app.js"></script>'
        )

    def test_css_tag(self):
        if not self.app.jinja:
            if not hasattr(self, "skipTest"):
                return
            self.skipTest("No Jinja2 template engine present")

        template = appier.Template("{{ value|css_tag }}")
        result = self.app.template(template, value="/static/style.css")
        self.assertEqual(
            result, '<link rel="stylesheet" type="text/css" href="/static/style.css" />'
        )

        template = appier.Template("{{ '/static/style.css'|css_tag }}")
        result = self.app.template(template)
        self.assertEqual(
            result, '<link rel="stylesheet" type="text/css" href="/static/style.css" />'
        )

    def test_stylesheet_tag(self):
        if not self.app.jinja:
            if not hasattr(self, "skipTest"):
                return
            self.skipTest("No Jinja2 template engine present")

        template = appier.Template("{{ value|stylesheet_tag }}")
        result = self.app.template(template, value="/static/main.css")
        self.assertEqual(
            result, '<link rel="stylesheet" type="text/css" href="/static/main.css" />'
        )

        template = appier.Template("{{ '/static/main.css'|stylesheet_tag }}")
        result = self.app.template(template)
        self.assertEqual(
            result, '<link rel="stylesheet" type="text/css" href="/static/main.css" />'
        )

    def test_asset_url(self):
        if not self.app.jinja:
            if not hasattr(self, "skipTest"):
                return
            self.skipTest("No Jinja2 template engine present")

        template = appier.Template("{{ filename|asset_url }}")
        result = self.app.template(template, filename="logo.png")
        self.assertEqual(result, "/static/assets/logo.png")

        template = appier.Template("{{ 'logo.png'|asset_url }}")
        result = self.app.template(template)
        self.assertEqual(result, "/static/assets/logo.png")
