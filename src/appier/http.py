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
import urllib
import urllib2
import logging

def get(url, params = {}):
    logging.info("GET %s with '%s'" % (url, str(params)))

    params_e = urllib.urlencode(params)
    file = urllib2.urlopen(url + "?" + params_e)
    try: result = file.read()
    finally: file.close()

    logging.info("GET %s returned '%s'" % (url, result))

    result_j = json.loads(result)
    return result_j

def post(url, data_j = {}, params = {}):
    logging.info("POST %s with '%s'" % (url, str(params)))

    data = json.dumps(data_j)

    headers = {
        "Content-Type" : "application/json",
        "Content-Length" : "%d" % len(data)
    }

    params_e = urllib.urlencode(params)
    request = urllib2.Request(url + "?" + params_e, data, headers)
    file = urllib2.urlopen(request)
    try: result = file.read()
    finally: file.close()

    logging.info("POST %s returned '%s'" % (url, result))

    result_j = json.loads(result)
    return result_j

def put(url, data_j = {}, params = {}):
    logging.info("PUT %s with '%s'" % (url, str(params)))

    data = json.dumps(data_j)

    headers = {
        "Content-Type" : "application/json",
        "Content-Length" : "%d" % len(data)
    }

    params_e = urllib.urlencode(params)
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url + "?" + params_e, data, headers)
    request.get_method = lambda: "PUT"
    file = opener.open(request)
    try: result = file.read()
    finally: file.close()

    logging.info("POST %s returned '%s'" % (url, result))

    result_j = json.loads(result)
    return result_j

def delete(url, params = {}):
    logging.info("DELETE %s with '%s'" % (url, str(params)))

    params_e = urllib.urlencode(params)
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url + "?" + params_e)
    request.get_method = lambda: "DELETE"
    file = opener.open(request)
    try: result = file.read()
    finally: file.close()

    logging.info("DELETE %s returned '%s'" % (url, result))

    result_j = json.loads(result)
    return result_j
