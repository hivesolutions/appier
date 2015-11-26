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

from . import mongo

class DataAdapter(object):
    pass

class MongoAdapter(DataAdapter):

    def collection(self, name, *args, **kwargs):
        db = self.get_db()
        collection = db[name]
        return MongoCollection(collection)

    def get_db(self):
        return mongo.get_db()

    def drop_db(self, *args, **kwargs):
        return mongo.drop_db()

class Collection(object):
    pass

class MongoCollection(Collection):

    def __init__(self, base):
        self._base = base

    def find(self, *args, **kwargs):
        return self._base.find(*args, **kwargs)

    def find_one(self, *args, **kwargs):
        return self._base.find_one(*args, **kwargs)

    def find_and_modify(self, *args, **kwargs):
        return mongo._store_find_and_modify(self._base, *args, **kwargs)

    def insert(self, *args, **kwargs):
        return mongo._store_insert(self._base, *args, **kwargs)

    def update(self, *args, **kwargs):
        return mongo._store_update(self._base, *args, **kwargs)

    def remove(self, *args, **kwargs):
        return self._base.remove(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self._base.count(*args, **kwargs)

    def ensure_index(self, *args, **kwargs):
        return mongo._store_ensure_index(self._base, *args, **kwargs)
