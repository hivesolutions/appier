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

import time
import mimetypes

import appier

class AsyncOldApp(appier.App):

    def __init__(self, *args, **kwargs):
        appier.App.__init__(
            self,
            name = "async_old",
            *args, **kwargs
        )

    @appier.route("/async", "GET")
    @appier.route("/async/hello", "GET")
    def hello(self):
        yield -1
        yield "before\n"
        yield appier.ensure_async(self.handler)
        yield "after\n"

    @appier.route("/async/callable", "GET")
    def callable(self):
        yield -1
        yield "before\n"
        yield appier.ensure_async(lambda: time.sleep(30.0))
        yield "after\n"

    @appier.route("/async/file", "GET")
    def file(self):
        file_path = self.field("path", None)
        delay = self.field("delay", 0, cast = int)
        thread = self.field("thread", False, cast = bool)
        type, _encoding = mimetypes.guess_type(file_path, strict = True)
        type = type or "application/octet-stream"
        self.request.content_type = type
        yield -1
        yield appier.ensure_async(
            self.read_file,
            args = [file_path],
            kwargs = dict(delay = delay),
            thread = thread
        )

    @appier.route("/async/http", "GET")
    def http(self):
        url = self.field("url", "https://www.flickr.com/")
        self.request.content_type = "text/html"
        yield -1
        for value in appier.get_a(appier.get, url): yield value

    @appier.coroutine
    def handler(self, future):
        message = "hello world\n"
        for value in appier.sleep(3.0): yield value
        message += "timeout: %.2f\n" % 3.0
        result = appier.Future()
        for value in self.calculator(result, 2, 2): yield value
        message += "result: %d\n" % result.result()
        future.set_result(message)

    @appier.coroutine
    def calculator(self, future, *args, **kwargs):
        print("computing...")
        for value in appier.sleep(3.0): yield value
        print("finished computing...")
        future.set_result(sum(args))

    @appier.coroutine
    def read_file(self, future, file_path, chunk = 65536, delay = 0):
        count = 0
        file = open(file_path, "rb")
        try:
            while True:
                data = file.read(chunk)
                if not data: break
                count += len(data)
                if delay:
                    for value in appier.sleep(delay): yield value
                yield data
        finally:
            file.close()
        future.set_result(count)

app = AsyncOldApp()
app.serve()
