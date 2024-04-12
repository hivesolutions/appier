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
import unittest

import appier


class SchedulerDateTest(unittest.TestCase):

    def test_from_cron(self):
        date = appier.SchedulerDate.from_cron("11")
        self.assertEqual(date.minutes, set((11,)))
        self.assertEqual(date.hours, set(range(0, 24)))
        self.assertEqual(date.days_of_month, set(range(1, 32)))
        self.assertEqual(date.months, set(range(1, 13)))
        self.assertEqual(date.days_of_week, set(range(0, 7)))

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
