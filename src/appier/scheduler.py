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

import datetime
import logging
import threading
import traceback

from . import config

LOOP_TIMEOUT = 60.0
""" The time value to be used to sleep the main sequence
loop between ticks, this value should not be too small
to spend many resources or to high to create a long set
of time between external interactions """


class Scheduler(threading.Thread):
    """
    Scheduler class that handles timeout based async tasks
    within the context of an Appier application.

    The architecture of the logic for the class should be
    modular in the sense that new task may be added to
    it through a queue or other external system. For that
    a proper preemption mechanism should exist allowing
    the scheduler to be stopped and started again.
    """

    def __init__(self, owner, timeout=LOOP_TIMEOUT, daemon=True):
        threading.Thread.__init__(self, name="Scheduler")
        self.owner = owner
        self.timeout = config.conf("SCHEDULER_TIMEOUT", timeout, cast=float)
        self.daemon = config.conf("SCHEDULER_DAEMON", daemon, cast=bool)
        self._condition = threading.Condition()

    def run(self):
        self.running = True
        self.load()
        while self.running:
            try:
                self.tick()
            except Exception as exception:
                self.logger.critical("Unhandled scheduler exception raised")
                self.logger.error(exception)
                lines = traceback.format_exc().splitlines()
                for line in lines:
                    self.logger.warning(line)
            self._condition.acquire()
            self._condition.wait(self.timeout)
            self._condition.release()

    def stop(self):
        self.running = False

    def tick(self):
        pass

    def load(self):
        pass

    def awake(self):
        self._condition.acquire()
        self._condition.notify()
        self._condition.release()

    @property
    def logger(self):
        if self.owner:
            return self.owner.logger
        else:
            return logging.getLogger()


class CronScheduler(Scheduler):
    """
    Specialized version of the scheduler that runs tasks
    based on a cron like configuration.

    The tasks are defined in a cron like format and are
    executed based on the current time.
    """

    def __init__(self, owner, timeout=LOOP_TIMEOUT, daemon=True):
        Scheduler.__init__(owner, timeout=timeout, daemon=daemon)
        self._tasks = []

    def schedule(self, task, cron):
        pass


class SchedulerDate(object):

    def __init__(
        self, minutes="*", hours="*", days_of_month="*", months="*", days_of_week="*"
    ):
        self.minutes = self._parse_field(minutes, 0, 59)
        self.hours = self._parse_field(hours, 0, 23)
        self.days_of_month = self._parse_field(days_of_month, 1, 31)
        self.months = self._parse_field(months, 1, 12)
        self.days_of_week = self._parse_field(days_of_week, 0, 6)

    @classmethod
    def from_cron(cls, cron):
        values = (value.strip().split(",") for value in cron.split(" "))
        return cls(*values)

    def next_timestamp(self):
        pass

    def next_run(self, now=None):
        """
        Calculate the next run time starting from the current time.
        This operation is done respecting Cron rules.

        :type now: datetime
        :param now: Optional date time to be used as the current time.
        :rtype: datetime
        :return: The next run time respecting Cron rules.
        """

        now = now or datetime.datetime.now()
        now_day = datetime.datetime(now.year, now.month, now.day)
        now_hour = datetime.datetime(now.year, now.month, now.day, hour=now.hour)
        now_minute = datetime.datetime(
            now.year, now.month, now.day, hour=now.hour, minute=now.minute
        )

        year = now.year

        while True:
            for month in sorted(self.months):
                if month < now.month and year < now.year:
                    continue

                for day in sorted(self.days_of_month):
                    try:
                        date = datetime.datetime(year, month, day)
                    except ValueError:
                        continue
                    if self.days_of_week and date.weekday() not in self.days_of_week:
                        continue
                    if date < now_day:
                        continue

                    for hour in sorted(self.hours):
                        if date.replace(hour=hour) < now_hour:
                            continue

                        for minute in sorted(self.minutes):
                            _date = date.replace(
                                hour=hour, minute=minute, second=0, microsecond=0
                            )
                            if _date > now_minute:
                                return _date

            year += 1

    def _find_next_valid(self, current, valid_values):
        for value in sorted(valid_values):
            if value >= current:
                return value
        return sorted(valid_values)[0]

    def _parse_field(self, field, min_value, max_value):
        if field in ("*", ["*"], ("*",)):
            return set(range(min_value, max_value + 1))
        elif isinstance(field, (list, tuple)):
            return set(int(v) for v in field)
        else:
            return set((int(field),))
