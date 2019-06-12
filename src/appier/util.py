#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import re
import sys
import json
import copy
import uuid
import types
import locale
import hashlib
import calendar
import datetime
import warnings
import functools
import threading
import mimetypes
import contextlib
import subprocess

from . import smtp
from . import legacy
from . import common
from . import defines
from . import exceptions

CREATION_COUNTER = 0
""" The global static creation counter value that
will be used to create an order in the declaration
of attributes for a set of classes """

FIRST_CAP_REGEX = re.compile("(.)([A-Z][a-z]+)")
""" Regular expression that ensures that the first
token of each camel string is properly capitalized """

ALL_CAP_REGEX = re.compile("([a-z0-9])([A-Z])")
""" The generalized transition from lower case to
upper case letter regex that will provide a way of
putting the underscore in the middle of the transition """

SORT_MAP = {
    "1" : 1,
    "-1" : -1,
    "ascending" : 1,
    "descending" : -1,
}
""" The map associating the normalized (text) way of
representing sorting with the current infra-structure
number way of representing the same information """

SEQUENCE_TYPES = (list, tuple)
""" The sequence defining the various types that are
considered to be sequence based for python """

defines = defines

def to_limit(limit_s):
    limit = int(limit_s)
    if limit < 0: return 0
    return limit

def to_find(find_s):
    if not find_s: return []
    find_t = type(find_s)
    if find_t == list: return find_s
    return [find_s]

def to_sort(sort_s):
    values = sort_s.split(":", 1)
    if len(values) == 1: values.append("descending")
    name, direction = values
    if name == "default": return None
    values[1] = SORT_MAP.get(direction, 1)
    return [tuple(values)]

ALIAS = {
    "context" : "find_d",
    "filters" : "find_d",
    "filters[]" : "find_d",
    "filter_def" : "find_d",
    "filter_string" : "find_s",
    "filter_name" : "find_n",
    "filter_operator" : "find_o",
    "insensitive" : "find_i",
    "order" : "sort",
    "offset" : "skip",
    "start_record" : "skip",
    "number_records" : "limit"
}
""" The map containing the various attribute alias
between the normalized manned and the appier manner """

FIND_TYPES = dict(
    skip = int,
    limit = to_limit,
    find_s = legacy.UNICODE,
    find_d = to_find,
    find_i = bool,
    find_t = legacy.UNICODE,
    find_n = legacy.UNICODE,
    find_o = legacy.UNICODE,
    sort = to_sort,
    meta = bool,
    fields = list
)
""" The map associating the various find fields with
their respective types, note that in case a special
conversion operation is required the associated value
may represent a conversion function instead """

FIND_DEFAULTS = dict(
    limit = 10
)
""" The map that defines the various default values
for a series of find related attributes """

def is_iterable(object):
    """
    Verifies if the provided object (value) is iterable
    meaning that the type of it is listed in a list of
    sequence based data types.

    :type object: Object
    :param object: The value that is going to be tested
    for iterable type.
    :rtype: bool
    :return: If the provided object represents an iterable
    object meaning that it belongs to sequence type.
    """

    return isinstance(object, defines.ITERABLES)

def is_mobile(user_agent):
    """
    Verifies if the provided user agent string represents a
    mobile agent, for that a series of regular expressions
    are matched against the user agent string.

    :type user_agent: String
    :param user_agent: The string containing the user agent
    value that is going to be verified against a series of
    regular expressions for mobile verification.
    :rtype: bool
    :return: If the provided user agent string represents a
    mobile browser or a regular (desktop) one.
    """

    if not user_agent: return False
    prefix = user_agent[:4]
    mobile = defines.MOBILE_REGEX.search(user_agent)
    mobile_prefix = defines.MOBILE_PREFIX_REGEX.search(prefix)
    is_mobile = True if mobile or mobile_prefix else False
    return is_mobile

def is_tablet(user_agent):
    """
    Verifies if the provided user agent string represents a
    tablet agent, for that a series of regular expressions
    are matched against the user agent string.

    :type user_agent: String
    :param user_agent: The string containing the user agent
    value that is going to be verified against a series of
    regular expressions for tablet verification.
    :rtype: bool
    :return: If the provided user agent string represents a
    tablet browser or a regular (desktop) one.
    """

    if not user_agent: return False
    prefix = user_agent[:4]
    tablet = defines.TABLET_REGEX.search(user_agent)
    mobile_prefix = defines.MOBILE_PREFIX_REGEX.search(prefix)
    is_tablet = True if tablet or mobile_prefix else False
    return is_tablet

def is_browser(user_agent):
    """
    Verifies if the provided user agent string represents a
    browser (interactive) agent, for that a series of verifications
    are going to be performed against the user agent string.

    :type user_agent: String
    :param user_agent: The string containing the user agent
    value that is going to be verified for browser presence.
    :rtype: bool
    :return: If the provided user agent string represents an
    interactive browser or not.
    """

    info = browser_info(user_agent)
    if not info: return False
    interactive = info.get("interactive", False)
    if not interactive: return False
    return True

def is_bot(user_agent):
    """
    Verifies if the provided user agent string represents a
    bot (automated) agent, for that a series of verifications
    are going to be performed against the user agent string.

    :type user_agent: String
    :param user_agent: The string containing the user agent
    value that is going to be verified for bot presence.
    :rtype: bool
    :return: If the provided user agent string represents an
    automated bot or not.
    """

    info = browser_info(user_agent = user_agent)
    if not info: return False
    bot = info.get("bot", False)
    if not bot: return False
    return True

def browser_info(user_agent):
    """
    Retrieves a dictionary containing information about the browser
    and the operative system associated with the provided user agent.

    The retrieval of the information depends on the kind of user
    agent string provided, as coverage is limited.

    :type user_agent: String
    :param user_agent: The HTTP based user agent string to be processed.
    :rtype: Dictionary
    :return: The dictionary/map containing the information processed from
    the provided user agent.
    """

    if not user_agent: return None

    info = dict()

    for browser_i in defines.BROWSER_INFO:
        identity = browser_i["identity"]
        sub_string = browser_i.get("sub_string", identity)
        version_search = browser_i.get("version_search", sub_string + "/")
        interactive = browser_i.get("interactive", True)
        bot = browser_i.get("bot", False)

        if not sub_string in user_agent: continue
        if not version_search in user_agent: continue

        version_i = user_agent.index(version_search) + len(version_search)
        version = user_agent[version_i:].split(" ", 1)[0].strip(" ;")
        try: version_f = float(".".join(version.split(".")[:2]))
        except ValueError: version_f = 0.0
        try: version_i = int(version_f)
        except ValueError: version_f = 0

        info.update(
            name = identity,
            version = version,
            version_f = version_f,
            version_i = version_i,
            interactive = interactive,
            bot = bot
        )
        break

    for os_i in defines.OS_INFO:
        identity = os_i["identity"]
        sub_string = os_i.get("sub_string", identity)

        if not sub_string in user_agent: continue

        info.update(os = identity)
        break

    return info if info else None

def email_parts(base, strip = True):
    """
    Unpacks the complete set of parts (name and email) from the
    provided generalized email string. The provided string may
    be a single email or the more complex form (eg: Name <email>).

    Note that the provided base argument may be a single string
    or a sequence of strings and the returning type will reflect
    that same provided parameter.

    :type base: String/List
    :param base: The base value that is going to be parsed as an
    email string or a sequence of such values.
    :type strip: bool
    :param strip: If the provided base value should be stripped
    of any extra space characters before processing.
    :rtype: Tuple/List
    :return: The resulting parsed tuple/tuples for the provided
    email strings, these tuples contain name and emails for each
    of the parsed values.
    """

    base_t = type(base)
    if base_t in SEQUENCE_TYPES:
        return [email_parts(base, strip = strip) for base in base]

    if not base: return (None, None)
    if strip: base = base.strip()

    match = defines.EMAIL_REGEX.match(base)
    if not match: return (None, None)

    email = match.group("email_a") or match.group("email_b")
    name = match.group("name") or email

    return (name, email)

def email_mime(base, encoding = "utf-8"):
    if legacy.PYTHON_3: encoding = None

    base_t = type(base)
    if base_t in SEQUENCE_TYPES:
        return [value for value in (email_mime(item, encoding = encoding) for item in base) if value]

    name, email = email_parts(base)
    if not name or not email: return None

    name = smtp.header(name, encoding = encoding)

    return "%s <%s>" % (name, email)

def email_name(base):
    base_t = type(base)
    if base_t in SEQUENCE_TYPES:
        return [value for value in (email_name(base) for base in base if email_name(base)) if value]
    name, _email = email_parts(base)
    return name

def email_base(base):
    base_t = type(base)
    if base_t in SEQUENCE_TYPES:
        return [value for value in (email_base(base) for base in base if email_base(base)) if value]
    _name, email = email_parts(base)
    return email

def date_to_timestamp(value, format = "%d/%m/%Y"):
    if not value: return None
    try: value = datetime.datetime.strptime(value, format)
    except Exception: return None
    value = value.utctimetuple()
    return calendar.timegm(value)

def obfuscate(value, display_l = 3, token = "*"):
    value_l = len(value)
    display_l = min([value_l, display_l])
    obfuscated = value[:display_l] + ((value_l - display_l) * token)
    return obfuscated

def import_pip(name, package = None, default = None):
    package = package or name
    try:
        module = __import__(name)
    except ImportError:
        try: module = install_pip_s(package)
        except Exception: return default
        try: module = __import__(name)
        except ImportError: return default
    return module

def ensure_pip(name, package = None, delayed = False):
    package = package or name
    try:
        __import__(name)
    except ImportError:
        install_pip_s(package, delayed = delayed)

def install_pip(package, delayed = False, user = False):
    import pip #@UnusedImport
    try: import pip._internal
    except ImportError: pip._internal = None
    args = ["install", package]
    if hasattr(pip._internal, "main"): pip_main = pip._internal.main
    else: pip_main = pip.main #@UndefinedVariable
    if user: args.insert(1, "--user")
    if delayed:
        import multiprocessing
        process = multiprocessing.Process(
            target = pip_main,
            args = (args,)
        )
        process.start()
        result = 0
    else:
        result = pip_main(args)
    if result == 0: return
    raise exceptions.OperationalError(message = "pip error")

def install_pip_s(package, delayed = False):
    try:
        install_pip(package, delayed = delayed, user = False)
    except exceptions.OperationalError:
        install_pip(package, delayed = delayed, user = True)

def request_json(request = None, encoding = "utf-8"):
    # retrieves the proper request object, either the provided
    # request or the default base request object and then in
    # case the the json data is already in the request properties
    # it is used (cached value) otherwise continues with the parse
    request = request or common.base().get_request()
    if "_data_j" in request.properties: return request.properties["_data_j"]

    # retrieves the current request data and tries to
    # "load" it as json data, in case it fails gracefully
    # handles the failure setting the value as an empty map
    data = request.data
    try:
        is_bytes = legacy.is_bytes(data)
        if is_bytes: data = data.decode(encoding)
        data_j = json.loads(data)
    except Exception:
        data_j = {}
    request.properties["_data_j"] = data_j

    # returns the json data object to the caller method so that it
    # may be used as the parsed value (post information)
    return data_j

def get_context(self):
    """
    Retrieves the "best" possible context object for the current
    execution life-cycle, typically this should be an "attached"
    request object.

    Multiple strategies should be used while trying to retrieved
    the "current" context.
    """

    # tries to retrieve the request attached to the current instance
    # (typically a property) and verifies the object compliance,
    # returning the object to the caller in case it's valid
    if hasattr(self, "request"):
        request = self.request
        is_valid = hasattr(request, "is_mock") and not request.is_mock()
        if is_valid: return request

    # uses the global strategy to try to retrieve a request for the
    # current execution environment (not thread safe)
    request = common.base().get_request()
    is_valid = hasattr(request, "is_mock") and not request.is_mock()
    if is_valid: return request

    # fallback return value meaning that it was not possible to retrieve
    # any valid execution context for the current environment
    return None

def get_object(
    object = None,
    alias = False,
    page = False,
    find = False,
    norm = True,
    **kwargs
):
    # retrieves the base request object that is going to be used in
    # the construction of the object
    request = common.base().get_request()

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
    for name, value in data_j.items(): object[name] = value
    for name, value in request.files_s.items(): object[name] = value
    for name, value in request.post_s.items(): object[name] = value
    for name, value in request.params_s.items(): object[name] = value

    # in case the alias flag is set tries to resolve the attribute
    # alias and in case the find types are set converts the find
    # based attributes using the currently defined mapping map
    alias and resolve_alias(object)
    page and page_types(object)
    find and find_types(object)
    find and find_defaults(object, kwargs)

    # in case the normalization flag is set runs the normalization
    # of the provided object so that sequences are properly handled
    # as defined in the specification (this allows multiple references)
    norm and norm_object(object)

    # returns the constructed object to the caller method this object
    # should be a structured representation of the data in the request
    return object

def resolve_alias(object):
    for name, value in legacy.eager(object.items()):
        if not name in ALIAS: continue
        _alias = ALIAS[name]
        object[_alias] = value
        del object[name]

def page_types(object, size = 50):
    page = object.get("page", 1)
    size = object.get("size", size)
    sorter = object.get("sorter", None)
    direction = object.get("direction", "descending")
    page = int(page)
    size = int(size)
    offset = page - 1
    object["skip"] = offset * size
    object["limit"] = size
    if sorter: object["sort"] = "%s:%s" % (sorter, direction)

def find_types(object):
    for name, value in legacy.eager(object.items()):
        if not name in FIND_TYPES:
            del object[name]
            continue
        find_type = FIND_TYPES[name]
        object[name] = find_type(value)

def find_defaults(object, kwargs):
    for name, value in legacy.iteritems(kwargs):
        if name in object: continue
        if not name in FIND_TYPES: continue
        object[name] = value

    for name, value in legacy.iteritems(FIND_DEFAULTS):
        if name in object: continue
        object[name] = value

def norm_object(object):
    # iterates over all the key value association in the
    # object, trying to find the ones that refer sequences
    # so that they may be normalized
    for name, value in object.items():
        # verifies if the current name references a sequence
        # and if that's not the case continues the loop trying
        # to find any other sequence based value
        if not name.endswith("[]"): continue

        # removes the current reference to the name as the value
        # is not in the valid structure and then normalizes the
        # name by removing the extra sequence indication value
        del object[name]
        name = name[:-2]

        # in case the current value is not valid (empty) the object
        # is set with an empty list for the current iteration as this
        # is considered to be the default value
        if not value: object[name] = []; continue

        # retrieves the normalized and linearized list of leafs
        # for the current value and ten verifies the size of each
        # of its values and uses it to measure the number of
        # dictionary elements that are going to be contained in
        # the sequence to be "generated", then uses this (size)
        # value to pre-generate the complete set of dictionaries
        leafs_l = leafs(value)
        first = leafs_l[0] if leafs_l else (None, [])
        _fqn, values = first
        size = len(values)
        list = [dict() for _index in range(size)]

        # sets the list of generates dictionaries in the object for
        # the newly normalized name of structure
        object[name] = list

        # iterates over the complete set of key value pairs in the
        # leafs list to gather the value into the various objects that
        # are contained in the sequence (normalization process)
        for _name, _value in leafs_l:
            for index in range(size):
                _object = list[index]
                _name_l = _name.split(".")
                set_object(_object, _name_l, _value[index])

def set_object(object, name_l, value):
    """
    Sets a composite value in an object, allowing for
    dynamic setting of random size key values.

    This method is useful for situations where one wants
    to set a value at a randomly defined depth inside
    an object without having to much work with the creation
    of the inner dictionaries.

    :type object: Dictionary
    :param object: The target object that is going to be
    changed and set with the target value.
    :type name_l: List
    :param name_l: The list of names that defined the fully
    qualified name to be used in the setting of the value
    for example path.to.end will be a three size list containing
    each of the partial names.
    :type value: Object
    :param value: The value that is going to be set in the
    defined target of the object.
    """

    # retrieves the first name in the names list this is the
    # value that is going to be used for the current iteration
    name = name_l[0]

    # in case the length of the current names list has reached
    # one this is the final iteration and so the value is set
    # at the current naming point
    if len(name_l) == 1: object[name] = value

    # otherwise this is a "normal" step and so a new map must
    # be created/retrieved and the iteration step should be
    # performed on this new map as it's set on the current naming
    # place (recursion step)
    else:
        map = object.get(name, {})
        object[name] = map
        set_object(map, name_l[1:], value)

def leafs(object):
    """
    Retrieves a list containing a series of tuples that
    each represent a leaf of the current object structure.

    A leaf is the last element of an object that is not a
    map, the other intermediary maps are considered to be
    trunks and should be percolated recursively.

    This is a recursive function that takes some memory for
    the construction of the list, and so should be used with
    the proper care to avoid bottlenecks.

    :type object: Dictionary
    :param object: The object for which the leafs list
    structure is meant to be retrieved.
    :rtype: List
    :return: The list of leaf node tuples for the provided
    object, as requested for each of the sequences.
    """

    # creates the list that will hold the various leaf nodes
    # "gathered" by the current recursion function
    leafs_l = []

    # iterates over all the key and value relations in the
    # object trying to find the leaf nodes (no map nodes)
    # creating a tuple of fqn (fully qualified name) and value
    for name, value in object.items():
        # retrieves the data type for the current value and
        # validation if it is a dictionary or any other type
        # in case it's a dictionary a new iteration step must
        # be performed retrieving the leafs of the value and
        # then incrementing the name with the current prefix
        value_t = type(value)
        if value_t == dict:
            _leafs = leafs(value)
            _leafs = [(name + "." + _name, value) for _name, value in _leafs]
            leafs_l.extend(_leafs)

        # otherwise this is a leaf node and so the leaf tuple
        # node must be constructed with the current value
        # (properly validated for sequence presence)
        else:
            value_t = type(value)
            if not value_t == list: value = [value]
            leafs_l.append((name, value))

    # returns the list of leaf nodes that was "just" created
    # to the caller method so that it may be used there
    return leafs_l

def gather_errors(lazy_dict, resolve = True):
    """
    Function responsible for the iterative gathering of
    lazy evaluation errors, allowing for a complete gathering
    of error instead of a single evaluation.

    :type lazy_dict: LazyDict
    :param lazy_dict: The lazy dictionary that is going to be
    percolated and evaluated sequentially.
    :type resolve: bool
    :param resolve: If the lazy dictionary values should be evaluated
    even if they have already been eager loaded, by unsetting this value
    there's a risk of not gathering all of the errors.
    :rtype: Dictionary
    :return: The final dictionary containing the complete set of
    errors that have been found.
    """

    # creates the dictionary that is going to hold sequences of
    # string based error indexed by parameter name
    errors = dict()

    # iterates over the complete set of keys in the lazy dictionary
    # to evaluate the values and check if there are errors associated
    for key in lazy_dict:
        try: _value = lazy_dict.__getitem__(key, resolve = resolve)
        except (exceptions.AppierException, exceptions.BaseInternalError) as exception:
            _errors = errors.get(key, [])
            _errors.append(exception.message)
            errors[key] = _errors

    # returns the final dictionary of error (indexed by name) to
    # the caller method so that it may be used for error handling
    return errors

def gen_token(limit = None, hash = hashlib.sha256):
    """
    Generates a random cryptographic ready token according
    to the framework specification, this is generated using
    a truly random UUID based seed and hashed using the
    provided hash digest strategy (SHA256 by default).

    The resulting value is returned as an hexadecimal based
    string according to the standard.

    :type limit: int
    :param limit: The maximum number of characters allowed
    for the token to be generated.
    :type hash: Function
    :param hash: The hashing method that is going to be used
    for the hash of the generated token, this should be compliant
    with the base python hashing infra-structure.
    :rtype: String
    :return: The hexadecimal based string value
    """

    token_s = str(uuid.uuid4())
    token_s = token_s.encode("utf-8")
    token = hash(token_s).hexdigest()
    if limit: token = token[:limit]
    return token

def html_to_text(data):
    """
    Converts the provided HTML textual data into a plain text
    representation of it. This method uses a series of heuristics
    for this conversion, and such conversion should not be considered
    to be completely reliable.

    The current implementation is not memory or processor efficient
    and should be used carefully to avoid performance problems.

    :type data: String
    :param data: The HTML string of text that is going to be used for
    the conversion into the plain text representation.
    :rtype: String
    :return: The approximate plain text representation to the provided
    HTML contents.
    """

    data = data.strip()
    data = data.replace("\n", "\r")

    data = data.replace("&copy;", "Copyright")
    data = data.replace("&middot;", "-")

    result = re.findall(defines.BODY_REGEX, data)
    data = result[0] if result else ""

    data = defines.TAG_REGEX.sub("", data)

    valid = []
    lines = data.splitlines(False)
    for line in lines:
        line = line.strip()
        if not line: continue
        valid.append(line)

    data = "\n".join(valid)
    data = data.replace("\n.", ".")
    return data

def camel_to_underscore(camel, separator = "_", lower = True):
    """
    Converts the provided camel cased based value into
    a normalized underscore based string.

    An optional lower parameter may be used to avoid the case
    of the letters from being lower cased.

    This is useful as most of the python string standards
    are compliant with the underscore strategy.

    :type camel: String
    :param camel: The camel cased string that is going to be
    converted into an underscore based string.
    :type separator: String
    :param separator: The separator token that is going to
    be used in the camel to underscore conversion.
    :type lower: bool
    :param lower: If the letter casing should be changed while
    convert the value from camel to underscore.
    :rtype: String
    :return: The underscore based string resulting from the
    conversion of the provided camel cased one.
    """

    value = FIRST_CAP_REGEX.sub(r"\1" + separator + r"\2", camel)
    value = ALL_CAP_REGEX.sub(r"\1" + separator + r"\2", value)
    if lower: value = value.lower()
    return value

def camel_to_readable(camel, lower = False, capitalize = False):
    """
    Converts the given camel cased oriented string value
    into a readable one meaning that the returned value
    is a set of strings separated by spaces.

    This method may be used to convert class names into
    something that is readable by an end user.

    :type camel: String
    :param camel: The camel case string value that is going
    to be used in the conversion into a readable string.
    :type lower: bool
    :param lower: If the camel based value should be lower
    cased before the conversion to readable.
    :type capitalize: bool
    :param capitalize: If all of the words should be capitalized
    or if instead only the first one should.
    :rtype: String
    :return: The final human readable string that may be
    used to display a value to an end user.
    """

    underscore = camel_to_underscore(camel, lower = lower)
    return underscore_to_readable(underscore, capitalize = capitalize)

def underscore_to_readable(underscore, capitalize = False):
    """
    Converts the given underscore oriented string value
    into a readable one meaning that the returned value
    is a set of strings separated by spaces.

    This method may be used to class attributes into
    something that is readable by an end user.

    :type camel: String
    :param camel: The underscore string value that is going
    to be used in the conversion into a readable string.
    :type capitalize: bool
    :param capitalize: If all of the words should be capitalized
    or if instead only the first one should.
    :rtype: String
    :return: The final human readable string that may be
    used to display a value to an end user.
    """

    parts = underscore.split("_")
    parts = [part for part in parts if part]
    if capitalize: parts = [part[0].upper() + part[1:] for part in parts]
    else: parts[0] = parts[0][0].upper() + parts[0][1:]
    return " ".join(parts)

def quote(value, *args, **kwargs):
    """
    Quotes the passed value according to the defined
    standard for URL escaping, the value is first encoded
    into the expected UTF-8 encoding as defined by standard.

    This method should be used instead of a direct call to
    the equivalent call in the URL library.

    :type value: String
    :param value: The string value that is going to be quoted
    according to the URL escaping scheme.
    :rtype: String
    :return: The quoted value according to the URL scheme this
    value may be safely used in urls.
    """

    is_unicode = isinstance(value, legacy.UNICODE)
    if is_unicode: value = value.encode("utf-8")
    return legacy.quote(value, *args, **kwargs)

def unquote(value, *args, **kwargs):
    """
    Unquotes the provided value according to the URL scheme
    the resulting value should be an unicode string representing
    the same value, the intermediary string value from the decoding
    should be an UTF-8 based value.

    This method should be used instead of a direct call to
    the equivalent call in the URL library.

    :type value: String
    :param value: The string value that is going to be unquoted
    according to the URL escaping scheme.
    :rtype: String
    :return: The unquoted value extracted as an unicode
    string that the represents the same value.
    """

    value = legacy.unquote(value, *args, **kwargs)
    is_bytes = isinstance(value, legacy.BYTES)
    if is_bytes: value = value.decode("utf-8")
    return value

def escape(value, char, escape = "\\"):
    """
    Escapes the provided string value according to the requested
    target character and escape value. Meaning that all the characters
    are going to be replaced by the escape plus character sequence.

    :type value: String
    :param value: The string that is going to have the target characters
    escaped according to the escape character.
    :type char: String
    :param char: The character that is going to be "target" of escaping.
    :type escape: String
    :param escape: The character to be used for escaping (normally`\`).
    :rtype: String
    :return: The final string with the target character properly escaped.
    """

    return value.replace(escape, escape + escape).replace(char, escape + char)

def unescape(value, escape = "\\"):
    """
    Unescapes the provided string value using the provided escape
    character as the reference for the unescape operation.

    This is considered to be a very expensive operation and so it
    should be used carefully.

    :type value: String
    :param value: The string value that is going to be unescape.
    :rtype: String
    :return: The final unescaped value.
    """

    result = []
    iterator = iter(value)
    for char in iterator:
        if char == escape:
            try:
                result.append(next(iterator))
            except StopIteration:
                result.append(escape)
        else:
            result.append(char)
    return "".join(result)

def split_unescape(value, delimiter = " ", max = -1, escape = "\\", unescape = True):
    """
    Splits the provided string around the delimiter character that
    has been provided and allows proper escaping of it using the
    provided escape character.

    This is considered to be a very expensive operation when compared
    to the simples split operation and so it should be used carefully.

    :type value: String
    :param value: The string value that is going to be split around
    the proper delimiter value taking into account the escaping.
    :type delimiter: String
    :param delimiter: The delimiter character to be used in the split
    operation.
    :type max: int
    :param max: The maximum number of split operations that are going
    to be performed by this operation.
    :type escape: String
    :param escape: The "special" escape character that will allow the
    delimiter to be also present in the choices selection.
    :type unescape: bool
    :param unescape: If the final resulting string should be already
    unescaped (normalized).
    :rtype: List
    :return: The final list containing the multiple string parts separated
    by the delimiter character and respecting the escape sequences.
    """

    result = []
    current = []
    iterator = iter(value)
    count = 0
    for char in iterator:
        if char == escape:
            try:
                if not unescape: current.append(escape)
                current.append(next(iterator))
            except StopIteration:
                if unescape: current.append(escape)
        elif char == delimiter and not count == max:
            result.append("".join(current))
            current = []
            count += 1
        else:
            current.append(char)
    result.append("".join(current))
    return result

def call_safe(callable, *args, **kwargs):
    """
    Method used to call a callable object using a "safe" approach,
    meaning that each of its keyword arguments will be validated
    for existence in the target callable definition.

    In case the validation of the keyword argument fails the same
    argument is removed from the map of keyword arguments.

    Note that in case the wildcard based kwargs value exists in
    the callable definition the callable is immediately considered
    to be valid and the call is ran.

    :type callable: Callable
    :callable callable: The callable that is going to have the keyword
    based arguments validated and the get called.
    :rtype: object
    :return: The resulting value from the safe call of the provided
    callable, this may have any data type.
    """

    # retrieves the arguments specification to the provided callable
    # and retrieves the various argument names and the existence or
    # not of the wildcard kwargs value in the callable and in case it
    # exists runs the callable call immediately
    argspec = legacy.getargspec(callable)
    method_args = argspec[0]
    method_kwargs = argspec[2]
    if method_kwargs: return callable(*args, **kwargs)

    # iterates over the complete set of keyword based arguments to be
    # used in the call and validates them against the method specification
    # in case they do not exist in the specification deletes them from
    # the map of keyword based arguments (not going to be sent)
    for name in legacy.keys(kwargs):
        if name in method_args: continue
        del kwargs[name]

    # runs the callable with the "remaining" arguments and keyword arguments
    # returning the value to the caller method
    return callable(*args, **kwargs)

def base_name(name, suffix = "_controller"):
    """
    Retrieves the base name of a class name that contains
    a suffix (eg: controller) the resulting value is the
    underscore version of the name without the suffix.

    This method provides an easy way to expose class names
    in external environments.

    :type name: String
    :param name: The name from which the base name will be
    extracted and treated.
    :type suffix: String
    :param suffix: The optional suffix value that if sent will
    be removed from the last part of the name string.
    :rtype: String
    :return: The resulting base name for the provided name, treated
    and with the suffix removed (in case it exists).
    """

    suffix_l = len(suffix)
    name = camel_to_underscore(name)
    if name.endswith(suffix): name = name[:suffix_l * -1]
    return name

def base_name_m(name, suffixes = ("_controller", "_part", "_app")):
    """
    Multiple iteration version of the base name function that provides
    a simple strategy for the retrieval of a "base name" without the
    complete set of provided suffixes attached to the value.

    :type name: String
    :param name: The name from which the base name will be
    extracted and treated, with multiple value strategy.
    :type suffixes: List/Tuple
    :param suffixes: The complete set of suffixes that are going
    to be removed from the provided value creating the base name.
    :rtype: String
    :return: The resulting base name for the provided name, treated
    and without the complete set of provided suffixes.
    """

    for suffix in suffixes: name = base_name(name, suffix = suffix)
    return name

def is_content_type(data, target):
    """
    Verifies if the any of the provided mime types (target) is
    valid for the provided content type string.

    :type data: String
    :param data: The content type string to be parsed and matched
    against the target mime type values.
    :type target: Tuple/String
    :param target: The tuple containing the multiple mime type values
    to be verified against the content type mime strings.
    :rtype: bool
    :return: If any of the provided mime types is considered valid
    for the content type.
    """

    if not isinstance(target, (list, tuple)): target = (target,)
    mime, _extra = parse_content_type(data)
    for item in target:
        type, _sub_type = item.split("/")
        wildcard = type + "/*"
        if item in mime: return True
        if wildcard in mime: return True
    return False

def parse_content_type(data):
    """
    Parses the provided content type string retrieving both the multiple
    mime types associated with the resource and the extra key to value
    items associated with the string in case they are defined (it's optional).

    :type data: String
    :param data: The content type data that is going to be parsed to
    obtain the structure of values for the content type string, this must
    be a plain unicode string and not a binary string.
    :rtype: Tuple
    :return: The sequence of mime types of the the content and the multiple
    extra values associated with the content type (eg: charset, boundary, etc.)
    """

    # creates the list of final normalized mime types and the
    # dictionary to store the extra values.
    types = []
    extra_m = dict()

    # in case no valid type has been sent returns the values
    # immediately to avoid further problems
    if not data: return types, extra_m

    # extracts the mime and the extra parts from the data string
    # they are the basis of the processing method
    data = data.strip(";")
    parts = data.split(";")
    mime = parts[0]
    extra = parts[1:]
    mime = mime.strip()

    # runs a series of verifications on the base mime value and in
    # case it's not valid returns the default values immediately
    if not "/" in mime: return types, extra_m

    # strips the complete set of valid extra values, note
    # that these values are going to be processed as key
    # to value items
    extra = [value.strip() for value in extra if extra]

    # splits the complete mime type into its type and sub
    # type components (first step of normalization)
    type, sub_type = mime.split("/", 1)
    sub_types = sub_type.split("+")

    # iterates over the complete set of sub types to
    # create the full mime type for each of them and
    # add the new full items to the types list (normalization)
    for sub_type in sub_types:
        types.append(type + "/" + sub_type)

    # goes through all of the extra key to value items
    # and converts them into proper dictionary values
    for extra_item in extra:
        if not "=" in extra_item: continue
        extra_item = extra_item.strip()
        key, value = extra_item.split("=")
        extra_m[key] = value

    # returns the final tuple containing both the normalized
    # mime types for the content and the extra key to value items
    return types, extra_m

def parse_cookie(data):
    """
    Parses/interprets the provided cookie data string, returning a
    map structure containing key to value associations of the various
    parts of the cookie.

    In case no key value association exists for the cookie the value
    for such cookie (key) is stored and an empty string (unset).

    :type data: String
    :param data: The cookie serialized data that is going to be parsed
    in order to create the final cookie dictionary/map.
    :rtype: Dictionary
    :return: The final map containing key the value association for the
    various parts of the provided cookie string.
    """

    # creates the dictionary that is going to hold the various cookie
    # key to value associations parsed from the "raw" data
    cookie_m = dict()

    # splits the data information around the proper cookie separator
    # and then iterates over each of the cookies to set them in the
    # final cookie map (with the key to value associations)
    cookies = [cookie.strip() for cookie in data.split(";")]
    for cookie in cookies:
        if not "=" in cookie: cookie += "="
        name, value = cookie.split("=", 1)
        cookie_m[name] = value

    # returns the final map of cookies to the caller method so that
    # proper and easy access is possible to the cookie
    return cookie_m

def parse_multipart(data, boundary):
    """
    Parses the provided data buffer as a set of multipart data
    the content type is not verified inside this method.

    The function returns a tuple containing both a map of "basic"
    form parameters, a map containing the set of file tuples and
    a sequence containing the name and values tuples in order.

    :type data: String
    :param data: The string containing the complete set of data
    that is going to be processed as multipart.
    :type boundary: String
    :param boundary: The string containing the basic boundary header
    value, should be provided from the caller function.
    :rtype: Tuple
    :return: A tuple containing both the map of post attributes,
    the map of file attributes and a list with the various name and
    value tuples (to be able to access ordered values).
    """

    ordered = []
    ordered_m = dict()
    post = dict()
    files = dict()

    boundary = str(boundary)
    boundary = boundary.strip()
    boundary_base = "--" + boundary[9:].strip("\"")
    boundary_value = legacy.bytes(boundary_base + "\r\n")
    boundary_extra = legacy.bytes(boundary_base + "--" + "\r\n")
    boundary_extra_l = len(boundary_extra)
    parts = data.split(boundary_value)
    parts[-1] = parts[-1][:boundary_extra_l * -1]

    # iterates over the complete set of parts in the multi part payload
    # to process them and add them to the appropriate dictionary and list
    for part in parts:
        # in case the current part is not valid or empty skips the
        # current cycle (nothing to be done)
        if not part: continue

        # splits the current part around the beginning of part sequence
        # and retrieves the proper contents if they exist
        part_s = part.split(b"\r\n\r\n", 1)
        headers = part_s[0]
        if len(part_s) > 1: contents = part_s[1]
        else: contents = None

        # strips the current headers string and then splits it around
        # the various lines that define the various headers
        headers_data = headers.strip()
        headers_lines = headers_data.split(b"\r\n")

        # creates the initial headers map of the headers that contains
        # the association between the byte based key and the data value
        # then retrieves the tuple of values and resets the map as it's
        # going to be changed and normalized with the new values
        headers = dict([line.split(b":", 1) for line in headers_lines])
        headers_t = legacy.eager(headers.items())
        headers.clear()

        # runs the normalization process using the header tuples, this
        # should create a map of headers with the key as a normal string
        # and the values encoded as byte based strings (contain data)
        # note that the headers are defined
        for key, value in headers_t:
            key = legacy.str(key).lower()
            value = value.strip()
            headers[key] = value

        # tries to retrieve the content disposition header for the current
        # part and in case there's none it's not possible to process the
        # current part (this header is considered required)
        disposition = headers.get("content-disposition", None)
        if not disposition: continue

        # creates the dictionary that will hold the various parts of the
        # content disposition header that are going to be extracted for
        # latter processing, this is required to make some decisions on
        # the type of part that is currently being processed
        parts = dict()
        parts_data = disposition.split(b";")
        for value in parts_data:
            value_s = value.split(b"=", 1)
            key = legacy.str(value_s[0]).strip().lower()
            if len(value_s) > 1: value = value_s[1].strip()
            else: value = None
            parts[key] = value

        # retrieves the various characteristics values from the headers
        # and from the content disposition of the current part, these
        # values are going to be used to decide on whether the current
        # part is a file or a normal key value attribute
        content_type = headers.get("content-type", None)
        name = parts.get("name", b"\"undefined\"").strip(b"\"")
        filename = parts.get("filename", b"").strip(b"\"")

        # decodes the various content disposition values into an unicode
        # based string so that may be latter be used safely inside the
        # application environment(as expected by the current structure)
        if content_type: content_type = content_type.decode("utf-8")
        name = name.decode("utf-8")
        filename = filename.decode("utf-8")

        # in case the currently discovered contents are valid they
        # must be stripped from the last two bytes so that the real
        # value is retrieved from the provided contents
        contents = contents if contents == None else contents[:-2]

        # verifies if the file name is included in the parts unpacked
        # from the content type in case it does this is considered to be
        # file part otherwise it's a normal key value part
        if "filename" in parts: is_file = True
        else: is_file = False

        if is_file:
            target = files
            file_tuple = (filename, content_type, contents)
            value = FileTuple(file_tuple)
        else:
            target = post
            value = contents if contents == None else contents.decode("utf-8")

        exists = name in ordered_m

        sequence = target.get(name, [])
        sequence.append(value)
        target[name] = sequence

        sequence_o = ordered_m.get(name, [])
        sequence_o.append(value)
        ordered_m[name] = sequence_o

        if exists: continue

        tuple_s = (name, sequence_o)
        ordered.append(tuple_s)

    return (post, files, ordered)

def decode_params(params):
    """
    Decodes the complete set of parameters defined in the
    provided map so that all of keys and values are created
    as unicode strings instead of UTF-8 based strings.

    This method's execution is mandatory on the retrieval of
    the parameters from the sent data.

    :type params: Dictionary
    :param params: The map containing the encoded set of values
    that are going to be decoded from the UTF-8 form.
    :rtype: Dictionary
    :return: The decoded map meaning that all the keys and values
    are in the unicode form instead of the string form.
    """

    # creates the dictionary that will hold the processed/decoded
    # sequences of parameters created from the provided (and original)
    # map of encoded parameters (raw values)
    _params = dict()

    for key, value in params.items():
        items = []
        for item in value:
            is_bytes = legacy.is_bytes(item)
            if is_bytes: item = item.decode("utf-8")
            items.append(item)
        is_bytes = legacy.is_bytes(key)
        if is_bytes: key = key.decode("utf-8")
        _params[key] = items

    return _params

def load_form(form):
    # creates the map that is going to hold the "structured"
    # version of the form with key value associations
    form_s = dict()

    # iterates over all the form items to parse their values
    # and populate the form structured version of it, note that
    # for the sake of parsing the order of the elements in the
    # form is relevant, in case there's multiple values for the
    # same name they are considered as a list, otherwise they are
    # considered as a single value
    for name in form:
        # retrieves the value (as a list) for the current name, then
        # in case the sequence is larger than one element sets it,
        # otherwise retrieves and sets the value as the first element
        value = form[name]
        value = value[0] if isinstance(value, (list, tuple)) and\
            len(value) == 1 else value

        # splits the complete name into its various components
        # and retrieves both the final (last) element and the
        # various partial elements from it
        names = name.split(".")
        final = names[-1]
        partials = names[:-1]

        # sets the initial "struct" reference as the form structured
        # that has just been created (initial structure for iteration)
        # then starts the iteration to retrieve or create the various
        # intermediate structures
        struct = form_s
        for _name in partials:
            _struct = struct.get(_name, {})
            struct[_name] = _struct
            struct = _struct

        # sets the current value in the currently loaded "struct" element
        # so that the reference gets properly updated
        struct[final] = value

    # retrieves the final "normalized" form structure containing
    # a series of chained maps resulting from the parsing of the
    # linear version of the attribute names
    return form_s

def check_login(self, token = None, request = None):
    # tries to retrieve the request from the current context
    # in case it has not been passed through other manner
    request = request or (self.request if self else None)

    # retrieves the data type of the token and creates the
    # tokens sequence value taking into account its type
    if isinstance(token, SEQUENCE_TYPES): tokens = token
    else: tokens = (token,)

    # in case the username value is set in session and there's
    # no token to be validated returns valid and in case the checking
    # of the complete set of tokens is valid also returns valid
    if check_user(self, request = request) and not token: return True
    if check_tokens(self, tokens, request = request): return True

    # returns the default value as invalid because if all the
    # validation procedures have failed the check is invalid
    return False

def check_user(self, request = None):
    # tries to retrieve the reference to the current request
    # either from the provided arguments or from the current context
    request = request or (self.request if self else None)

    # runs the multiple verification strategies available an
    # in case at least one of them succeeds the user is considered
    # to be currently authenticated
    if request and "username" in request.session: return True
    if request and hasattr(request, "tokens_p"): return True

    # by default the user is considered to be not authenticated, all
    # of the tests for authentication have failed
    return False

def check_token(self, token, tokens_m = None, request = None):
    # in case the provided token is invalid or empty the method
    # return immediately in success (simple validation)
    if not token: return True

    # tries to retrieve the tokens map from the provided argument
    # defaulting to the session one in case none is provided
    if tokens_m == None: tokens_m = get_tokens_m(self, request = request)

    # splits the provided token string into its parts, note that
    # a namespace is defined around the dot character
    token_l = token.split(".")

    # iterates over the complete set of parts in the token list
    # of parts to validate the complete chain of values against
    # the map of token parts (namespace validation)
    for token_p in token_l:
        if not isinstance(tokens_m, dict): return False
        if "*" in tokens_m and tokens_m["*"] == True: return True
        if not token_p in tokens_m: return False
        tokens_m = tokens_m[token_p]

    # determines if the final tokens map value is a dictionary
    # and "selects" the proper validation result accordingly
    is_dict = isinstance(tokens_m, dict)
    result = tokens_m.get("_", False) if is_dict else tokens_m

    # verifies if the "final" result value is valid and returns
    # the final validation result accordingly
    return True if result == True else False

def check_tokens(self, tokens, tokens_m = None, request = None):
    # iterates over the complete set of tokens that are going
    # to be validated against the current context and if any of
    # them fails an invalid result is returned otherwise a valid
    # result is returned (indicating that all is valid)
    for token in tokens:
        if not check_token(
            self,
            token,
            tokens_m = tokens_m,
            request = request
        ): return False
    return True

def ensure_login(self, token = None, context = None, request = None):
    request = request or (self.request if self else None)
    is_auth = check_user(self, request = request)
    if not is_auth: raise exceptions.AppierException(
        message = "User not authenticated",
        code = 403,
        token = token,
        context = context
    )
    if check_token(self, token, request = request): return
    raise exceptions.AppierException(
        message = "Not enough permissions",
        code = 403,
        token = token,
        context = context
    )

def get_tokens_m(self, request = None, set = None):
    """
    Retrieves the map of tokens from the current session so that
    they can be used for proper ACL validation.

    In case the current session contains a sequence based representation
    of the tokens they are converted to their equivalent map value.

    :type request: Request
    :param request: The request that is going to be used to access
    the session information, if any.
    :type set: bool
    :param set: If the possibly converted tokens list should be persisted
    into the current session, sparing some CPU cycles on next execution,
    in case no value is provided a default value is applied taking into
    account the current execution context.
    :rtype: Dictionary
    :return: The map of tokens to be used for ACL validation.
    """

    # tries to retrieve the request from the current context
    # in case it has not been passed through other manner, if
    # no valid context is found returns invalid value immediately
    request = request or (self.request if self else None)
    if not request: return dict()

    # verifies if the set flag is set and if that's not the case
    # ensures proper default value taking into account if there's
    # a token "provider method" defined or not
    if set == None:
        set = False if hasattr(request, "tokens_p") else True

    # tries to retrieve the "provider method "for the tokens under the
    # current request an in case it's not available used the default
    # one (simple session access)
    try:
        if hasattr(request, "tokens_p"): tokens_m = request.tokens_p()
        else: tokens_m = request.session.get("tokens", {})
    except Exception:
        return dict()

    # verifies if the resulting value is either a map or a sequence,
    # going to be used for decisions on normalization
    is_map = isinstance(tokens_m, dict)
    is_sequence = isinstance(tokens_m, (list, tuple))

    # if the tokens value is already a map then an immediate return
    # is going to be performed (it is a valid tokens map)
    if is_map: return tokens_m

    # in case the value present in the tokens value is a sequence
    # it must be properly converted into the equivalent map value
    if is_sequence:
        # converts the tokens sequence into a map version of it
        # so that proper structured verification is possible
        tokens_m = to_tokens_m(tokens_m)

        # in case the set flag is set the tokens map should
        # be set in the request session (may be dangerous)
        # and then returns the tokens map to the caller method
        if set: request.session["tokens"] = tokens_m
        return tokens_m

    # returns the "default" empty tokens map as it was not possible
    # to retrieve any information regarding tokens from the
    # current context and environment
    return dict()

def to_tokens_m(tokens):
    # creates a new map to be used to store tokens map that is
    # going to be created from the list/sequence version
    tokens_m = dict()

    # iterates over the complete set of tokens in the
    # sequence to properly add their namespace parts
    # to the tokens map (as specified)
    for token in tokens:
        tokens_c = tokens_m
        token_l = token.split(".")
        head, tail = token_l[:-1], token_l[-1]

        for token_p in head:
            current = tokens_c.get(token_p, {})
            is_dict = isinstance(current, dict)
            if not is_dict: current = {"_" : current}
            tokens_c[token_p] = current
            tokens_c = current

        leaf = tokens_c.get(tail, None)
        if leaf and isinstance(leaf, dict): leaf["_"] = True
        else: tokens_c[tail] = True

    # returns the final map version of the token to the caller
    # method so that it may be used for structure verification
    return tokens_m

def dict_merge(first, second, override = True, recursive = False):
    # in case no override exists then the order of the items is
    # exchanged so that the first overrides the second values
    # and not the exact opposite
    if not override: first, second = second, first

    # in case the recursive flag is set, must iterate over all
    # of the first items to try to merge any possible dictionary
    # value using a recursive strategy
    if recursive:
        # creates the dictionary that is going to store the final
        # merged value resulting from both dictionaries
        final = dict()

        # runs the main iteration cycles around the first dictionary
        # trying to find possible conflicts that would required a
        # smarter merge strategy
        for key, value in legacy.iteritems(first):
            # in case the current key is not present in the second
            # dictionary (there's no conflict) and so a simple set
            # strategy should be applied
            if not key in second:
                final[key] = value
                continue

            # retrieves the other (second) value and determines if
            # it represents a dictionary (smart merge) or if instead
            # it's of any other type (no smart merge possible)
            other = second[key]
            if isinstance(value, dict) and isinstance(other, dict):
                final[key] = dict_merge(
                    value,
                    other,
                    override = override,
                    recursive = recursive
                )
            else:
                final[key] = other

        # runs the final iteration cycles around the second dictionary
        # values to try to set the unique second values in the final
        for key, value in legacy.iteritems(second):
            if key in final: continue
            final[key] = value

        # returns the final merged result to the caller method, this
        # result should contain all of its dictionary values properly
        # merged within both the first and second values
        return final

    # otherwise (uses a simple strategy) and creates a new dictionary
    # for the first value, then updates it with the second set of
    # dictionary values, returning then the newly created dictionary
    # to the caller method (basic update strategy)
    else:
        final = dict(first)
        final.update(second)
        return final

def deprecated(message = "Function %s is now deprecated"):
    """
    Decorator that marks a certain function or method as
    deprecated so that whenever such function is called
    an output messaged warns the developer about the
    deprecation (incentive).

    :type message: String
    :param message: The message template to be used in the
    output operation of the error.
    :rtype: Decorator
    :return: The decorator that should be used to wrap a
    function and mark it as deprecated (send warning).
    """

    def decorator(function):

        name = function.__name__ if hasattr(function, "__name__") else None

        @functools.wraps(function)
        def interceptor(*args, **kwargs):
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                message % name,
                category = DeprecationWarning,
                stacklevel = 2
            )
            warnings.simplefilter("default", DeprecationWarning)
            return function(*args, **kwargs)

        return interceptor

    return decorator

def cached(function):
    """
    Decorator that marks a certain function as cached meaning that
    the local context of the instance associated with the function
    (method) is going to be used to store the result and further
    requests to the function will use the cached result, resulting
    in an improved resolution time.

    The life-cycle of the context is critical to avoid issues with
    invalid cache invalidation.

    :rtype: Decorator
    :return: The decorator that should be used to wrap a function
    marking it as ready to cache it's return value on current context.
    """

    name = function.__name__

    @functools.wraps(function)
    def _cached(self, *args, **kwargs):
        # tries to retrieve the current execution context, most
        # of the times this should be a request object for the
        # current temporary execution life-cycle
        context = get_context(self)

        # retrieves the properties map (if possible) and then
        # verifies the existence or not of the name in such map
        # returning the value immediately if it's cached
        properties = context.properties if context else None
        exists = name in properties if properties else False
        if exists: return properties[name]

        # as no cache retrieval was possible executes the function
        # operation and caches the resulting value into the properties
        # map (in case it exists)
        value = function(self, *args, **kwargs)
        if not properties == None: properties[name] = value
        return value

    return _cached

def private(function):

    @functools.wraps(function)
    def _private(self, *args, **kwargs):
        ensure = kwargs.get("ensure", True)
        request = kwargs.get("request", self.request)
        if ensure: ensure_login(self, request = request)
        sanitize(function, kwargs)
        return function(self, *args, **kwargs)

    return _private

def ensure(token = None, context = None):

    def decorator(function):

        @functools.wraps(function)
        def interceptor(self, *args, **kwargs):
            ensure = kwargs.get("ensure", True)
            request = kwargs.get("request", self.request)
            if ensure: ensure_login(
                self,
                token = token,
                context = context,
                request = request
            )
            sanitize(function, kwargs)
            return function(self, *args, **kwargs)

        return interceptor

    return decorator

def delayed(function):

    @functools.wraps(function)
    def _delayed(self, *args, **kwargs):
        _args = [self] + list(args)
        return self.owner.delay(function, _args, kwargs)

    return _delayed

def route(url, method = "GET", asynchronous = False, json = False, opts = None):

    def decorator(function, *args, **kwargs):
        if is_detached(function): delay(function, *args, **kwargs)
        else: common.base().App.add_route(
            method,
            url,
            function,
            asynchronous = asynchronous,
            json = json,
            opts = opts
        )
        return function

    def delay(function, *args, **kwargs):
        global CREATION_COUNTER
        route = (url, method, asynchronous, json, opts)
        if not hasattr(function, "_routes"): function._routes = []
        function._routes.append(route)
        function.creation_counter = CREATION_COUNTER
        CREATION_COUNTER += 1

    return decorator

def error_handler(code, scope = None, json = False, opts = None):

    def decorator(function, *args, **kwargs):
        if is_detached(function): delay(function, *args, **kwargs)
        else: common.base().App.add_error(
            code,
            function,
            json = json,
            opts = opts
        )
        return function

    def delay(function, *args, **kwargs):
        global CREATION_COUNTER
        error = (code, scope, json, opts)
        if not hasattr(function, "_errors"): function._errors = []
        function._errors.append(error)
        function.creation_counter = CREATION_COUNTER
        CREATION_COUNTER += 1
        return function

    return decorator

def exception_handler(exception, scope = None, json = False, opts = None):

    def decorator(function, *args, **kwargs):
        if is_detached(function): delay(function, *args, **kwargs)
        else: common.base().App.add_exception(
            exception,
            function,
            json = json,
            opts = opts
        )
        return function

    def delay(function, *args, **kwargs):
        global CREATION_COUNTER
        _exception = (exception, scope, json, opts)
        if not hasattr(function, "_exceptions"): function._exceptions = []
        function._exceptions.append(_exception)
        function.creation_counter = CREATION_COUNTER
        CREATION_COUNTER += 1
        return function

    return decorator

def before_request(scope = "all", opts = None):

    def decorator(function, *args, **kwargs):
        if is_detached(function): delay(function, *args, **kwargs)
        else: common.base().App.add_custom("before_request", function, opts = opts)
        return function

    def delay(function, *args, **kwargs):
        global CREATION_COUNTER
        _custom = ("before_request", opts)
        if not hasattr(function, "_customs"): function._customs = []
        function._customs.append(_custom)
        function.creation_counter = CREATION_COUNTER
        CREATION_COUNTER += 1
        return function

    return decorator

def after_request(scope = "all", opts = None):

    def decorator(function, *args, **kwargs):
        if is_detached(function): delay(function, *args, **kwargs)
        else: common.base().App.add_custom("after_request", function, opts = opts)
        return function

    def delay(function, *args, **kwargs):
        global CREATION_COUNTER
        _custom = ("after_request", opts)
        if not hasattr(function, "_customs"): function._customs = []
        function._customs.append(_custom)
        function.creation_counter = CREATION_COUNTER
        CREATION_COUNTER += 1
        return function

    return decorator

def is_detached(function):
    """
    Verifies if the provided function value is considered to be
    a detached method from a class, this is valid for situations
    where the type of the value is a function and there's a reference
    to the parent class of definition.

    This method is not completely safe as it relies on the fact that
    by convention the first argument of a "future" method is the "self"
    one, meaning that a "normal function" would be detected as a
    method if the first argument of it is named self.

    :type function: Function
    :param function: The function value that is going to be evaluated
    for the presence of a detached method.
    :rtype: bool
    :return: If the provided function value refers a detached method
    of a certain class.
    """

    # verifies if the provided value is a valid function type
    # an in case it's not it's considered to not be a detached
    is_function = isinstance(function, types.FunctionType)
    if not is_function: return False

    # retrieves the function's specification (should include arguments)
    # and then verifies that they are valid and that at least one valid
    # argument exists for the specification (as required by methods)
    spec = legacy.getargspec(function)
    if not spec: return False
    if not spec.args: return False

    # verifies that the name of the first argument of the function is the
    # the instance one, if that's the case this should be a detached method
    # that is currently being identified as a function
    return spec.args[0] == "self"

def sanitize(function, kwargs):
    removal = []
    method_a = legacy.getargspec(function)[0]
    for name in kwargs:
        if name in method_a: continue
        removal.append(name)
    for name in removal: del kwargs[name]

def verify(condition, message = None, code = None, exception = None, **kwargs):
    if condition: return
    exception = exception or exceptions.AssertionError
    kwargs = dict(kwargs)
    if not message == None: kwargs["message"] = message
    if not code == None: kwargs["code"] = code
    raise exception(**kwargs)

def verify_equal(first, second, message = None, code = None, exception = None, **kwargs):
    message = message or "Expected %s got %s" % (repr(second), repr(first))
    return verify(
        first == second,
        message = message,
        code = code,
        exception = exception,
        **kwargs
    )

def verify_not_equal(first, second, message = None, code = None, exception = None, **kwargs):
    message = message or "Expected %s not equal to %s" % (repr(first), repr(second))
    return verify(
        not first == second,
        message = message,
        code = code,
        exception = exception,
        **kwargs
    )

def verify_many(sequence, message = None, code = None, exception = None, **kwargs):
    for condition in sequence:
        verify(
            condition,
            message = message,
            code = code,
            exception = exception,
            **kwargs
        )

def execute(args, command = None, path = None, shell = None, encoding = None):
    if shell == None: shell = os.name == "nt"
    if not encoding: encoding = sys.getfilesystemencoding()
    if command: args = command.split(" ")
    process = subprocess.Popen(
        args,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        shell = shell,
        cwd = path
    )
    code = process.wait()
    stdout = process.stdout.read()
    stderr = process.stderr.read()
    stdout = stdout.decode(encoding)
    stderr = stderr.decode(encoding)
    return dict(
        stdout = stdout,
        stderr = stderr,
        code = code
    )

@contextlib.contextmanager
def ctx_locale(name = "", force = False):
    saved = locale.setlocale(locale.LC_ALL)
    if saved == name and not force: yield saved; return
    try: yield locale.setlocale(locale.LC_ALL, name)
    finally: locale.setlocale(locale.LC_ALL, saved)

@contextlib.contextmanager
def ctx_request(app = None):
    app = app or common.base().get_app()
    _request = app._request
    app._request = app._mock
    try: yield True
    finally: app._request = _request

class FileTuple(tuple):
    """
    Tuple class (inherits from tuple) that represents
    the name, content type and (data) contents of a file
    in the context of the appier infra-structure.

    This class shares many of the signature with the
    typical python file interface, allowing most of
    the operation to be performed (eg: read, seek,
    tell, etc.).
    """

    def __init__(self, *args, **kwargs):
        tuple.__init__(*args, **kwargs)
        self._position = 0

    @classmethod
    def from_data(cls, data, name = None, mime = None):
        file_tuple = cls((name, mime, data))
        return file_tuple

    @classmethod
    def from_file(cls, file, name = None, mime = None):
        data = file.read()
        file_tuple = cls.from_data(data, name = name, mime = mime)
        return file_tuple

    @classmethod
    def from_path(cls, path, name = None, mime = None, guess = True):
        mime = cls.guess(path) if mime == None and guess else mime
        file = open(path, "rb")
        try: file_tuple = cls.from_file(file, name = name, mime = mime)
        finally: file.close()
        return file_tuple

    @classmethod
    def guess(self, name):
        mime = mimetypes.guess_type(name, strict = False)[0]
        if mime: return mime
        return None

    def read(self, count = None):
        data, data_l = self[2], len(self[2])
        if not count and self._position == 0: data, offset = data, data_l
        elif not count: data, offset = data[self._position:], data_l - self._position
        else: data, offset = data[self._position:self._position + count], count
        self._position += offset
        return data

    def seek(self, offset, whence = os.SEEK_SET):
        if whence == os.SEEK_SET:
            self._position = offset
        if whence == os.SEEK_CUR:
            self._position += offset
        if whence == os.SEEK_END:
            self._position = len(self[2]) + offset

    def tell(self):
        return self._position

    def save(self, path):
        contents = self[2]
        file = open(path, "wb")
        try: file.write(contents)
        finally: file.close()

    @property
    def name(self):
        return self[0]

    @property
    def mime(self):
        return self[1]

    @property
    def data(self):
        return self[2]

class BaseThread(threading.Thread):
    """
    The top level thread class that is meant to encapsulate
    a running base object and run it in a new context.

    This base thread may be used to run a network loop allowing
    a main thread to continue with execution logic.
    """

    def __init__(self, owner = None, daemon = False, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.owner = owner
        self.daemon = daemon

    def run(self):
        threading.Thread.run(self)
        if not self.owner: return
        self.owner.start()
        self.owner = None

class JSONEncoder(json.JSONEncoder):

    def __init__(self, *args, **kwargs):
        self.permissive = kwargs.pop("permissive", True)
        json.JSONEncoder.__init__(self, *args, **kwargs)

    def default(self, obj, **kwargs):
        if hasattr(obj, "json_v"): return obj.json_v()
        if self.permissive: return str(obj)
        return json.JSONEncoder.default(self, obj, **kwargs)
