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

import appier

class CryptTest(unittest.TestCase):

    def test_rc4(self):
        rc4 = appier.RC4(b"hello key")
        result = rc4.encrypt(b"hello world")

        self.assertEqual(result, b"\xc54L\x00\xac\xb4\xf2\xcf\x8b5\xa7")

        rc4 = appier.RC4(b"hello key")
        data = rc4.decrypt(result)

        self.assertEqual(data, b"hello world")

        rc4 = appier.Cipher.new("rc4", b"hello key")
        result = rc4.encrypt(b"hello world")

        self.assertEqual(result, b"\xc54L\x00\xac\xb4\xf2\xcf\x8b5\xa7")

        rc4 = appier.Cipher.new("rc4", b"hello key")
        data = rc4.decrypt(result)

        self.assertEqual(data, b"hello world")

    def test_spritz(self):
        spritz = appier.Spritz(b"hello key")
        result = spritz.encrypt(b"hello world")

        self.assertEqual(result, b"\xbch\x0c\xb4X21\\\x07\xde\xe1")

        spritz = appier.Spritz(b"hello key")
        data = spritz.decrypt(result)

        self.assertEqual(data, b"hello world")

        spritz = appier.Cipher.new("spritz", b"hello key")
        result = spritz.encrypt(b"hello world")

        self.assertEqual(result, b"\xbch\x0c\xb4X21\\\x07\xde\xe1")

        spritz = appier.Cipher.new("spritz", b"hello key")
        data = spritz.decrypt(result)

        self.assertEqual(data, b"hello world")
