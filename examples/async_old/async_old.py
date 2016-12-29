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

app = AsyncOldApp()
app.serve()
