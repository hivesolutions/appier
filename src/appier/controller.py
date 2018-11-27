#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2018 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import meta
from . import legacy
from . import observer

class Controller(legacy.with_meta(meta.Indexed, observer.Observable)):
    """
    Top level abstract controller class from which all the
    concrete controller should inherit. Should provide structure
    for the creation of part of code that may act as entry levels
    for the business logic, these methods should be called action
    methods and may be implemented in the controller or application.

    Most of the controller logic is a simple redirection to the owner
    object that should be an application.
    """

    def __init__(self, owner, *args, **kwargs):
        observer.Observable.__init__(self, *args, **kwargs)
        self.owner = owner

    def __getattr__(self, name):
        if hasattr(self.owner, name):
            return getattr(self.owner, name)
        raise AttributeError("'%s' not found" % name)

    def register(self, lazy = False):
        if lazy: return
        self.setup()

    def unregister(self, lazy = False):
        if lazy: return
        self.teardown()

    def setup(self):
        pass

    def teardown(self):
        pass
