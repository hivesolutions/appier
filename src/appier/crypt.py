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

from . import legacy
from . import exceptions

class Cipher(object):

    def __init__(self, key):
        self.key = key

    def encrypt(self, data):
        raise exceptions.NotImplementedError()

    def decrypt(self, data):
        raise exceptions.NotImplementedError()

class RC4(Cipher):
    """
    Class that implements the basis for the
    encryption using the RC4 stream cipher.
    The implementation of the algorithm follows
    the typical implementation details.

    @see: http://en.wikipedia.org/wiki/RC4
    """

    def __init__(self, key):
        Cipher.__init__(self, key)

        self.box = legacy.range(256)
        self.x = 0
        self.y = 0
        self._start()

    def encrypt(self, data):
        out = array.array("B", [0] * len(data))
        index = 0

        box = self.box
        x = self.x
        y = self.y

        for char in data:
            x = (x + 1) % 256
            y = (y + box[x]) % 256

            _x = box[x]
            box[x] = box[y]
            box[y] = _x

            k = box[(box[x] + box[y]) % 256]
            ciph = legacy.ord(char) ^ k
            out[index] = ciph
            index += 1

        self.x = x
        self.y = y

        return out.tostring()

    def decrypt(self, data):
        return self.encrypt(data)

    def _start(self):
        x = 0
        for i in range(256):
            x = (x + self.box[i] + legacy.ord(self.key[i % len(self.key)])) % 256
            self.box[i], self.box[x] = self.box[x], self.box[i]
