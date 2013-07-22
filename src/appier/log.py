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

import logging

LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
""" The format to be used for the logging operation in
the app, these operations are going to be handled by
multiple stream handlers """

class MemoryHandler(logging.Handler):

    MAX_LENGTH = 1000
    """ The maximum amount of messages that are kept in
    memory until they are discarded, avoid a very large
    number for this value or else a large amount of memory
    may be used for logging purposes """

    def __init__(self, level = logging.NOTSET):
        logging.Handler.__init__(self, level = level)
        self.messages = []

        formatter = logging.Formatter(LOGGING_FORMAT)
        self.setFormatter(formatter)

    def emit(self, record):
        message = self.format(record)
        self.messages.insert(0, message)
        messages_l = len(self.messages)
        if messages_l > MemoryHandler.MAX_LENGTH:
            self.messages.pop()

    def get_latest(self, count = 100):
        return self.messages[:count]
