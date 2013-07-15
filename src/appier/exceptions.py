#!/usr/bin/python
# -*- coding: utf-8 -*-

class BotException(Exception):
    """
    Top level exception to be used as the root of
    all the exceptions to be raised by the bot infra-
    structure. Should be compatible with http status
    codes for proper http serialization.
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        self.error_code = kwargs.get("error_code", 500)
