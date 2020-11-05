#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2020 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import json
import uuid

from . import common
from . import legacy

class AppierException(Exception):
    """
    Top level exception to be used as the root of
    all the exceptions to be raised by the appier infra-
    structure. Should be compatible with HTTP status
    codes for proper HTTP serialization.
    """

    message = None
    """ The message value stored to describe the
    current exception value """

    code = None
    """ The internal error code to be used in objective
    serialization of the error (eg: HTTP) """

    headers = None
    """ Optional list of MIME compliant headers to be sent
    in a client/server paradigm """

    meta = None
    """ The meta information associated with the error
    that should be considered private in context, this
    should be structured data ready to be serializable """

    def __init__(self, *args, **kwargs):
        """
        Initialize the message.

        Args:
            self: (todo): write your description
        """
        Exception.__init__(self, *args)
        self.name = self._name()
        self.message = kwargs.get("message", self.name)
        self.code = kwargs.get("code", 500)
        self.headers = kwargs.get("headers", None)
        self.meta = kwargs.get("meta", None)
        self.args = args
        self.kwargs = kwargs
        self._uid = None

    def __str__(self):
        """
        Returns a unicode.

        Args:
            self: (todo): write your description
        """
        if legacy.PYTHON_3: return self.__unicode__()
        is_unicode = legacy.is_unicode(self.message)
        if is_unicode: return self.message.encode("utf-8")
        return self.message

    def __unicode__(self):
        """
        Return unicode string.

        Args:
            self: (todo): write your description
        """
        is_unicode = legacy.is_unicode(self.message)
        if not is_unicode: return self.message.decode("utf-8")
        return self.message

    def get_meta(self, name, default = None):
        """
        Get the meta value of the given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
            default: (todo): write your description
        """
        if not self.meta: return default
        return self.meta.get(name, default)

    def set_meta(self, name, value):
        """
        Sets the meta.

        Args:
            self: (todo): write your description
            name: (str): write your description
            value: (todo): write your description
        """
        if not self.meta: self.meta = {}
        self.meta[name] = value

    def del_meta(self, name):
        """
        Remove meta from meta data dict

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        if not self.meta: return
        if not name in self.meta: return
        del self.meta[name]

    @property
    def uid(self):
        """
        Returns the unique uid.

        Args:
            self: (todo): write your description
        """
        if self._uid: return self._uid
        self._uid = uuid.uuid4()
        return self._uid

    def _name(self):
        """
        Return the name of this class.

        Args:
            self: (todo): write your description
        """
        cls = self.__class__
        return common.util().camel_to_readable(cls.__name__)

class OperationalError(AppierException):
    """
    Error raised for a runtime error and as a result
    of an operational routine that failed.
    This should not be used for coherent development
    bugs, that are raised continuously.
    """

    pass

class SecurityError(AppierException):
    """
    Error used to indicate security problems that may
    arise during the execution (runtime) of an appier
    application. This error should not be used to notify
    development related problems.
    """

    pass

class AssertionError(OperationalError):
    """
    Error raised for failure to meet any pre-condition or
    assertion for a certain data set.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize this function.

        Args:
            self: (todo): write your description
        """
        kwargs["message"] = kwargs.get("message", "Assertion of data failed")
        kwargs["code"] = kwargs.get("code", None)
        OperationalError.__init__(self, *args, **kwargs)

class ValidationError(OperationalError):
    """
    Error raised when a validation on the model fails
    the error should associate a name in the model with
    a message describing the validation failure.
    """

    errors = None
    """ The map containing an association between the name
    of a field and a list of validation errors for it """

    model = None
    """ The model containing the values in it after the
    process of validation has completed """

    def __init__(self, errors, model, *args, **kwargs):
        """
        Initialize errors.

        Args:
            self: (todo): write your description
            errors: (str): write your description
            model: (todo): write your description
        """
        kwargs["message"] = kwargs.get("message", "Validation of submitted data failed")
        kwargs["code"] = kwargs.get("code", 400)
        OperationalError.__init__(self, *args, **kwargs)
        self.errors = errors
        self.model = model
        self.set_meta("errors", self.errors)

    def __str__(self):
        """
        Returns a string representation of model.

        Args:
            self: (todo): write your description
        """
        if legacy.PYTHON_3: return self.__unicode__()
        message = OperationalError.__str__(self)
        extended = common.is_devel()
        if not extended: return message
        errors_s = self.errors_s()
        if not errors_s: return message
        if self.model:
            message += " for model '%s' with id '%s'" % (
                self.model.__class__._name(),
                self.model._id if hasattr(self.model, "_id") else "unset"
            )
        errors_s = errors_s.encode("utf-8")
        message += " (" + errors_s + ")"
        return message

    def __unicode__(self):
        """
        The unicode string of this message.

        Args:
            self: (todo): write your description
        """
        message = OperationalError.__unicode__(self)
        extended = common.is_devel()
        if not extended: return message
        errors_s = self.errors_s()
        if not errors_s: return message
        if self.model:
            message += " for model '%s' with id '%s'" % (
                self.model.__class__._name(),
                self.model._id if hasattr(self.model, "_id") else "unset"
            )
        message += " (" + errors_s + ")"
        return message

    def errors_s(self, encoding = "utf-8"):
        """
        Return a unicode string with the errors.

        Args:
            self: (todo): write your description
            encoding: (str): write your description
        """
        if not self.errors: return ""
        buffer = []
        is_first = True
        for name, errors in legacy.iteritems(self.errors):
            for error in errors:
                is_bytes = legacy.is_bytes(error)
                if is_bytes: error = error.decode(encoding)
                if is_first: is_first = False
                else: buffer.append(", ")
                buffer.append(name)
                buffer.append(" => ")
                buffer.append(error)
        return legacy.u("").join(buffer)

class NotFoundError(OperationalError):
    """
    Error originated from an operation that was not able
    to be performed because it was not able to found the
    requested entity/value as defined by specification.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the class.

        Args:
            self: (todo): write your description
        """
        kwargs["code"] = kwargs.get("code", 404)
        OperationalError.__init__(self, *args, **kwargs)

class NotImplementedError(OperationalError):
    """
    Error to be raised when a certain feature or route is not
    yet implemented or is not meant to be implemented at the
    defined abstraction level.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize an instance.

        Args:
            self: (todo): write your description
        """
        kwargs["code"] = kwargs.get("code", 501)
        OperationalError.__init__(self, *args, **kwargs)

class BaseInternalError(RuntimeError):
    """
    The base (internal) error class from which all the
    internal error classes should inherit, contains basic
    functionality to be inherited by all the internal "errors".
    """

    message = None
    """ The message value stored to describe the
    current error, this should be a valid string """

    meta = None
    """ The meta information associated with the error
    that should be considered private in context, this
    should be structured data ready to be serializable """

    def __init__(self, message, meta = None):
        """
        Initialize the message.

        Args:
            self: (todo): write your description
            message: (str): write your description
            meta: (float): write your description
        """
        RuntimeError.__init__(self, message)
        self.message = message
        self.meta = meta

    def __str__(self):
        """
        Returns a unicode.

        Args:
            self: (todo): write your description
        """
        if legacy.PYTHON_3: return self.__unicode__()
        is_unicode = legacy.is_unicode(self.message)
        if is_unicode: return self.message.encode("utf-8")
        return self.message

    def __unicode__(self):
        """
        Return unicode string.

        Args:
            self: (todo): write your description
        """
        is_unicode = legacy.is_unicode(self.message)
        if not is_unicode: return self.message.decode("utf-8")
        return self.message

    def get_meta(self, name, default = None):
        """
        Get the meta value of the given name.

        Args:
            self: (todo): write your description
            name: (str): write your description
            default: (todo): write your description
        """
        if not self.meta: return default
        return self.meta.get(name, default)

    def set_meta(self, name, value):
        """
        Sets the meta.

        Args:
            self: (todo): write your description
            name: (str): write your description
            value: (todo): write your description
        """
        if not self.meta: self.meta = {}
        self.meta[name] = value

    def del_meta(self, name):
        """
        Remove meta from meta data dict

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        if not self.meta: return
        if not name in self.meta: return
        del self.meta[name]

class ValidationInternalError(BaseInternalError):
    """
    Error raised when a validation on the model fails
    the error should associate a name in the model with
    a message describing the validation failure.
    """

    name = None
    """ The name of the attribute that failed
    the validation, for latter reference """

    def __init__(self, name, message, meta = None):
        """
        Initialize the message.

        Args:
            self: (todo): write your description
            name: (str): write your description
            message: (str): write your description
            meta: (float): write your description
        """
        BaseInternalError.__init__(self, message, meta = meta)
        self.name = name

class ValidationMultipleError(ValidationInternalError):
    """
    Exception/error considered to be equivalent to the
    validation internal error, with the exception that it
    may handle multiple errors at the same time.
    """

    errors = []
    """ The sequence containing the multiple errors associated
    with the validation multiple error """

    def __init__(self, name = None, message = None, meta = None):
        """
        Initialize the message.

        Args:
            self: (todo): write your description
            name: (str): write your description
            message: (str): write your description
            meta: (float): write your description
        """
        ValidationInternalError.__init__(self, name, message , meta = meta)
        self.errors = []
        self.set_meta("errors", self.errors)

    def add_error(self, name, message):
        """
        Add a new error.

        Args:
            self: (todo): write your description
            name: (str): write your description
            message: (str): write your description
        """
        if not self.name: self.name = name
        if not self.message: self.message = message
        self.errors.append((name, message))

    def add_exception(self, exception):
        """
        Add an error message.

        Args:
            self: (todo): write your description
            exception: (todo): write your description
        """
        self.add_error(exception.name, exception.message)

class HTTPError(BaseInternalError):
    """
    Top level HTTP error raised whenever a bad response
    is received from the server peer. This error is meant
    to be used by the client library.
    """

    error = None
    """ The reference to the original and internal
    HTTP error that is going to be used in the reading
    of the underlying internal buffer """

    _data = None
    """ The underlying/internal data attribute that is
    going to be used to cache the binary contents of the
    error associated with this exception (data) stream """

    def __init__(self, error, code = None, message = None, extended = None, meta = None):
        """
        Initialize error message.

        Args:
            self: (todo): write your description
            error: (str): write your description
            code: (int): write your description
            message: (str): write your description
            extended: (str): write your description
            meta: (float): write your description
        """
        message = message or "Problem in the HTTP request"
        if extended == None: extended = common.is_devel()
        if code: message = "[%d] %s" % (code, message)
        if extended:
            data = self.read(error = error)
            try: data = data.decode("utf-8")
            except Exception: data = legacy.str(data)
            if data: message = message + "\n" + data if message else data
        BaseInternalError.__init__(self, message, meta = meta)
        self.code = code
        self.error = error

    def read(self, error = None):
        """
        Reads the error message.

        Args:
            self: (todo): write your description
            error: (todo): write your description
        """
        error = error or self.error
        if not self._data == None: return self._data
        self._data = error.read()
        return self._data

    def read_json(self, error = None):
        """
        Reads the json data structure.

        Args:
            self: (todo): write your description
            error: (todo): write your description
        """
        error = error or self.error
        data = self.read(error = error)
        if legacy.is_bytes(data): data = data.decode("utf-8")
        try: data_j = json.loads(data)
        except Exception: data_j = None
        return data_j

class APIError(BaseInternalError):
    """
    Highest level error for API related problems that may be
    raised from the appier API infra-structure. These kind of
    errors should be encapsulated around proper structures
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the message.

        Args:
            self: (todo): write your description
        """
        message = kwargs.get("message", None)
        meta = kwargs.get("meta", None)
        BaseInternalError.__init__(self, message, meta = meta)

class APIAccessError(APIError):
    """
    General purpose access error exception, to be raised under
    situations where the access to a certain functionalities is
    denied for insufficient permissions/invalid credentials.
    """

    original = None
    """ The reference to the original error/exception that originated
    this API access error, this may be unset in case no concrete
    error has originated this error """

    def __init__(self, *args, **kwargs):
        """
        Initialize the original message to be called from self.

        Args:
            self: (todo): write your description
        """
        self.original = kwargs.get("original", None)
        if self.original and hasattr(self.original, "message"):
            kwargs["message"] = self.original.message
        APIError.__init__(self, *args, **kwargs)

class OAuthAccessError(APIAccessError):
    """
    OAuth related problems that typically involve either outdated
    tokens or invalid ones. Triggering this exception should imply
    a revalidation of the current token.
    """

    pass
