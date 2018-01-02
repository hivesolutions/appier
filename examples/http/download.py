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

import sys

import appier

length = -1
received = 0

def callback_headers(headers):
    global length
    _length = headers.get("content-length", None)
    if _length == None: return
    length = int(_length)

def callback_data(data):
    global received
    if length == -1: return
    received += len(data)
    percent = float(received) / float(length) * 100.0
    sys.stdout.write("%.02f%%\r" % percent)

def callback_result(result):
    sys.stdout.write("\n")

_contents, response = appier.get(
    "https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.14.10.tar.xz",
    handle = True,
    callback_headers = callback_headers,
    callback_data = callback_data,
    callback_result = callback_result
)
