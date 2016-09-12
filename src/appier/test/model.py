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

import unittest

import appier

from . import mock

class ModelTest(unittest.TestCase):

    def setUp(self):
        self.app = appier.App()
        self.app._register_models_m(mock, "Mocks")

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_basic(self):
        person = mock.Person(fill = False)
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

    def test_delete(self):
        result = mock.Person.count()
        self.assertEqual(result, 0)

        person = mock.Person()
        person.age = 1
        person.name = "Name"
        person.save()

        result = mock.Person.count()
        self.assertEqual(result, 1)

        person.delete()

        result = mock.Person.count()
        self.assertEqual(result, 0)

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
        self.assertEqual(person.identifier_safe, 1)
        self.assertEqual(person.name, "Name")

        person_m = person.map()

        self.assertEqual(isinstance(person_m, dict), True)
        self.assertEqual(person_m["identifier"], 1)
        self.assertEqual(person_m["identifier_safe"], 1)
        self.assertEqual(person_m["name"], "Name")

        person.age = 20
        person.hidden = "Hidden"

        self.assertEqual(person.age, 20)
        self.assertEqual(person.hidden, "Hidden")

        person_m = person.map(all = True)

        self.assertEqual(isinstance(person_m, dict), True)
        self.assertEqual(person_m["identifier"], 1)
        self.assertEqual(person_m["identifier_safe"], 1)
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

        self.assertEqual(isinstance(person_m, dict), True)
        self.assertEqual(isinstance(person_m["cats"], list), True)
        self.assertEqual(isinstance(person_m["cats"][0], dict), True)
        self.assertEqual(person_m["cats"][0]["identifier"], 1)
        self.assertEqual(person_m["cats"][0]["identifier_safe"], 1)
        self.assertEqual(person_m["cats"][0]["name"], "NameCat")

        person = mock.Person.get(identifier = 1)

        self.assertEqual(person.cats[0].name, "NameCat")

        person = mock.Person.get(identifier = 1)

        person_m = person.map(all = True)

        self.assertEqual(person_m["cats"][0], 1)

        person_m = person.map(resolve = True, all = True)

        self.assertEqual(isinstance(person_m, dict), True)
        self.assertEqual(isinstance(person_m["cats"], list), True)
        self.assertEqual(isinstance(person_m["cats"][0], dict), True)
        self.assertEqual(person_m["cats"][0]["identifier"], 1)
        self.assertEqual(person_m["cats"][0]["identifier_safe"], 1)
        self.assertEqual(person_m["cats"][0]["name"], "NameCat")

    def test_increment(self):
        person = mock.Person()
        person.name = "Name1"
        person.save()

        self.assertEqual(person.identifier, 1)
        self.assertEqual(person.name, "Name1")

        person = mock.Person()
        person.name = "Name2"
        person.save()

        self.assertEqual(person.identifier, 2)
        self.assertEqual(person.name, "Name2")

        person = mock.Person()
        person.name = "Name3"
        person.save()

        self.assertEqual(person.identifier, 3)
        self.assertEqual(person.name, "Name3")

        person.delete()

        person = mock.Person()
        person.name = "Name4"
        person.save()

        self.assertEqual(person.identifier, 4)
        self.assertEqual(person.name, "Name4")

    def test_sort(self):
        person = mock.Person()
        person.name = "Name"
        person.save()

        other = mock.Person()
        other.name = "NameOther"
        other.save()

        result = mock.Person.find()

        self.assertEqual(result[0].identifier, person.identifier)
        self.assertEqual(result[1].identifier, other.identifier)

        result = mock.Person.find(sort = [("identifier", -1)])

        self.assertEqual(result[0].identifier, other.identifier)
        self.assertEqual(result[1].identifier, person.identifier)

        result = mock.Person.get(sort = [("identifier", -1)])

        self.assertEqual(result.identifier, other.identifier)

    def test_range(self):
        for index in range(10):
            person = mock.Person()
            person.name = "Name%d" % index
            person.save()

        result = mock.Person.find(limit = 5)

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].name, "Name0")

        result = mock.Person.find(skip = 2, limit = 5)

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].name, "Name2")

        result = mock.Person.find(skip = 3, limit = 20)

        self.assertEqual(len(result), 7)
        self.assertEqual(result[0].name, "Name3")

    def test_references(self):
        person = mock.Person()
        person.name = "Name"

        cat = mock.Cat()
        cat.name = "NameCat"
        cat.save()

        person.cats = [cat]
        person.save()

        person = mock.Person.get(identifier = 1)

        self.assertEqual(person.cats[0].name, "NameCat")

        person.cats = mock.Person.cats["type"]([cat])
        person.save()

        person = mock.Person.get(identifier = 1)

        self.assertEqual(person.cats.is_resolved(), False)
        self.assertEqual(person.car, None)
        self.assertEqual(person.cats[0].name, "NameCat")

        person = mock.Person.get(identifier = 1, map = True)

        self.assertEqual(isinstance(person, dict), True)
        self.assertEqual(isinstance(person["cats"], list), True)
        self.assertEqual(isinstance(person["cats"][0], int), True)
        self.assertEqual(len(person["cats"]), 1)

        person = mock.Person.get(identifier = 1, eager = ("cats",))

        self.assertEqual(person.cats.is_resolved(), True)

        person = mock.Person.get(
            identifier = 1,
            map = True,
            eager = ("cats",)
        )

        self.assertEqual(isinstance(person, dict), True)
        self.assertEqual(isinstance(person["cats"], list), True)
        self.assertEqual(isinstance(person["cats"][0], dict), True)

        person = mock.Person.get(identifier = 1)

        person.cats = []
        person.save()

        person = mock.Person.get(identifier = 1)

        self.assertEqual(len(person.cats), 0)

        person = mock.Person.get(map = True, eager = ("cats",))

        self.assertEqual(isinstance(person, dict), True)
        self.assertEqual(isinstance(person["cats"], list), True)
        self.assertEqual(len(person["cats"]), 0)

    def test_eager(self):
        person = mock.Person()
        person.name = "Name"
        person.save()

        car = mock.Car()
        car.name = "Car"
        car.save()

        garage = mock.Garage()
        garage.name = "Garage"
        garage.save()

        address = mock.Address()
        address.street = "Address"
        address.save()

        person = mock.Person.get(identifier = 1, eager_l = True)
        person.car = car
        person.save()

        car = mock.Car.get(identifier = 1, eager_l = True)
        car.garage = garage
        car.save()

        garage = mock.Garage.get(identifier = 1, eager_l = True)
        garage.address = address
        garage.save()

        person = mock.Person.get(identifier = 1, eager_l = True)

        self.assertEqual(isinstance(person.car, appier.Reference), True)
        self.assertEqual(person.car.is_resolved(), True)
        self.assertEqual(person.car.name, "Car")
        self.assertEqual(person.car.garage.is_resolved(), True)
        self.assertEqual(person.car.garage.name, "Garage")
        self.assertEqual(person.car.garage.address.is_resolved(), True)
        self.assertEqual(person.car.garage.address.street, "Address")

        person = mock.Person.get(identifier = 1, eager_l = False)

        self.assertEqual(isinstance(person.car, appier.Reference), True)
        self.assertEqual(person.car.is_resolved(), False)
        self.assertEqual(person.car.name, "Car")
        self.assertEqual(person.car.garage.is_resolved(), False)
        self.assertEqual(person.car.garage.name, "Garage")
        self.assertEqual(person.car.garage.address.is_resolved(), False)
        self.assertEqual(person.car.garage.address.street, "Address")

        person = mock.Person.get(identifier = 1)

        self.assertEqual(isinstance(person.car, appier.Reference), True)
        self.assertEqual(person.car.is_resolved(), False)
        self.assertEqual(person.car.name, "Car")
        self.assertEqual(person.car.garage.is_resolved(), False)
        self.assertEqual(person.car.garage.name, "Garage")
        self.assertEqual(person.car.garage.address.is_resolved(), False)
        self.assertEqual(person.car.garage.address.street, "Address")

        person = mock.Person.get(identifier = 1, map = True)

        self.assertEqual(person["car"]["name"], "Car")
        self.assertEqual(person["car"]["garage"]["name"], "Garage")
        self.assertEqual(person["car"]["garage"]["address"]["street"], "Address")

        person = mock.Person.get(identifier = 1, eager_l = True)

        person.car.name = "CarChanged"
        person.car.save()

        person = mock.Person.get(identifier = 1, eager_l = True)

        self.assertEqual(person.car.name, "CarChanged")

        father = mock.Person()
        father.name = "Father"
        father.save()

        car_father = mock.Car()
        car_father.name = "CarFather"
        car_father.save()

        father.car = car_father
        father.save()

        person.father = father
        person.save()

        person = mock.Person.get(identifier = 1, eager_l = True)

        self.assertEqual(isinstance(person.father, appier.Reference), True)
        self.assertEqual(person.father.is_resolved(), False)
        self.assertEqual(person.car.is_resolved(), True)

        person.father.resolve()

        self.assertEqual(person.car.is_resolved(), True)
        self.assertEqual(person.father.is_resolved(), True)
        self.assertEqual(person.father.car.is_resolved(), False)
        self.assertEqual(person.father.name, "Father")

        person.father.car.resolve()

        self.assertEqual(person.father.car.is_resolved(), True)
        self.assertEqual(person.father.car.name, "CarFather")

    def test_exists(self):
        person = mock.Person()
        person.name = "Name"

        self.assertEqual(person.exists(), False)

        person.save()

        self.assertEqual(person.exists(), True)

        person = mock.Person.get(name = "Name")

        self.assertEqual(person.exists(), True)

        person.delete()

        self.assertEqual(person.exists(), False)

    def test_wrap(self):
        person = mock.Person.wrap(dict(name = "Person"))
        self.assertEqual(person.name, "Person")

        person = mock.Person.wrap(dict(other = "Other"))
        self.assertEqual(person.other, "Other")

    def test_meta(self):
        self.assertEqual(appier.Model._to_meta(str), "string")
        self.assertEqual(appier.Model._to_meta(bool), "bool")
        self.assertEqual(appier.Model._to_meta(list), "list")
        self.assertEqual(appier.Model._to_meta(dict), "map")
        self.assertEqual(appier.Model._to_meta("text"), "text")
        self.assertEqual(appier.Model._to_meta("longtext"), "longtext")
        self.assertEqual(appier.Model._to_meta("longmap"), "longmap")
        self.assertEqual(appier.Model._to_meta(mock.Person.father["type"]), "reference")

    def test_meta_map(self):
        method = appier.model.METAS["map"]

        map = dict(hello = "world")
        result = method(map, {})

        self.assertEqual(type(result), str)
        self.assertEqual(result, "{\"hello\": \"world\"}")

        map = dict(mundo = "olá")

        self.assertEqual(type(result), str)
        self.assertEqual(method(map, {}), "{\"mundo\": \"olá\"}")

    def test_meta_longmap(self):
        method = appier.model.METAS["longmap"]

        map = dict(hello = "world")
        result = method(map, {})

        self.assertEqual(type(result), str)
        self.assertEqual(result, "{\"hello\": \"world\"}")

        map = dict(mundo = "olá")

        self.assertEqual(type(result), str)
        self.assertEqual(method(map, {}), "{\"mundo\": \"olá\"}")
