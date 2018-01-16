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

from . import util
from . import common

class Component(object):
    """
    Top level component class to be used as an abstract definition
    of a loadable/unloadable component of the system.

    This provides a strict (yet simple) set of rules to how such
    component should behave and the life-cycle stages for it.
    """

    def __init__(self, name = "component", owner = None, *args, **kwargs):
        object.__init__(self)
        self.id = util.gen_token()
        self.name = name
        self.owner = owner or common.base().APP
        self.loaded = False

    def load(self, *args, **kwargs):
        self._load(*args, **kwargs)
        return self

    def unload(self, *args, **kwargs):
        self._unload(*args, **kwargs)
        return self

    @property
    def is_loaded(self):
        return self.loaded

    def _load(self, *args, **kwargs):
        self.loaded = True

    def _unload(self, *args, **kwargs):
        self.owner = None
        self.loaded = False
