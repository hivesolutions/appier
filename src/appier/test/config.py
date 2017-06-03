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

class ConfigTest(unittest.TestCase):

    def test_basic(self):
        appier.conf_s("NAME", "name")
        result = appier.conf("NAME")

        self.assertEqual(result, "name")

        result = appier.conf("NAME", cast = str)

        self.assertEqual(result, "name")
        self.assertEqual(type(result), str)

        result = appier.conf("NAME", cast = "str")

        self.assertEqual(result, "name")
        self.assertEqual(type(result), str)

        appier.conf_s("AGE", "10")
        result = appier.conf("AGE", cast = int)

        self.assertEqual(result, 10)
        self.assertEqual(type(result), int)

        result = appier.conf("AGE", cast = "int")

        self.assertEqual(result, 10)
        self.assertEqual(type(result), int)

        result = appier.conf("AGE", cast = str)

        self.assertEqual(result, "10")
        self.assertEqual(type(result), str)

        result = appier.conf("HEIGHT")

        self.assertEqual(result, None)
