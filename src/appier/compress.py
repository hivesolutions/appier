#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2021 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2021 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os

from . import legacy
from . import exceptions

class Compress(object):

    def __init__(self):
        self._load_compress()

    def load_jsmin(self):
        try: import jsmin
        except ImportError: self.jsmin = None; return
        self.jsmin = jsmin

    def type_jpeg(self):
        return "image/jpeg"

    def compress(self, file_path, modified = None, method = None):
        # retrieves the modification data from the requested file and
        # uses it to construct the complete (cache) key to be used in
        # cache try, in case there's a match returns the new file
        modified = modified or os.path.getmtime(file_path)
        key = "%s:%s" % (method, file_path)
        result = self.try_cache(key, modified)
        if result: return (len(result), legacy.BytesIO(result))

        # in case there's no provided method a proper not found exception
        # should be raised so that the end user is notified about the non
        # existence of such unset compressor (as expected)
        if method == None: raise exceptions.NotFoundError(
            message = "Compressor is not defined"
        )

        # in case the compress string is defined, tries to find the proper
        # compress method and in case it's not found raises an exception
        if not hasattr(self, "compress_" + method): raise exceptions.NotFoundError(
            message = "Compressor '%s' not found" % method
        )

        # retrieves the proper compressor method for the requested compress
        # technique, this should be used in a dynamic way enforcing some
        # overhead to avoid extra issues while handling with files
        compressor = getattr(self, "compress_" + method)

        # opens the requested file and reads the complete set of information
        # from it closing the file object after the operation is complete
        file = open(file_path, "rb")
        try: data = file.read()
        finally: file.close()

        # runs the compressing operation using the target compressor and uses
        # the resulting (compressed) data as the value to be returned
        result = compressor(data)

        # constructs both the size and the file object from the resulting plain
        # string data (bytes sequence), these values are considered the result
        result_size = len(result)
        result_file = legacy.BytesIO(result)

        # flags the proper values in the cache so that they may be re-used in case
        # the flag remains the same for the key, then returns the resulting tuple
        self.flag_cache(key, modified, result)
        return (result_size, result_file)

    def compress_jpeg(self, file_path):
        if self.jinja: return self.compress_jpeg_pil(file_path)
        return self.compress_fallback(file_path)

    def compress_jpeg_pil(self, data, quality = 80):
        input = legacy.BytesIO(data)
        output = legacy.BytesIO()
        image = self.pil.Image.open(input)
        image.save(output, format = "jpeg", quality = quality, optimize = True)
        output.seek(0, os.SEEK_SET)
        data = output.read()
        return data

    def compress_js(self, data):
        if self.jsmin: return self.compress_js_jsmin(data)
        return self.compress_fallback(data)

    def compress_js_jsmin(self, data):
        return self.jsmin.jsmin(data)

    def compress_fallback(self, data):
        return data

    def _load_compress(self):
        self.load_jsmin()
