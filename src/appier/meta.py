#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Appier Framework. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

from appier import common
from appier import legacy

class Ordered(type):
    """
    Metaclass to be used for classes where the
    definition order of its attributes is critical
    for the correct process.
    """

    def __new__(cls, name, bases, attrs):
        new_cls = super(Ordered, cls).__new__(cls, name, bases, attrs)
        new_cls._ordered = [(name, attrs.pop(name)) for name, value in\
            legacy.eager(attrs.items()) if hasattr(value, "creation_counter")]
        new_cls._ordered.sort(key = lambda item: item[1].creation_counter)
        new_cls._ordered = [name for name, value in new_cls._ordered]
        return new_cls

    def __init__(cls, name, bases, attrs):
        super(Ordered, cls).__init__(name, bases, attrs)

class Indexed(type):
    """
    Meta class data type for the indexing of the various route
    oriented methods of a controller, should be able to dynamically
    add such methods to the current running application registry.
    """

    def __new__(cls, name, bases, attrs):
        new_cls = super(Indexed, cls).__new__(cls, name, bases, attrs)
        new_name = new_cls.__name__

        ordered = [(name, attrs.pop(name)) for name, value in\
            legacy.eager(attrs.items()) if hasattr(value, "creation_counter")]
        ordered.sort(key = lambda item: item[1].creation_counter)

        for name, function in ordered:
            is_route = hasattr(function, "_route")
            is_error =  hasattr(function, "_error")
            is_exception =  hasattr(function, "_exception")

            if is_route:
                url, method, async, json = function._route
                function = getattr(new_cls, name)
                common.base().App.add_route(
                    method,
                    url,
                    function,
                    async = async,
                    json = json,
                    context = new_name
                )

            if is_error:
                code, = function._error
                common.base().App.add_error(
                    code,
                    function,
                    context = new_name
                )

            if is_exception:
                exception, = function._exception
                common.base().App.add_exception(
                    exception,
                    function,
                    context = new_name
                )

        return new_cls

    def __init__(cls, name, bases, attrs):
        super(Indexed, cls).__init__(name, bases, attrs)
