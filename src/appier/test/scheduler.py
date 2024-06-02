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

import calendar
import datetime
import unittest

import appier


class CronSchedulerTest(unittest.TestCase):

    def test_basic(self):
        state = dict(value=0)

        def increment():
            state["value"] += 1

        scheduler = appier.CronScheduler(None)
        task = scheduler.schedule(
            lambda: increment(),
            "11",
            now=datetime.datetime(2013, 1, 1, hour=1, minute=1),
        )
        self.assertNotEqual(task, None)
        self.assertEqual(isinstance(task, appier.SchedulerTask), True)
        self.assertEqual(task.enabled, True)
        self.assertEqual(
            scheduler.next_run(), datetime.datetime(2013, 1, 1, hour=1, minute=11)
        )

        scheduler.tick(
            now_ts=calendar.timegm(
                datetime.datetime(2013, 1, 1, hour=1, minute=1).utctimetuple()
            )
        )
        self.assertEqual(state["value"], 0)
        self.assertEqual(scheduler.timeout, 600)

        scheduler.tick(
            now_ts=calendar.timegm(
                datetime.datetime(2013, 1, 1, hour=1, minute=11).utctimetuple()
            )
        )
        self.assertEqual(state["value"], 1)
        self.assertEqual(scheduler.timeout, 3600)

        scheduler.tick(
            now_ts=calendar.timegm(
                datetime.datetime(2013, 1, 1, hour=2, minute=11).utctimetuple()
            )
        )
        self.assertEqual(state["value"], 2)
        self.assertEqual(scheduler.timeout, 3600)

    def test_scheduler_date(self):
        state = dict(value=0)

        def increment():
            state["value"] += 1

        scheduler = appier.CronScheduler(None)
        task = scheduler.schedule(
            lambda: increment(),
            appier.SchedulerDate(minutes=11),
            now=datetime.datetime(2013, 1, 1, hour=1, minute=1),
        )
        self.assertNotEqual(task, None)
        self.assertEqual(isinstance(task, appier.SchedulerTask), True)
        self.assertEqual(task.enabled, True)
        self.assertEqual(
            scheduler.next_run(), datetime.datetime(2013, 1, 1, hour=1, minute=11)
        )

        scheduler.tick(
            now_ts=calendar.timegm(
                datetime.datetime(2013, 1, 1, hour=1, minute=1).utctimetuple()
            )
        )
        self.assertEqual(state["value"], 0)
        self.assertEqual(scheduler.timeout, 600)

        scheduler.tick(
            now_ts=calendar.timegm(
                datetime.datetime(2013, 1, 1, hour=1, minute=11).utctimetuple()
            )
        )
        self.assertEqual(state["value"], 1)
        self.assertEqual(scheduler.timeout, 3600)

    def test_week_days(self):
        state = dict(value=0)

        def increment():
            state["value"] += 1

        scheduler = appier.CronScheduler(None)
        task = scheduler.schedule(
            lambda: increment(),
            appier.SchedulerDate(minutes=11, days_of_month=10, days_of_week=2),
            now=datetime.datetime(2013, 1, 1, hour=1, minute=1),
        )
        self.assertNotEqual(task, None)
        self.assertEqual(isinstance(task, appier.SchedulerTask), True)
        self.assertEqual(task.enabled, True)
        self.assertEqual(
            scheduler.next_run(), datetime.datetime(2013, 4, 10, hour=0, minute=11)
        )

    def test_duplicate(self):
        state = dict(value=0)

        def increment():
            state["value"] += 1

        scheduler = appier.CronScheduler(None)
        task1 = scheduler.schedule(
            lambda: increment(),
            appier.SchedulerDate(minutes=11, days_of_month=10, days_of_week=2),
            now=datetime.datetime(2013, 1, 1, hour=1, minute=1),
        )
        task2 = scheduler.schedule(
            lambda: increment(),
            appier.SchedulerDate(minutes=11, days_of_month=10, days_of_week=2),
            now=datetime.datetime(2013, 1, 1, hour=1, minute=1),
        )
        self.assertNotEqual(task1, None)
        self.assertNotEqual(task2, None)
        self.assertEqual(isinstance(task1, appier.SchedulerTask), True)
        self.assertEqual(isinstance(task2, appier.SchedulerTask), True)
        self.assertEqual(task1.enabled, True)
        self.assertEqual(task2.enabled, True)
        self.assertEqual(
            scheduler.next_run(), datetime.datetime(2013, 4, 10, hour=0, minute=11)
        )


class SchedulerDateTest(unittest.TestCase):

    def test_repr(self):
        date = appier.SchedulerDate.from_cron("11")
        self.assertEqual(
            repr(date), "<SchedulerDate: 11 * * * *, %s>" % str(date.next_run())
        )

    def test_from_cron(self):
        date = appier.SchedulerDate.from_cron("11")
        self.assertEqual(date.minutes, set((11,)))
        self.assertEqual(date.hours, set(range(0, 24)))
        self.assertEqual(date.days_of_month, set(range(1, 32)))
        self.assertEqual(date.months, set(range(1, 13)))
        self.assertEqual(date.days_of_week, set(range(0, 7)))

    def test_into_cron(self):
        date = appier.SchedulerDate.from_cron("11")
        self.assertEqual(date.into_cron(), "11 * * * *")

        date = appier.SchedulerDate.from_cron("11 3")
        self.assertEqual(date.into_cron(), "11 3 * * *")

        date = appier.SchedulerDate.from_cron("11 3 10")
        self.assertEqual(date.into_cron(), "11 3 10 * *")

        date = appier.SchedulerDate.from_cron("11 3 10 5")
        self.assertEqual(date.into_cron(), "11 3 10 5 *")

        date = appier.SchedulerDate.from_cron("11 3 10 5 2")
        self.assertEqual(date.into_cron(), "11 3 10 5 2")

        date = appier.SchedulerDate.from_cron("* 3 10 5 2")
        self.assertEqual(date.into_cron(), "* 3 10 5 2")

    def test_next_run(self):
        date = appier.SchedulerDate.from_cron("11")

        value = date.next_run(now=datetime.datetime(2013, 1, 1, hour=1, minute=1))
        self.assertEqual(value, datetime.datetime(2013, 1, 1, hour=1, minute=11))

        value = date.next_run(now=datetime.datetime(2013, 1, 1, hour=1, minute=12))
        self.assertEqual(value, datetime.datetime(2013, 1, 1, hour=2, minute=11))

        value = date.next_run(now=datetime.datetime(2013, 12, 31, hour=23, minute=12))
        self.assertEqual(value, datetime.datetime(2014, 1, 1, hour=0, minute=11))

    def test_next_run_complex(self):
        date = appier.SchedulerDate.from_cron("11 3 10,16,20")
        value = date.next_run(now=datetime.datetime(2013, 1, 1, hour=1, minute=1))
        self.assertEqual(value, datetime.datetime(2013, 1, 10, hour=3, minute=11))

        value = date.next_run(now=datetime.datetime(2013, 1, 10, hour=4, minute=1))
        self.assertEqual(value, datetime.datetime(2013, 1, 16, hour=3, minute=11))

        date = appier.SchedulerDate.from_cron("* 3 10,16,20")
        value = date.next_run(now=datetime.datetime(2013, 1, 10, hour=3, minute=1))
        self.assertEqual(value, datetime.datetime(2013, 1, 10, hour=3, minute=2))

        value = date.next_run(now=datetime.datetime(2013, 1, 10, hour=3, minute=2))
        self.assertEqual(value, datetime.datetime(2013, 1, 10, hour=3, minute=3))
