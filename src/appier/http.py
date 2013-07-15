#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
import logging

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
