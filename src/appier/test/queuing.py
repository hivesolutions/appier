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

class QueuingTest(unittest.TestCase):

    def test_memory(self):
        queue = appier.MemoryQueue()
        queue.push("hello")
        result = queue.pop()

        self.assertEqual(result, "hello")

        identifier = queue.push("hello")
        queue.pop()

        self.assertEqual(identifier, None)

        identifier = queue.push("hello", identify = True)

        self.assertNotEqual(identifier, None)

        priority, _identifier, result = queue.pop(full = True)

        self.assertEqual(priority, None)
        self.assertEqual(_identifier, identifier)
        self.assertEqual(result, "hello")

        identifier_1 = queue.push("hello", priority = 10, identify = True)
        identifier_2 = queue.push("hello", priority = 1, identify = True)
        identifier_3 = queue.push("hello", priority = 100, identify = True)

        self.assertEqual(queue.length(), 3)

        _priority, _identifier_3, _result = queue.pop(full = True)
        _priority, _identifier_1, _result = queue.pop(full = True)
        _priority, _identifier_2, _result = queue.pop(full = True)

        self.assertEqual(_identifier_3, identifier_3)
        self.assertEqual(_identifier_1, identifier_1)
        self.assertEqual(_identifier_2, identifier_2)

    def test_multiprocess(self):
        queue = appier.MultiprocessQueue()
        queue.push("hello")
        result = queue.pop()

        self.assertEqual(result, "hello")

        queue = appier.MultiprocessQueue()
        identifier = queue.push("hello")
        queue.pop()

        self.assertEqual(identifier, None)

        identifier = queue.push("hello", identify = True)

        self.assertNotEqual(identifier, None)

        priority, _identifier, result = queue.pop(full = True)

        self.assertEqual(priority, None)
        self.assertEqual(_identifier, identifier)
        self.assertEqual(result, "hello")

        identifier_1 = queue.push("hello", priority = 10, identify = True)
        identifier_2 = queue.push("hello", priority = 1, identify = True)
        identifier_3 = queue.push("hello", priority = 100, identify = True)

        self.assertEqual(queue.length(), 3)

        _priority, _identifier_3, _result = queue.pop(full = True)
        _priority, _identifier_1, _result = queue.pop(full = True)
        _priority, _identifier_2, _result = queue.pop(full = True)

        self.assertEqual(_identifier_3, identifier_3)
        self.assertEqual(_identifier_1, identifier_1)
        self.assertEqual(_identifier_2, identifier_2)
