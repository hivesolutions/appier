#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Appier Framework. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import datetime
import unittest

import appier

class SessionTest(unittest.TestCase):

    def test_memory(self):
        session = appier.MemorySession.new()

        session["first"] = 1
        session["second"] = 2

        session.flush()

        self.assertNotEqual(session.sid, None)

        self.assertEqual(session["first"], 1)
        self.assertEqual(session["second"], 2)

    def test_file(self):
        session = appier.FileSession.new()

        session["first"] = 1
        session["second"] = 2

        session.flush()

        self.assertNotEqual(session.sid, None)

        self.assertEqual(session["first"], 1)
        self.assertEqual(session["second"], 2)

        appier.FileSession.close()

    def test_expire(self):
        expire = datetime.timedelta(days = 0)
        session = appier.MemorySession.new(expire = expire)

        self.assertEqual(session.is_expired(), True)

        session = appier.MemorySession.get_s(session.sid)
        self.assertEqual(session, None)

        expire = datetime.timedelta(days = 1)
        session = appier.MemorySession.new(expire = expire)

        self.assertEqual(session.is_expired(), False)

        session = appier.MemorySession.get_s(session.sid)
        self.assertNotEqual(session, None)
