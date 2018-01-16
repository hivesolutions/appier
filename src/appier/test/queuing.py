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

class QueuingTest(unittest.TestCase):

    def test_memory(self):
        queue = appier.MemoryQueue()
        queue.clear()
        queue.push("hello")
        result = queue.pop()

        self.assertEqual(queue.length(), 0)
        self.assertEqual(result, "hello")

        identifier = queue.push("hello")
        queue.pop()

        self.assertEqual(identifier, None)
        self.assertEqual(result, "hello")

        identifier = queue.push("hello", identify = True)

        self.assertNotEqual(identifier, None)

        priority, _identifier, result = queue.pop(full = True)

        self.assertEqual(priority, None)
        self.assertEqual(_identifier, identifier)
        self.assertEqual(result, "hello")

        identifier_1 = queue.push("hello 1", priority = 3, identify = True)
        identifier_2 = queue.push("hello 2", priority = 1, identify = True)
        identifier_3 = queue.push("hello 3", priority = 5, identify = True)

        self.assertEqual(queue.length(), 3)

        _priority, _identifier_3, _result_3 = queue.pop(full = True)
        _priority, _identifier_1, _result_1 = queue.pop(full = True)
        _priority, _identifier_2, _result_2 = queue.pop(full = True)

        self.assertEqual(_result_1, "hello 1")
        self.assertEqual(_result_2, "hello 2")
        self.assertEqual(_result_3, "hello 3")
        self.assertEqual(_identifier_1, identifier_1)
        self.assertEqual(_identifier_2, identifier_2)
        self.assertEqual(_identifier_3, identifier_3)

    def test_multiprocess(self):
        queue = appier.MultiprocessQueue()
        queue.clear()
        queue.push("hello")
        result = queue.pop()

        self.assertEqual(queue.length(), 0)
        self.assertEqual(result, "hello")

        identifier = queue.push("hello")
        queue.pop()

        self.assertEqual(identifier, None)
        self.assertEqual(result, "hello")

        identifier = queue.push("hello", identify = True)

        self.assertNotEqual(identifier, None)

        priority, _identifier, result = queue.pop(full = True)

        self.assertEqual(priority, None)
        self.assertEqual(_identifier, identifier)
        self.assertEqual(result, "hello")

        identifier_1 = queue.push("hello 1", priority = 3, identify = True)
        identifier_2 = queue.push("hello 2", priority = 1, identify = True)
        identifier_3 = queue.push("hello 3", priority = 5, identify = True)

        self.assertEqual(queue.length(), 3)

        _priority, _identifier_3, _result_3 = queue.pop(full = True)
        _priority, _identifier_1, _result_1 = queue.pop(full = True)
        _priority, _identifier_2, _result_2 = queue.pop(full = True)

        self.assertEqual(_result_1, "hello 1")
        self.assertEqual(_result_2, "hello 2")
        self.assertEqual(_result_3, "hello 3")
        self.assertEqual(_identifier_1, identifier_1)
        self.assertEqual(_identifier_2, identifier_2)
        self.assertEqual(_identifier_3, identifier_3)

    def test_amqp(self):
        try: queue = appier.AMQPQueue()
        except:
            if not hasattr(self, "skipTest"): return
            self.skipTest("No AMQP server present")

        queue.clear()
        queue.push("hello")
        result = queue.pop()

        self.assertEqual(result, "hello")

        identifier = queue.push("hello")
        queue.pop()

        self.assertEqual(identifier, None)
        self.assertEqual(result, "hello")

        identifier = queue.push("hello", identify = True)

        self.assertNotEqual(identifier, None)

        priority, _identifier, result = queue.pop(full = True)

        self.assertEqual(priority, None)
        self.assertEqual(_identifier, identifier)
        self.assertEqual(result, "hello")

        identifier_1 = queue.push("hello 1", priority = 3, identify = True)
        identifier_2 = queue.push("hello 2", priority = 1, identify = True)
        identifier_3 = queue.push("hello 3", priority = 5, identify = True)

        _priority, _identifier_3, _result_3 = queue.pop(full = True)
        _priority, _identifier_1, _result_1 = queue.pop(full = True)
        _priority, _identifier_2, _result_2 = queue.pop(full = True)

        self.assertEqual(_result_1, "hello 1")
        self.assertEqual(_result_2, "hello 2")
        self.assertEqual(_result_3, "hello 3")
        self.assertEqual(_identifier_1, identifier_1)
        self.assertEqual(_identifier_2, identifier_2)
        self.assertEqual(_identifier_3, identifier_3)
