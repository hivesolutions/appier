#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2020 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time
import unittest

import appier

class CacheTest(unittest.TestCase):

    def setUp(self):
        """
        Sets the application that application.

        Args:
            self: (todo): write your description
        """
        self.app = appier.App()

    def tearDown(self):
        """
        Tear down the application.

        Args:
            self: (todo): write your description
        """
        self.app.unload()

    def test_memory(self):
        """
        Test if the cache.

        Args:
            self: (todo): write your description
        """
        cache = appier.MemoryCache.new()

        cache["first"] = 1
        cache["second"] = 2

        self.assertEqual(cache["first"], 1)
        self.assertEqual(cache["second"], 2)

        cache.set_item("first", 1, timeout = -1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", 1, timeout = 3600)

        self.assertEqual(cache["first"], 1)

        cache.set_item("first", 1, expires = time.time() - 1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", 1, expires = time.time() + 3600)

        self.assertEqual(cache["first"], 1)

        cache["third"] = 3

        self.assertEqual("third" in cache, True)
        self.assertNotEqual(cache.length(), 0)

        cache.clear()

        self.assertEqual("third" in cache, False)
        self.assertEqual(cache.length(), 0)

    def test_file(self):
        """
        Create a new cache file.

        Args:
            self: (todo): write your description
        """
        cache = appier.FileCache.new()

        cache["first"] = b"1"
        cache["second"] = b"2"

        self.assertEqual(cache["first"], b"1")
        self.assertEqual(cache["second"], b"2")

        cache.set_item("first", b"1", timeout = -1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", b"1", timeout = 3600)

        self.assertEqual(cache["first"], b"1")

        cache.set_item("first", b"1", expires = time.time() - 1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", b"1", expires = time.time() + 3600)

        self.assertEqual(cache["first"], b"1")

        cache["third"] = b"3"

        self.assertEqual("third" in cache, True)
        self.assertNotEqual(cache.length(), 0)

        cache.clear()

        self.assertEqual("third" in cache, False)
        self.assertEqual(cache.length(), 0)

    def test_redis(self):
        """
        Create a redis test.

        Args:
            self: (todo): write your description
        """
        try:
            cache = appier.RedisCache.new()
        except Exception:
            if not hasattr(self, "skipTest"): return
            self.skipTest("No Redis server present")

        cache["first"] = b"1"
        cache["second"] = b"2"

        self.assertEqual(cache["first"], b"1")
        self.assertEqual(cache["second"], b"2")

        cache.set_item("first", b"1", timeout = -1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", b"1", timeout = 3600)

        self.assertEqual(cache["first"], b"1")

        cache.set_item("first", b"1", expires = time.time() - 1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", b"1", expires = time.time() + 3600)

        self.assertEqual(cache["first"], b"1")

        cache["third"] = b"3"

        self.assertEqual("third" in cache, True)
        self.assertNotEqual(cache.length(), 0)

        cache.clear()

        self.assertEqual("third" in cache, False)
        self.assertEqual(cache.length(), 0)

    def test_redis_hash(self):
        """
        Generate the hash of a hash of the database.

        Args:
            self: (todo): write your description
        """
        try:
            cache = appier.RedisCache.new(hash = True)
        except Exception:
            if not hasattr(self, "skipTest"): return
            self.skipTest("No Redis server present")

        cache["first"] = b"1"
        cache["second"] = b"2"

        self.assertEqual(cache["first"], b"1")
        self.assertEqual(cache["second"], b"2")

        cache.set_item("first", b"1", timeout = -1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", b"1", timeout = 3600)

        self.assertEqual(cache["first"], b"1")

        cache.set_item("first", b"1", expires = time.time() - 1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", b"1", expires = time.time() + 3600)

        self.assertEqual(cache["first"], b"1")

        cache["third"] = b"3"

        self.assertEqual("third" in cache, True)
        self.assertNotEqual(cache.length(), 0)

        cache.clear()

        self.assertEqual("third" in cache, False)
        self.assertEqual(cache.length(), 0)

    def test_serialized(self):
        """
        Create a serialization of the given test.

        Args:
            self: (todo): write your description
        """
        cache = appier.FileCache.new()
        cache = appier.SerializedCache(cache)

        cache["first"] = 1
        cache["second"] = 2

        self.assertEqual(cache["first"], 1)
        self.assertEqual(cache["second"], 2)

        cache.set_item("first", 1, timeout = -1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", 1, timeout = 3600)

        self.assertEqual(cache["first"], 1)

        cache.set_item("first", 1, expires = time.time() - 1)

        self.assertEqual("first" in cache, False)
        self.assertRaises(KeyError, lambda: cache["first"])

        cache.set_item("first", 1, expires = time.time() + 3600)

        self.assertEqual(cache["first"], 1)

        cache["third"] = 3

        self.assertEqual("third" in cache, True)
        self.assertNotEqual(cache.length(), 0)

        cache.clear()

        self.assertEqual("third" in cache, False)
        self.assertEqual(cache.length(), 0)
