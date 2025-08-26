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

import appier

from models.user import User


class UserController(appier.Controller):
    @appier.route("/users", "GET", json=True)
    def list(self):
        object = appier.get_object(alias=True, find=True)
        users = User.find(**object)
        return users

    @appier.route("/users/populate", ("GET", "POST"), json=True)
    def populate(self):
        users = User.populate()
        return users

    @appier.route("/users/<str:email>", "GET", json=True)
    def show(self, email):
        users = User.find_by_email(email=email, map=True)
        return users
