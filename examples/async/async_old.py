#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2020 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time
import mimetypes

import appier

class AsyncOldApp(appier.App):

    def __init__(self, *args, **kwargs):
        """
        Initialize the application.

        Args:
            self: (todo): write your description
        """
        appier.App.__init__(
            self,
            name = "async_old",
            *args, **kwargs
        )

    @appier.route("/async", "GET")
    @appier.route("/async/hello", "GET")
    def hello(self):
        """
        A context manager that yields a request body.

        Args:
            self: (todo): write your description
        """
        partial = self.field("partial", True, cast = bool)
        handler = self.handler_partial if partial else self.handler
        for value in appier.header_a(): yield value
        yield "before\n"
        for value in handler(): yield value
        yield "after\n"

    @appier.route("/async/callable", "GET")
    def callable(self):
        """
        Yield all callable callable fields.

        Args:
            self: (todo): write your description
        """
        sleep = self.field("sleep", 3.0, cast = float)
        for value in appier.header_a(): yield value
        yield "before\n"
        for value in appier.ensure_a(lambda: time.sleep(sleep)): yield value
        yield "after\n"

    @appier.route("/async/file", "GET")
    def file(self):
        """
        Yield file contents of file.

        Args:
            self: (todo): write your description
        """
        file_path = self.field("path", None, mandatory = True)
        delay = self.field("delay", 0.0, cast = float)
        thread = self.field("thread", False, cast = bool)
        type, _encoding = mimetypes.guess_type(file_path, strict = True)
        type = type or "application/octet-stream"
        self.request.content_type = type
        for value in appier.header_a(): yield value
        for value in appier.ensure_a(
            self.read_file,
            args = [file_path],
            kwargs = dict(delay = delay),
            thread = thread
        ): yield value

    @appier.route("/async/http", "GET")
    def http(self):
        """
        Yields the http response.

        Args:
            self: (todo): write your description
        """
        url = self.field("url", "https://www.flickr.com/")
        delay = self.field("delay", 0.0, cast = float)
        self.request.content_type = "text/html"
        for value in appier.header_a(): yield value
        for value in appier.sleep(delay): yield value
        for value in appier.get_a(url):
            yield value
            yield value.result()

    @appier.coroutine
    def handler(self):
        """
        Handle a message handler.

        Args:
            self: (todo): write your description
        """
        message = "hello world\n"
        for value in appier.sleep(3.0): yield value
        message += "timeout: %.2f\n" % 3.0
        future = appier.build_future()
        for value in self.calculator(future, 2, 2): yield value
        message += "result: %d\n" % future.result()
        yield message

    @appier.coroutine
    def handler_partial(self):
        """
        Context manager for partial exceptions.

        Args:
            self: (todo): write your description
        """
        yield "hello world\n"
        for value in appier.sleep(3.0): yield value
        yield "timeout: %.2f\n" % 3.0
        result = appier.build_future()
        for value in self.calculator(result, 2, 2): yield value
        yield "result: %d\n" % result.result()

    @appier.coroutine
    def calculator(self, future, *args, **kwargs):
        """
        Calculate the result of the given future.

        Args:
            self: (todo): write your description
            future: (todo): write your description
        """
        print("computing...")
        for value in appier.sleep(3.0): yield value
        print("finished computing...")
        future.set_result(sum(args))

    @appier.coroutine
    def read_file(self, file_path, chunk = 65536, delay = 0.0):
        """
        Read a generator.

        Args:
            self: (str): write your description
            file_path: (str): write your description
            chunk: (str): write your description
            delay: (str): write your description
        """
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

app = AsyncOldApp()
app.serve()
