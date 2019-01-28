#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import unittest
import threading

import appier

class HTTPTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.httpbin = appier.conf("HTTPBIN", "httpbin.org")

    def test_parse_url(self):
        url, scheme, host, authorization, params = appier.http._parse_url("http://hive.pt/")

        self.assertEqual(url, "http://hive.pt:80/")
        self.assertEqual(scheme, "http")
        self.assertEqual(host, "hive.pt")
        self.assertEqual(authorization, None)
        self.assertEqual(params, {})

        url, scheme, host, authorization, params = appier.http._parse_url("http://username@hive.pt/")

        self.assertEqual(url, "http://hive.pt:80/")
        self.assertEqual(scheme, "http")
        self.assertEqual(host, "hive.pt")
        self.assertEqual(authorization, None)
        self.assertEqual(params, {})

        url, scheme, host, authorization, params = appier.http._parse_url("http://username:password@hive.pt/")

        self.assertEqual(url, "http://hive.pt:80/")
        self.assertEqual(scheme, "http")
        self.assertEqual(host, "hive.pt")
        self.assertEqual(authorization, "dXNlcm5hbWU6cGFzc3dvcmQ=")
        self.assertEqual(params, {})

        url, scheme, host, authorization, params = appier.http._parse_url("http://username:password@hive.pt/hello/world")

        self.assertEqual(url, "http://hive.pt:80/hello/world")
        self.assertEqual(scheme, "http")
        self.assertEqual(host, "hive.pt")
        self.assertEqual(authorization, "dXNlcm5hbWU6cGFzc3dvcmQ=")
        self.assertEqual(params, {})

        url, scheme, host, authorization, params = appier.http._parse_url("http://username:password@hive.pt/hello/world?hello=world")

        self.assertEqual(url, "http://hive.pt:80/hello/world")
        self.assertEqual(scheme, "http")
        self.assertEqual(host, "hive.pt")
        self.assertEqual(authorization, "dXNlcm5hbWU6cGFzc3dvcmQ=")
        self.assertEqual(params, dict(hello = ["world"]))

    def test_redirect(self):
        _data, response = appier.get(
            "https://%s/redirect-to" % self.httpbin ,
            params = dict(url = "https://%s/" % self.httpbin),
            handle = True,
            redirect = True
        )

        code = response.getcode()
        self.assertNotEqual(code, 302)
        self.assertEqual(code, 200)

        quoted = appier.legacy.quote("https://%s/" % self.httpbin)
        _data, response = appier.get(
            "https://%s/redirect-to?url=%s" % (self.httpbin, quoted),
            handle = True,
            redirect = True
        )

        code = response.getcode()
        self.assertNotEqual(code, 302)
        self.assertEqual(code, 200)

        _data, response = appier.get(
            "https://%s/relative-redirect/2" % self.httpbin ,
            handle = True,
            redirect = True
        )

        code = response.getcode()
        self.assertNotEqual(code, 302)
        self.assertEqual(code, 200)

    def test_timeout(self):
        self.assertRaises(
            BaseException,
            lambda: appier.get(
                "https://%s/delay/3" % self.httpbin,
                handle = True,
                redirect = True,
                timeout = 1
            )
        )

        data, response = appier.get(
            "https://%s/delay/1" % self.httpbin,
            handle = True,
            redirect = True,
            timeout = 30
        )

        code = response.getcode()
        self.assertEqual(code, 200)
        self.assertNotEqual(len(data), 0)
        self.assertNotEqual(data, None)

    def test_get_f(self):
        file = appier.get_f("https://%s/image/png" % self.httpbin)

        self.assertEqual(file.file_name, "default")
        self.assertEqual(file.mime, "image/png")
        self.assertEqual(len(file.data) > 100, True)
        self.assertEqual(len(file.data_b64) > 100, True)

        file = appier.get_f(
            "https://%s/image/png" % self.httpbin,
            name = "dummy"
        )

        self.assertEqual(file.file_name, "dummy")
        self.assertEqual(file.mime, "image/png")
        self.assertEqual(len(file.data) > 100, True)
        self.assertEqual(len(file.data_b64) > 100, True)

    def test_generator(self):
        def text_g(message = [b"hello", b" ", b"world"]):
            yield sum(len(value) for value in message)
            for value in message:
                yield value

        data, response = appier.post(
            "https://%s/post" % self.httpbin,
            data = text_g(),
            handle = True,
            reuse = False
        )

        code = response.getcode()
        self.assertNotEqual(code, 302)
        self.assertEqual(code, 200)
        self.assertEqual(data["data"], "hello world")

    def test_file(self):
        data, response = appier.post(
            "https://%s/post" % self.httpbin,
            data = appier.legacy.BytesIO(b"hello world"),
            handle = True,
            reuse = False
        )

        code = response.getcode()
        self.assertNotEqual(code, 302)
        self.assertEqual(code, 200)
        self.assertEqual(data["data"], "hello world")

    def test_multithread(self):
        threads = []
        results = []

        for index in range(10):
            result = dict()
            results.append(result)

            def generate(index):
                def caller():
                    data, response = appier.get(
                        "https://%s/ip" % self.httpbin,
                        handle = True
                    )
                    result = results[index]
                    result["data"] = data
                    result["response"] = response
                return caller

            callable = generate(index)
            thread = threading.Thread(target = callable, name = "TestMultithread")
            thread.start()
            threads.append(thread)

        for thread, result in zip(threads, results):
            thread.join()

            response = result["response"]
            code = response.getcode()
            self.assertNotEqual(code, 302)
            self.assertEqual(code, 200)

    def test_error(self):
        self.assertRaises(
            appier.HTTPError,
            lambda: appier.get("https://%s/status/404" % self.httpbin)
        )

    def test_invalid(self):
        self.assertRaises(
            BaseException,
            lambda: appier.get("https://invalidlargedomain.org/")
        )
