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

import unittest

import appier


class ExceptionHandlerTest(unittest.TestCase):
    def setUp(self):
        self._original_handlers = appier.common.base().App._ERROR_HANDLERS
        appier.common.base().App._ERROR_HANDLERS = {}
        self.app = appier.App()

    def tearDown(self):
        self.app.unload()
        appier.common.base().App._ERROR_HANDLERS = self._original_handlers

    def test_basic_registration_and_call(self):
        """
        Decorator should register the handler and it must be invoked by
        :pyfunc:`appier.App.call_error` when an exception matching the provided
        type is raised.

        The exception handler is a JSON handler by default, to be able to properly
        handle errors in an App.
        """

        @appier.exception_handler(appier.exceptions.NotFoundError, json=True)
        def not_found(_):
            return "resource not found"

        exc = appier.exceptions.NotFoundError("dummy")
        result = self.app.call_error(exc, scope=None, json=True)
        self.assertEqual(result, "resource not found")

        handlers = appier.common.base().App._ERROR_HANDLERS.get(
            appier.exceptions.NotFoundError
        )
        self.assertNotEqual(handlers, None)
        self.assertEqual(len(handlers), 1)

        method, scope, json, opts, ctx, priority = handlers[0]
        self.assertEqual(method, not_found)
        self.assertEqual(scope, None)
        self.assertEqual(json, True)
        self.assertEqual(opts, None)
        self.assertEqual(ctx, None)
        self.assertEqual(priority, 1)

    def test_web_handler(self):
        """
        Test that in which the exception handler is a web handler by default, to be
        able to properly handle errors in an WebApp, because this is an App no
        handler is called.
        """

        @appier.exception_handler(appier.exceptions.NotFoundError, json=False)
        def not_found(_):
            return "resource not found"

        exc = appier.exceptions.NotFoundError("dummy")
        result = self.app.call_error(exc, scope=None, json=True)
        self.assertEqual(result, None)

        handlers = appier.common.base().App._ERROR_HANDLERS.get(
            appier.exceptions.NotFoundError
        )
        self.assertNotEqual(handlers, None)
        self.assertEqual(len(handlers), 1)

        method, scope, json, opts, ctx, priority = handlers[0]
        self.assertEqual(method, not_found)
        self.assertEqual(scope, None)
        self.assertEqual(json, False)
        self.assertEqual(opts, None)
        self.assertEqual(ctx, None)
        self.assertEqual(priority, 1)

    def test_scope_registration(self):
        """
        When a *scope* argument is provided, it should be stored in the handler
        metadata so that the framework can later match it appropriately.

        The exception handler is a JSON handler by default, to be able to properly
        handle errors in an App.
        """

        class DummyScope:
            pass

        class DummyException(Exception):
            code = 400

        @appier.exception_handler(DummyException, scope=DummyScope)
        def bad_request(_):
            return "bad request"

        exc = DummyException("dummy")
        result = self.app.call_error(exc, scope=DummyScope, json=True)
        self.assertEqual(result, "bad request")

        result = None
        exc = DummyException("dummy")
        result = self.app.call_error(exc, json=True)
        self.assertEqual(result, None)

        handlers = appier.common.base().App._ERROR_HANDLERS.get(DummyException)
        self.assertNotEqual(handlers, None)
        self.assertEqual(len(handlers), 1)

        method, scope, json, opts, ctx, priority = handlers[0]

        self.assertEqual(method, bad_request)
        self.assertEqual(scope, DummyScope)
        self.assertEqual(json, None)
        self.assertEqual(opts, None)
        self.assertEqual(ctx, None)
        self.assertEqual(priority, 1)
