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

import json
import asyncio

import appier

import aiohttp

class Person(appier.Model):

    identifier = appier.field(
        type = int,
        index = True,
        increment = True,
        default = True
    )

    name = appier.field()

class AsyncHTTPApp(appier.App):

    def __init__(self, *args, **kwargs):
        appier.App.__init__(
            self,
            name = "async_neo",
            *args, **kwargs
        )
        self._register_model(Person)

    @appier.route("/async", "GET")
    @appier.route("/async/request", "GET")
    async def request_(self):
        url = self.field("url", "https://httpbin.bemisc.com/ip")
        size = self.field("size", 4096, cast = int)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                while True:
                    data = await response.content.read(size)
                    if not data: break
                    await self.send(data, content_type = response.content_type)

    @appier.route("/async/sleep", "GET")
    async def sleep_(self):
        sleep = self.field("sleep", 5.0, cast = float)
        await asyncio.sleep(sleep)
        return json.dumps(dict(sleep = sleep))

    @appier.route("/async/list", "GET")
    async def list_(self):
        name = self.field("name", "John Doe")
        persons = await Person.find_a(name = name, map = True)
        return json.dumps(persons)

    @appier.route("/async/create", ("GET", "POST"))
    async def create_(self):
        name = self.field("name", "John Doe")
        person = Person(name = name)
        await person.save_a()
        person = await Person.get_a(name = name, map = True)
        return json.dumps(person)

    @appier.route("/async/read", "GET")
    async def read_(self):
        name = self.field("name", "John Doe")
        person = await Person.get_a(name = name, map = True)
        return json.dumps(person)

    @appier.route("/async/delete", "GET")
    async def delete_(self):
        name = self.field("name", "John Doe")
        persons = await Person.find_a(name = name)
        person_c = len(persons)
        await asyncio.gather(*[person.delete_a() for person in persons])
        return json.dumps(dict(count = person_c))

app = AsyncHTTPApp()
app.serve()
