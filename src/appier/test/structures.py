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

class OrderedDictTest(unittest.TestCase):

    def test_basic(self):
        struct = appier.OrderedDict()

        struct["first"] = 1
        struct["second"] = 2
        struct["third"] = 3

        self.assertEqual(struct["first"], 1)
        self.assertEqual(struct["second"], 2)
        self.assertEqual(struct["third"], 3)

    def test_order(self):
        struct = appier.OrderedDict()

        struct["first"] = 1
        struct["second"] = 2
        struct["third"] = 3

        iterator = iter(struct)

        self.assertEqual(next(iterator), ["first", 1])
        self.assertEqual(next(iterator), ["second", 2])
        self.assertEqual(next(iterator), ["third", 3])

    def test_build(self):
        base = dict(first = 1, second = 2, third = 3)

        struct = appier.OrderedDict(base)

        self.assertEqual(struct._dict, base)

        iterator = iter(struct)

        self.assertEqual(next(iterator), ["first", 1])
        self.assertEqual(next(iterator), ["second", 2])
        self.assertEqual(next(iterator), ["third", 3])

        struct.sort()

        self.assertEqual(struct._dict, base)

        iterator = iter(struct)

        self.assertEqual(next(iterator), ["first", 1])
        self.assertEqual(next(iterator), ["second", 2])
        self.assertEqual(next(iterator), ["third", 3])

        struct["fourth"] = 4

        self.assertEqual(len(base), 4)
        self.assertEqual(len(struct), 4)
        self.assertEqual(base["fourth"], 4)

        iterator = iter(struct)

        self.assertEqual(next(iterator), ["first", 1])
        self.assertEqual(next(iterator), ["second", 2])
        self.assertEqual(next(iterator), ["third", 3])
        self.assertEqual(next(iterator), ["fourth", 4])

        del base["first"]

        self.assertEqual(len(base), 3)
        self.assertEqual(len(struct), 3)

        iterator = iter(struct)

        self.assertEqual(next(iterator), ["second", 2])
        self.assertEqual(next(iterator), ["third", 3])
        self.assertEqual(next(iterator), ["fourth", 4])

        del base["third"]
        del base["fourth"]

        self.assertEqual(len(base), 1)
        self.assertEqual(len(struct), 1)

        iterator = iter(struct)

        self.assertEqual(next(iterator), ["second", 2])

        base["fifth"] = 5

        self.assertEqual(len(base), 2)
        self.assertEqual(len(struct), 2)

        iterator = iter(struct)

        self.assertEqual(next(iterator), ["second", 2])
        self.assertEqual(next(iterator), ["fifth", 5])

    def test_stack(self):
        struct = appier.OrderedDict()

        struct.push(["first", 1])
        struct.push(["second", 2])
        struct.push(["third", 3])

        iterator = iter(struct)

        self.assertEqual(next(iterator), ["first", 1])
        self.assertEqual(next(iterator), ["second", 2])
        self.assertEqual(next(iterator), ["third", 3])

        value = struct.pop()

        self.assertEqual(value, ["third", 3])
        self.assertEqual(len(value), 2)

    def test_delete(self):
        struct = appier.OrderedDict()

        struct.push(["first", 1])
        struct.push(["second", 2])

        self.assertEqual("first" in struct, True)
        self.assertEqual("second" in struct, True)

        del struct["first"]

        self.assertEqual("first" in struct, False)
        self.assertEqual("second" in struct, True)

    def test_repr(self):
        struct = appier.OrderedDict()

        struct.push(["first", 1])
        struct.push(["second", 2])
        struct.push(["third", 3])

        self.assertEqual(repr(struct), "[['first', 1], ['second', 2], ['third', 3]]")
        self.assertEqual(str(struct), "[['first', 1], ['second', 2], ['third', 3]]")

class LazyDictTest(unittest.TestCase):

    def test_lazy(self):
        struct = appier.LazyDict()

        struct["first"] = appier.LazyValue(lambda: 2)

        self.assertEqual(isinstance(struct.__getitem__("first", True), appier.LazyValue), True)
        self.assertEqual(struct["first"], 2)

    def test_resolve(self):
        struct = appier.LazyDict(
            first = appier.LazyValue(lambda: 1),
            second = appier.LazyValue(lambda: 2)
        )

        resolved = struct.resolve(force = True)

        self.assertNotEqual(type(struct) == dict, True)
        self.assertNotEqual(struct, dict(first = 1, second = 2))
        self.assertEqual(type(resolved) == dict, True)
        self.assertEqual(resolved, dict(first = 1, second = 2))

        resolved = struct.to_dict()

        self.assertNotEqual(type(struct) == dict, True)
        self.assertNotEqual(struct, dict(first = 1, second = 2))
        self.assertEqual(type(resolved) == dict, True)
        self.assertEqual(resolved, dict(first = 1, second = 2))

    def test_naming(self):
        struct = appier.lazy_dict()

        struct["first"] = appier.lazy(lambda: 1)

        self.assertEqual(isinstance(struct.__getitem__("first", True), appier.lazy), True)
        self.assertEqual(struct["first"], 1)

    def test_concrete(self):
        struct = appier.lazy_dict()

        struct["first"] = appier.lazy(lambda: 1)
        struct["second"] = 2

        self.assertEqual(isinstance(struct.__getitem__("first", True), appier.lazy), True)
        self.assertEqual(struct["first"], 1)
        self.assertEqual(isinstance(struct.__getitem__("second", True), int), True)
        self.assertEqual(struct["second"], 2)
