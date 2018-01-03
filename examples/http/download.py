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
import time

import appier

MIN_DELTA = 0.01

BIG_BUCK_URL = "http://download.blender.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_h264.mov"

length = -1
received = 0
percent = 0.0
start = None

url = sys.argv[1] if len(sys.argv) > 1 else BIG_BUCK_URL
name = os.path.basename(appier.legacy.urlparse(url).path)

def callback_headers(headers):
    global length, received, percent, start
    _length = headers.get("content-length", None)
    if _length == None: _length = "-1"
    length = int(_length)
    received = 0
    percent = 0.0
    start = time.time()

def callback_data(data):
    global received, percent
    if length == -1: return
    received += len(data)
    _percent = float(received) / float(length) * 100.0
    if _percent - percent < MIN_DELTA: return
    percent = _percent
    output()

def callback_result(result):
    percent = 100.0
    output()
    sys.stdout.write("\n")

def output():
    delta = time.time() - start
    speed = float(received) / float(delta) / (1024 * 1024)
    sys.stdout.write("\r[%s] %.02f%% %.02fMB/s" % (name, percent, speed))

def copy(input, name, buffer_size = 16384):
    output = open(name, "wb")
    try:
        while True:
            data = input.read(buffer_size)
            if not data: break
            output.write(data)
    finally:
        output.close()

contents, _response = appier.get(
    url,
    handle = True,
    retry = 0,
    use_file = True,
    callback_headers = callback_headers,
    callback_data = callback_data,
    callback_result = callback_result
)

try: copy(contents, name)
finally: contents.close()
