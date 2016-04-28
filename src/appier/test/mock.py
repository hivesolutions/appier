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

import appier

class Person(appier.Model):

    identifier = appier.field(
        type = int,
        index = True,
        increment = True,
        default = True
    )

    identifier_safe = appier.field(
        type = int,
        index = True,
        increment = True,
        safe = True
    )

    name = appier.field()

    age = appier.field(
        type = int
    )

    father = appier.field(
        type = appier.reference(
            "Person",
            name = "identifier"
        )
    )

    car = appier.field(
        type = appier.reference(
            "Car",
            name = "identifier"
        ),
        eager = True
    )

    cats = appier.field(
        type = appier.references(
            "Cat",
            name = "identifier"
        )
    )

    @classmethod
    def validate(cls):
        return super(Person, cls).validate() + [
            appier.not_null("name"),
            appier.not_empty("name"),
            appier.not_duplicate("name", cls._name())
        ]

class Cat(appier.Model):

    identifier = appier.field(
        type = int,
        index = True,
        increment = True,
        default = True
    )

    identifier_safe = appier.field(
        type = int,
        index = True,
        increment = True,
        safe = True
    )

    name = appier.field()

class Car(appier.Model):

    identifier = appier.field(
        type = int,
        index = True,
        increment = True,
        default = True
    )

    identifier_safe = appier.field(
        type = int,
        index = True,
        increment = True,
        safe = True
    )

    name = appier.field()

    brand = appier.field()

    variant = appier.field()

    garage = appier.field(
        type = appier.reference(
            "Garage",
            name = "identifier"
        ),
        eager = True
    )

class Garage(appier.Model):

    identifier = appier.field(
        type = int,
        index = True,
        increment = True,
        default = True
    )

    identifier_safe = appier.field(
        type = int,
        index = True,
        increment = True,
        safe = True
    )

    name = appier.field()

    address = appier.field(
        type = appier.reference(
            "Address",
            name = "identifier"
        ),
        eager = True
    )

class Address(appier.Model):

    identifier = appier.field(
        type = int,
        index = True,
        increment = True,
        default = True
    )

    identifier_safe = appier.field(
        type = int,
        index = True,
        increment = True,
        safe = True
    )

    street = appier.field()
