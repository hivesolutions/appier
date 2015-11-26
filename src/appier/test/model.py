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

import unittest

import appier

from . import mock

class ModelTest(unittest.TestCase):

    def setUp(self):
        app = appier.App()
        app._register_models_m(mock, "Mocks")

    def tearDown(self):
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        person = mock.Person()
        person.name = "Name"

        self.assertEqual(person.name, "Name")
        self.assertEqual(person["name"], "Name")
        self.assertEqual(len(person), 1)

        person["age"] = 20

        self.assertEqual(person.age, 20)
        self.assertEqual(person["age"], 20)
        self.assertEqual(len(person), 2)

        self.assertEqual("age" in person, True)
        self.assertEqual("boss" in person, False)
        self.assertEqual(bool(person), True)

        del person["name"]

        self.assertRaises(AttributeError, lambda: person.name)
        self.assertRaises(KeyError, lambda: person["name"])

        del person.age

        self.assertRaises(AttributeError, lambda: person.age)
        self.assertRaises(KeyError, lambda: person["age"])

        self.assertEqual(bool(person), False)

    def test_find(self):
        result = mock.Person.find(age = 1)
        self.assertEqual(len(result), 0)

        person = mock.Person()
        person.age = 1
        person.name = "Name"
        person.save()

        result = mock.Person.find(age = 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].age, 1)

    def test_count(self):
        result = mock.Person.count()
        self.assertEqual(result, 0)

        person = mock.Person()
        person.age = 1
        person.name = "Name"
        person.save()

        result = mock.Person.count()
        self.assertEqual(result, 1)

    def test_validation(self):
        person = mock.Person()

        self.assertRaises(appier.ValidationError, person.save)

        person = mock.Person()
        person.name = "Name"
        person.save()

        person = mock.Person()
        person.name = "Name"

        self.assertRaises(appier.ValidationError, person.save)

    def test_map(self):
        person = mock.Person()
        person.name = "Name"

        self.assertEqual(person.name, "Name")

        person.save()

        self.assertEqual(person.identifier, 1)
        self.assertEqual(person.name, "Name")

        person_m = person.map()

        self.assertEqual(person_m["identifier"], 1)
        self.assertEqual(person_m["name"], "Name")

        person.age = 20
        person.hidden = "Hidden"

        self.assertEqual(person.age, 20)
        self.assertEqual(person.hidden, "Hidden")

        person_m = person.map(all = True)

        self.assertEqual(person_m["identifier"], 1)
        self.assertEqual(person_m["name"], "Name")
        self.assertEqual(person_m["age"], 20)
        self.assertEqual(person_m["hidden"], "Hidden")

        cat = mock.Cat()
        cat.name = "NameCat"

        self.assertEqual(cat.name, "NameCat")

        cat.save()

        self.assertEqual(cat.identifier, 1)

        person.cats = [cat]
        person.save()

        person_m = person.map(resolve = True, all = True)

        self.assertEqual(person_m["cats"][0]["identifier"], 1)
        self.assertEqual(person_m["cats"][0]["name"], "NameCat")

        person = mock.Person.get(identifier = 1)

        self.assertEqual(person.cats[0].name, "NameCat")

        person_m = person.map(all = True)

        self.assertEqual(person_m["cats"][0], 1)

        person_m = person.map(resolve = True, all = True)

        self.assertEqual(person_m["cats"][0]["identifier"], 1)
        self.assertEqual(person_m["cats"][0]["name"], "NameCat")
