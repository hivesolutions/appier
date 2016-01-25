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

class OrderedDict(list):

    def __getitem__(self, key):
        for _key, value in self:
            if not _key == key: continue
            return value
        raise KeyError("not found")

    def __setitem__(self, key, value):
        self.append([key, value])

    def __delitem__(self, key):
        value = self.__getitem__(key)
        self.remove([key, value])

    def __contains__(self, item):
        for key, _value in self:
            if not key == item: continue
            return True
        return False

    def items(self):
        return self

    def item(self, key):
        for item in self:
            if not item[0] == key: continue
            return item
        raise KeyError("not found")

    def get(self, key, default = None):
        if not key in self: return default
        return self[key]

    def set(self, key, value, append = False):
        if key in self and not append: self.item(key)[1] = value
        else: self[key] = value
