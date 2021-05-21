#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2021 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2021 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
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

        del session["first"]

        self.assertRaises(KeyError, lambda: session["first"])
        self.assertEqual(session.get("first"), None)

    def test_file(self):
        session = appier.FileSession.new()

        session["first"] = 1
        session["second"] = 2

        session.flush()

        self.assertNotEqual(session.sid, None)

        self.assertEqual(session["first"], 1)
        self.assertEqual(session["second"], 2)

        del session["first"]

        self.assertRaises(KeyError, lambda: session["first"])
        self.assertEqual(session.get("first"), None)

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
        self.assertEqual(session.duration, 86400)

        session = appier.MemorySession.get_s(session.sid)
        self.assertNotEqual(session, None)

        expire = session.extend(duration = 60)

        self.assertEqual(session.duration, 60)
        self.assertEqual(session.expire, expire)
        self.assertEqual(session.expire, session.modify + 60)

    def test_transient(self):
        session = appier.MemorySession.new()

        session["first"] = 1
        self.assertEqual(len(session), 2)

        session.set_t("second", 2)
        self.assertEqual(len(session), 3)
        self.assertEqual(len(session.data), 2)
        self.assertEqual(session["first"], 1)
        self.assertEqual(session["second"], 2)
        self.assertEqual(session.get_t("second"), 2)
        self.assertEqual(session.get_t("first"), None)
        self.assertEqual("second" in session, True)
        self.assertEqual(len(list(iter(session))), 3)

        sid = session["sid"]
        session.flush()

        session = appier.MemorySession.get_s(sid = sid)
        self.assertEqual(len(session), 2)
        self.assertEqual(session["first"], 1)
        self.assertRaises(KeyError, lambda: session["second"])

        session.set_t("second", 2)
        self.assertEqual(session["second"], 2)
        self.assertEqual(session.get_t("second"), 2)

        session.delete("first")
        self.assertEqual(session.get("first"), None)
        self.assertRaises(KeyError, lambda: session["first"])

        session.delete_t("second")
        self.assertEqual(session.get_t("second"), None)
        self.assertRaises(KeyError, lambda: session["second"])

        self.assertEqual(session.delete_t("second"), None)
        self.assertRaises(KeyError, lambda: session.delete_t("second", force = True))
