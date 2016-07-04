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

import os
import tempfile

from . import exceptions

class StorageEngine(object):

    @classmethod
    def load(cls, file, *args, **kwargs):
        raise exceptions.NotImplementedError()

    @classmethod
    def store(cls, file, *args, **kwargs):
        raise exceptions.NotImplementedError()

    @classmethod
    def read(cls, file, *args, **kwargs):
        raise exceptions.NotImplementedError()

class BaseEngine(StorageEngine):

    @classmethod
    def load(self, file, *args, **kwargs):
        force = kwargs.get("force", False)
        if not self.file_name: return
        if self.data and not force: return

        path = tempfile.mkdtemp()
        path_f = os.path.join(path, self.file_name)
        self.file.save(path_f)

        file = open(path_f, "rb")
        try: self.data = file.read()
        finally: file.close()

        self._compute()

    @classmethod
    def store(cls, file, *args, **kwargs):
        pass

    @classmethod
    def read(cls, file, *args, **kwargs):
        return file.data

class FsEngine(StorageEngine):

    @classmethod
    def store(cls, file, *args, **kwargs):
        file_path = cls._file_path(file)
        handle = open(file_path, "wb")
        try: handle.write(file.data)
        finally: handle.close()

    @classmethod
    def load(cls, file, *args, **kwargs):
        force = kwargs.get("force", False)
        if file.data and not force: return
        file_path = cls._file_path(file, ensure = False)
        handle = open(file_path, "rb")
        try: file.data = handle.read()
        finally: handle.close()
        file._compute()

    @classmethod
    def read(cls, file, *args, **kwargs):
        size = kwargs.get("size", None)
        data = None
        file_path = cls._file_path(file, ensure = False)
        handle = hasattr(file, "_handle") and file._handle
        if not handle: handle = open(file_path, "rb")
        file._handle = handle
        try: data = handle.read(size or -1)
        finally:
            is_final = True if not size or not data else False
            is_final and cls._cleanup(file)
        return data

    @classmethod
    def _cleanup(cls, file):
        file._handle.close()
        file._handle = None

    @classmethod
    def _file_path(cls, file, ensure = True, base = "~/.data"):
        # verifies that the standard params value is defined and
        # if that's no the case defaults the value, then tries to
        # retrieve a series of parameters for file path discovery
        params = file.params or {}
        file_path = params.get("file_path", None)

        # defines the default file path in case it's not defined from
        # the params (using the guid value) and then normalizes such
        # value using a series of operations
        file_path = file_path or os.path.join(base, file.guid)
        file_path = os.path.expanduser(file_path)
        file_path = os.path.normpath(file_path)
        dir_path = os.path.dirname(file_path)

        # verifies if the ensure flag is not set of if the directory
        # path associated with the current file path exists and if
        # that's the case returns the file path immediately
        if not ensure: return file_path
        if os.path.exists(dir_path): return file_path

        # creates the directories (concrete and parents) as requested
        # and then returns the "final" file path value to the caller
        # method so that it can be used for reading or writing
        os.makedirs(dir_path)
        return file_path
