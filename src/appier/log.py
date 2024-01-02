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

import json
import socket
import inspect
import logging
import itertools
import threading
import collections

from . import common
from . import config
from . import legacy

LOGGING_FORMAT_T = "%%(asctime)s [%%(levelname)s] %s%%(message)s"
""" The format to be used for the logging operation in
the app, these operations are going to be handled by
multiple stream handlers """

LOGGING_FORMAT_TID_T = "%%(asctime)s [%%(levelname)s] %s[%%(thread)d] %%(message)s"
""" The format to be used for the logging operation in
the app, these operations are going to be handled by
multiple stream handlers, this version of the string
includes the thread identification number and should be
used for messages called from outside the main thread """

LOGGING_EXTRA = "[%(name)s] " if config.conf("LOGGING_EXTRA", cast=bool) else ""
""" The extra logging attributes that are going to be applied
to the format strings to obtain the final on the logging """

LOGGIGN_SYSLOG = '1 %%(asctime)s %%(hostname)s %s %%(process)d %%(thread)d \
[appierSDID@0 tid="%%(thread)d"] %%(json)s'
""" The format to be used for the message sent using the syslog
logger, should contain extra structured data """

MAX_LENGTH = 10000
""" The maximum amount of messages that are kept in
memory until they are discarded, avoid a very large
number for this value or else a large amount of memory
may be used for logging purposes """

SILENT = logging.CRITICAL + 1
""" The "artificial" silent level used to silent a logger
or an handler, this is used as an utility for debugging
purposes more that a real feature for production systems """

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
""" The sequence of levels from the least sever to the
most sever this sequence may be used to find all the
levels that are considered more sever that a level """

LEVEL_ALIAS = {
    "DEBU": "DEBUG",
    "WARN": "WARNING",
    "INF": "INFO",
    "ERR": "ERROR",
    "CRIT": "CRITICAL",
}
""" Map defining a series of alias that may be used latter
for proper debug level resolution """

SYSLOG_PORTS = dict(tcp=601, udp=514)
""" Dictionary that maps the multiple transport protocol
used by syslog with the appropriate default ports """

LOGGING_FORMAT = LOGGING_FORMAT_T % LOGGING_EXTRA
LOGGING_FORMAT_TID = LOGGING_FORMAT_TID_T % LOGGING_EXTRA


class MemoryHandler(logging.Handler):
    """
    Logging handler that is used to store information in
    memory so that anyone else may consult it latter as
    long as the execution session is the same.
    """

    def __init__(self, level=logging.NOTSET, max_length=MAX_LENGTH):
        logging.Handler.__init__(self, level=level)
        self.max_length = max_length
        self.messages = collections.deque()
        self.messages_l = dict()

        format = config.conf("LOGGING_FORMAT", None)
        format_base = format or LOGGING_FORMAT
        format_tid = format or LOGGING_FORMAT_TID

        formatter = ThreadFormatter(format_base)
        formatter.set_tid(format_tid)
        self.setFormatter(formatter)

    def get_messages_l(self, level):
        # in case the level is not found in the list of levels
        # it's not considered valid and so an empty list is returned
        try:
            index = LEVELS.index(level)
        except Exception:
            return collections.deque()

        # retrieves the complete set of levels that are considered
        # equal or more severe than the requested one
        levels = LEVELS[: index + 1]

        # creates the list that will hold the various message
        # lists associated with the current severity level
        messages_l = collections.deque()

        # iterates over the complete set of levels considered
        # equal or less sever to add the respective messages
        # list to the list of message lists
        for level in levels:
            _messages_l = self.messages_l.get(level, None)
            if _messages_l == None:
                _messages_l = collections.deque()
            self.messages_l[level] = _messages_l
            messages_l.append(_messages_l)

        # returns the complete set of messages lists that
        # have a level equal or less severe that the one
        # that has been requested by argument
        return messages_l

    def emit(self, record):
        # formats the current record according to the defined
        # logging rules so that we can used the resulting message
        # for any logging purposes
        message = self.format(record)

        # retrieves the level (as a string) associated with
        # the current record to emit and uses it to retrieve
        # the associated messages list
        level = record.levelname
        messages_l = self.get_messages_l(level)

        # inserts the message into the messages queue and in
        # case the current length of the message queue overflows
        # the one defined as maximum must pop message from queue
        self.messages.appendleft(message)
        messages_s = len(self.messages)
        if messages_s > self.max_length:
            self.messages.pop()

        # iterates over all the messages list included in the retrieve
        # messages list to add the logging message to each of them
        for _messages_l in messages_l:
            # inserts the message into the proper level specific queue
            # and in case it overflows runs the same pop operation as
            # specified also for the more general queue
            _messages_l.appendleft(message)
            messages_s = len(_messages_l)
            if messages_s > self.max_length:
                _messages_l.pop()

    def clear(self):
        self.messages = collections.deque()
        self.messages_l = dict()

    def get_latest(self, count=None, level=None):
        count = count or 100
        is_level = level and not legacy.is_string(level)
        if is_level:
            level = logging.getLevelName(level)
        level = level.upper() if level else level
        level = LEVEL_ALIAS.get(level, level)
        messages = self.messages_l.get(level, []) if level else self.messages
        slice = itertools.islice(messages, 0, count)
        return list(slice)

    def flush_to_file(self, path, count=None, level=None, reverse=True, clear=True):
        messages = self.get_latest(level=level, count=count or 65536)
        if not messages:
            return
        if reverse:
            messages.reverse()
        is_path = isinstance(path, legacy.STRINGS)
        file = open(path, "wb") if is_path else path
        try:
            for message in messages:
                message = legacy.bytes(message, "utf-8", force=True)
                file.write(message + b"\n")
        finally:
            if is_path:
                file.close()
        if clear:
            self.clear()


class BaseFormatter(logging.Formatter):
    """
    The base Appier logging formatted used to add some extra
    functionality on top of Python's base formatting infra-structure.

    Most of its usage focus on empowering the base record object
    with some extra values.
    """

    def __init__(self, *args, **kwargs):
        self._wrap = kwargs.pop("wrap", False)
        logging.Formatter.__init__(self, *args, **kwargs)

    @classmethod
    def _wrap_record(cls, record):
        if hasattr(record, "_wrapped"):
            return
        record.hostname = socket.gethostname()
        record.json = json.dumps(
            dict(
                message=str(record.msg),
                hostname=record.hostname,
                lineno=record.lineno,
                module=record.module,
                callable=record.funcName,
                level=record.levelname,
                thread=record.thread,
                process=record.process,
                logger=record.name,
            )
        )
        record._wrapped = True

    def format(self, record):
        # runs the wrapping operation on the record so that more
        # information becomes available in it (as expected)
        if self._wrap:
            self.__class__._wrap_record(record)

        # runs the basic format operation on the record so that
        # it gets properly formatted into a plain string
        return logging.Formatter.format(self, record)


class ThreadFormatter(BaseFormatter):
    """
    Custom formatter class that changing the default format
    behavior so that the thread identifier is printed when
    the threading printing the log records is not the main one.
    """

    def __init__(self, *args, **kwargs):
        BaseFormatter.__init__(self, *args, **kwargs)
        self._basefmt = BaseFormatter(*args, **kwargs)
        self._tidfmt = BaseFormatter(*args, **kwargs)

    def format(self, record):
        # runs the wrapping operation on the record so that more
        # information becomes available in it (as expected)
        if self._wrap:
            self.__class__._wrap_record(record)

        # retrieves the reference to the current thread and verifies
        # if it represent the current process main thread, then selects
        # the appropriate formating string taking that into account
        current = threading.current_thread()
        is_main = current.name == "MainThread"
        if not is_main:
            return self._tidfmt.format(record)
        return self._basefmt.format(record)

    def set_base(self, value, *args, **kwargs):
        self._basefmt = BaseFormatter(value, *args, **kwargs)

    def set_tid(self, value, *args, **kwargs):
        self._tidfmt = BaseFormatter(value, *args, **kwargs)


class DummyLogger(object):
    def debug(self, object):
        pass

    def info(self, object):
        pass

    def warning(self, object):
        pass

    def error(self, object):
        pass

    def critical(self, object):
        pass


def reload_format(app=None):
    global LOGGING_FORMAT
    global LOGGING_FORMAT_TID

    app = app or common.base().get_app()

    extra = LOGGING_EXTRA
    if app and not app.is_parent():
        extra = "[%(process)d] " + extra

    LOGGING_FORMAT = LOGGING_FORMAT_T % extra
    LOGGING_FORMAT_TID = LOGGING_FORMAT_TID_T % extra


def rotating_handler(
    path="appier.log", max_bytes=1048576, max_log=5, encoding=None, delay=False
):
    return logging.handlers.RotatingFileHandler(
        path, maxBytes=max_bytes, backupCount=max_log, encoding=encoding, delay=delay
    )


def smtp_handler(
    host="localhost",
    port=25,
    sender="no-reply@appier.com",
    receivers=[],
    subject="Appier logging",
    username=None,
    password=None,
    stls=False,
):
    address = (host, port)
    if username and password:
        credentials = (username, password)
    else:
        credentials = None
    has_secure = in_signature(logging.handlers.SMTPHandler.__init__, "secure")
    if has_secure:
        kwargs = dict(secure=() if stls else None)
    else:
        kwargs = dict()
    return logging.handlers.SMTPHandler(
        address, sender, receivers, subject, credentials=credentials, **kwargs
    )


def in_signature(callable, name):
    has_full = hasattr(inspect, "getfullargspec")
    if has_full:
        spec = inspect.getfullargspec(callable)
    else:
        spec = inspect.getargspec(callable)
    args, _varargs, kwargs = spec[:3]
    return (args and name in args) or (kwargs and "secure" in kwargs)
