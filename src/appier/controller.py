#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2012 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

class Controller(object):

    def __init__(self, owner, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.owner = owner

    def __getattr__(self, name):
        if hasattr(self.owner, name):
            return getattr(self.owner, name)
        raise AttributeError("'%s' not found" % name)

    def redirect(self, *args, **kwargs):
        return self.owner.redirect(*args, **kwargs)

    def template(self, *args, **kwargs):
        return self.owner.template(*args, **kwargs)

    def content_type(self, *args, **kwargs):
        return self.owner.content_type(*args, **kwargs)

    def field(self, *args, **kwargs):
        return self.owner.field(*args, **kwargs)

    def get_field(self, *args, **kwargs):
        return self.owner.get_field(*args, **kwargs)

    def get_request(self):
        return self.owner.get_request()

    def url_for(self, *args, **kwargs):
        return self.owner.url_for(*args, **kwargs)
