#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2016 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import re
import copy
import datetime

from . import util
from . import common
from . import legacy
from . import exceptions

SIMPLE_REGEX_VALUE = "^[\:\.\s\w-]+$"
""" The simple regex value used to validate
if the provided value is a "simple" one meaning
that it may be used safely for url parts """

EMAIL_REGEX_VALUE = "^[\w\d\._%+-]+@[\w\d\.\-]+$"
""" The email regex value used to validate
if the provided value is in fact an email """

URL_REGEX_VALUE = "^\w+\:\/\/[^\:\/\?#]+(\:\d+)?(\/[^\?#]+)*\/?(\?[^#]*)?(#.*)?$"
""" The url regex value used to validate
if the provided value is in fact an URL/URI """

SIMPLE_REGEX = re.compile(SIMPLE_REGEX_VALUE)
""" The simple regex used to validate
if the provided value is a "simple" one meaning
that it may be used safely for url parts """

EMAIL_REGEX = re.compile(EMAIL_REGEX_VALUE)
""" The email regex used to validate
if the provided value is in fact an email """

URL_REGEX = re.compile(URL_REGEX_VALUE)
""" The url regex used to validate
if the provided value is in fact an URL/URI """

def validate(method = None, methods = [], object = None, ctx = None, build = True):
    # retrieves the base request object that is going to be used in
    # the construction of the object
    request = common.base().get_request()

    # uses the provided method to retrieves the complete
    # set of methods to be used for validation, this provides
    # an extra level of indirection
    methods = method() if method else methods
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
        for name, value in data_j.items(): object[name] = value
        for name, value in request.files_s.items(): object[name] = value
        for name, value in request.post_s.items(): object[name] = value
        for name, value in request.params_s.items(): object[name] = value

    # iterates over the complete set of methods registered for validation
    # and runs them expecting exceptions to be raised from them, each adding
    # new errors to the current errors stack
    for method in methods:
        try: method(object, ctx = ctx)
        except exceptions.ValidationMultipleError as error:
            errors.extend(error.errors)
        except exceptions.ValidationInternalError as error:
            errors.append((error.name, error.message))

    # creates the map that will be used to store the association between the
    # field name of the object and the validation errors associated with it
    errors_map = dict()
    for name, message in errors:
        if not name in errors_map: errors_map[name] = []
        _errors = errors_map[name]
        _errors.append(message)

    # returns both the newly created errors map that associates each of the
    # model name with the sequence of errors and the validated object (state)
    return errors_map, object

def validate_b(method = None, methods = [], object = None, ctx = None, build = True):
    errors_map, object = validate(
        method = method,
        methods = methods,
        object = object,
        ctx = ctx,
        build = build
    )
    result = False if errors_map else True
    return result

def validate_e(method = None, methods = [], object = None, ctx = None, build = True):
    errors_map, object = validate(
        method = method,
        methods = methods,
        object = object,
        ctx = ctx,
        build = build
    )
    if not errors_map: return
    raise exceptions.ValidationError(errors_map, object)

def safe(comparision):
    try: return comparision()
    except TypeError: return False

def eq(name, value_c, message = "must be equal to %s", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == value_c: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % str(value_c))
    return validation

def gt(name, value_c, message = "must be greater than %s", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if safe(lambda: value > value_c): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % str(value_c))
    return validation

def gte(name, value_c, message = "must be greater than or equal to %s", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if safe(lambda: value >= value_c): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % str(value_c))
    return validation

def lt(name, value_c, message = "must be less than %s", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if safe(lambda: value < value_c): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % str(value_c))
    return validation

def lte(name, value_c, message = "must be less than or equal to %s", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if safe(lambda: value <= value_c): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % str(value_c))
    return validation

def not_null(name, message = "value is not set", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if not value == None: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def not_empty(name, message = "value is empty", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if len(value): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def not_false(name, message = "value is false", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if not value == False: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def is_in(name, values, message = "value is not in set", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value in values: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def is_lower(name, message = "value contains upper cased characters", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        if value == value.lower(): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def is_simple(name, message = "value contains invalid characters", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        if SIMPLE_REGEX.match(value): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def is_email(name, message = "value is not a valid email", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        if EMAIL_REGEX.match(value): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def is_url(name, message = "value is not a valid url", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        if URL_REGEX.match(value): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def is_regex(name, regex, message = "value has incorrect format", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        match = re.match(regex, value)
        if match: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def field_eq(name, field, message = "must be equal to %s", locale = True):
    def validation(object, ctx):
        name_v = object.get(name, None)
        field_v = object.get(field, None)
        if name_v == None: return True
        if field_v == None: return True
        if name_v == field_v: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % field)
    return validation

def field_gt(name, field, message = "must be greater than %s", locale = True):
    def validation(object, ctx):
        name_v = object.get(name, None)
        field_v = object.get(field, None)
        if name_v == None: return True
        if field_v == None: return True
        if safe(lambda: name_v > field_v): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % field)
    return validation

def field_gte(name, field, message = "must be greater or equal than %s", locale = True):
    def validation(object, ctx):
        name_v = object.get(name, None)
        field_v = object.get(field, None)
        if name_v == None: return True
        if field_v == None: return True
        if safe(lambda: name_v >= field_v): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % field)
    return validation

def field_lt(name, field, message = "must be less than %s", locale = True):
    def validation(object, ctx):
        name_v = object.get(name, None)
        field_v = object.get(field, None)
        if name_v == None: return True
        if field_v == None: return True
        if safe(lambda: name_v < field_v): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % field)
    return validation

def field_lte(name, field, message = "must be less or equal than %s", locale = True):
    def validation(object, ctx):
        name_v = object.get(name, None)
        field_v = object.get(field, None)
        if name_v == None: return True
        if field_v == None: return True
        if safe(lambda: name_v <= field_v): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % field)
    return validation

def string_gt(name, size, message = "must be larger than %d characters", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        if len(value) > size: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % size)
    return validation

def string_lt(name, size, message = "must be smaller than %d characters", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        if len(value) < size: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % size)
    return validation

def string_eq(name, size, message = "must be exactly %d characters", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        if len(value) == size: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l % size)
    return validation

def equals(first_name, second_name, message = "value is not equal to %s", locale = True):
    def validation(object, ctx):
        first_value = object.get(first_name, None)
        second_value = object.get(second_name, None)
        if first_value == None: return True
        if second_value == None: return True
        if first_value == second_value: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(first_name, message_l % second_name)
    return validation

def not_past(name, message = "date is in the past", locale = True):
    def validation(object, ctx):
        value = object.get(name, None)
        if value == None: return True
        if value >= datetime.datetime.utcnow(): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def not_duplicate(name, collection, message = "value is duplicate", locale = True):
    def validation(object, ctx):
        _id = object.get("_id", None)
        value = object.get(name, None)
        if value == None: return True
        if value == "": return True
        adapter = common.base().get_adapter()
        _collection = adapter.collection(collection)
        item = _collection.find_one({name : value})
        if not item: return True
        if str(item["_id"]) == str(_id): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def all_different(name, name_ref = None, message = "has duplicates", locale = True):
    def validation(object, ctx):
        # uses the currently provided context to retrieve
        # the definition of the name to be validation and
        # in it's a valid relation type tries to retrieve
        # the underlying referenced name otherwise default
        # to the provided one or the id name
        cls = ctx.__class__
        definition = cls.definition_n(name)
        type = definition.get("type", legacy.UNICODE)
        _name_ref = name_ref or (hasattr(type, "_name") and type._name or "id")

        # tries to retrieve both the value for the identifier
        # in the current object and the values of the sequence
        # that is going to be used for all different matching in
        # case any of them does not exist returns valid
        value = object.get(name, None)
        if value == None: return True
        if len(value) == 0: return True

        # verifies if the sequence is in fact a proxy object and
        # contains the ids attribute in case that's the case the
        # ids attributes is retrieved as the sequence instead
        if hasattr(value, "ids"): values = value.ids

        # otherwise this is a normal sequence and the it must be
        # iterates to check if the reference name should be retrieve
        # or if the concrete values should be used instead
        else: values = [getattr(_value, _name_ref) if hasattr(_value, _name_ref) else _value\
            for _value in value]

        # creates a set structure from the the sequence of values
        # and in case the size of the sequence and the set are the
        # same the sequence is considered to not contain duplicates
        values_set = set(values)
        if len(value) == len(values_set): return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def no_self(name, name_ref = None, message = "contains self", locale = True):
    def validation(object, ctx):
        # uses the currently provided context to retrieve
        # the definition of the name to be validation and
        # in it's a valid relation type tries to retrieve
        # the underlying referenced name otherwise default
        # to the provided one or the id name
        cls = ctx.__class__
        definition = cls.definition_n(name)
        type = definition.get("type", legacy.UNICODE)
        _name_ref = name_ref or (hasattr(type, "_name") and type._name or "id")

        # tries to retrieve both the value for the identifier
        # in the current object and the values of the sequence
        # that is going to be used for existence matching in
        # case any of them does not exist returns valid
        _id = object.get(_name_ref, None)
        value = object.get(name, None)
        if _id == None: return True
        if value == None: return True

        # verifies if the sequence is in fact a proxy object and
        # contains the ids attribute in case that's the case the
        # ids attributes is retrieved as the sequence instead
        if hasattr(value, "ids"): values = value.ids

        # otherwise this is a normal sequence and the it must be
        # iterates to check if the reference name should be retrieve
        # or if the concrete values should be used instead
        else: values = [getattr(_value, _name_ref) if hasattr(_value, _name_ref) else _value\
            for _value in value]

        # verifies if the current identifier value exists in the
        # sequence and if that's the case raises the validation
        # exception indicating the validation problem
        exists = _id in values
        if not exists: return True
        message_l = _to_locale(message) if locale else message
        raise exceptions.ValidationInternalError(name, message_l)
    return validation

def _to_locale(value):
    return common.base().to_locale(value)
