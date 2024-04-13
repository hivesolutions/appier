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

from datetime import datetime
from logging import Logger
from threading import Thread
from typing import Callable

from .base import App

LOOP_TIMEOUT: float = ...

JobFunction = Callable[[], None]
CronField = str | int | list | tuple

class Scheduler(Thread):
    owner: App | None
    timeout: float
    daemon: bool

    def __init__(self, owner: App | None, timeout: float = ..., daemon: bool = ...): ...
    def run(self): ...
    def stop(self): ...
    def tick(self): ...
    def load(self): ...
    def awake(self): ...
    @property
    def logger(self) -> Logger: ...

class CronScheduler(Scheduler):
    def __init__(self, owner: App | None, timeout: float = ..., daemon: bool = ...): ...
    def tick(self, now_ts: float | None = ...): ...
    def schedule(
        self, job: JobFunction, cron: str, now: datetime | None = ...
    ) -> SchedulerTask: ...

class SchedulerTask(object):
    job: JobFunction
    date: SchedulerDate

    def __init__(self, job: JobFunction, cron: str): ...
    def enable(self): ...
    def disable(self): ...
    def next_timestamp(self, now: datetime | None = ...) -> float: ...
    @property
    def enabled(self) -> bool: ...

class SchedulerDate(object):
    minutes: set[int]
    hours: set[int]
    days_of_month: set[int]
    months: set[int]
    days_of_week: set[int]

    def __init__(
        self,
        minutes: CronField = ...,
        hours: CronField = ...,
        days_of_month: CronField = ...,
        months: CronField = ...,
        days_of_week: CronField = ...,
    ): ...
    @classmethod
    def from_cron(cls, cron: str) -> SchedulerDate: ...
    def next_timestamp(self, now: datetime | None = None) -> float: ...
    def next_run(self, now: datetime | None = None) -> datetime: ...
    def _parse_field(
        self, field: CronField, min_value: int, max_value: int
    ) -> set[int]: ...
