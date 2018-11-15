#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2018 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import time
import uuid
import hmac
import zlib
import pickle
import shelve
import base64
import hashlib
import datetime

from . import config
from . import legacy
from . import redisdb
from . import exceptions

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

    def __init__(
        self,
        name = "session",
        expire = EXPIRE_TIME,
        sid = None,
        address = None,
        growing = True
    ):
        object.__init__(self)
        self.sid = sid if sid else self._gen_sid()
        self.name = name
        self.address = address
        self.create = time.time()
        self.modify = self.create
        self.duration = self._to_seconds(expire)
        self.expire = self.create + self.duration
        self.growing = growing
        self.dirty = True
        self.transient = dict()

    def __len__(self):
        return self.transient.__len__()

    def __getitem__(self, key):
        return self.transient.__getitem__(key)

    def __setitem__(self, key, value):
        self.mark(extend = self.growing)
        self.transient.__setitem__(key, value)

    def __delitem__(self, key):
        self.mark(extend = self.growing)
        self.transient.__delitem__(key)

    def __iter__(self):
        return self.transient.__iter__()

    def __contains__(self, item):
        return self.transient.__contains__(item)

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    def __getstate__(self):
        return dict(
            sid = self.sid,
            name = self.name,
            address = self.address,
            create = self.create,
            modify = self.modify,
            duration = self.duration,
            expire = self.expire,
            growing = self.growing,
            dirty = self.dirty
        )

    def __setstate__(self, state):
        for name in (
            "sid",
            "name",
            "address",
            "create",
            "modify",
            "duration",
            "expire",
            "growing",
            "dirty"
        ):
            value = state.get(name, None)
            setattr(self, name, value)
        self.transient = dict()

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(*args, **kwargs)

    @classmethod
    def get_s(cls, sid, request = None):
        return cls()

    @classmethod
    def expire(self, sid):
        pass

    @classmethod
    def count(cls):
        return 0

    @classmethod
    def all(cls):
        return {}

    @classmethod
    def open(cls):
        cls.gc()

    @classmethod
    def close(cls):
        pass

    @classmethod
    def empty(cls):
        pass

    @classmethod
    def gc(cls):
        pass

    def keys(self):
        return ()

    def iterkeys(self):
        return self.keys()

    def values(self):
        return ()

    def itervalues(self):
        return self.values()

    def items(self):
        return ()

    def iteritems(self):
        return self.items()

    def pop(self, key, default = None):
        if not key in self: return default
        value = self[key]
        del self[key]
        return value

    def start(self):
        pass

    def flush(self, request = None):
        self.mark(dirty = False)

    def mark(self, dirty = True, extend = False):
        self.dirty = dirty
        if extend: self.extend()

    def extend(self, duration = None):
        duration = duration or self.duration
        if not duration: return
        self.modify = time.time()
        self.duration = duration
        self.expire = self.modify + duration
        self.mark()
        return self.expire

    def is_expired(self):
        has_expire = hasattr(self, "expire")
        if not has_expire: return False

        current = time.time()
        return current >= self.expire

    def is_dirty(self):
        if not hasattr(self, "dirty"): return True
        return self.dirty

    def ensure(self, *args, **kwargs):
        return self

    def get(self, key, default = None):
        try: value = self.__getitem__(key)
        except KeyError: value = default
        return value

    def set(self, key, value):
        self.__setitem__(key, value)

    def delete(self, key, force = False):
        if not force and not key in self: return
        self.__delitem__(key)

    def get_t(self, key, default = None):
        try: value = self.transient[key]
        except KeyError: value = default
        return value

    def set_t(self, key, value):
        self.transient[key] = value

    def delete_t(self, key, force = False):
        if not force and not key in self.transient: return
        del self.transient[key]

    def timeout(self):
        current = time.time()
        return self.expire - current

    def _gen_sid(self):
        token_s = str(uuid.uuid4())
        token_s = legacy.bytes(token_s)
        token = hashlib.sha256(token_s).hexdigest()
        return token

    def _to_seconds(self, delta):
        return (delta.microseconds +
            (delta.seconds + delta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

class MockSession(Session):
    """
    Temporary mock session to be used while no final
    session is yet defined in the request, this is a
    special case of a session and should not comply
    with the pre-defined standard operations.
    """

    def __init__(self, request, name = "mock", *args, **kwargs):
        Session.__init__(self, name = name, *args, **kwargs)
        self.request = request

    def __setitem__(self, key, value):
        session = self.ensure(
            sid = self.sid,
            address = self.address
        )
        return session.__setitem__(key, value)

    def __setstate__(self, state):
        Session.__setstate__(self, state)
        self.request = None

    def ensure(self, *args, **kwargs):
        self._ensure_names(kwargs)
        session_c = self.request.session_c
        session = session_c.new(*args, **kwargs)
        self.request.session = session
        self.request.set_cookie = "sid=%s" % session.sid
        return session

    def _ensure_names(self, kwargs):
        for name in ("sid", "address"):
            if name in kwargs: continue
            kwargs[name] = getattr(self, name)

class DataSession(Session):

    def __init__(self, *args, **kwargs):
        Session.__init__(self, *args, **kwargs)
        self.data = {}

    def __len__(self):
        return Session.__len__(self) + self.data.__len__()

    def __getitem__(self, key):
        try: return self.data.__getitem__(key)
        except KeyError: return Session.__getitem__(self, key)

    def __setitem__(self, key, value):
        self.mark(extend = self.growing)
        return self.data.__setitem__(key, value)

    def __delitem__(self, key):
        try:
            self.mark(extend = self.growing)
            return self.data.__delitem__(key)
        except KeyError:
            return Session.__delitem__(self, key)

    def __iter__(self):
        return self._merged.__iter__()

    def __contains__(self, item):
        return Session.__contains__(self, item) or\
            self.data.__contains__(item)

    def __getstate__(self):
        state = Session.__getstate__(self)
        state.update(
            data = self.data
        )
        return state

    def __setstate__(self, state):
        Session.__setstate__(self, state)
        for name in ("data",):
            setattr(self, name, state[name])

    def keys(self):
        return self._merged.keys()

    def values(self):
        return self._merged.values()

    def items(self):
        return self._merged.items()

    def sorted(self):
        keys = self.keys()
        keys = list(keys)
        keys.sort()
        return keys

    @property
    def _merged(self):
        if not self.transient: return self.data
        if not self.data: return self.transient
        merged = dict()
        merged.update(self.transient)
        merged.update(self.data)
        return merged

class MemorySession(DataSession):

    SESSIONS = {}
    """ Global static sessions map where all the
    (in-memory) session instances are going to be
    stored to be latter retrieved """

    def __init__(self, name = "session", *args, **kwargs):
        DataSession.__init__(self, name = name, *args, **kwargs)
        self["sid"] = self.sid

    @classmethod
    def new(cls, *args, **kwargs):
        session = cls(*args, **kwargs)
        cls.SESSIONS[session.sid] = session.__getstate__()
        return session

    @classmethod
    def get_s(cls, sid, request = None):
        state = cls.SESSIONS.get(sid, None)
        if not state: return state
        session = cls.__new__(cls)
        session.__setstate__(state)
        is_expired = session.is_expired()
        if is_expired: cls.expire(sid)
        session = None if is_expired else session
        return session

    @classmethod
    def expire(cls, sid):
        del cls.SESSIONS[sid]

    @classmethod
    def count(cls):
        return len(cls.SESSIONS)

    @classmethod
    def all(cls):
        return cls.SESSIONS

    @classmethod
    def empty(cls):
        cls.SESSIONS.empty()

class FileSession(DataSession):
    """
    Shelve based file system session engine that store the
    session information in a single file.

    This session engine should be used carefully as race
    conditions in the file access may corrupt its contents,
    thus making it not suitable for multi-threaded or multi-
    process environments.
    """

    SHELVE = None
    """ Global shelve object reference should reflect the
    result of opening a file in shelve mode, this is a global
    object and only one instance should exist per process """

    def __init__(self, name = "file", *args, **kwargs):
        DataSession.__init__(self, name = name, *args, **kwargs)
        self["sid"] = self.sid

    @classmethod
    def new(cls, *args, **kwargs):
        if cls.SHELVE == None: cls.open()
        session = cls(*args, **kwargs)
        cls.SHELVE[session.sid] = session
        return session

    @classmethod
    def get_s(cls, sid, request = None):
        if cls.SHELVE == None: cls.open()
        session = cls.SHELVE.get(sid, None)
        if not session: return session
        is_expired = session.is_expired()
        if is_expired: cls.expire(sid)
        session = None if is_expired else session
        return session

    @classmethod
    def expire(cls, sid):
        del cls.SHELVE[sid]

    @classmethod
    def count(cls):
        return len(cls.SHELVE)

    @classmethod
    def all(cls):
        return cls.SHELVE

    @classmethod
    def open(cls, file_path = "session.shelve"):
        base_path = config.conf("APPIER_BASE_PATH", "")
        base_path = config.conf("SESSION_FILE_PATH", base_path)
        if base_path and not os.path.exists(base_path): os.makedirs(base_path)
        base_path = os.path.expanduser(base_path)
        base_path = os.path.abspath(base_path)
        base_path = os.path.normpath(base_path)
        file_path = os.path.join(base_path, file_path)
        cls.SHELVE = shelve.open(
            file_path,
            protocol = 2,
            writeback = True
        )
        cls.gc()

    @classmethod
    def close(cls):
        if not cls.SHELVE: return
        cls.SHELVE.close()
        cls.SHELVE = None

    @classmethod
    def empty(cls):
        for sid in cls.SHELVE: del cls.SHELVE[sid]

    @classmethod
    def gc(cls):
        for sid in cls.SHELVE:
            session = cls.SHELVE.get(sid, None)
            is_expired = session.is_expired()
            if is_expired: cls.expire(sid)

    @classmethod
    def db_type(cls):
        shelve_cls = type(cls.SHELVE.dict)
        shelve_dbm = shelve_cls.__name__
        return shelve_dbm

    @classmethod
    def db_secure(cls):
        return cls.db_type() == "dbm"

    def flush(self, request = None, secure = None):
        if not self.is_dirty(): return
        self.mark(dirty = False)
        self.sync(secure = secure)

    def sync(self, secure = None):
        cls = self.__class__
        if secure == None:
            secure = cls.db_secure()
        if secure:
            cls.SHELVE.close()
            cls.open()
        else:
            cls.SHELVE.sync()

class RedisSession(DataSession):

    REDIS = None
    """ Global shelve object reference should reflect the
    result of opening a file in shelve mode, this is a global
    object and only one instance should exist per process """

    SERIALIZER = pickle
    """ The serializer to be used for the values contained in
    the session (used on top of the class) """

    def __init__(self, name = "redis", *args, **kwargs):
        DataSession.__init__(self, name = name, *args, **kwargs)
        self["sid"] = self.sid

    @classmethod
    def new(cls, *args, **kwargs):
        if cls.REDIS == None: cls.open()
        session = cls(*args, **kwargs)
        data = cls.SERIALIZER.dumps(session)
        timeout = session.timeout()
        timeout = int(timeout)
        cls.REDIS.setex(
            session.sid,
            value = data,
            time = timeout
        )
        return session

    @classmethod
    def get_s(cls, sid, request = None):
        if cls.REDIS == None: cls.open()
        data = cls.REDIS.get(sid)
        if not data: return data
        session = cls.SERIALIZER.loads(data)
        is_expired = session.is_expired()
        if is_expired: cls.expire(sid)
        session = None if is_expired else session
        return session

    @classmethod
    def expire(cls, sid):
        cls.REDIS.delete(sid)

    @classmethod
    def count(cls):
        if cls.REDIS == None: cls.open()
        return cls.REDIS.dbsize()

    @classmethod
    def all(cls):
        if cls.REDIS == None: cls.open()
        sessions = dict()
        sids = cls.REDIS.keys()
        for sid in sids:
            data = cls.REDIS.get(sid)
            try: session = cls.SERIALIZER.loads(data)
            except: continue
            sessions[sid] = session
        return sessions

    @classmethod
    def open(cls):
        cls.REDIS = redisdb.get_connection()

    @classmethod
    def empty(cls):
        if cls.REDIS == None: cls.open()
        cls.REDIS.flushdb()

    def flush(self, request = None):
        if not self.is_dirty(): return
        self.mark(dirty = False)
        cls = self.__class__
        data = cls.SERIALIZER.dumps(self)
        timeout = self.timeout()
        timeout = int(timeout)
        cls.REDIS.setex(
            self.sid,
            value = data,
            time = timeout
        )

class ClientSession(DataSession):
    """
    Client side based session, that used encryption to store the
    complete set of information for the session on the client side
    through the usage of cookies.

    This session class provides extreme scalability as every server
    instance is independent and does not require inter-communication.
    """

    SERIALIZER = pickle
    """ The serializer to be used for the values contained in
    the session (used on top of the class) """

    COOKIE_LIMIT = 4096
    """ The limit (in bytes) of a cookie to be properly handled
    by most of the modern web browsers """

    def __init__(self, name = "client", *args, **kwargs):
        DataSession.__init__(self, name = name, *args, **kwargs)
        self["sid"] = self.sid

    @classmethod
    def get_s(cls, sid, request = None):
        data_b64 = request.cookies.get("session", None)
        if not data_b64: return None
        data = base64.b64decode(data_b64)
        data = zlib.decompress(data)
        data = cls._verify(data, request)
        session = cls.SERIALIZER.loads(data)
        is_expired = session.is_expired()
        if is_expired: cls.expire(sid)
        session = None if is_expired else session
        return session

    @classmethod
    def _sign(cls, data, request):
        secret = cls._secret(request)
        secret = legacy.bytes(secret)
        digest = hmac.new(secret, data).hexdigest()
        digest = legacy.bytes(digest)
        data = digest + b":" + data
        return data

    @classmethod
    def _verify(cls, data, request):
        secret = cls._secret(request)
        secret = legacy.bytes(secret)
        digest, data = data.split(b":", 1)
        expected = hmac.new(secret, data).hexdigest()
        expected = legacy.bytes(expected)
        valid = digest == expected
        if not valid: raise exceptions.SecurityError(
            message = "Invalid signature for message"
        )
        return data

    @classmethod
    def _secret(cls, request):
        owner = request.owner
        if not hasattr(owner, "secret"): return None
        return owner.secret

    def flush(self, request = None):
        cls = self.__class__
        if not self.is_dirty(): return
        self.mark(dirty = False)
        cls = self.__class__
        data = cls.SERIALIZER.dumps(self)
        data = cls._sign(data, request)
        data = zlib.compress(data)
        data_b64 = base64.b64encode(data)
        data_b64 = legacy.str(data_b64)
        valid = len(data_b64) <= cls.COOKIE_LIMIT
        if not valid: raise exceptions.OperationalError(
            message = "Session payload size over cookie limit"
        )
        request.set_cookie = "session=%s" % data_b64
