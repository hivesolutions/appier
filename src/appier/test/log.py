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

import os
import logging
import logging.handlers
import tempfile
import unittest

import appier

from appier import log


class LogTest(unittest.TestCase):
    def test_silent_value(self):
        self.assertEqual(appier.SILENT, logging.CRITICAL + 1)
        self.assertEqual(type(appier.SILENT), int)

    def test_silent_above_critical(self):
        self.assertTrue(appier.SILENT > logging.CRITICAL)

    def test_trace_value(self):
        self.assertEqual(appier.TRACE, 5)
        self.assertEqual(appier.TRACE, logging.DEBUG - 5)
        self.assertEqual(type(appier.TRACE), int)

    def test_trace_below_debug(self):
        self.assertTrue(appier.TRACE < logging.DEBUG)

    def test_level_ordering(self):
        self.assertTrue(appier.TRACE < logging.DEBUG)
        self.assertTrue(logging.DEBUG < logging.INFO)
        self.assertTrue(logging.INFO < logging.WARNING)
        self.assertTrue(logging.WARNING < logging.ERROR)
        self.assertTrue(logging.ERROR < logging.CRITICAL)
        self.assertTrue(logging.CRITICAL < appier.SILENT)

    def test_rotating_handler(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        try:
            handler = appier.rotating_handler(path=path, max_bytes=1024, max_log=3)

            self.assertEqual(type(handler), logging.handlers.RotatingFileHandler)
            self.assertEqual(handler.maxBytes, 1024)
            self.assertEqual(handler.backupCount, 3)

            handler.close()
        finally:
            os.unlink(path)

    def test_rotating_handler_defaults(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        try:
            handler = appier.rotating_handler(path=path)

            self.assertEqual(handler.maxBytes, 1048576)
            self.assertEqual(handler.backupCount, 5)

            handler.close()
        finally:
            os.unlink(path)

    def test_patch_logging(self):
        appier.patch_logging()

        result = logging.getLevelName(appier.TRACE)

        self.assertEqual(result, "TRACE")

    def test_patch_logging_reverse(self):
        appier.patch_logging()

        result = logging.getLevelName("TRACE")

        self.assertEqual(result, appier.TRACE)

    def test_patch_logging_idempotent(self):
        appier.patch_logging()
        appier.patch_logging()

        result = logging.getLevelName(appier.TRACE)

        self.assertEqual(result, "TRACE")

    def test_patch_logging_logger_trace(self):
        appier.patch_logging()

        logger = logging.getLogger("appier.test.trace")

        self.assertTrue(hasattr(logger, "trace"))
        self.assertTrue(callable(logger.trace))

    def test_patch_logging_logger_trace_call(self):
        appier.patch_logging()

        logger = logging.getLogger("appier.test.trace.call")
        logger.setLevel(appier.TRACE)
        records = []
        handler = logging.Handler()
        handler.setLevel(appier.TRACE)
        handler.emit = lambda record: records.append(record)
        logger.addHandler(handler)

        try:
            logger.trace("trace test message")

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].getMessage(), "trace test message")
            self.assertEqual(records[0].levelno, appier.TRACE)
            self.assertEqual(records[0].levelname, "TRACE")
        finally:
            logger.removeHandler(handler)

    def test_patch_logging_logger_trace_filtered(self):
        appier.patch_logging()

        logger = logging.getLogger("appier.test.trace.filtered")
        logger.setLevel(logging.DEBUG)
        records = []
        handler = logging.Handler()
        handler.setLevel(appier.TRACE)
        handler.emit = lambda record: records.append(record)
        logger.addHandler(handler)

        try:
            # the trace message should be filtered since the logger
            # level is set to DEBUG which is above TRACE
            logger.trace("this should be filtered")

            self.assertEqual(len(records), 0)
        finally:
            logger.removeHandler(handler)

    def test_level_trace_before_patch(self):
        # temporarily removes the patched state to simulate a
        # scenario where patch_logging() has not been called yet
        patched = getattr(logging, "_appier_patched", None)
        if patched:
            del logging._appier_patched
        trace_method = getattr(logging.Logger, "trace", None)
        if trace_method:
            del logging.Logger.trace
        try:
            result = appier.App._level("TRACE")

            self.assertEqual(result, appier.TRACE)
            self.assertEqual(result, 5)
        finally:
            if patched:
                logging._appier_patched = patched
            if trace_method:
                logging.Logger.trace = trace_method

    def test_level_trace_after_patch(self):
        appier.patch_logging()

        result = appier.App._level("TRACE")

        self.assertEqual(result, appier.TRACE)
        self.assertEqual(result, 5)

    def test_level_silent(self):
        result = appier.App._level("SILENT")

        self.assertEqual(result, appier.SILENT)

    def test_level_integer(self):
        result = appier.App._level(logging.DEBUG)

        self.assertEqual(result, logging.DEBUG)

    def test_level_none(self):
        result = appier.App._level(None)

        self.assertEqual(result, None)

    def test_in_signature(self):
        def sample(a, b, secure=None):
            pass

        result = log.in_signature(sample, "secure")

        self.assertEqual(result, True)

    def test_in_signature_missing(self):
        def sample(a, b):
            pass

        result = log.in_signature(sample, "secure")

        self.assertEqual(result, False)

    def test_in_signature_args(self):
        def sample(a, b, secure):
            pass

        result = log.in_signature(sample, "secure")

        self.assertEqual(result, True)

    def test_memory_handler(self):
        memory_handler = appier.MemoryHandler()
        formatter = logging.Formatter("%(message)s")
        memory_handler.setFormatter(formatter)

        latest = memory_handler.get_latest()
        self.assertEqual(len(latest), 0)
        self.assertEqual(latest, [])

        record = logging.makeLogRecord(
            dict(msg="hello world", levelname=logging.getLevelName(logging.INFO))
        )
        memory_handler.emit(record)
        latest = memory_handler.get_latest()

        self.assertEqual(len(latest), 1)
        self.assertEqual(latest, ["hello world"])

        record = logging.makeLogRecord(
            dict(msg="hello world 2", levelname=logging.getLevelName(logging.ERROR))
        )
        memory_handler.emit(record)
        latest = memory_handler.get_latest()

        self.assertEqual(len(latest), 2)
        self.assertEqual(latest, ["hello world 2", "hello world"])

        latest = memory_handler.get_latest(level=logging.ERROR)

        self.assertEqual(len(latest), 1)
        self.assertEqual(latest, ["hello world 2"])

        latest = memory_handler.get_latest(level=logging.CRITICAL)

        self.assertEqual(len(latest), 0)
        self.assertEqual(latest, [])

        latest = memory_handler.get_latest(level=logging.INFO)

        self.assertEqual(len(latest), 2)
        self.assertEqual(latest, ["hello world 2", "hello world"])

        latest = memory_handler.get_latest(count=1, level=logging.INFO)

        self.assertEqual(len(latest), 1)
        self.assertEqual(latest, ["hello world 2"])

    def test_memory_handler_file(self):
        memory_handler = appier.MemoryHandler()
        formatter = logging.Formatter("%(message)s")
        memory_handler.setFormatter(formatter)

        latest = memory_handler.get_latest()
        self.assertEqual(len(latest), 0)
        self.assertEqual(latest, [])

        record = logging.makeLogRecord(
            dict(msg="hello world", levelname=logging.getLevelName(logging.INFO))
        )
        memory_handler.emit(record)
        record = logging.makeLogRecord(
            dict(msg="hello world 2", levelname=logging.getLevelName(logging.INFO))
        )
        memory_handler.emit(record)

        file = appier.legacy.BytesIO()

        memory_handler.flush_to_file(file, clear=False)

        file.seek(0)
        contents = file.read()

        self.assertEqual(contents, b"hello world\nhello world 2\n")

        file = appier.legacy.BytesIO()

        memory_handler.flush_to_file(file, reverse=False)

        file.seek(0)
        contents = file.read()

        self.assertEqual(contents, b"hello world 2\nhello world\n")

        latest = memory_handler.get_latest(count=1)
        self.assertEqual(len(latest), 0)
