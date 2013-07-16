#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
""" The format to be used for the logging operation in
the app, these operations are going to be handled by
multiple stream handlers """

class MemoryHandler(logging.Handler):

    MAX_LENGTH = 1000
    """ The maximum amount of messages that are kept in
    memory until they are discarded, avoid a very large
    number for this value or else a large amount of memory
    may be used for logging purposes """

    def __init__(self, level = logging.NOTSET):
        logging.Handler.__init__(self, level = level)
        self.messages = []

        formatter = logging.Formatter(LOGGING_FORMAT)
        self.setFormatter(formatter)

    def emit(self, record):
        message = self.format(record)
        self.messages.insert(0, message)
        messages_l = len(self.messages)
        if messages_l > MemoryHandler.MAX_LENGTH:
            self.messages.pop()

    def get_latest(self, count = 100):
        return self.messages[:count]
