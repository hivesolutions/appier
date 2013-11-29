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

import re
import copy
import base
import datetime

import util
import mongo
import exceptions

EMAIL_REGEX_VALUE = "^[\w\d\._%+-]+@[\w\d\.\-]+$"
""" The email regex value used to validate
if the provided value is in fact an email """

URL_REGEX_VALUE = "^\w+\:\/\/[^\:\/\?#]+(\:\d+)?(\/[^\?#]+)*\/?(\?[^#]*)?(#.*)?$"
""" The url regex value used to validate
if the provided value is in fact an URL/URI """

EMAIL_REGEX = re.compile(EMAIL_REGEX_VALUE)
""" The email regex used to validate
if the provided value is in fact an email """

URL_REGEX = re.compile(URL_REGEX_VALUE)
""" The url regex used to validate
if the provided value is in fact an URL/URI """

def validate(method = None, methods = [], object = None, build = True):
    # retrieves the base request object that is going to be used in
    # the construction of the object
    request = base.get_request()

    # uses the provided method to retrieves the complete
    # set of methods to be used for validation, this provides
    # an extra level of indirection
    methods = method and method() or methods
    errors = []

    # verifies if the provided object is valid in such case creates
    # a copy of it and uses it as the base object for validation
    # otherwise used an empty map (form validation)
    object = object and copy.copy(object) or {}

    # in case the build flag is set must process the received request
    # to correctly retrieve populate the object from it
    if build:
        # retrieves the current request data and tries to
        # "load" it as json data, in case it fails gracefully
        # handles the failure setting the value as an empty map
        data_j = util.request_json()

        # uses all the values referencing data in the request to try
        # to populate the object this way it may be constructed using
        # any of theses strategies (easier for the developer)
        for name, value in data_j.iteritems(): object[name] = value
        for name, value in request.files_s.iteritems(): object[name] = value
        for name, value in request.post_s.iteritems(): object[name] = value
        for name, value in request.params_s.iteritems(): object[name] = value

    for method in methods:
        try: method(object)
        except exceptions.ValidationInternalError, error:
            errors.append((error.name, error.message))

    errors_map = {}
    for name, message in errors:
        if not name in errors_map: errors_map[name] = []
        _errors = errors_map[name]
        _errors.append(message)

    return errors_map, object

def validate_b(method = None, methods = [], object = None, build = True):
    errors_map, object = validate(
        method = method,
        methods = methods,
        object = object,
        build = build
    )
    result = False if errors_map else True
    return result

def eq(name, value_c):
    def validation(object):
        value = object.get(name, None)
        if value == value_c: return True
        raise exceptions.ValidationInternalError(
            name, "must be equal to %s" % str(value_c)
        )
    return validation

def gt(name, value_c):
    def validation(object):
        value = object.get(name, None)
        if value > value_c: return True
        raise exceptions.ValidationInternalError(
            name, "must be greater than %s" % str(value_c)
        )
    return validation

def gte(name, value_c):
    def validation(object):
        value = object.get(name, None)
        if value >= value_c: return True
        raise exceptions.ValidationInternalError(
            name, "must be greater than or equal to %s" % str(value_c)
        )
    return validation

def lt(name, value_c):
    def validation(object):
        value = object.get(name, None)
        if value < value_c: return True
        raise exceptions.ValidationInternalError(
            name, "must be less than %s" % str(value_c)
        )
    return validation

def lte(name, value_c):
    def validation(object):
        value = object.get(name, None)
        if value <= value_c: return True
        raise exceptions.ValidationInternalError(
            name, "must be less than or equal to %s" % str(value_c)
        )
    return validation

def not_null(name):
    def validation(object):
        value = object.get(name, None)
        if not value == None: return True
        raise exceptions.ValidationInternalError(name, "value is not set")
    return validation

def not_empty(name):
    def validation(object):
        value = object.get(name, None)
        if value == None: return True
        if len(value): return True
        raise exceptions.ValidationInternalError(name, "value is empty")
    return validation

def is_in(name, values):
    def validation(object):
        value = object.get(name, None)
        if value == None: return True
        if value in values: return True
        raise exceptions.ValidationInternalError(name, "value is not in set")
    return validation

def is_email(name):
    def validation(object):
        value = object.get(name, None)
        if value == None: return True
        if EMAIL_REGEX.match(value): return True
        raise exceptions.ValidationInternalError(name, "value is not a valid email")
    return validation

def is_url(name):
    def validation(object):
        value = object.get(name, None)
        if value == None: return True
        if URL_REGEX.match(value): return True
        raise exceptions.ValidationInternalError(name, "value is not a valid url")
    return validation

def is_regex(name, regex):
    def validation(object):
        value = object.get(name, None)
        if value == None: return True
        match = re.match(regex, value)
        if match: return True
        raise exceptions.ValidationInternalError(
            name, "value has incorrect format"
        )
    return validation

def string_gt(name, size):
    def validation(object):
        value = object.get(name, None)
        if value == None: return True
        if len(value) > size: return True
        raise exceptions.ValidationInternalError(
            name, "must be larger than %d characters" % size
        )
    return validation

def string_lt(name, size):
    def validation(object):
        value = object.get(name, None)
        if value == None: return True
        if len(value) < size: return True
        raise exceptions.ValidationInternalError(
            name, "must be smaller than %d characters" % size
        )
    return validation

def equals(first_name, second_name):
    def validation(object):
        first_value = object.get(first_name, None)
        second_value = object.get(second_name, None)
        if first_value == None: return True
        if second_value == None: return True
        if first_value == second_value: return True
        raise exceptions.ValidationInternalError(
            first_name, "value is not equals to %s" % second_name
        )
    return validation

def not_past(name):
    def validation(object):
        value = object.get(name, None)
        if value == None: return True
        if value >= datetime.datetime.utcnow(): return True
        raise exceptions.ValidationInternalError(
            name, "date is in the past"
        )
    return validation

def not_duplicate(name, collection):
    def validation(object):
        _id = object.get("_id", None)
        value = object.get(name, None)
        if value == None: return True
        db = mongo.get_db()
        _collection = db[collection]
        item = _collection.find_one({name : value})
        if not item: return True
        if str(item["_id"]) == str(_id): return True
        raise exceptions.ValidationInternalError(name, "value is duplicate")
    return validation
