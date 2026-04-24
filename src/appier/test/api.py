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


class APITest(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.captured = []

        test_case = self

        class SpyAPI(appier.API):
            def build(
                self,
                method,
                url,
                data=None,
                data_j=None,
                data_m=None,
                headers=None,
                params=None,
                mime=None,
                kwargs=None,
            ):
                kwargs["access_token"] = "TOKEN"

            def request(self, method, url, params=None, **kwargs):
                test_case.captured.append(params)
                raise RuntimeError("stop")

        self.spy_cls = SpyAPI

    def test_get(self):
        api = self.spy_cls()

        self.assertRaises(RuntimeError, api.get, "http://hive.pt/", token=True)

        params = self.captured[-1]

        self.assertEqual(params["token"], True)
        self.assertEqual(params["access_token"], "TOKEN")
        self.assertEqual("uuid" in params, False)

    def test_post(self):
        api = self.spy_cls()

        self.assertRaises(RuntimeError, api.post, "http://hive.pt/", token=True)

        params = self.captured[-1]

        self.assertEqual(params["token"], True)
        self.assertEqual(params["access_token"], "TOKEN")
        self.assertEqual("uuid" in params, False)

    def test_put(self):
        api = self.spy_cls()

        self.assertRaises(RuntimeError, api.put, "http://hive.pt/", token=True)

        params = self.captured[-1]

        self.assertEqual(params["token"], True)
        self.assertEqual(params["access_token"], "TOKEN")
        self.assertEqual("uuid" in params, False)

    def test_delete(self):
        api = self.spy_cls()

        self.assertRaises(RuntimeError, api.delete, "http://hive.pt/", token=True)

        params = self.captured[-1]

        self.assertEqual(params["token"], True)
        self.assertEqual(params["access_token"], "TOKEN")
        self.assertEqual("uuid" in params, False)

    def test_patch(self):
        api = self.spy_cls()

        self.assertRaises(RuntimeError, api.patch, "http://hive.pt/", token=True)

        params = self.captured[-1]

        self.assertEqual(params["token"], True)
        self.assertEqual(params["access_token"], "TOKEN")
        self.assertEqual("uuid" in params, False)

    def test__sanitize_kwargs(self):
        api = appier.API()

        result = api._sanitize_kwargs(dict(token=True, uuid="abc"))

        self.assertEqual(result, dict(token=True))
        self.assertEqual(isinstance(result, dict), True)

        result = api._sanitize_kwargs(
            dict(token=True, uuid="abc"), cls_t=appier.OrderedDict
        )

        self.assertEqual(result["token"], True)
        self.assertEqual("uuid" in result, False)
        self.assertEqual(isinstance(result, appier.OrderedDict), True)

    def test__desanitize_kwargs(self):
        api = appier.API()

        result = api._desanitize_kwargs(dict(token=True, uuid="abc"))

        self.assertEqual(result, dict(uuid="abc"))
        self.assertEqual(isinstance(result, dict), True)

        result = api._desanitize_kwargs(
            dict(token=True, uuid="abc"), cls_t=appier.OrderedDict
        )

        self.assertEqual(result["uuid"], "abc")
        self.assertEqual("token" in result, False)
        self.assertEqual(isinstance(result, appier.OrderedDict), True)
