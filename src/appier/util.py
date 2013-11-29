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
import copy
import uuid
import hashlib
import inspect

import base
import defines
import exceptions

CONTEXT = None
""" The current context that is going to be used for new
routes that are going to be registered with decorators """

ALIAS = {
    "filter_string" : "find_s",
    "start_record" : "skip",
    "number_records" : "limit"
}
""" The map containing the various attribute alias
between the normalized manned and the appier manner """

FIND_TYPES = {
    "skip" : int,
    "limit" : int,
    "find_s" : str
}
""" The map associating the various find fields with
their respective types """

def is_iterable(object):
    return type(object) in defines.ITERABLES

def request_json(request = None):
    # retrieves the proper request object, either the provided
    # request or the default base request object and then in
    # case the the json data is already in the request properties
    # it is used (cached value) otherwise continues with the parse
    request = request or base.get_request()
    if "_data_j" in request.properties: return request.properties["_data_j"]

    # retrieves the current request data and tries to
    # "load" it as json data, in case it fails gracefully
    # handles the failure setting the value as an empty map
    data = request.data
    try: data_j = json.loads(data)
    except: data_j = {}
    request.properties["_data_j"] = data_j

    # returns the json data object to the caller method so that it
    # may be used as the parsed value (post information)
    return data_j

def get_object(object = None, alias = False, find = False):
    # retrieves the base request object that is going to be used in
    # the construction of the object
    request = base.get_request()

    # verifies if the provided object is valid in such case creates
    # a copy of it and uses it as the base object for validation
    # otherwise used an empty map (form validation)
    object = object and copy.copy(object) or {}

    # retrieves the current request data and tries to
    # "load" it as json data, in case it fails gracefully
    # handles the failure setting the value as an empty map
    data_j = request_json()

    # uses all the values referencing data in the request to try
    # to populate the object this way it may be constructed using
    # any of theses strategies (easier for the developer)
    for name, value in data_j.iteritems(): object[name] = value
    for name, value in request.files.iteritems(): object[name] = value[0]
    for name, value in request.post.iteritems(): object[name] = value[0]
    for name, value in request.params.iteritems(): object[name] = value[0]

    # in case the alias flag is set tries to resolve the attribute
    # alias and in case the find types are set converts the find
    # based attributes using the currently defined mapping map
    alias and resolve_alias(object)
    find and find_types(object)

    # returns the constructed object to the caller method this object
    # should be a structured representation of the data in the request
    return object

def resolve_alias(object):
    for name, value in object.items():
        if not name in ALIAS: continue
        _alias = ALIAS[name]
        object[_alias] = value
        del object[name]

def find_types(object):
    for name, value in object.items():
        if not name in FIND_TYPES:
            del object[name]
            continue
        find_type = FIND_TYPES[name]
        object[name] = find_type(value)

def gen_token():
    """
    Generates a random cryptographic ready token according
    to the framework specification, this is generated using
    a truly random uuid based seed and hashed using the
    sha256 hash digest.

    The resulting value is returned as an hexadecimal based
    string according to the standard.

    @rtype: String
    @return: The hexadecimal based string value
    """

    token_s = str(uuid.uuid4())
    token = hashlib.sha256(token_s).hexdigest()
    return token

def camel_to_underscore(camel):
    """
    Converts the provided camel cased based value into
    a normalized underscore based string.

    This is useful as most of the python string standards
    are compliant with the underscore strategy.

    @type camel: String
    @param camel: The camel cased string that is going to be
    converted into an underscore based string.
    @rtype: String
    @return The underscore based string resulting from the
    conversion of the provided camel cased one.
    """

    values = []
    camel_l = len(camel)

    for index in xrange(camel_l):
        char = camel[index]
        is_upper = char.isupper()

        if is_upper and not index == 0: values.append("_")
        values.append(char)

    return "".join(values).lower()

def base_name(name, suffix = "_controller"):
    """
    Retrieves the base name of a class name that contains
    a suffix (eg: controller) the resulting value is the
    underscore version of the name without the suffix.

    This method provides an easy way to expose class names
    in external environments.

    @type name: String
    @param name: The name from which the base name will be
    extracted and treated.
    @type suffix: String
    @param suffix: The optional suffix value that if sent will
    be removed from the last part of the name string.
    @rtype: String
    @return: The resulting base name for the provided name, treated
    and with the suffix removed (in case it exists).
    """

    name = camel_to_underscore(name)
    if name.endswith(suffix): name = name[:-11]
    return name

def parse_multipart(data, boundary):
    """
    Parses the provided data buffer as a set of multipart data
    the content type is not verified inside this method.

    The function returns a tuple containing both a map of "basic"
    form parameters and a map containing the set of file tuples.

    @type data: String
    @param data: The string containing the complete set of data
    that is going to be processed as multipart.
    @type boundary: String
    @param boundary: The string containing the basic boundary header
    value, should be provided from the caller function.
    @rtype: Tuple
    @return: A tuple containing both the map of post attributes and
    the map of file attributes.
    """

    post = dict()
    files = dict()

    boundary = boundary.strip()
    boundary_base = "--" + boundary[9:]
    boundary_value = boundary_base + "\r\n"
    boundary_extra = boundary_base + "--" + "\r\n"
    parts = data.split(boundary_value)
    parts[-1] = parts[-1].strip(boundary_extra)

    for part in parts:
        if not part: continue
        part_s = part.split("\r\n\r\n", 1)
        headers = part_s[0]
        if len(part_s) > 1: contents = part_s[1]
        else: contents = None

        headers_data = headers.strip()
        headers_lines = headers_data.split("\r\n")
        headers = dict([line.split(":", 1) for line in headers_lines])
        for key, value in headers.items(): headers[key.lower()] = value.strip()

        disposition = headers.get("content-disposition", None)
        if not disposition: continue

        parts = dict()
        parts_data = disposition.split(";")
        for value in parts_data:
            value_s = value.split("=", 1)
            key = value_s[0].strip().lower()
            if len(value_s) > 1: value = value_s[1].strip()
            else: value = None
            parts[key] = value

        content_type = headers.get("content-type", None)
        name = parts.get("name", "\"undefined\"")[1:-1]
        filename = parts.get("filename", "")[1:-1]

        if filename: is_file = True
        else: is_file = False

        if is_file:
            target = files
            value = (filename, content_type, contents)
        else:
            target = post
            value = contents[:-2] if contents else contents

        sequence = target.get(name, [])
        sequence.append(value)
        target[name] = sequence

    return (post, files)

def private(function):

    def _private(self, *args, **kwargs):
        is_auth = "username" in self.request.session
        if not is_auth: raise exceptions.AppierException(
            message = "Method '%s' requires authentication" % function.__name__,
            error_code = 403
        )

        sanitize(function, kwargs)
        return function(self, *args, **kwargs)

    return _private

def controller(controller):

    def decorator(function, *args, **kwargs):
        global CONTEXT
        CONTEXT = controller
        return function

    return decorator

def route(url, method = "GET"):

    def decorator(function, *args, **kwargs):
        base.App.add_route(method, url, function, context = CONTEXT)
        return function

    return decorator

def sanitize(function, kwargs):
    removal = []
    method_a = inspect.getargspec(function)[0]
    for name in kwargs:
        if name in method_a: continue
        removal.append(name)
    for name in removal: del kwargs[name]
