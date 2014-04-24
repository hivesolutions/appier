#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2014 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import csv
import uuid

from appier import model
from appier import legacy
from appier import typesf

def serialize(obj):
    if isinstance(obj, model.Model): return obj.model
    if isinstance(obj, typesf.Type): return obj.json_v()
    if type(obj) == type(None): return ""
    return legacy.UNICODE(obj)

def serialize_csv(items, encoding = "utf-8"):
    if not items: raise RuntimeError("Empty object provided")

    encoder = build_encoder(encoding)

    keys = items[0].keys()
    keys = legacy.eager(keys)
    keys.sort()

    keys_row = [encoder(key) if type(key) == legacy.UNICODE else\
        key for key in keys]

    buffer = legacy.StringIO()
    writer = csv.writer(buffer, delimiter = ";")
    writer.writerow(keys_row)

    for item in items:
        row = []
        for key in keys:
            value = item[key]
            value = serialize(value)
            is_unicode = type(value) == legacy.UNICODE
            if is_unicode: value = encoder(value)
            row.append(value)
        writer.writerow(row)

    result = buffer.getvalue()
    return result

def serialize_ics(items, encoding = "utf-8"):
    encoder = build_encoder(encoding)

    buffer = legacy.StringIO()
    buffer.write("BEGIN:VCALENDAR\r\n")
    buffer.write("METHOD:PUBLISH\r\n")
    buffer.write("X-WR-TIMEZONE:America/Los_Angeles\r\n")
    buffer.write("CALSCALE:GREGORIAN\r\n")
    buffer.write("VERSION:2.0\r\n")
    buffer.write("PRODID:-//PUC Calendar// v2.0//EN)\r\n")

    for item in items:
        start = item["start"]
        end = item["end"]
        description = item["description"]
        location = item["location"]
        timezone = item.get("timezone", "Etc/GMT")
        _uuid = item.get("uuid", None)
        _uuid = _uuid or str(uuid.uuid4())

        start = encoder(start)
        end = encoder(end)
        description = encoder(description)
        location = encoder(location)
        timezone = encoder(timezone)
        _uuid = encoder(_uuid)

        buffer.write("BEGIN:VEVENT\r\n")
        buffer.write("UID:%s\r\n" % _uuid)
        buffer.write("TZID:%s\r\n" % timezone)
        buffer.write("DTSTART:%s\r\n" % start)
        buffer.write("DTEND:%s\r\n" % end)
        buffer.write("DTSTAMP:%s\r\n" % start)
        buffer.write("SUMMARY:%s\r\n" % description)
        buffer.write("LOCATION:%s\r\n" % location)
        buffer.write("END:VEVENT\r\n")

    buffer.write("END:VCALENDAR\r\n")

    result = buffer.getvalue()
    return result

def build_encoder(encoding):
    if legacy.PYTHON_3: return lambda v: v
    else: return lambda v: v if v == None else v.encode(encoding)
