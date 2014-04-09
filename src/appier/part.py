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

import re

class Part(object):
    """
    Abstract top level class for the "part" module infra-structure
    should implement the base method for the proper working of a
    part and raise exception for mandatory methods.
    """

    def routes(self):
        return []

class CaptchaPart(Part):
    """
    Modular part class that provides the required infra-structure
    for the generation and management of a captcha image.

    Should be used with proper knowledge of the inner workings of
    the captcha mechanism to avoid any security problems.

    @see: http://en.wikipedia.org/wiki/CAPTCHA
    """

    def routes(self):
        return [
            (("GET",), re.compile("^/captcha/image$"), self.image)
        ]

    def image(self):
        return ""

    def generate(self, value, width = 300, height = 50, letter_count = 5):
        pass

