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
import tempfile
import unittest

import appier


class DataTest(unittest.TestCase):
    def test_id(self):
        adapter = appier.DataAdapter()
        identifier = adapter._id()

        self.assertEqual(type(identifier), str)
        self.assertEqual(len(identifier), 24)

    def test_drop_db_missing(self):
        fd, file_path = tempfile.mkstemp()
        os.close(fd)
        adapter = appier.TinyAdapter(file_path=file_path)
        adapter.get_db()
        os.remove(file_path)
        adapter.drop_db()
