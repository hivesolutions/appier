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

import os
import json
import zipfile
import tempfile

from . import legacy

try: import bson
except: bson = None

IGNORE = 1
""" Ignore strategy for conflict solving in the import operation
basically this strategy skips importing a document that has the same
key value as one that already exists in the collection """

OVERWRITE = 2
""" Strategy for conflict solving that overwrites (completely) a
previously existing document in the data source if it has the same
key value as the one being imported, this should be used carefully
as it may create data loss """

DUPLICATE = 3
""" Conflict solving strategy that basically duplicates the entries
in the data source even if they have the same key value, this may
create a somehow inconsistent state and so must be used carefully """

JOIN = 4
""" Join strategy for conflict solving in document collision, that
basically adds new fields or updates existing fields in a previously
existing document, this strategy does not remove extra fields existing
in the previous document """

class ExportManager(object):

    db = None
    single = None
    multiple = None

    def __init__(self, db, single = (), multiple = ()):
        self.db = db
        self.single = single
        self.multiple = multiple

    def import_data(self, file_path, policy = IGNORE):
        temporary_path = tempfile.mkdtemp()
        base_path = temporary_path
        single_path = os.path.join(base_path, "settings")

        self._deploy_zip(file_path, temporary_path)

        for name, key in self.single:
            collection = self.db[name]
            source_path = os.path.join(single_path, "%s.json" % name)
            file = open(source_path, "rb")
            try: data = file.read()
            finally: file.close()
            self._import_single(
                collection,
                data,
                key = key,
                policy = policy
            )

        for name, key in self.multiple:
            source_directory = os.path.join(base_path, name)
            if not os.path.exists(source_directory): continue

            collection = self.db[name]
            items = os.listdir(source_directory)
            data = []

            for item in items:
                value, _extension = os.path.splitext(item)
                source_path = os.path.join(source_directory, item)
                file = open(source_path, "rb")
                try: _data = file.read()
                finally: file.close()

                data.append((value, _data))

            self._import_multiple(
                collection,
                data,
                key = key,
                policy = policy
            )

    def export_data(self, file_path):
        temporary_path = tempfile.mkdtemp()
        base_path = temporary_path
        single_path = os.path.join(base_path, "settings")
        if not os.path.exists(single_path): os.makedirs(single_path)

        for name, key in self.single:
            collection = self.db[name]
            data = self._export_single(collection, key)
            target_path = os.path.join(single_path, "%s.json" % name)
            file = open(target_path, "wb")
            try: file.write(data)
            finally: file.close()

        for name, key in self.multiple:
            collection = self.db[name]
            data = self._export_multiple(collection, key)

            target_directory = os.path.join(base_path, name)
            if not os.path.exists(target_directory): os.makedirs(target_directory)

            for value, _data in data:
                target_path = os.path.join(target_directory, "%s.json" % value)
                file = open(target_path, "wb")
                try: file.write(_data)
                finally: file.close()

        self._create_zip(file_path, temporary_path)

    def _import_single(self, collection, data, key, policy = IGNORE):
        # loads the provided json data as a sequence of key value items
        # and then starts loading all the values into the data source
        data = data.decode("utf-8")
        data_s = json.loads(data)
        for _key, entity in data_s.items():
            # verifies if the "native" object id value for the mongo
            # database exists and if that's the case tries to convert
            # the value from the "underlying" string value to object
            # identifier, defaulting to a string value if it fails
            if "_id" in entity:
                try: entity["_id"] = bson.ObjectId(entity["_id"])
                except: entity["_id"] = entity["_id"]

            # retrieves the key value for the current entity to
            # be inserted and then tries to retrieve an existing
            # entity for the same key, to avoid duplicated entry
            value = entity.get(key, None)
            if value: entity_e = collection.find_one({key : value})
            else: entity_e = None

            # in case there's no existing entity for the same key
            # (normal situation) only need to insert the new entity
            # otherwise must apply the selected conflict policy for
            # the resolution of the data source conflict
            if not entity_e: collection.insert(entity)
            elif policy == IGNORE: continue
            elif policy == OVERWRITE:
                collection.remove({key : value})
                collection.insert(entity)
            elif policy == DUPLICATE:
                collection.insert(entity)
            elif policy == JOIN:
                if "_id" in entity: del entity["_id"]
                collection.update({
                    "_id" : entity_e["_id"]
                }, {
                    "$set" : entity
                })

    def _import_multiple(self, collection, data, key, policy = IGNORE):
        # iterates over the complete set of data element to load
        # the json contents and then load the corresponding entity
        # value into the data source
        for _value, _data in data:
            # loads the current data in iteration from the file
            # as the entity to be loaded into the data source
            _data = _data.decode("utf-8")
            entity = json.loads(_data)

            # verifies if the "native" object id value for the mongo
            # database exists and if that's the case tries to convert
            # the value from the "underlying" string value to object
            # identifier, defaulting to a string value if it fails
            if "_id" in entity:
                try: entity["_id"] = bson.ObjectId(entity["_id"])
                except: entity["_id"] = entity["_id"]

            # retrieves the key value for the current entity to
            # be inserted and then tries to retrieve an existing
            # entity for the same key, to avoid duplicated entry
            value = entity.get(key, None)
            if value: entity_e = collection.find_one({key : value})
            else: entity_e = None

            # in case there's no existing entity for the same key
            # (normal situation) only need to insert the new entity
            # otherwise must apply the selected conflict policy for
            # the resolution of the data source conflict
            if not entity_e: collection.insert(entity)
            elif policy == IGNORE: continue
            elif policy == OVERWRITE:
                collection.remove({key : value})
                collection.insert(entity)
            elif policy == DUPLICATE:
                collection.insert(entity)
            elif policy == JOIN:
                if "_id" in entity: del entity["_id"]
                collection.update({
                    "_id" : entity_e["_id"]
                }, {
                    "$set" : entity
                })

    def _export_single(self, collection, key = "_id"):
        entities = collection.find()
        _entities = {}
        for entity in entities:
            value = entity[key]
            value_s = self._to_key(value)
            _entities[value_s] = entity
        data = json.dumps(_entities, cls = MongoEncoder)
        data = legacy.bytes(data)
        return data

    def _export_multiple(self, collection, key = "_id"):
        entities = collection.find()
        for entity in entities:
            value = entity[key]
            value_s = self._to_key(value)
            value_s = self._escape_key(value_s)
            _data = json.dumps(entity, cls = MongoEncoder)
            _data = legacy.bytes(_data)
            yield (value_s, _data)

    def _to_key(self, key):
        key_t = type(key)
        if key_t in legacy.STRINGS: return key
        key = legacy.UNICODE(key)
        return key

    def _escape_key(self, key):
        return key.replace(":", "_")

    def _deploy_zip(self, zip_path, path):
        zip_file = zipfile.ZipFile(
            zip_path,
            mode = "r",
            compression = zipfile.ZIP_DEFLATED
        )

        try: zip_file.extractall(path)
        finally: zip_file.close()

    def _create_zip(self, zip_path, path):
        zip_file = zipfile.ZipFile(
            zip_path,
            mode = "w",
            compression = zipfile.ZIP_DEFLATED
        )

        try:
            list = os.listdir(path)
            for name in list:
                _path = os.path.join(path, name)
                is_file = os.path.isfile(_path)

                if is_file: zip_file.write(_path)
                else: self.__add_to_zip(zip_file, _path, base = path)
        finally:
            zip_file.close()

    def __add_to_zip(self, zip_file, path, base = ""):
        list = os.listdir(path)
        for name in list:
            _path = os.path.join(path, name)
            _path_out = _path[len(base):]
            _path_out = _path_out.replace("\\", "/")
            _path_out = _path_out.strip("/")

            if os.path.isfile(_path):
                zip_file.write(_path, _path_out)
            elif os.path.isdir(_path):
                self.__add_to_zip(zip_file, _path, base = base)

class MongoEncoder(json.JSONEncoder):

    def default(self, obj, **kwargs):
        if isinstance(obj, bson.objectid.ObjectId): return str(obj)
        else: return json.JSONEncoder.default(obj, **kwargs)
