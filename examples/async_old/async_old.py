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

import appier

class AsyncOldApp(appier.App):

    def __init__(self, *args, **kwargs):
        appier.App.__init__(
            self,
            name = "async_old",
            *args, **kwargs
        )

    @appier.route("/async", "GET")
    def hello(self):
        yield -1
        yield "before\n"
        yield netius.ensure(self.handler)
        yield "after\n"

    @netius.coroutine
    def handler(self, future):
        loop = netius.get_loop()
        message = "hello world\n"
        yield loop.sleep(3.0)
        message += "timeout: %.2f\n" % 3.0
        yield self.calculator(2, 2)
        message += "result: %d\n" % 4
        future.set_result(message)

    @netius.coroutine
    def calculator(self, *args, **kwargs):
        loop = netius.get_loop()
        print("computing...")
        yield loop.sleep(3.0)
        print("finished computing...")

app = AsyncOldApp()
app.serve()
