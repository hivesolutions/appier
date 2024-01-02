#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2024 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time
import mimetypes

import appier


class AsyncNeoApp(appier.App):
    def __init__(self, *args, **kwargs):
        appier.App.__init__(self, name="async_neo", *args, **kwargs)

    @appier.route("/async", "GET")
    @appier.route("/async/hello", "GET")
    async def hello(self):
        partial = self.field("partial", True, cast=bool)
        handler = self.handler_partial if partial else self.handler
        yield "before\n"
        await handler()
        yield "after\n"

    @appier.route("/async/sender", "GET")
    async def sender(self):
        import asyncio

        sleep = self.field("sleep", 1.0, cast=float)
        self.request.set_content_type("text/plain")
        await asyncio.sleep(sleep)
        await self.request.send(b"Sender (1)\n")
        await asyncio.sleep(sleep)
        await self.request.send(b"Sender (2)\n")
        await asyncio.sleep(sleep)
        await self.request.send(b"Sender (3)\n")

    @appier.route("/async/callable", "GET")
    async def callable(self):
        sleep = self.field("sleep", 3.0, cast=float)
        yield "before\n"
        await appier.ensure_a(lambda: time.sleep(sleep))
        yield "after\n"

    @appier.route("/async/file", "GET")
    async def file(self):
        file_path = self.field("path", None, mandatory=True)
        delay = self.field("delay", 0.0, cast=float)
        thread = self.field("thread", False, cast=bool)
        type, _encoding = mimetypes.guess_type(file_path, strict=True)
        type = type or "application/octet-stream"
        self.request.content_type = type
        await appier.ensure_a(
            self.read_file, args=[file_path], kwargs=dict(delay=delay), thread=thread
        )

    @appier.route("/async/http", "GET")
    async def http(self):
        url = self.field("url", "https://www.flickr.com/")
        delay = self.field("delay", 0.0, cast=float)
        self.request.content_type = "text/html"
        await appier.sleep(delay)
        yield await appier.get_w(url)

    async def handler(self):
        message = "hello world\n"
        timeout = await appier.sleep(3.0)
        message += "timeout: %.2f\n" % timeout
        result = await self.calculator(2, 2)
        message += "result: %d\n" % result
        await appier.await_yield("hello world\n")

    async def handler_partial(self):
        await appier.await_yield("hello world\n")
        timeout = await appier.sleep(3.0)
        await appier.await_yield("timeout: %.2f\n" % timeout)
        result = await self.calculator(2, 2)
        await appier.await_yield("result: %d\n" % result)

    async def calculator(self, *args, **kwargs):
        print("computing...")
        await appier.sleep(3.0)
        print("finished computing...")
        return sum(args)

    async def read_file(self, file_path, chunk=65536, delay=0.0):
        count = 0
        file = open(file_path, "rb")
        try:
            while True:
                data = file.read(chunk)
                if not data:
                    break
                count += len(data)
                if delay:
                    await appier.sleep(delay)
                await appier.await_yield(data)
        finally:
            file.close()
        return count


app = AsyncNeoApp()
app.serve()
