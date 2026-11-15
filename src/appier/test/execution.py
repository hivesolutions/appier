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


class ExecutionTest(unittest.TestCase):

    def test_minutes_eval(self):
        now = datetime.datetime(year=2014, month=1, day=1)
        result = appier.minutes_eval(0, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, minute=1)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2014, month=1, day=1, second=10)
        result = appier.minutes_eval(0, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, minute=1)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2014, month=1, day=1, second=10)
        result = appier.minutes_eval(30, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, second=30)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2014, month=1, day=1, second=30)
        result = appier.minutes_eval(30, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, minute=1, second=30)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(
            year=2013, month=12, day=31, hour=23, minute=59, second=45
        )
        result = appier.minutes_eval(30, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, second=30)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

    def test_hourly_eval(self):
        now = datetime.datetime(year=2014, month=1, day=1)
        result = appier.hourly_eval(0, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, hour=1)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2014, month=1, day=1, minute=10)
        result = appier.hourly_eval(0, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, hour=1)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2014, month=1, day=1, minute=10)
        result = appier.hourly_eval(1800, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, minute=30)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2014, month=1, day=1, minute=30)
        result = appier.hourly_eval(1800, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, hour=1, minute=30)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2013, month=12, day=31, hour=23, minute=45)
        result = appier.hourly_eval(1800, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, minute=30)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

    def test_daily_eval(self):
        now = datetime.datetime(year=2014, month=1, day=1)
        result = appier.daily_eval(0, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=2)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2013, month=12, day=31, hour=1)
        result = appier.daily_eval(0, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2013, month=12, day=31, hour=1)
        result = appier.daily_eval(3600, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, hour=1)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2013, month=12, day=31, minute=13)
        result = appier.daily_eval(14400, now=now)
        expected_d = datetime.datetime(year=2013, month=12, day=31, hour=4)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(
            year=2013, month=12, day=31, hour=3, minute=59, second=59
        )
        result = appier.daily_eval(14400, now=now)
        expected_d = datetime.datetime(year=2013, month=12, day=31, hour=4)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2013, month=12, day=31, hour=4, microsecond=1)
        result = appier.daily_eval(14400, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, hour=4)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)

        now = datetime.datetime(year=2013, month=12, day=31, hour=5)
        result = appier.daily_eval(14400, now=now)
        expected_d = datetime.datetime(year=2014, month=1, day=1, hour=4)
        expected_t = calendar.timegm(expected_d.utctimetuple())
        self.assertEqual(result, expected_t)
