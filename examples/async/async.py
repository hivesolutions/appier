#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2016 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import netius
import mimetypes
import threading

import appier

class AsyncApp(appier.App):

    def __init__(self, *args, **kwargs):
        appier.App.__init__(
            self,
            name = "async",
            *args, **kwargs
        )

    @appier.route("/async", "GET")
    def async(self):
        yield -1
        yield "before\n"
        yield netius.ensure(self.handler, thread = True)
        yield "after\n"

    @appier.route("/async_file", "GET")
    def async_file(self):
        file_path = self.field("path", None)
        type, _encoding = mimetypes.guess_type(file_path, strict = True)
        type = type or "application/octet-stream"
        self.request.content_type = type
        yield -1
        yield netius.ensure(
            self.read_file,
            args = [file_path],
            thread = True
        )

    @netius.coroutine
    def handler(self, future):
        thread = threading.current_thread()
        print("executing in %s" % thread)
        message = "hello world\n"
        timeout = yield from netius.sleep(3.0)
        message += "timeout: %.2f\n" % timeout
        result = yield from self.calculator(2, 2)
        message += "result: %d\n" % result
        future.set_result(message)

    @netius.coroutine
    def calculator(self, *args, **kwargs):
        thread = threading.current_thread()
        print("executing in %s" % thread)
        print("computing...")
        yield from netius.sleep(3.0)
        print("finished computing...")
        return sum(args)

    @netius.coroutine
    def read_file(self, future, file_path, chunk = 4096, delay = 0):
        count = 0
        file = open(file_path, "rb")
        try:
            while True:
                data = file.read(chunk)
                if not data: break
                count += len(data)
                if delay: yield from netius.sleep(delay)
                yield data
        finally:
            file.close()
        future.set_result(None)
        return count

app = AsyncApp()
app.serve()
