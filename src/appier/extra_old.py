#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from . import http
from . import asynchronous

def get_a(*args, **kwargs):
    kwargs["async"] = True
    for value in asynchronous.to_coroutine(http.get, *args, **kwargs): yield value

def post_a(*args, **kwargs):
    kwargs["async"] = True
    for value in asynchronous.to_coroutine(http.post, *args, **kwargs): yield value

def put_a(*args, **kwargs):
    kwargs["async"] = True
    for value in asynchronous.to_coroutine(http.put, *args, **kwargs): yield value

def delete_a(*args, **kwargs):
    kwargs["async"] = True
    for value in asynchronous.to_coroutine(http.delete, *args, **kwargs): yield value

def patch_a(*args, **kwargs):
    kwargs["async"] = True
    for value in asynchronous.to_coroutine(http.patch, *args, **kwargs): yield value

get_w = None
post_w = None
put_w = None
delete_w = None
patch_w = None
