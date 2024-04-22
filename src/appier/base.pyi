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

from os import PathLike
from logging import Handler
from typing import Sequence, Type

from .bus import Bus
from .part import Part
from .cache import Cache
from .data import DataAdapter
from .session import Session
from .preferences import Preferences
from .asynchronous import AsyncManager
from .scheduler import SchedulerTask, JobFunction, Cron

class App:
    def __init__(
        self,
        name: str | None = ...,
        locales: Sequence[str] = ...,
        parts: Sequence[Type[Part]] = ...,
        level: str | int | None = ...,
        handlers: Sequence[Handler] | None = ...,
        service: bool = ...,
        safe: bool = ...,
        lazy: bool = ...,
        payload: bool = ...,
        cache_s: int = ...,
        cache_c: Type[Cache] = ...,
        preferences_c: Type[Preferences] = ...,
        bus_c: Type[Bus] = ...,
        session_c: Type[Session] = ...,
        adapter_c: Type[DataAdapter] = ...,
        manager_c: Type[AsyncManager] = ...,
    ): ...
    def start(self, refresh: bool = ...): ...
    def stop(self, refresh: bool = ...): ...
    def serve(
        self,
        server: str = ...,
        host: str = ...,
        port: int = ...,
        ipv6: bool = ...,
        ssl: bool = ...,
        key_file: PathLike[str] | None = ...,
        cer_file: PathLike[str] | None = ...,
        backlog: int = ...,
        threaded: bool = ...,
        conf: bool = ...,
        **kwargs
    ): ...
    def template(
        self,
        template: Template | PathLike[str] | str,
        content_type: str = ...,
        templates_path: PathLike[str] | str | None = ...,
        cache: bool = ...,
        detached: bool = ...,
        locale: str | None = ...,
        asynchronous: bool = ...,
        **kwargs
    ) -> str: ...
    def cron(self, job: JobFunction, cron: Cron) -> SchedulerTask: ...
    def url_for(
        self,
        type: str,
        filename: str | None = ...,
        prefix: str | None = ...,
        query: str | None = ...,
        params: str | None = ...,
        absolute: bool = ...,
        touch: bool = ...,
        session: bool = ...,
        compress: str | None = ...,
        base_url: str | None = ...,
        *args,
        **kwargs
    ) -> str | None: ...
    ...

class APIApp(App): ...
class WebApp(App): ...
class Template: ...

def get_app() -> App: ...
def get_name() -> str | None: ...
def get_base_path() -> PathLike[str] | None: ...
