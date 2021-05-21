#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2021 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2021 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import sys
import logging

from . import util

class Part(object):
    """
    Abstract top level class for the "part" module infra-structure
    should implement the base methods for the proper working of a
    part and raise exception for mandatory methods.

    A part should extend the functionality of an application by adding
    features to it in a "transparent" way.
    """

    def __init__(self, owner = None, *args, **kwargs):
        self.owner = owner
        self.loaded = False
        self._load_paths()
        if owner: self.register(owner)

    def __getattr__(self, name):
        if self.owner and hasattr(self.owner, name):
            return getattr(self.owner, name)
        raise AttributeError("'%s' not found" % name)

    @classmethod
    def _merge_paths(cls, first, second):
        if not isinstance(first, (list, tuple)): first = [first]
        if not isinstance(second, (list, tuple)): second = [second]
        if isinstance(first, tuple): first = list(first)
        if isinstance(second, tuple): second = list(second)
        return first + second

    def name(self):
        cls = self.__class__
        cls_name = cls.__name__
        name = util.camel_to_underscore(cls_name)
        if name.endswith("_part"): name = name[:-5]
        return name

    def version(self):
        return None

    def info(self):
        return dict(
            name = self.name(),
            version = self.version(),
            class_name = self.class_name()
        )

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
        kwargs["templates_path"] = self._merged_paths
        return self.owner.template(*args, **kwargs)

    def is_loaded(self):
        return self.loaded

    @property
    def logger(self):
        if self.owner: return self.owner.logger
        else: return logging.getLogger()

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

    @property
    def _merged_paths(self):
        cls = self.__class__
        return cls._merge_paths(self.owner.templates_path, self.templates_path)
