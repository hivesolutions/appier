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


class ValidationTest(unittest.TestCase):

    def test_is_simple(self):
        self.assertEqual(appier.is_simple("value")(dict(value=""), None), True)
        self.assertEqual(appier.is_simple("value")(dict(value="hello"), None), True)
        self.assertEqual(
            appier.is_simple("value")(dict(value="hello world"), None), True
        )

        with self.assertRaises(appier.ValidationInternalError):
            self.assertEqual(
                appier.is_simple("value")(dict(value="hello?world"), None), True
            )
        with self.assertRaises(appier.ValidationInternalError):
            self.assertEqual(
                appier.is_simple("value")(dict(value="hello=world"), None), True
            )
        with self.assertRaises(appier.ValidationInternalError):
            self.assertEqual(
                appier.is_simple("value")(
                    dict(value=appier.legacy.u("你好世界")), None
                ),
                True,
            )

    def test_is_email(self):
        self.assertEqual(appier.is_email("value")(dict(value=""), None), True)
        self.assertEqual(
            appier.is_email("value")(dict(value="user@domain.com"), None), True
        )
        self.assertEqual(
            appier.is_email("value")(dict(value="first.second@domain.com"), None), True
        )
        self.assertEqual(
            appier.is_email("value")(dict(value="first+second@domain.com"), None), True
        )
        self.assertEqual(
            appier.is_email("value")(
                dict(value=appier.legacy.u("你好世界@domain.com")), None
            ),
            True,
        )

        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value="user"), None)
        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value="domain"), None)
        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value="domain.com"), None)
        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value="user@"), None)
        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value=appier.legacy.u("你好世界")), None)
        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value=appier.legacy.u("你好世界@")), None)

    def test_is_url(self):
        self.assertEqual(appier.is_url("value")(dict(value=""), None), True)
        self.assertEqual(
            appier.is_url("value")(dict(value="http://hello.com"), None), True
        )
        self.assertEqual(
            appier.is_url("value")(dict(value="http://hello.world"), None), True
        )
        self.assertEqual(
            appier.is_url("value")(dict(value="https://hello.world"), None), True
        )
        self.assertEqual(
            appier.is_url("value")(
                dict(value=appier.legacy.u("https://你好世界")), None
            ),
            True,
        )
        self.assertEqual(appier.is_url("value")(dict(value="http://hello"), None), True)
        self.assertEqual(
            appier.is_url("value")(dict(value="mailto://hello"), None), True
        )

        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value=appier.legacy.u("http:")), None)
        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value=appier.legacy.u("http://")), None)
        with self.assertRaises(appier.ValidationInternalError):
            appier.is_email("value")(dict(value=appier.legacy.u("mailto://")), None)
