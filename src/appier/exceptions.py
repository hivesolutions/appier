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

class AppierException(Exception):
    """
    Top level exception to be used as the root of
    all the exceptions to be raised by the appier infra-
    structure. Should be compatible with http status
    codes for proper http serialization.
    """

    message = None
    """ The message value stored to describe the
    current exception value """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        self.message = kwargs.get("message", "Unknown error")
        self.error_code = kwargs.get("error_code", 500)

class OperationalError(AppierException):
    """
    Error raised for a runtime error and as a result
    of an operational routine that failed.
    This should not be used for coherent development
    bugs, that are raised continuously.
    """

    pass
