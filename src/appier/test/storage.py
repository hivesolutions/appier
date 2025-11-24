#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2024 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import shutil
import tempfile
import unittest

import appier


class FsEngineTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_store(self):
        file_data = b"Hello World"
        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": os.path.join(self.temp_dir, "test.txt")}

        appier.FsEngine.store(file)

        file_path = os.path.join(self.temp_dir, "test.txt")
        self.assertEqual(os.path.exists(file_path), True)

        handle = open(file_path, "rb")
        try:
            data = handle.read()
        finally:
            handle.close()

        self.assertEqual(data, file_data)

    def test_load(self):
        file_data = b"Hello World"
        file_path = os.path.join(self.temp_dir, "test.txt")

        handle = open(file_path, "wb")
        try:
            handle.write(file_data)
        finally:
            handle.close()

        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": file_path}

        appier.FsEngine.load(file)

        self.assertEqual(file.size, len(file_data))
        self.assertEqual(file.hash != None, True)
        self.assertEqual(file.etag != None, True)

    def test_delete(self):
        file_data = b"Hello World"
        file_path = os.path.join(self.temp_dir, "test.txt")

        handle = open(file_path, "wb")
        try:
            handle.write(file_data)
        finally:
            handle.close()

        self.assertEqual(os.path.exists(file_path), True)

        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": file_path}

        appier.FsEngine.delete(file)

        self.assertEqual(os.path.exists(file_path), False)

    def test_read(self):
        file_data = b"Hello World"
        file_path = os.path.join(self.temp_dir, "test.txt")

        handle = open(file_path, "wb")
        try:
            handle.write(file_data)
        finally:
            handle.close()

        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": file_path}

        data = appier.FsEngine.read(file)

        self.assertEqual(data, file_data)

    def test_read_size(self):
        file_data = b"Hello World"
        file_path = os.path.join(self.temp_dir, "test.txt")

        handle = open(file_path, "wb")
        try:
            handle.write(file_data)
        finally:
            handle.close()

        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": file_path}

        data = appier.FsEngine.read(file, size=5)

        self.assertEqual(data, b"Hello")

        data = appier.FsEngine.read(file, size=6)

        self.assertEqual(data, b" World")

        data = appier.FsEngine.read(file, size=6)

        self.assertEqual(data, b"")

    def test_seek(self):
        file_data = b"Hello World"
        file_path = os.path.join(self.temp_dir, "test.txt")

        handle = open(file_path, "wb")
        try:
            handle.write(file_data)
        finally:
            handle.close()

        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": file_path}

        appier.FsEngine.seek(file, offset=6)

        data = appier.FsEngine.read(file)

        self.assertEqual(data, b"World")

    def test_cleanup(self):
        file_data = b"Hello World"
        file_path = os.path.join(self.temp_dir, "test.txt")

        handle = open(file_path, "wb")
        try:
            handle.write(file_data)
        finally:
            handle.close()

        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": file_path}

        appier.FsEngine._handle(file)

        self.assertEqual(hasattr(file, "_handle"), True)

        appier.FsEngine.cleanup(file)

        self.assertEqual(hasattr(file, "_handle"), False)

    def test_is_seekable(self):
        self.assertEqual(appier.FsEngine.is_seekable(), True)

    def test_file_path(self):
        file = appier.File((b"test.txt", None, b"Hello World"))
        file.engine = "fs"
        file.params = {"file_path": os.path.join(self.temp_dir, "custom.txt")}

        file_path = appier.FsEngine._file_path(file)

        self.assertEqual(file_path, os.path.join(self.temp_dir, "custom.txt"))

    def test_file_path_default(self):
        file = appier.File((b"test.txt", None, b"Hello World"))
        file.engine = "fs"

        file_path = appier.FsEngine._file_path(file, base=self.temp_dir)

        expected_path = os.path.join(self.temp_dir, file.guid)
        self.assertEqual(file_path, expected_path)

    def test_file_path_ensure(self):
        sub_dir = os.path.join(self.temp_dir, "sub", "directory")
        file = appier.File((b"test.txt", None, b"Hello World"))
        file.engine = "fs"
        file.params = {"file_path": os.path.join(sub_dir, "test.txt")}

        self.assertEqual(os.path.exists(sub_dir), False)

        file_path = appier.FsEngine._file_path(file, ensure=True)

        self.assertEqual(os.path.exists(sub_dir), True)
        self.assertEqual(file_path, os.path.join(sub_dir, "test.txt"))

    def test_compute(self):
        file_data = b"Hello World"
        file_path = os.path.join(self.temp_dir, "test.txt")

        handle = open(file_path, "wb")
        try:
            handle.write(file_data)
        finally:
            handle.close()

        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": file_path}

        appier.FsEngine._compute(file)

        self.assertEqual(file.size, len(file_data))
        self.assertEqual(type(file.hash), str)
        self.assertEqual(type(file.etag), str)
        self.assertEqual(file.hash, file.etag)

    def test_handle(self):
        file_data = b"Hello World"
        file_path = os.path.join(self.temp_dir, "test.txt")

        handle = open(file_path, "wb")
        try:
            handle.write(file_data)
        finally:
            handle.close()

        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": file_path}

        handle = appier.FsEngine._handle(file)

        self.assertEqual(hasattr(file, "_handle"), True)
        self.assertEqual(handle != None, True)
        self.assertEqual(handle.closed, False)

        appier.FsEngine.cleanup(file)

    def test_integration(self):
        file_data = b"Hello World"
        file = appier.File((b"test.txt", None, file_data))
        file.engine = "fs"
        file.params = {"file_path": os.path.join(self.temp_dir, "test.txt")}

        appier.FsEngine.store(file)

        file2 = appier.File((b"test.txt", None, file_data))
        file2.engine = "fs"
        file2.params = {"file_path": os.path.join(self.temp_dir, "test.txt")}

        appier.FsEngine.load(file2)

        self.assertEqual(file2.size, len(file_data))

        data = appier.FsEngine.read(file2)

        self.assertEqual(data, file_data)

        appier.FsEngine.delete(file2)

        file_path = os.path.join(self.temp_dir, "test.txt")
        self.assertEqual(os.path.exists(file_path), False)


class BaseEngineTest(unittest.TestCase):
    def test_is_stored(self):
        self.assertEqual(appier.BaseEngine.is_stored(), True)


class StorageEngineTest(unittest.TestCase):
    def test_is_seekable(self):
        self.assertEqual(appier.StorageEngine.is_seekable(), False)

    def test_is_stored(self):
        self.assertEqual(appier.StorageEngine.is_stored(), False)
