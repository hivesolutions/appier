#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2012 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Appier Framework. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import os
import types
import base64
import tempfile

import base
import util

class Type(object):

    def json_v(self):
        return str(self)

class File(Type):

    def __init__(self, file):
        file_t = type(file)
        if file_t == types.DictType: self.build_b64(file)
        elif file_t == types.TupleType: self.build_t(file)
        elif isinstance(file, File): self.build_i(file)
        else: self.build_f(file)

    def __repr__(self):
        return "<File: %s>" % self.file_name

    def __str__(self):
        return self.file_name

    def __len__(self):
        return self.size

    def build_b64(self, file_m):
        name = file_m["name"]
        data_b64 = file_m["data"]
        mime = file_m.get("mime", None)

        self.data = base64.b64decode(data_b64)
        self.data_b64 = data_b64
        self.file = None
        self.size = len(self.data)
        self.file_name = name
        self.mime = mime

    def build_t(self, file_t):
        name, content_type, data = file_t

        self.data = data
        self.data_b64 = base64.b64encode(data)
        self.file = None
        self.size = len(self.data)
        self.file_name = name
        self.mime = content_type

    def build_i(self, file):
        self.file = file.file
        self.size = file.size
        self.file_name = file.file_name
        self.mime = file.mime
        self.data = file.data
        self.data_b64 = file.data_b64

    def build_f(self, file):
        self.file = file
        self.size = file.content_length
        self.file_name = file.filename
        self.mime = file.content_type
        self.data = None
        self.data_b64 = None

        self._flush()

    def read(self):
        return self.data

    def json_v(self):
        return {
            "name" : self.file_name,
            "data" : self.data_b64,
            "mime" : self.mime
        }

    def is_empty(self):
        return self.size <= 0

    def _flush(self):
        if not self.file_name: return
        if self.data: return

        path = tempfile.mkdtemp()
        path_f = os.path.join(path, self.file_name)
        self.file.save(path_f)

        file = open(path_f, "rb")
        try: data = file.read()
        finally: file.close()

        self.data = data
        self.data_b64 = base64.b64encode(data)
        self.size = len(data)

def reference(target, name = None, eager = False):
    name = name or "id"
    target_t = type(target)
    is_reference = target_t in types.StringTypes

    class Reference(Type):

        _name = name
        """ The name of the key (join) attribute for the
        reference that is going to be created, this name
        may latter be used to cast the value """

        def __init__(self, id):
            self.__start__()
            if isinstance(id, Reference): self.build_i(id)
            else: self.build(id)

        def __len__(self):
            is_empty = self.id == "" or self.id == None
            return 0 if is_empty else 1

        def __getattr__(self, name):
            self.resolve()
            exists = hasattr(self._object, name)
            if exists: return getattr(self._object, name)
            raise AttributeError("'%s' not found" % name)

        def __setattr__(self, name, value):
            # verifies if the reference object exists in the current
            # reference instance, that's the case if the object name is
            # defined in the dictionary and the referenced object contains
            # an attribute with the name referred, for those situations
            # defers the setting of the attribute to the reference object
            exists = "_object" in self.__dict__ and hasattr(self._object, name)
            if exists: return setattr(self._object, name, value)

            # otherwise this is a normal attribute setting and the current
            # object's dictionary must be changed so that the new value is set
            self.__dict__[name] = value

        def __start__(self):
            if is_reference: self._target = getattr(base.APP.models, target)
            else: self._target = target
            meta = getattr(self._target, name)
            self._type = meta.get("type", str)

        @classmethod
        def _default(cls):
            return cls(None)

        def build(self, id):
            self.id = id
            self._object = None

        def build_i(self, reference):
            self.id = reference.id
            self._object = reference._object

        def ref_v(self):
            return self.value()

        def json_v(self):
            if eager: self.resolve(); return self._object
            else: return self.value()

        def value(self):
            is_empty = self.id == "" or self.id == None
            if is_empty: return None
            return self._type(self.id)

        def resolve(self):
            # verifies if the underlying object reference exists
            # in the current names dictionary and if it exists
            # verifies if it's valid (value is valid) if that's
            # the case returns the current value immediately
            exists = "_object" in self.__dict__
            if exists and self._object: return self._object

            # verifies if there's an id value currently set in
            # the reference in case it does not exists sets the
            # object value in the current instance with a none
            # value and then returns this (invalid value)
            if not self.id:
                object = None
                self.__dict__["object"] = object
                return object

            # creates the map of keyword based arguments that is going
            # to be used in the resolution of the reference and uses the
            # data source based get attribute to retrieve the object
            # that represents the reference
            kwargs = {
                name : self.id
            }
            _object = self._target.get(**kwargs)

            # sets the resolved object (using the current id attribute)
            # in the current instance's dictionary and then returns this
            # value to the caller method as the resolved value
            self.__dict__["_object"] = _object
            return _object

    return Reference

def references(target, name = None, eager = False):
    name = name or "id"
    reference_c = reference(target, name = name, eager = eager)

    class References(Type):

        _name = name
        """ The name of the key (join) attribute for the
        reference that is going to be created, this name
        may latter be used to cast the value """

        def __init__(self, ids):
            if isinstance(ids, References): self.build_i(ids)
            else: self.build(ids)

        def __len__(self):
            return self.objects.__len__()

        def __iter__(self):
            return self.objects.__iter__()

        def __contains__(self, item):
            return self.contains(item)

        @classmethod
        def _default(cls):
            return cls([])

        def build(self, ids):
            is_valid = not ids == None
            is_iterable = util.is_iterable(ids)
            if is_valid and not is_iterable: ids = [ids]

            self.ids = ids
            self.objects = []
            self.objects_m = {}

            self.set_ids(self.ids)

        def build_i(self, references):
            self.ids = references.ids
            self.objects = references.objects
            self.objects_m = references.objects_m

        def set_ids(self, ids):
            ids = ids or []
            for id in ids:
                if id == "" or id == None: continue
                object = reference_c(id)
                self.objects.append(object)
                self.objects_m[id] = object

        def ref_v(self):
            return [object.ref_v() for object in self.objects]

        def json_v(self):
            return [object.json_v() for object in self.objects]

        def list(self):
            return [object.value() for object in self.objects]

        def is_empty(self):
            ids_l = len(self.ids)
            return ids_l == 0

        def append(self, id):
            is_object = hasattr(id, self._name)
            if is_object: id = getattr(id, self._name)
            object = reference_c(id)
            self.ids.append(id)
            self.objects.append(object)
            self.objects_m[id] = object

        def remove(self, id):
            is_object = hasattr(id, self._name)
            if is_object: id = getattr(id, self._name)
            object = self.objects_m[id]
            self.ids.remove(id)
            self.objects.remove(object)
            del self.objects_m[id]

        def contains(self, id):
            is_object = hasattr(id, self._name)
            if is_object: id = getattr(id, self._name)
            return id in self.objects_m

    return References
