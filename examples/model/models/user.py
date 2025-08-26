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
# MERCHANTABILITY or FITNESS FOR ANY PARTICULAR PURPOSE. See the
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

import time

import appier


class User(appier.Model):
    name = appier.field(
        index=True, required=True, meta="text", description="The full name of the user"
    )

    email = appier.field(
        index=True,
        required=True,
        unique=True,
        meta="text",
        description="The email address of the user",
    )

    age = appier.field(
        type=int, index=True, required=False, description="The age of the user"
    )

    is_active = appier.field(
        type=bool,
        default=True,
        index=True,
        description="Whether the user account is active",
    )

    created = appier.field(
        type=float, index=True, description="Timestamp when the user was created"
    )

    updated = appier.field(
        type=float, index=True, description="Timestamp when the user was last updated"
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<User: %s (%s)>" % (self.name, self.email)

    @classmethod
    def find_by_email(cls, email, **kwargs):
        return cls.get(email=email, **kwargs)

    @classmethod
    def find_active_users(cls, **kwargs):
        return cls.find(is_active=True, **kwargs)

    @classmethod
    def find_users_by_age_range(cls, min_age, max_age, **kwargs):
        return cls.find(age={"$gte": min_age, "$lte": max_age}, **kwargs)

    @classmethod
    def populate(cls):
        for i in range(10):
            user = User(name=f"User {i}", email=f"user{i}@example.com", age=i)
            user.save()

    def pre_create(self):
        self.created = time.time()
        self.updated = time.time()

    def pre_save(self):
        self.updated = time.time()

    def to_dict(self):
        return {
            "id": str(self._id),
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "is_active": self.is_active,
            "created": self.created,
            "updated": self.updated,
        }
