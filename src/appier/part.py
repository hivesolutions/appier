#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2017 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import sys

from . import util

class Part(object):
    """
    Abstract top level class for the "part" module infra-structure
    should implement the base method for the proper working of a
    part and raise exception for mandatory methods.
    """

    def __init__(self, owner = None):
        self.owner = owner
        self.loaded = False
        self._load_paths()
        if owner: self.register(owner)

    def __getattr__(self, name):
        if self.owner and hasattr(self.owner, name):
            return getattr(self.owner, name)
        raise AttributeError("'%s' not found" % name)

    def name(self):
        cls = self.__class__
        cls_name = cls.__name__
        name = util.camel_to_underscore(cls_name)
        if name.endswith("_part"): name = name[:-5]
        return name

    def class_name(self):
        cls = self.__class__
        if not self.__module__: return cls.__name__
        return self.__module__ + "." + cls.__name__

    def register(self, owner):
        self.owner = owner

    def load(self):
        self.loaded = True

    def unload(self):
        self.loaded = False

    def routes(self):
        return []

    def models(self):
        return None

    def template(self, *args, **kwargs):
        kwargs["cache"] = False
        kwargs["templates_path"] = self.templates_path
        return self.owner.template(*args, **kwargs)

    def is_loaded(self):
        return self.loaded

    def _load_paths(self):
        module = self.__class__.__module__
        module = sys.modules[module]
        self.base_path = os.path.dirname(module.__file__)
        self.root_path = os.path.join(self.base_path, "..")
        self.root_path = os.path.abspath(self.root_path)
        self.root_path = os.path.normpath(self.root_path)
        self.static_path = os.path.join(self.base_path, "static")
        self.controllers_path = os.path.join(self.base_path, "controllers")
        self.models_path = os.path.join(self.base_path, "models")
        self.templates_path = os.path.join(self.base_path, "templates")
        self.bundles_path = os.path.join(self.base_path, "bundles")
