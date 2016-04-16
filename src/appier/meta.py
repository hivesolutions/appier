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

from . import common
from . import legacy

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

    def __cmp__(self, value):
        return cmp(self.__name__, value.__name__) #@UndefinedVariable

    def __lt__(self, value):
        return self.__name__.__lt__(value.__name__)

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

        # in case there's no ordered related values there's nothing remaining
        # to be done under this class creation and so the created class must
        # be returned immediately to the caller method
        if not ordered: return new_cls

        # retrieves the reference to the current global application instance
        # and verifies if the global (cache) base registered value is defined
        # in case it's not defines it as it's going to be used to avoid the
        # duplicated registration of routes
        app = common.base().App
        if not hasattr(app, "_BASE_REGISTERED"): app._BASE_REGISTERED = []
        registered = app._BASE_REGISTERED

        # iterates over the complete set of ordered elements to be able to
        # register the associated elements for each of the ordered functions
        for name, function in ordered:
            # retrieves the complete set of sequence attributes for the function
            # to be able to register each of them properly
            routes = function._routes if hasattr(function, "_routes") else []
            errors = function._errors if hasattr(function, "_errors") else []
            exceptions = function._exceptions if hasattr(function, "_exceptions") else []
            customs = function._customs if hasattr(function, "_customs") else []

            # iterates over the complete set of routes associated with the current
            # function to be able to add the route to the application
            for route in routes:
                # unpacks the route into each components to process them and then
                # retrieves the method reference associated with the function, this
                # is required as the current reference is just an unbound function
                # and the bound method is required for registration
                url, method, async, json = route
                function = getattr(new_cls, name)

                # creates the tuple that identifies the route as a set
                # of method plus url regex validation and verifies if
                # it's already contained in the registered routes, in case
                # that's the situation continues the loop to be able to
                # avoid duplicated route registration (possible with imports)
                route_t = (method, url)
                if route_t in registered: continue
                registered.append(route_t)

                # adds the new route to the application using the provided/unpacked
                # values to define it properly as expected by specification
                app.add_route(
                    method,
                    url,
                    function,
                    async = async,
                    json = json,
                    context = new_name
                )

            for error in errors:
                code, scope, json = error
                app.add_error(
                    code,
                    function,
                    scope = scope,
                    json = json,
                    context = new_name
                )

            for exception in exceptions:
                exception, scope, json = exception
                app.add_exception(
                    exception,
                    function,
                    scope = scope,
                    json = json,
                    context = new_name
                )

            for custom in customs:
                key, = custom
                app.add_custom(
                    key,
                    function,
                    context = new_name
                )

        return new_cls

    def __init__(cls, name, bases, attrs):
        super(Indexed, cls).__init__(name, bases, attrs)
