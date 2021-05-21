#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2021 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2021 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import sys
import gzip

from . import http
from . import util
from . import legacy

class GeoResolver(object):

    DB_NAME = "GeoLite2-City.mmdb"
    """ The name of the file that contains the GeoIP
    information database (to be used in execution) """

    DOWNLOAD_URL = "https://files.bemisc.com/maxmind/GeoLite2-City.mmdb.gz"
    """ The URL to the Gzip compressed version of the
    GeoIP city database used for geo resolution """

    VALID = ("continent", "country", "city", "location")
    """ The sequence of names that are considered to be valid
    under the simplified representation model """

    PREFIXES = ("", "~/", "/")
    """ The various prefixes that are going to be used in the
    search for the GeoIP database file, the order in which
    they are defined as they are search from the beginning """

    _db = None
    """ The reference to the internal database reference object
    that is going to be used in the GeoIP resolution """

    @classmethod
    def resolve(cls, address, simplified = True):
        db = cls._get_db()
        if not db: return None
        result = db.get(address)
        if simplified: result = cls._simplify(result)
        return result

    @classmethod
    def _simplify(cls, result, locale = "en", valid = VALID):
        if not result: return result
        for name, value in legacy.items(result):
            if not name in valid: del result[name]
            if not "names" in value: continue
            names = value["names"]
            value["name"] = names.get(locale, None)
            del value["names"]
        return result

    @classmethod
    def _get_db(cls):
        if cls._db: return cls._db
        maxminddb = util.import_pip("maxminddb")
        if not maxminddb: return None
        path = cls._try_all()
        if not path: return None
        cls._db = maxminddb.open_database(path)
        return cls._db

    @classmethod
    def _try_all(cls, prefixes = PREFIXES):
        for prefix in cls.PREFIXES:
            path = cls._try_db(path = prefix + cls.DB_NAME)
            if path: return path
        path = cls._try_db(path = cls.DB_NAME, download = True)
        if path: return path
        return None

    @classmethod
    def _try_db(cls, path = DB_NAME, download = False):
        path = os.path.expanduser(path)
        path = os.path.normpath(path)
        exists = os.path.exists(path)
        if exists: return path
        if not download: return None
        cls._download_db(path = path)
        exists = os.path.exists(path)
        if not exists: return None
        return path

    @classmethod
    def _download_db(cls, path = DB_NAME):
        contents = http.get(cls.DOWNLOAD_URL)
        cls._store_db(contents, path = path)

    @classmethod
    def _store_db(cls, contents, path = DB_NAME):
        path_gz = path + ".gz"
        file = open(path_gz, "wb")
        try: file.write(contents)
        finally: file.close()
        file = gzip.open(path_gz, "rb")
        try: contents = file.read()
        finally: file.close()
        file = open(path, "wb")
        try: file.write(contents)
        finally: file.close()
        os.remove(path_gz)
        return path

if __name__ == "__main__":
    prefix = "~/"
    if len(sys.argv) > 1: prefix = sys.argv[1]
    if not prefix.endswith("/"): prefix += "/"
    GeoResolver._try_db(
        path = prefix + GeoResolver.DB_NAME,
        download = True
    )
else:
    __path__ = []
