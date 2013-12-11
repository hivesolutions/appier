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

import json
import types
import string
import random
import urllib
import urllib2
import logging

import exceptions

RANGE = string.ascii_letters + string.digits
""" The range of characters that are going to be used in
the generation of the boundary value for the mime """

SEQUENCE_TYPES = (types.ListType, types.TupleType)
""" The sequence defining the various types that are
considered to be sequence based for python """

def try_auth(auth_callback, params):
    if not auth_callback: raise
    auth_callback(params)

def get(url, params = None, auth_callback = None):
    return _method(
        _get,
        url,
        params = params,
        auth_callback = auth_callback
    )

def post(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    mime = None,
    auth_callback = None
):
    return _method(
        _post,
        url,
        params = params,
        data = data,
        data_j = data_j,
        data_m = data_m,
        mime = mime,
        auth_callback = auth_callback
    )

def put(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    mime = None,
    auth_callback = None
):
    return _method(
        _put,
        url,
        params = params,
        data = data,
        data_j = data_j,
        data_m = data_m,
        mime = mime,
        auth_callback = auth_callback
    )

def delete(url, params = None, auth_callback = None):
    return _method(
        _delete,
        url,
        params = params,
        auth_callback = auth_callback
    )

def _method(method, *args, **kwargs):
    try:
        auth_callback = kwargs.get("auth_callback", None)
        if "auth_callback" in kwargs: del kwargs["auth_callback"]
        result = method(*args, **kwargs)
    except urllib2.HTTPError, error:
        try:
            params = kwargs.get("params", None)
            if not error.code == 403: raise
            try_auth(auth_callback, params)
            result = method(*args, **kwargs)
        except urllib2.HTTPError, error:
            raise exceptions.HTTPError(error)

    return result

def _get(url, params = {}):
    values = params or {}

    logging.info("GET %s with '%s'" % (url, str(values)))

    data = _urlencode(values)
    url = url + "?" + data
    file = urllib2.urlopen(url)
    try: result = file.read()
    finally: file.close()

    code = file.getcode()
    logging.info("GET %s returned '%d'" % (url, code))

    result_j = json.loads(result)
    return result_j

def _post(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    mime = None
):
    values = params or {}

    logging.info("POST %s with '%s'" % (url, str(values)))

    data_e = _urlencode(values)

    if data:
        url = url + "?" + data_e
    elif data_j:
        data = json.dumps(data_j)
        url = url + "?" + data_e
        mime = mime or "application/json"
    elif data_m:
        url = url + "?" + data_e
        content_type, data = _encode_multipart(data_m, doseq = True)
        mime = mime or content_type
    elif data_e:
        data = data_e
        mime = mime or "application/x-www-form-urlencoded"

    length = len(data) if data else 0

    headers = dict()
    headers["Content-Length"] = length
    if mime: headers["Content-Type"] = mime

    request = urllib2.Request(url, data, headers)
    file = urllib2.urlopen(request)
    try: result = file.read()
    finally: file.close()

    code = file.getcode()
    logging.info("POST %s returned '%d'" % (url, code))

    result_j = json.loads(result)
    return result_j

def _put(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    mime = None
):
    values = params or {}

    logging.info("PUT %s with '%s'" % (url, str(params)))

    data_e = _urlencode(values)

    if data:
        url = url + "?" + data_e
    elif data_j:
        data = json.dumps(data_j)
        url = url + "?" + data_e
        mime = mime or "application/json"
    elif data_m:
        url = url + "?" + data_e
        content_type, data = _encode_multipart(data_m, doseq = True)
        mime = mime or content_type
    elif data_e:
        data = data_e
        mime = mime or "application/x-www-form-urlencoded"

    length = len(data) if data else 0

    headers = dict()
    headers["Content-Length"] = length
    if mime: headers["Content-Type"] = mime

    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data, headers)
    request.get_method = lambda: "PUT"
    file = opener.open(request)
    try: result = file.read()
    finally: file.close()

    code = file.getcode()
    logging.info("POST %s returned '%d'" % (url, code))

    result_j = json.loads(result)
    return result_j

def _delete(url, params = None):
    values = params or {}

    logging.info("DELETE %s with '%s'" % (url, str(values)))

    data = _urlencode(values)
    url = url + "?" + data
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url)
    request.get_method = lambda: "DELETE"
    file = opener.open(request)
    try: result = file.read()
    finally: file.close()

    code = file.getcode()
    logging.info("DELETE %s returned '%d'" % (url, code))

    result_j = json.loads(result)
    return result_j

def _urlencode(values):
    # creates the dictionary that will hold the final
    # dictionary of values (without the unset and´
    # invalid values)
    final = dict()

    # iterates over all the items in the values map to
    # try to filter the values that are not valid
    for key, value in values.iteritems():
        # creates the list that will hold the valid values
        # of the current key in iteration (sanitized values)
        _values = []

        # verifies the type of the current value and in case
        # it's sequence based converts it into a list using
        # the conversion method otherwise creates a new list
        # and includes the value in it
        value_t = type(value)
        if value_t in SEQUENCE_TYPES: value = list(value)
        else: value = [value]

        # iterates over all the values in the current sequence
        # and adds the valid values to the sanitized sequence
        for _value in value:
            if _value == None: continue
            _values.append(_value)

        # sets the sanitized list of values as the new value for
        # the key in the final dictionary of values
        final[key] = _values

    # runs the encoding with sequence support on the final map
    # of sanitized values and returns the encoded result to the
    # caller method as the encoded value
    return urllib.urlencode(final, doseq = True)

def _encode_multipart(fields, doseq = False):
    boundary = _create_boundary(fields, doseq = doseq)
    buffer = []

    for key, values in fields.iteritems():
        is_list = doseq and type(values) == types.ListType
        values = values if is_list else [values]

        for value in values:
            value_t = type(value)

            if value_t == types.TupleType: is_file = True
            else: is_file = False

            if is_file:
                header = "Content-Disposition: form-data; name=\"%s\"; filename=\"%s\"" %\
                    (key, value[0])
                value = value[1]
            else:
                header = "Content-Disposition: form-data; name=\"%s\"" % key
                value = unicode(value).encode("utf-8")

            buffer.append("--" + boundary)
            buffer.append(header)
            buffer.append("")
            buffer.append(value)

    buffer.append("--" + boundary + "--")
    buffer.append("")
    body = "\r\n".join(buffer)
    content_type = "multipart/form-data; boundary=%s" % boundary

    return content_type, body

def _create_boundary(fields, size = 32, doseq = False):
    while True:
        base = "".join(random.choice(RANGE) for _value in range(size))
        boundary = "----------" + base
        result = _try_boundary(fields, boundary, doseq = doseq)
        if result: break

    return boundary

def _try_boundary(fields, boundary, doseq = False):
    for key, values in fields.iteritems():
        is_list = doseq and type(values) == types.ListType
        values = values if is_list else [values]

        for value in values:
            value_t = type(value)

            if value_t == types.TupleType: is_file = True
            else: is_file = False

            if is_file: name = value[0]; value = value[1]
            else: name = ""; value = unicode(value).encode("utf-8")

            if not key.find(boundary) == -1: return False
            if not name.find(boundary) == -1: return False
            if not value.find(boundary) == -1: return False

    return True
