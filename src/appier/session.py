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

import time
import uuid
import shelve
import hashlib
import datetime

EXPIRE_TIME = datetime.timedelta(days = 31)
""" The default expire time to be used in new sessions
in case no expire time is provided to the creation of
the session instance """

class Session(object):
    """
    Abstract session class to be used as a reference in
    the implementation of the proper classes.

    Some of the global functionality may be abstracted
    under this class and reused in the concrete classes.
    """

    def __init__(self, name = "session", expire = EXPIRE_TIME):
        object.__init__(self)
        self.sid = self._gen_sid()
        self.name = name
        self.expire = time.time() + self._to_seconds(expire)

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return None

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __contains__(self, item):
        return False

    def __nonzero__(self):
        return True

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def get_s(cls, sid):
        return cls()

    def start(self):
        pass

    def flush(self):
        pass

    def is_expired(self):
        has_expire = hasattr(self, "expire")
        if not has_expire: return False

        current = time.time()
        return current >= self.expire

    def ensure(self, *args, **kwargs):
        return self

    def get(self, key, default = None):
        try: value = self.__getitem__(key)
        except KeyError: value = default
        return value

    def _gen_sid(self):
        token_s = str(uuid.uuid4())
        token = hashlib.sha256(token_s).hexdigest()
        return token

    def _to_seconds(self, delta):
        return (delta.microseconds +
            (delta.seconds + delta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

class MockSession(Session):

    def __init__(self, request, name = "mock", *args, **kwargs):
        Session.__init__(self, name = name, *args, **kwargs)
        self.request = request

    def __setitem__(self, key, value):
        session = self.ensure()
        return session.__setitem__(key, value)

    def ensure(self, *args, **kwargs):
        session_c = self.request.session_c
        session = session_c.new(*args, **kwargs)
        self.request.session = session
        self.request.set_cookie = "sid=%s" % session.sid
        return session

class MemorySession(Session):

    SESSIONS = {}
    """ Global static sessions map where all the
    (in-memory) session instances are going to be
    stored to be latter retrieved """

    def __init__(self, name = "session", *args, **kwargs):
        Session.__init__(self, name = name, *args, **kwargs)
        self.data = {}
        self["sid"] = self.sid

    def __len__(self):
        return self.data.__len__()

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def __delitem__(self, key):
        return self.data.__delitem__(key)

    def __contains__(self, item):
        return self.data.__contains__(item)

    @classmethod
    def new(cls, *args, **kwargs):
        session = cls(*args, **kwargs)
        cls.SESSIONS[session.sid] = session
        return session

    @classmethod
    def get_s(cls, sid):
        session = cls.SESSIONS.get(sid, None)
        if not session: return session
        is_expired = session.is_expired()
        if is_expired: del cls.SESSIONS[sid]
        session = None if is_expired else session
        return session

class FileSession(Session):

    SHELVE = None
    """ Global shelve object reference should reflect the
    result of opening a file in shelve mode, this is a global
    object and only one instance should exist per process """

    def __init__(self, name = "file", *args, **kwargs):
        Session.__init__(self, name = name, *args, **kwargs)
        self.data = {}
        self["sid"] = self.sid

    @classmethod
    def new(cls, *args, **kwargs):
        if not cls.SHELVE: cls.open()
        session = cls(*args, **kwargs)
        cls.SHELVE[session.sid] = session
        return session

    @classmethod
    def get_s(cls, sid):
        if not cls.SHELVE: cls.open()
        session = cls.SHELVE.get(sid, None)
        if not session: return session
        is_expired = session.is_expired()
        if is_expired: del cls.SHELVE[sid]
        session = None if is_expired else session
        return session

    @classmethod
    def open(cls, file = "session.shelve"):
        cls.SHELVE = shelve.open(file, writeback = True)

    @classmethod
    def close(cls):
        cls.SHELVE.close()
        cls.SHELVE = None

    def __len__(self):
        return self.data.__len__()

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def __delitem__(self, key):
        return self.data.__delitem__(key)

    def __contains__(self, item):
        return self.data.__contains__(item)

    def flush(self):
        cls = self.__class__
        cls.SHELVE.sync()

class RedisSession(Session):
    pass
