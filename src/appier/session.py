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
import hashlib

import exceptions

class Session(object):
    """
    Abstract session class to be used as a reference in
    the implementation of the proper classes.

    Some of the global functionality may be abstracted
    under this class and reused in the concrete classes.
    """

    def __init__(self, name = "session"):
        object.__init__(self)
        self.id = self._gen_id()
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
    def get_s(cls, id):
        return cls()

    def start(self):
        pass

    def flush(self):
        pass

    def _gen_id(self):
        token_s = str(uuid.uuid4())
        token = hashlib.sha256(token_s).hexdigest()
        return token

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
        cls.SESSIONS[session.id] = session
        return session

    @classmethod
    def get_s(cls, id):
        session = cls.SESSIONS.get(id, None)
        if not session: raise exceptions.OperationalError(
            message = "no in memory session found for id '%'" % id
        )
        return session

class FileSession(Session):

    def __init__(self, name = "file", *args, **kwargs):
        Session.__init__(self, name = name, *args, **kwargs)
        #shelve.open(filename, flag='c', protocol=None, writeback=False)

class RedisSession(Session):
    pass
