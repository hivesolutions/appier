#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2016 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import array
import unittest

import appier

class LegacyTest(unittest.TestCase):

    def test_argspec(self):
        hello_world = lambda message, extra = "": "hello world %s" % message

        spec = appier.legacy.getargspec(hello_world)
        self.assertEqual(spec[0], ["message", "extra"])
        self.assertEqual(spec.args, ["message", "extra"])
        self.assertEqual(spec.varargs, None)
        self.assertEqual(spec.keywords, None)
        self.assertEqual(spec.defaults, ("",))

    def test_tobytes(self):
        value = array.array("B")
        value.append(ord("h"))
        value.append(ord("e"))
        value.append(ord("l"))
        value.append(ord("l"))
        value.append(ord("o"))
        result = appier.legacy.tobytes(value)
        self.assertEqual(result, b"hello")

    def test_tostring(self):
        value = array.array("B")
        value.append(ord("h"))
        value.append(ord("e"))
        value.append(ord("l"))
        value.append(ord("l"))
        value.append(ord("o"))
        result = appier.legacy.tostring(value)
        self.assertEqual(result, b"hello")
