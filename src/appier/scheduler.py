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

"""appier.scheduler

Lightweight job scheduler for periodic tasks inside an Appier app.
Wraps Python's `threading.Timer` / `sched` to run functions at given
intervals with minimal overhead. Powers cache refresh routines and
background clean-up jobs without external dependencies.
"""

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time
import uuid
import heapq
import datetime
import logging
import threading
import traceback

from . import config
from . import legacy

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

    def stop(self, awake=True):
        self.running = False
        if awake:
            self.awake()

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
        Scheduler.__init__(self, owner, timeout=timeout, daemon=daemon)
        self._tasks = []

    def tick(self, now_ts=None):
        current_ts = lambda: now_ts if now_ts else time.time()
        current_dt = lambda: (
            legacy.to_datetime(now_ts) if now_ts else legacy.utc_now()
        )

        timestamp = current_ts() + 5.0

        while True:
            if not self._tasks:
                break

            timestamp, task = self._tasks[0]
            if timestamp > current_ts():
                break

            heapq.heappop(self._tasks)

            if task.enabled:
                task.job()
                heapq.heappush(
                    self._tasks, (task.next_timestamp(now=current_dt()), task)
                )

        self.timeout = max(0, timestamp - current_ts())

    def schedule(self, job, cron, id=None, description=None, now=None):
        """
        Schedules the provided job function for execution according
        to the provided cron string.

        The optional now parameter may be used to provide the current
        time reference for the scheduling operation, meaning that the next
        timestamp will be calculated using this value as reference.

        :type job: Function
        :param job: The function to be executed as the job.
        :type cron: String/SchedulerDate
        :param cron: The cron like string defining the schedule.
        :type id: String
        :param id: The unique identifier for the task to be created.
        :type description: String
        :param description: The description for the task to be created
        that describes the goal of the task.
        :type now: datetime
        :param now: Optional time reference for the job scheduling.
        :rtype: SchedulerTask
        :return: The task object that was created for the job.
        """

        task = SchedulerTask(job, cron, id=id, description=description)
        heapq.heappush(self._tasks, (task.next_timestamp(now=now), task))
        self.awake()
        return task

    def next_run(self):
        timestamp = self.next_timestamp()
        if not timestamp:
            return None
        return legacy.to_datetime(timestamp)

    def next_timestamp(self):
        if not self._tasks:
            return None
        return self._tasks[0][0]


class SchedulerTask(object):

    def __init__(self, job, cron, id=None, description=None):
        self.job = job
        self.date = SchedulerDate.from_cron(cron)
        self.id = str(uuid.uuid4()) if id == None else id
        self.description = description
        self._enabled = True

    def __repr__(self):
        return "<SchedulerTask: [%s] %s, %s>" % (self.id[:-12], self.job, self.date)

    def __str__(self):
        return "<SchedulerTask: [%s] %s, %s>" % (self.id[:-12], self.job, self.date)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True
        return False

    def __lt__(self, other):
        return False

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def next_run(self, now=None):
        return self.date.next_run(now=now)

    def next_timestamp(self, now=None):
        return self.date.next_timestamp(now=now)

    @property
    def enabled(self):
        return self._enabled

    @property
    def cron(self):
        return self.date.into_cron()


class SchedulerDate(object):

    def __init__(
        self, minutes="*", hours="*", days_of_month="*", months="*", days_of_week="*"
    ):
        self.minutes = self._parse_field(minutes, 0, 59)
        self.hours = self._parse_field(hours, 0, 23)
        self.days_of_month = self._parse_field(days_of_month, 1, 31)
        self.months = self._parse_field(months, 1, 12)
        self.days_of_week = self._parse_field(days_of_week, 0, 6)

    def __repr__(self):
        return "<SchedulerDate: %s, %s>" % (self.into_cron(), self.next_run())

    def __str__(self):
        return "<SchedulerDate: %s, %s>" % (self.into_cron(), self.next_run())

    @classmethod
    def from_cron(cls, cron):
        if isinstance(cron, cls):
            return cron
        values = (value.strip().split(",") for value in cron.split(" "))
        return cls(*values)

    def into_cron(self):
        return " ".join(
            [
                self._into_cron_field(self.minutes, 0, 59),
                self._into_cron_field(self.hours, 0, 23),
                self._into_cron_field(self.days_of_month, 1, 31),
                self._into_cron_field(self.months, 1, 12),
                self._into_cron_field(self.days_of_week, 0, 6),
            ]
        )

    def next_timestamp(self, now=None):
        date = self.next_run(now=now)
        return legacy.to_timestamp(date)

    def next_run(self, now=None):
        """
        Calculate the next run time starting from the current time.
        This operation is done respecting Cron rules.

        :type now: datetime
        :param now: Optional date time to be used as the current time.
        :rtype: datetime
        :return: The next run time respecting Cron rules.
        """

        now = now or legacy.utc_now()
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
                    if self.days_of_week and not date.weekday() in self.days_of_week:
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

    def _parse_field(self, field, min_value, max_value):
        if field in ("*", ["*"], ("*",)):
            return set(range(min_value, max_value + 1))
        elif isinstance(field, (list, tuple)):
            return set(int(v) for v in field)
        else:
            return set((int(field),))

    def _into_cron_field(self, field, min_value, max_value):
        if field == set(range(min_value, max_value + 1)):
            return "*"
        return ",".join(str(v) for v in sorted(field))


class Cron(object):
    pass
