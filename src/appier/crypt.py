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

import array

from . import legacy
from . import exceptions

class Cipher(object):

    def __init__(self, key):
        self.key = key

    @classmethod
    def new(cls, cipher, key):
        cipher = cls._cipher(cipher)
        return cipher(key)

    @classmethod
    def _cipher(cls, name):
        for subclass in cls.__subclasses__():
            if not subclass.__name__.lower() == name: continue
            return subclass
        return None

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

    :see: http://en.wikipedia.org/wiki/RC4
    """

    def __init__(self, key):
        Cipher.__init__(self, key)
        self._start()

    def encrypt(self, data):
        out = array.array("B", [0] * len(data))
        self._encrypt(data, out)
        return legacy.tobytes(out)

    def decrypt(self, data):
        return self.encrypt(data)

    def _encrypt(self, data, out):
        index = 0

        box = self.box
        i = self.i
        j = self.j

        for char in data:
            i = (i + 1) % 256
            j = (j + box[i]) % 256

            box[i], box[j] = box[j], self.box[i]
            k = box[(box[i] + box[j]) % 256]

            ciph = legacy.ord(char) ^ k
            out[index] = ciph
            index += 1

        self.i = i
        self.j = j

    def _start(self):
        self.box = legacy.range(256)
        self.i = 0
        self.j = 0

        x = 0
        for i in range(256):
            x = (x + self.box[i] + legacy.ord(self.key[i % len(self.key)])) % 256
            self.box[i], self.box[x] = self.box[x], self.box[i]

class Spritz(Cipher):
    """
    Class that implements the basis for the
    encryption using the Spritz stream cipher
    a variation of the original RC4 cipher.

    The implementation of the algorithm follows
    the typical implementation details.

    :see: http://en.wikipedia.org/wiki/RC4#Spritz
    """

    def __init__(self, key):
        Cipher.__init__(self, key)
        self._start()
        self.absorb(self.key)

    def encrypt(self, data):
        data = bytearray(data)
        sequezing = self.squeeze(len(data))
        out = bytearray(self._add(b1, b2) for b1, b2 in zip(data, sequezing))
        return bytes(out)

    def decrypt(self, data):
        data = bytearray(data)
        sequezing = self.squeeze(len(data))
        out = bytearray(self._add(b1, -b2) for b1, b2 in zip(data, sequezing))
        return bytes(out)

    def absorb(self, data):
        data = bytearray(data)
        for byte in data: self._absorb_byte(byte)

    def shuffle(self):
        self.whip(512)
        self.crush()
        self.whip(512)
        self.crush()
        self.whip(512)
        self.a = 0

    def whip(self, r):
        for _ in range(r): self._update()
        self.w = self._add(self.w, 2)

    def crush(self):
        for v in range(128):
            if self.S[v] <= self.S[255 - v]: continue
            self._swap(v, 255 - v)

    def squeeze(self, r):
        if self.a > 0: self.shuffle()
        return bytearray([self.drip() for _ in range(r)])

    def drip(self):
        if self.a > 0: self.shuffle()
        self._update()
        return self._output()

    def _update(self):
        self.i = self._add(self.i, self.w)
        self.j = self._add(self.k, self.S[self._add(self.j, self.S[self.i])])
        self.k = self._add(self.i, self.k, self.S[self.j])
        self._swap(self.i, self.j)

    def _output(self):
        self.z = self.S[self._add(self.j, self.S[self._add(self.i, self.S[self._add(self.z, self.k)])])]
        return self.z

    def _add(self, *args):
        return sum(args) % 256

    def _swap(self, i1, i2):
        self.S[i1], self.S[i2] = self.S[i2], self.S[i1]

    def _start(self):
        self.i = 0
        self.j = 0
        self.k = 0
        self.z = 0
        self.a = 0
        self.w = 1
        self.S = bytearray(range(256))

    def _absorb_byte(self, byte):
        self._absorb_nibble(byte & 0xf)
        self._absorb_nibble(byte >> 4)

    def _absorb_nibble(self, nibble):
        if self.a == 128: self.shuffle()
        self._swap(self.a, 128 + nibble)
        self.a = self._add(self.a, 1)
