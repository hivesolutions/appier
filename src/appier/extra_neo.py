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

from . import http
from . import asynchronous

def get_a(*args, **kwargs):
    kwargs["async"] = True
    value = yield from asynchronous.to_coroutine(http.get, *args, **kwargs)
    return value

def post_a(*args, **kwargs):
    kwargs["async"] = True
    value = yield from asynchronous.to_coroutine(http.post, *args, **kwargs)
    return value

def put_a(*args, **kwargs):
    kwargs["async"] = True
    value = yield from asynchronous.to_coroutine(http.put, *args, **kwargs)
    return value

def delete_a(*args, **kwargs):
    kwargs["async"] = True
    value = yield from asynchronous.to_coroutine(http.delete, *args, **kwargs)
    return value

def patch_a(*args, **kwargs):
    kwargs["async"] = True
    value = yield from asynchronous.to_coroutine(http.patch, *args, **kwargs)
    return value

get_w = lambda *args, **kwargs: asynchronous.await_wrap(get_a(*args, **kwargs))
post_w = lambda *args, **kwargs: asynchronous.await_wrap(post_w(*args, **kwargs))
put_w = lambda *args, **kwargs: asynchronous.await_wrap(put_w(*args, **kwargs))
delete_w = lambda *args, **kwargs: asynchronous.await_wrap(delete_w(*args, **kwargs))
patch_w = lambda *args, **kwargs: asynchronous.await_wrap(patch_w(*args, **kwargs))
