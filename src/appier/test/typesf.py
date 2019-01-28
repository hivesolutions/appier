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

import calendar
import unittest
import datetime

import appier

from . import mock

class TypesfTest(unittest.TestCase):

    def setUp(self):
        self.app = appier.App()
        self.app._register_models_m(mock, "Mocks")

    def tearDown(self):
        self.app.unload()
        adapter = appier.get_adapter()
        adapter.drop_db()

    def test_reference(self):
        person = mock.Person()
        person.name = "Name"
        person.car = mock.Person.car["type"]("")

        self.assertEqual(person.car, None)
        self.assertEqual(person.car, mock.Person.car["type"](""))
        self.assertEqual(person.car, mock.Person.car["type"](b""))
        self.assertEqual(person.car, mock.Person.car["type"](None))
        self.assertNotEqual(person.car, mock.Person.father["type"](1))
        self.assertNotEqual(person.car, mock.Person.car["type"](1))
        self.assertNotEqual(person.car, "car")
        self.assertEqual(isinstance(person.car, appier.Reference), True)
        self.assertEqual(len(person.car), 0)

        person = mock.Person()
        person.name = "Name"
        person.car = mock.Person.car["type"](b"")

        self.assertEqual(person.car, None)
        self.assertEqual(person.car, mock.Person.car["type"](""))
        self.assertEqual(person.car, mock.Person.car["type"](b""))
        self.assertEqual(person.car, mock.Person.car["type"](None))
        self.assertNotEqual(person.car, mock.Person.father["type"](1))
        self.assertNotEqual(person.car, mock.Person.car["type"](1))
        self.assertNotEqual(person.car, "car")
        self.assertEqual(isinstance(person.car, appier.Reference), True)
        self.assertEqual(len(person.car), 0)

        person = mock.Person()
        person.name = "Name"
        person.car = mock.Person.car["type"](None)

        self.assertEqual(person.car, None)
        self.assertEqual(person.car, mock.Person.car["type"](""))
        self.assertEqual(person.car, mock.Person.car["type"](b""))
        self.assertEqual(person.car, mock.Person.car["type"](None))
        self.assertNotEqual(person.car, mock.Person.father["type"](1))
        self.assertNotEqual(person.car, mock.Person.car["type"](1))
        self.assertNotEqual(person.car, "car")
        self.assertEqual(isinstance(person.car, appier.Reference), True)
        self.assertEqual(len(person.car), 0)

        person = mock.Person()
        person.name = "Name"
        person.car = mock.Person.car["type"](1)

        self.assertEqual(person.car, mock.Person.car["type"](1))
        self.assertNotEqual(person.car, None)
        self.assertNotEqual(person.car, mock.Person.car["type"](""))
        self.assertNotEqual(person.car, mock.Person.car["type"](b""))
        self.assertNotEqual(person.car, mock.Person.car["type"](None))
        self.assertNotEqual(person.car, mock.Person.father["type"](1))
        self.assertNotEqual(person.car, "car")
        self.assertEqual(isinstance(person.car, appier.Reference), True)
        self.assertEqual(len(person.car), 1)

    def test_references(self):
        person = mock.Person()
        person.name = "Name"
        person.cats = mock.Person.cats["type"]([1, 2, 3])

        self.assertEqual(mock.Cat(identifier = 1) in person.cats, True)
        self.assertEqual(mock.Cat(identifier = 3) in person.cats, True)
        self.assertNotEqual(mock.Cat(identifier = 4) in person.cats, True)
        self.assertNotEqual(person.cats, None)
        self.assertNotEqual(person.cats, [])
        self.assertNotEqual(person.cats, "cars")
        self.assertEqual(isinstance(person.cats, appier.References), True)
        self.assertEqual(len(person.cats), 3)

    def test_file(self):
        file_m = dict(name = "hello", data = b"SGVsbG8gV29ybGQ=")
        file = appier.File(file_m)

        self.assertEqual(type(file.file_name), str)
        self.assertEqual(type(file.data_b64), str)
        self.assertEqual(type(file.data), appier.legacy.BYTES)
        self.assertEqual(file.file_name, "hello")
        self.assertEqual(file.data, b"Hello World")
        self.assertEqual(file.data_b64, "SGVsbG8gV29ybGQ=")

        file_d = b"Hello World"
        file = appier.File(file_d)

        self.assertEqual(type(file.file_name), str)
        self.assertEqual(type(file.data_b64), str)
        self.assertEqual(type(file.data), appier.legacy.BYTES)
        self.assertEqual(file.file_name, "default")
        self.assertEqual(file.data, b"Hello World")
        self.assertEqual(file.data_b64, "SGVsbG8gV29ybGQ=")

    def test_encrypted(self):
        encrypted = appier.encrypted(key = b"hello key")
        result = encrypted("hello world")

        self.assertEqual(str(result), "hello world")
        self.assertEqual(result.value, "hello world")
        self.assertEqual(result.encrypted, "vGgMtFgyMVwH3uE=:encrypted")

        result = encrypted("vGgMtFgyMVwH3uE=:encrypted")

        self.assertEqual(str(result), "hello world")
        self.assertEqual(result.value, "hello world")
        self.assertEqual(result.encrypted, "vGgMtFgyMVwH3uE=:encrypted")

        encrypted = appier.encrypted(key = None)
        result = encrypted("hello world")

        self.assertEqual(str(result), "hello world")
        self.assertEqual(result.value, "hello world")
        self.assertEqual(result.value, "hello world")

        result = encrypted("vGgMtFgyMVwH3uE=:encrypted")

        self.assertEqual(str(result), "vGgMtFgyMVwH3uE=:encrypted")
        self.assertEqual(result.value, "vGgMtFgyMVwH3uE=:encrypted")
        self.assertEqual(result.encrypted, "vGgMtFgyMVwH3uE=:encrypted")

    def test_dumpall(self):
        person = mock.Person()
        person.name = "Name"
        person.save()

        car = mock.Car()
        car.name = "Car"
        car.save()

        father = mock.Person()
        father.name = "Father"
        father.save()

        brother = mock.Person()
        brother.name = "Brother"
        brother.save()

        person.car = car
        person.father = father
        person.brother = brother
        person.save()

        person = mock.Person.get(identifier = 1)

        result = person.json_v()

        self.assertEqual(type(result), dict)
        self.assertEqual(result["name"], "Name")

        result = person.car.json_v()

        self.assertEqual(type(result), int)
        self.assertEqual(result, 1)

        result = person.father.json_v()

        self.assertEqual(type(result), mock.Person)
        self.assertEqual(result.name, "Father")

        result = person.brother.json_v()

        self.assertEqual(type(result), int)
        self.assertEqual(result, 3)

    def test_custom(self):

        class DateTime(appier.Type):

            def loads(self, value):
                cls = self.__class__
                if isinstance(value, cls):
                    self._datetime = value._datetime
                elif isinstance(value, datetime.datetime):
                    self._datetime = value
                elif isinstance(value, (int, float)):
                    self._datetime = datetime.datetime.utcfromtimestamp(value)
                else:
                    raise appier.OperationalError()

            def dumps(self):
                return self.timestamp()

            def timestamp(self):
                return calendar.timegm(self._datetime.utctimetuple())

        class CustomPerson(mock.Person):

            birth = appier.field(
                type = DateTime
            )

        self.app._register_model(CustomPerson)

        person = CustomPerson()
        person.name = "Name"
        person.birth = DateTime(0)
        person.save()

        self.assertEqual(person.name, "Name")
        self.assertEqual(type(person.birth), DateTime)
        self.assertEqual(person.birth.timestamp(), 0)

        person = CustomPerson.get(name = "Name")

        self.assertEqual(person.name, "Name")
        self.assertEqual(type(person.birth), DateTime)
        self.assertEqual(person.birth.timestamp(), 0)

        person = CustomPerson(name = "New Name", birth = 1)
        person.save()

        self.assertEqual(person.name, "New Name")
        self.assertEqual(type(person.birth), DateTime)
        self.assertEqual(person.birth.timestamp(), 1)

        person = CustomPerson.get(birth = 1)

        self.assertEqual(person.name, "New Name")
        self.assertEqual(type(person.birth), DateTime)
        self.assertEqual(person.birth.timestamp(), 1)
