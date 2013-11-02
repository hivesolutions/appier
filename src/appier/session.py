#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2012 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import uuid
import shelve
import hashlib

class Session(object):
    """
    Abstract session class to be used as a reference in
    the implementation of the proper classes.

    Some of the global functionality may be abstracted
    under this class and reused in the concrete classes.
    """

    def __init__(self, name = "session"):
        object.__init__(self)
        self.sid = self._gen_sid()
        self.name = name

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return None

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    @classmethod
    def new(cls):
        return cls()

    @classmethod
    def get_s(cls, sid):
        return cls()

    def start(self):
        pass

    def flush(self):
        pass

    def _gen_sid(self):
        token_s = str(uuid.uuid4())
        token = hashlib.sha256(token_s).hexdigest()
        return token

class MockSession(Session):

    def __init__(self, request, name = "mock", *args, **kwargs):
        Session.__init__(self, name = name, *args, **kwargs)
        self.request = request

    def __setitem__(self, key, value):
        session_c = self.request.session_c
        session = session_c.new()
        self.request.session = session
        return session.__setitem__(key, value)

class MemorySession(Session):

    SESSIONS = {}
    """ Global static sessions map where all the
    (in-memory) session instances are going to be
    stored to be latter retrieved """

    def __init__(self, name = "session", *args, **kwargs):
        Session.__init__(self, name = name, *args, **kwargs)
        self.data = {}

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def __delitem__(self, key):
        return self.data.__delitem__(key)

    @classmethod
    def new(cls):
        session = cls()
        cls.SESSIONS[session.sid] = session
        return session

    @classmethod
    def get_s(cls, sid):
        session = cls.SESSIONS.get(sid, None)
        return session

class FileSession(Session):

    SHELVE = None

    def __init__(self, name = "file", *args, **kwargs):
        Session.__init__(self, name = name, *args, **kwargs)
        self.data = {}

    @classmethod
    def new(cls):
        if not cls.SHELVE: cls.open()
        session = cls()
        cls.SHELVE[session.sid] = session
        return session

    @classmethod
    def get_s(cls, sid):
        if not cls.SHELVE: cls.open()
        session = cls.SHELVE.get(sid, None)
        return session

    @classmethod
    def open(cls, file = "session.shelve"):
        cls.SHELVE = shelve.open(file)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def __delitem__(self, key):
        return self.data.__delitem__(key)

    def flush(self):
        cls = self.__class__
        cls.SHELVE.sync()

class RedisSession(Session):
    pass
