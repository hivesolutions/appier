#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2015 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import unittest

import appier

class UtilTest(unittest.TestCase):

    def test_email_parts(self):
        name, email = appier.email_parts("João Magalhães <joamag@hive.pt>")
        self.assertEqual(type(name), str)
        self.assertEqual(type(email), str)
        self.assertEqual(name, "João Magalhães")
        self.assertEqual(email, "joamag@hive.pt")

        name, email = appier.email_parts(appier.legacy.u("João Magalhães <joamag@hive.pt>"))
        self.assertEqual(type(name), appier.legacy.UNICODE)
        self.assertEqual(type(email), appier.legacy.UNICODE)
        self.assertEqual(name, appier.legacy.u("João Magalhães"))
        self.assertEqual(email, appier.legacy.u("joamag@hive.pt"))

        name, email = appier.email_parts(appier.legacy.u("你好世界 <hello@hive.pt>"))
        self.assertEqual(type(name), appier.legacy.UNICODE)
        self.assertEqual(type(email), appier.legacy.UNICODE)
        self.assertEqual(name, appier.legacy.u("你好世界"))
        self.assertEqual(email, appier.legacy.u("hello@hive.pt"))

    def test_email_mime(self):
        result = appier.email_mime("João Magalhães <joamag@hive.pt>")
        self.assertEqual(type(result), str)
        self.assertEqual(result, "=?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>")

        result = appier.email_mime(appier.legacy.u("João Magalhães <joamag@hive.pt>"))
        self.assertEqual(type(result), appier.legacy.UNICODE)
        self.assertEqual(result, appier.legacy.u("=?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>"))
