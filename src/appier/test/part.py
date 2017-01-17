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

class MockPart(appier.Part):

    def load(self):
        appier.Part.load(self)
        self.owner.mock_loaded = True

    def unload(self):
        appier.Part.unload(self)
        self.owner.mock_loaded = False

class PartTest(unittest.TestCase):

    def setUp(self):
        self.app = appier.App(parts = (MockPart,))

    def tearDown(self):
        self.app.unload()

    def test_basic(self):
        self.assertEqual(self.app.mock_loaded, True)

        result = self.app.mock_part
        self.assertEqual(isinstance(result, appier.Part), True)
        self.assertEqual(isinstance(result, MockPart), True)
        self.assertEqual(result.name(), "mock")
        self.assertEqual(result.class_name(), "appier.test.part.MockPart")
        self.assertEqual(result.is_loaded(), True)

        result = self.app.get_part("mock")
        self.assertEqual(isinstance(result, appier.Part), True)
        self.assertEqual(isinstance(result, MockPart), True)
        self.assertEqual(result.name(), "mock")
        self.assertEqual(result.class_name(), "appier.test.part.MockPart")
        self.assertEqual(result.is_loaded(), True)

        result = self.app.get_part("appier.test.part.MockPart")
        self.assertEqual(isinstance(result, appier.Part), True)
        self.assertEqual(isinstance(result, MockPart), True)
        self.assertEqual(result.name(), "mock")
        self.assertEqual(result.class_name(), "appier.test.part.MockPart")
        self.assertEqual(result.is_loaded(), True)

        self.app.unload()

        self.assertEqual(self.app.mock_loaded, False)

        result = self.app.get_part("mock")
        self.assertEqual(isinstance(result, appier.Part), True)
        self.assertEqual(isinstance(result, MockPart), True)
        self.assertEqual(result.name(), "mock")
        self.assertEqual(result.class_name(), "appier.test.part.MockPart")
        self.assertEqual(result.is_loaded(), False)
