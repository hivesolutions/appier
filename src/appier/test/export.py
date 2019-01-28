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

import json
import unittest

import appier

class ExportTest(unittest.TestCase):

    def setUp(self):
        self.app = appier.App()

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_import_single(self):
        structure = {
            "person:id" : dict(_id = "person:id", seq = 11),
            "account:id" : dict(_id = "account:id", seq = 33)
        }
        data = json.dumps(structure)
        data = appier.legacy.bytes(data)

        adapter = appier.get_adapter()
        manager = appier.ExportManager(
            adapter,
            multiple = self.app.resolve()
        )

        collection = adapter.collection("counter")
        manager._import_single(collection, data, key = "_id")

        values = collection.find()
        values = [value for value in values]

        self.assertEqual(type(values), list)
        self.assertEqual(len(values), 2)

        value = collection.find_one(dict(_id = "person:id"))

        self.assertEqual(value["seq"], 11)

    def test_import_multiple(self):
        data = [
            (
                "person:id",
                appier.legacy.bytes(
                    json.dumps(dict(_id = "person:id", seq = 11)),
                    encoding = "utf-8"
                )
            ),
            (
                "account:id",
                appier.legacy.bytes(
                    json.dumps(dict(_id = "account:id", seq = 33)),
                    encoding = "utf-8"
                )
            )
        ]

        adapter = appier.get_adapter()
        manager = appier.ExportManager(
            adapter,
            multiple = self.app.resolve()
        )

        collection = adapter.collection("counter")
        manager._import_multiple(collection, data, key = "_id")

        values = collection.find()
        values = [value for value in values]

        self.assertEqual(type(values), list)
        self.assertEqual(len(values), 2)

        value = collection.find_one(dict(_id = "person:id"))

        self.assertEqual(value["seq"], 11)
