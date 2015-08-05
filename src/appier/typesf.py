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
import base64
import hashlib
import tempfile

from . import util
from . import legacy
from . import common

class Type(object):

    def json_v(self):
        return str(self)

class File(Type):

    def __init__(self, file):
        file_t = type(file)
        if file_t == dict: self.build_b64(file)
        elif isinstance(file, tuple): self.build_t(file)
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

        is_valid = name and data_b64
        data = base64.b64decode(data_b64) if is_valid else None
        size = len(data) if is_valid else 0
        etag = self._etag(data)

        self.data = data
        self.data_b64 = data_b64
        self.file = None
        self.size = size
        self.file_name = name
        self.mime = mime
        self.etag = etag

    def build_t(self, file_t):
        name, content_type, data = file_t

        is_valid = name and data
        data_b64 = base64.b64encode(data) if is_valid else None
        size = len(data) if is_valid else 0
        etag = self._etag(data)

        self.data = data
        self.data_b64 = data_b64
        self.file = None
        self.size = size
        self.file_name = name
        self.mime = content_type
        self.etag = etag

    def build_i(self, file):
        self.file = file.file
        self.size = file.size
        self.file_name = file.file_name
        self.mime = file.mime
        self.etag = file.etag
        self.data = file.data
        self.data_b64 = file.data_b64

    def build_f(self, file):
        self.file = file
        self.size = file.content_length
        self.file_name = file.filename
        self.mime = file.content_type
        self.etag = None
        self.data = None
        self.data_b64 = None

        self._flush()

    def read(self):
        return self.data

    def json_v(self):
        return dict(
            name = self.file_name,
            data = self.data_b64,
            mime = self.mime
        ) if self.is_valid() else None

    def is_valid(self):
        return self.file_name or (self.data or self.data_b64)

    def is_empty(self):
        return self.size <= 0

    def _etag(self, data):
        if not data: return None
        hash = hashlib.md5(data)
        digest = hash.hexdigest()
        return digest

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
        self.etag = self._etag(data)

class Files(Type):

    def __init__(self, files):
        if isinstance(files, Files): self.build_i(files)
        else: self.build_f(files)

    def __repr__(self):
        return "<Files: %d files>" % len(self._files)

    def __len__(self):
        return self._files.__len__()

    def __iter__(self):
        return self._files.__iter__()

    def __getitem__(self, key):
        return self._files.__getitem__(key)

    def base(self):
        return File

    def build_i(self, files):
        self._files = files._files

    def build_f(self, files):
        self._files = []
        base = self.base()
        if not type(files) == list: files = [files]
        for file in files:
            _file = base(file)
            if not _file.is_valid(): continue
            self._files.append(_file)

    def json_v(self):
        return [file.json_v() for file in self._files]

    def is_empty(self):
        return len(self._files) == 0

    def _flush(self):
        for file in self._files: file._flush()

class ImageFile(File):

    def build_b64(self, file_m):
        File.build_b64(self, file_m)
        self.width = file_m.get("width", 0)
        self.height = file_m.get("height", 0)

    def build_t(self, file_t):
        File.build_t(self, file_t)
        self.width, self.height = self._size()

    def build_i(self, file):
        File.build_i(self, file)
        self.width = file.width
        self.height = file.height

    def build_f(self, file):
        File.build_f(self, file)
        self.width, self.height = self._size()

    def json_v(self):
        return dict(
            name = self.file_name,
            data = self.data_b64,
            mime = self.mime,
            width = self.width,
            height = self.height
        ) if self.is_valid() else None

    def _size(self):
        try: return self._size_image()
        except: return self._size_default()

    def _size_image(self):
        import PIL.Image
        if not self.data: return self._size_default()
        buffer = legacy.BytesIO(self.data)
        try:
            image = PIL.Image.open(buffer)
            size = image.size
        finally:
            buffer.close()
        return size

    def _size_default(self):
        return (0, 0)

class ImageFiles(Files):

    def base(self):
        return ImageFile

def image(width = None, height = None, format = "png"):

    class _ImageFile(ImageFile):

        def build_t(self, file_t):
            name, content_type, data = file_t
            try: _data = self._resize(data)
            except: _data = data
            file_t = (name, content_type, _data)
            ImageFile.build_t(self, file_t)

        def _resize(self, data):
            import PIL.Image
            if not data: return data

            is_resized = True if width or height else False
            if not is_resized: return data

            size = (width, height)
            in_buffer = legacy.BytesIO(data)
            out_buffer = legacy.BytesIO()
            try:
                image = PIL.Image.open(in_buffer)
                image = self.__resize(image, size)
                image.save(out_buffer, format)
                data = out_buffer.getvalue()
            finally:
                in_buffer.close()
                out_buffer.close()

            return data

        def __resize(self, image, size):
            import PIL.Image

            # unpacks the provided tuple containing the size dimension into the
            # with and the height an in case one of these values is not defined
            # an error is raises indicating the problem
            width, height = size
            if not height and not width: raise AttributeError("invalid values")

            # retrieves the size of the loaded image and uses the values to calculate
            # the aspect ration of the provided image, this value is going to be
            # used latter for some of the resizing calculus
            image_width, image_height = image.size
            image_ratio = float(image_width) / float(image_height)

            # in case one of the size dimensions has not been specified
            # it must be calculated from the base values taking into account
            # that the aspect ration should be preserved
            if not height: height = int(image_height * width / float(image_width))
            if not width: width = int(image_width * height / float(image_height))

            # re-constructs the size tuple with the new values for the width
            # the height that have been calculated from the ratios
            size = (width, height)

            # calculates the target aspect ration for the image that is going
            # to be resized, this value is going to be used in the comparison
            # with the original image's aspect ration for determining the type
            # of image (horizontal or vertical) that we're going to resize
            size_ratio = width / float(height)

            # in case the image ratio is bigger than the size ratio this image
            # should be cropped horizontally meaning that some of the horizontal
            # image is going to disappear (horizontal cropping)
            if image_ratio > size_ratio:
                x_offset = int((image_width - size_ratio * image_height) / 2.0)
                image = image.crop((x_offset, 0, image_width - x_offset, image_height))

            # otherwise, in case the image ratio is smaller than the size ratio
            # the image is going to be cropped vertically
            elif image_ratio < size_ratio:
                y_offset = int((image_height - image_width / size_ratio) / 2.0)
                image = image.crop((0, y_offset, image_width, image_height - y_offset))

            # resizes the already cropped image into the target size using an
            # anti alias based algorithm (default expectations)
            image = image.resize(size, PIL.Image.ANTIALIAS)
            return image

    return _ImageFile

def images(width = None, height = None, format = "png"):

    image_c = image(
        width = width,
        height = height,
        format = format
    )

    class _ImageFiles(ImageFiles):

        def base(self):
            return image_c

    return _ImageFiles

class Reference(Type):
    pass

def reference(target, name = None, eager = False):
    name = name or "id"
    target_t = type(target)
    is_reference = target_t in legacy.STRINGS

    class _Reference(Reference):

        _name = name
        """ The name of the key (join) attribute for the
        reference that is going to be created, this name
        may latter be used to cast the value """

        def __init__(self, id):
            self.__start__()
            if isinstance(id, _Reference): self.build_i(id)
            else: self.build(id)

        def __str__(self):
            self.resolve()
            has_str = hasattr(self._object, "__str__")
            if has_str: return self._object.__str__()
            else: return str(self._object) or str()

        def __unicode__(self):
            self.resolve()
            has_unicode = hasattr(self._object, "__unicode__")
            if has_unicode: return self._object.__unicode__()
            else: return legacy.UNICODE(self._object) or legacy.UNICODE()

        def __len__(self):
            is_empty = self.id in ("", b"", None)
            return 0 if is_empty else 1

        def __bool__(self):
            is_empty = self.id in ("", b"", None)
            return not is_empty

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
            if is_reference: self._target = self.__class__._target()
            else: self._target = target
            meta = getattr(self._target, name)
            self._type = meta.get("type", legacy.UNICODE)

        @classmethod
        def _default(cls):
            return cls(None)

        @classmethod
        def _target(cls):
            if is_reference: return getattr(common.base().APP.models_i, target)
            return target

        @classmethod
        def _btype(cls):
            if is_reference: _target = cls._target()
            else: _target = target
            meta = getattr(_target, name)
            return meta.get("type", legacy.UNICODE)

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
            is_empty = self.id in ("", b"", None)
            if is_empty: return None
            return self._type(self.id)

        def resolve(self, strict = False):
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
                _object = None
                self.__dict__["_object"] = _object
                return _object

            # creates the map of keyword based arguments that is going
            # to be used in the resolution of the reference and uses the
            # data source based get attribute to retrieve the object
            # that represents the reference
            kwargs = {
                name : self._target.cast(name, self.id)
            }
            _object = self._target.get(raise_e = strict, **kwargs)

            # sets the resolved object (using the current id attribute)
            # in the current instance's dictionary and then returns this
            # value to the caller method as the resolved value
            self.__dict__["_object"] = _object
            return _object

    return _Reference

class References(Type):
    pass

def references(target, name = None, eager = False):
    name = name or "id"
    reference_c = reference(target, name = name, eager = eager)

    class _References(References):

        _name = name
        """ The name of the key (join) attribute for the
        reference that is going to be created, this name
        may latter be used to cast the value """

        def __init__(self, ids):
            if isinstance(ids, _References): self.build_i(ids)
            else: self.build(ids)

        def __len__(self):
            return self.objects.__len__()

        def __iter__(self):
            return self.objects.__iter__()

        def __bool__(self):
            return bool(self.objects)

        def __getitem__(self, key):
            return self.objects.__getitem__(key)

        def __contains__(self, item):
            return self.contains(item)

        @classmethod
        def _default(cls):
            return cls([])

        @classmethod
        def _target(cls):
            return reference_c._target()

        @classmethod
        def _btype(cls):
            return reference_c._btype()

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

        def resolve(self):
            return [object.resolve() for object in self.objects]

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

    return _References
