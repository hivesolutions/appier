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

import uuid
import base64
import hashlib

from . import util
from . import crypt
from . import legacy
from . import common
from . import storage
from . import exceptions

class AbstractType(object):

    def json_v(self, *args, **kwargs):
        return str(self)

    def map_v(self, *args, **kwargs):
        return self.json_v()

class Type(AbstractType):

    def __init__(self, value):
        cls = self.__class__
        self.loads(value)

    def json_v(self, *args, **kwargs):
        return self.dumps()

    def loads(self, value):
        raise exceptions.NotImplementedError()

    def dumps(self):
        raise exceptions.NotImplementedError()

class File(AbstractType):

    def __init__(self, file):
        if isinstance(file, legacy.BYTES): self.build_d(file)
        elif isinstance(file, dict): self.build_b64(file)
        elif isinstance(file, tuple): self.build_t(file)
        elif isinstance(file, File): self.build_i(file)
        else: self.build_f(file)

    def __repr__(self):
        return "<File: %s>" % self.file_name

    def __str__(self):
        return self.file_name

    def __len__(self):
        return self.size

    def build_d(self, file_d, name = "default"):
        self.build_t((name, None, file_d))

    def build_b64(self, file_m):
        name = file_m["name"]
        data_b64 = file_m["data"]
        hash = file_m.get("hash", None)
        mime = file_m.get("mime", None)
        etag = file_m.get("etag", None)
        guid = file_m.get("guid", None)
        params = file_m.get("params", None)
        engine = file_m.get("engine", None)

        is_valid = name and data_b64
        data_b64_b = legacy.bytes(data_b64)
        data = base64.b64decode(data_b64_b) if is_valid else None
        data_b64 = legacy.str(data_b64)
        size = len(data) if is_valid else 0
        hash = hash or self._hash(data)
        etag = etag or self._etag(data)
        guid = guid or self._guid()

        self.data = data
        self.data_b64 = data_b64
        self.file = None
        self.hash = hash
        self.size = size
        self.file_name = name
        self.mime = mime
        self.etag = etag
        self.guid = guid
        self.params = params
        self.engine = engine

        self._load()

    def build_t(self, file_t):
        name, content_type, data = file_t

        is_valid = name and data
        data_b64 = base64.b64encode(data) if is_valid else None
        data_b64 = legacy.str(data_b64)
        size = len(data) if is_valid else 0
        etag = self._etag(data)
        hash = self._hash(data)
        guid = self._guid()

        self.data = data
        self.data_b64 = data_b64
        self.file = None
        self.hash = hash
        self.size = size
        self.file_name = name
        self.mime = content_type
        self.etag = etag
        self.guid = guid
        self.params = None
        self.engine = None

        self._load()

    def build_i(self, file):
        self.data = file.data
        self.data_b64 = file.data_b64
        self.file = file.file
        self.hash = file.hash
        self.size = file.size
        self.file_name = file.file_name
        self.mime = file.mime
        self.etag = file.etag
        self.guid = file.guid
        self.params = file.params
        self.engine = file.engine

        self._load()

    def build_f(self, file):
        self.data = None
        self.data_b64 = None
        self.file = file
        self.hash = hash
        self.size = file.content_length
        self.file_name = file.filename
        self.mime = file.content_type
        self.etag = None
        self.guid = self._guid()
        self.params = None
        self.engine = None

        self._load()

    def read(self, size = None):
        engine = self._engine()
        return engine.read(self, size = size)

    def seek(self, offset = None):
        engine = self._engine()
        return engine.seek(self, offset = offset)

    def delete(self):
        engine = self._engine()
        return engine.delete(self)

    def cleanup(self):
        engine = self._engine()
        return engine.cleanup(self)

    def json_v(self, *args, **kwargs):
        if not self.is_valid(): return None
        store = kwargs.get("store", True)
        if store: self._store()
        data = self.data_b64 if self.is_stored() else None
        return dict(
            name = self.file_name,
            data = data,
            hash = self.hash,
            mime = self.mime,
            etag = self.etag,
            guid = self.guid,
            params = self.params,
            engine = self.engine
        )

    def is_seekable(self):
        engine = self._engine()
        return engine.is_seekable()

    def is_stored(self):
        engine = self._engine()
        return engine.is_stored()

    def is_valid(self):
        return self.file_name or (self.data or self.data_b64)

    def is_empty(self):
        return self.size <= 0

    def _hash(self, data):
        if not data: return None
        hash = hashlib.sha256(data)
        digest = hash.hexdigest()
        return digest

    def _etag(self, data):
        if not data: return None
        hash = hashlib.md5(data)
        digest = hash.hexdigest()
        return digest

    def _guid(self):
        return str(uuid.uuid4())

    def _load(self, force = False):
        engine = self._engine()
        engine.load(self, force = force)

    def _store(self, force = False):
        engine = self._engine()
        engine.store(self, force = force)

    def _compute(self):
        """
        Computes a series of "calculated" attributes related with
        the data associated with the current file, these values may
        include: length, hash values, etag, etc.

        This method should be called whenever the data attributes are
        changed as defined in specification.
        """

        self.data_b64 = base64.b64encode(self.data)
        self.data_b64 = legacy.str(self.data_b64)
        self.hash = self._hash(self.data)
        self.size = len(self.data)
        self.etag = self._etag(self.data)

    def _engine(self):
        if not self.engine: return storage.BaseEngine
        return getattr(storage, self.engine.capitalize() + "Engine")

class Files(AbstractType):

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

    def json_v(self, *args, **kwargs):
        return [file.json_v(*args, **kwargs) for file in self._files]

    def is_empty(self):
        return len(self._files) == 0

    def _load(self):
        for file in self._files: file._load()

class ImageFile(File):

    def build_b64(self, file_m):
        File.build_b64(self, file_m)
        self.width = file_m.get("width", 0)
        self.height = file_m.get("height", 0)
        self.format = file_m.get("format", None)
        self.kwargs = file_m.get("kwargs", {})
        self._ensure_all()

    def build_t(self, file_t):
        File.build_t(self, file_t)
        self._ensure_all()

    def build_i(self, file):
        File.build_i(self, file)
        self.width = file.width if hasattr(file, "width") else 0
        self.height = file.height if hasattr(file, "height") else 0
        self.format = file.format if hasattr(file, "format") else None
        self.kwargs = file.kwargs if hasattr(file, "kwargs") else {}
        self._ensure_all()

    def build_f(self, file):
        File.build_f(self, file)
        self._ensure_all()

    def json_v(self, *args, **kwargs):
        if not self.is_valid(): return None
        value = File.json_v(self, *args, **kwargs)
        value.update(
            width = self.width,
            height = self.height,
            format = self.format,
            kwargs = self.kwargs
        )
        return value

    def _ensure_all(self):
        self._ensure_size()
        self._ensure_mime()
        self._ensure_kwargs()

    def _ensure_size(self):
        if hasattr(self, "width") and self.width and\
            hasattr(self, "height") and self.height: return
        self.width, self.height = self._size()

    def _ensure_mime(self):
        if hasattr(self, "format") and self.format and\
            hasattr(self, "mime") and self.mime: return
        self.format, self.mime = self._mime()

    def _ensure_kwargs(self):
        if hasattr(self, "kwargs"): return
        self.kwargs = dict()

    def _size(self):
        try: return self._size_image()
        except Exception: return self._size_default()

    def _size_image(self):
        if self.data: return self._size_pil()
        else: return self._size_default()

    def _size_pil(self):
        util.ensure_pip("PIL", package = "pillow")
        import PIL.Image
        buffer = legacy.BytesIO(self.data)
        try:
            image = PIL.Image.open(buffer)
            size = image.size
        finally:
            buffer.close()
        return size

    def _size_default(self):
        return (0, 0)

    def _mime(self):
        try: return self._mime_image()
        except Exception: return self._mime_default()

    def _mime_image(self):
        if self.data: return self._mime_pil()
        else: return self._mime_default()

    def _mime_pil(self):
        util.ensure_pip("PIL", package = "pillow")
        import PIL.Image
        buffer = legacy.BytesIO(self.data)
        try:
            image = PIL.Image.open(buffer)
            format = image.format.lower()
            mime = PIL.Image.MIME[image.format]
        finally:
            buffer.close()
        return format, mime

    def _mime_default(self):
        return None, "application/octet-stream"

class ImageFiles(Files):

    def base(self):
        return ImageFile

def image(width = None, height = None, format = "png", **kwargs):

    class _ImageFile(ImageFile):

        RGB_FORMATS = ("jpg", "jpeg")
        """ The set of format that are considered to be
        RGB based and should be handled with special care """

        def build_b64(self, file_m):
            ImageFile.build_b64(self, file_m)

            # verifies if there's valid data in the current file
            # if that's not the case there's nothing remaining to
            # be done (not going to process the file)
            if not self.data_b64: return

            # determines if a resize operation is required for the
            # current image data, if that's not the case returns the
            # control flow immediately (nothing to be done)
            need_resize = self.need_resize(
                width_o = self.width,
                height_o = self.height,
                format_o = self.format,
                kwargs_o = self.kwargs
            )
            if not need_resize: return

            # decodes the base 64 based data and then runs the resize
            # operation with the current data re-encoding it back to
            # the base 64 model to be used in the map storage
            data_b64 = legacy.bytes(self.data_b64)
            data = base64.b64decode(data_b64)
            data = self.resize(data)
            data_b64 = base64.b64encode(data)
            data_b64 = legacy.str(data_b64)

            # updates the data attribute of the file map wit the
            # "newly" resize data value coming from the resize
            # operation, note that this "new" data may have different
            # width, height and format from the original one
            file_m["data"] = data_b64

            # updates the parameters attributes in the file map so
            # that the new file is marked with proper values
            file_m["kwargs"] = kwargs

            # removes a series of keys from the file map as
            # they are no longer reliable and may reflect
            # different values from the ones contained in data
            # theses should be update by the "ensure" methods
            for name in ("width", "height", "format"):
                if name in file_m: del file_m[name]

            # runs the rebuilding of the information taking into
            # account the new information from the file
            ImageFile.build_b64(self, file_m)

        def build_t(self, file_t):
            # unpacks the file tuple into its component to be
            # used for the format and size ensure operations
            name, content_type, data = file_t

            # tries to run the resize operation to ensure that
            # the proper size and format is present in the data
            try: _data = self.resize(data) if data else data
            except Exception: _data = data

            # updates the parameters attributes in the instance so
            # that the new file is marked with proper values
            self.kwargs = kwargs

            # creates the "new" file tuple with the newly resized
            # image data and runs the parent tuple build method
            file_t = (name, content_type, _data)
            ImageFile.build_t(self, file_t)

        def resize(self, data = None):
            util.ensure_pip("PIL", package = "pillow")
            import PIL.Image

            data = data or self.data
            if not data: return data

            is_resized = True if width or height else False
            if not is_resized: return data

            params = kwargs.get("params", {})
            background = kwargs.get("background", "ffffff")

            size = (width, height)
            in_buffer = legacy.BytesIO(data)
            out_buffer = legacy.BytesIO()
            try:
                image = PIL.Image.open(in_buffer)
                image = self._resize(image, size)
                image = self._format(image, format, background)
                image.save(out_buffer, format, **params)
                data = out_buffer.getvalue()
            finally:
                in_buffer.close()
                out_buffer.close()

            return data

        def need_resize(
            self,
            width_o = None,
            height_o = None,
            format_o = None,
            kwargs_o = None
        ):
            if width and not width == width_o: return True
            if height and not height == height_o: return True
            if format and not format == format_o: return True
            if kwargs and not kwargs == kwargs_o: return True
            return False

        def _resize(self, image, size):
            util.ensure_pip("PIL", package = "pillow")
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

        def _format(self, image, format, background):
            util.ensure_pip("PIL", package = "pillow")
            import PIL.Image

            # retrieves the reference to the top level class that is
            # going to be used for the access to some of the values
            cls = self.__class__

            # converts the target format into the lower based version
            # (normalization) and verifies if it's considered to be
            # an RGB only format, if that's not the case there's nothing
            # remaining to be done (no conversion required)
            format = format.lower()
            if not format in cls.RGB_FORMATS: return image

            # in case the format/mode of the original image is already
            # RGB there's no need to run the conversion process
            if image.mode == "RGB": return image

            # creates a new RGB based image with the target size and
            # with the provided background and copies it as the target
            new = PIL.Image.new("RGB", (image.width, image.height), "#" + background)
            new.paste(image, image)
            return new

    return _ImageFile

def images(width = None, height = None, format = "png", **kwargs):

    image_c = image(
        width = width,
        height = height,
        format = format,
        **kwargs
    )

    class _ImageFiles(ImageFiles):

        def base(self):
            return image_c

    return _ImageFiles

class Reference(AbstractType):
    pass

def reference(target, name = None, dumpall = False):
    name = name or "id"
    target_t = type(target)
    is_reference = target_t in legacy.STRINGS
    reserved = ("id", "_target", "_object", "_type", "__dict__")

    class _Reference(Reference):

        _name = name
        """ The name of the key (join) attribute for the
        reference that is going to be created, this name
        may latter be used to cast the value """

        def __init__(self, id):
            self.__start__()
            if isinstance(id, _Reference): self.build_i(id)
            elif isinstance(id, self._target): self.build_o(id)
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

        def __eq__(self, other):
            if other == None: return self.id in ("", b"", None)
            if isinstance(other, Reference): return self.equals(other)
            return id(self) == id(other)

        def __ne__(self, other):
            return not self.__eq__(other)

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
            # in case the name that is being set is not part of the reserved
            # names for the reference underlying structure the object resolution
            # is triggered to make sure the underlying object exists and is loaded
            if not name in reserved: self.resolve()

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
            util.verify(self._target)
            meta = getattr(self._target, name)
            self._type = meta.get("type", legacy.UNICODE)

        @classmethod
        def _default(cls):
            return cls(None)

        @classmethod
        def _target(cls):
            if is_reference: return common.base().APP.get_model(target)
            return target

        @classmethod
        def _btype(cls):
            if is_reference: _target = cls._target()
            else: _target = target
            meta = getattr(_target, name)
            return meta.get("type", legacy.UNICODE)

        def build(self, id, cast = True):
            is_unset = id in ("", b"", None)
            cast = cast and not is_unset
            if cast: id = self._target.cast(name, id)
            self.id = id
            self._object = None

        def build_i(self, reference):
            self.id = reference.id
            self._object = reference._object

        def build_o(self, object):
            self.id = getattr(object, self._name)
            self._object = object

        def ref_v(self, *args, **kwargs):
            return self.val()

        def json_v(self, *args, **kwargs):
            if dumpall: return self.resolve()
            return self.val()

        def map_v(self, *args, **kwargs):
            resolve = kwargs.get("resolve", True)
            value = self.resolve() if resolve else self._object
            if resolve and not value: return value
            if not value: return self.val()
            return value.map(*args, **kwargs)

        def val(self):
            is_empty = self.id in ("", b"", None)
            if is_empty: return None
            return self._type(self.id)

        def resolve(self, *args, **kwargs):
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

            # creates the map of keyword based arguments that are going
            # to be used in the resolution of the reference and uses the
            # data source based get attribute to retrieve the object
            # that represents the reference
            kwargs = dict(kwargs)
            kwargs[name] = self._target.cast(name, self.id)
            kwargs["raise_e"] = kwargs.get("raise_e", False)
            kwargs["eager_l"] = kwargs.get("eager_l", False)
            _object = self._target.get(*args, **kwargs)

            # sets the resolved object (using the current id attribute)
            # in the current instance's dictionary and then returns this
            # value to the caller method as the resolved value
            self.__dict__["_object"] = _object
            return _object

        def equals(self, other):
            if not self.__class__ == other.__class__: return False
            if not self._target == other._target: return False
            if not self.id == other.id: return False
            return True

        def is_resolved(self):
            exists = "_object" in self.__dict__
            return True if exists and self._object else False

        def is_resolvable(self):
            self.resolve()
            return False if self._object == None else True

    return _Reference

class References(AbstractType):
    pass

def references(target, name = None, dumpall = False):
    name = name or "id"
    target_t = type(target)
    is_reference = target_t in legacy.STRINGS
    reference_c = reference(target, name = name, dumpall = dumpall)

    class _References(References):

        _name = name
        """ The name of the key (join) attribute for the
        reference that is going to be created, this name
        may latter be used to cast the value """

        def __init__(self, ids):
            self.__start__()
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

        def __start__(self):
            if is_reference: self._target = self.__class__._target()
            else: self._target = target
            util.verify(self._target)

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
            self.ids = []
            for id in ids:
                if id == "" or id == None: continue
                object = reference_c(id)
                object_id = object.id
                self.ids.append(object_id)
                self.objects.append(object)
                self.objects_m[object_id] = object

        def ref_v(self, *args, **kwargs):
            return [object.ref_v(*args, **kwargs) for object in self.objects]

        def json_v(self, *args, **kwargs):
            return [object.json_v(*args, **kwargs) for object in self.objects]

        def map_v(self, *args, **kwargs):
            return [object.map_v(*args, **kwargs) for object in self.objects]

        def list(self):
            return [object.val() for object in self.objects]

        def resolve(self, *args, **kwargs):
            return [object.resolve(*args, **kwargs) for object in self.objects]

        def find(self, *args, **kwargs):
            kwargs = dict(kwargs)
            kwargs[name] = {"$in" : [self._target.cast(name, _id) for _id in self.ids]}
            return self._target.find(*args, **kwargs)

        def paginate(self, *args, **kwargs):
            kwargs = dict(kwargs)
            kwargs[name] = {"$in" : [self._target.cast(name, _id) for _id in self.ids]}
            return self._target.paginate(*args, **kwargs)

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

        def is_resolved(self):
            if not self.objects: return True
            return self.objects[0].is_resolved()

    return _References

class Encrypted(AbstractType):

    PADDING = ":encrypted"

def encrypted(cipher = "spritz", key = None, encoding = "utf-8"):
    key = key or None

    class _Encrypted(Encrypted):

        def __init__(self, value):
            cls = self.__class__
            util.verify(
                isinstance(value, legacy.ALL_STRINGS) or\
                isinstance(value, Encrypted)
            )
            self.key = key or common.base().APP.crypt_secret
            self.key = legacy.bytes(self.key)
            if isinstance(value, Encrypted): self.build_i(value)
            elif value.endswith(cls.PADDING): self.build_e(value)
            else: self.build(value)

        def __str__(self):
            return self.value

        def __unicode__(self):
            return self.value

        def __len__(self):
            return self.value.__len__()

        def __iter__(self):
            return self.value.__iter__()

        def __bool__(self):
            return bool(self.value)

        def build(self, value):
            self.value = value
            self.encrypted = self._encrypt(value)

        def build_e(self, encrypted):
            self.encrypted = encrypted
            self.value = self._decrypt(encrypted)

        def build_i(self, instance):
            self.key = instance.key
            self.value = instance.value
            self.encrypted = instance.encrypted

        def json_v(self, *args, **kwargs):
            return self.encrypted

        def _encrypt(self, value, strict = False):
            if not self.key and not strict: return value
            cls = self.__class__
            value = legacy.bytes(value, encoding = encoding)
            cipher_i = crypt.Cipher.new(cipher, self.key)
            encrypted = cipher_i.encrypt(value)
            encrypted = base64.b64encode(encrypted)
            encrypted = legacy.str(encrypted, encoding = encoding)
            return encrypted + cls.PADDING

        def _decrypt(self, value, strict = False):
            if not self.key and not strict: return value
            cls = self.__class__
            util.verify(value.endswith(cls.PADDING))
            value = value[:-len(cls.PADDING)]
            value = legacy.bytes(value)
            value = base64.b64decode(value)
            cipher_i = crypt.Cipher.new(cipher, self.key)
            decrypted = cipher_i.decrypt(value)
            decrypted = legacy.str(decrypted, encoding = encoding)
            return decrypted

    return _Encrypted

secure = encrypted()
