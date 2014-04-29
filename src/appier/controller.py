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

from appier import meta
from appier import legacy
from appier import observer

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
