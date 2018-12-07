#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2018 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import sys
import json

from . import legacy

FILE_NAME = "appier.json"
""" The default name of the file that is going to be
used for the loading of configuration values from json """

FILE_TEMPLATE = "appier.%s.json"
""" The template to be used in the construction of the
domain specific configuration file paths """

HOME_FILE = "~/.home"
""" The location of the file that may be used to "redirect"
the home directory contents to a different directory """

IMPORT_NAMES = ("$import", "$include", "$IMPORT", "$INCLUDE")
""" The multiple possible definitions of the special configuration
name that references a list of include files to be loaded """

CASTS = {
    bool : lambda v: v if isinstance(v, bool) else v in ("1", "true", "True"),
    list : lambda v: v if isinstance(v, list) else v.split(";"),
    tuple : lambda v: v if isinstance(v, tuple) else tuple(v.split(";"))
}
""" The map containing the various cast method
operation associated with the various data types,
they provide a different type of casting strategy """

ENV_ENCODINGS = (
    "utf-8",
    sys.getdefaultencoding(),
    sys.getfilesystemencoding()
)
""" The sequence of encodings that are going to
be used to try to decode possible byte based strings
for the various environment variable values """

CONFIGS = {}
""" The map that contains the key value association
for all the currently set global configurations """

CONFIG_F = []
""" The list of files that have been used for the loading
of the configuration through this session, every time a
loading of configuration from a file occurs the same path
is added to this global list """

HOMES = []
""" Global reference to the paths to the directory considered
to be the home on in terms of configuration, this value should
be set on the initial loading of the ".home" file """

if not isinstance(__builtins__, dict):
    __builtins__ = __builtins__.__dict__

def conf(name, default = None, cast = None, ctx = None):
    """
    Retrieves the configuration value for the provided value
    defaulting to the provided default value in case no value
    is found for the provided name.

    An optional cast operation may be performed on the value
    in case it's requested.

    :type name: String
    :param name: The name of the configuration value to be
    retrieved.
    :type default: Object
    :param default: The default value to be retrieved in case
    no value was found for the provided name.
    :type cast: Type/String
    :param cast: The cast operation to be performed in the
    resolved value (optional).
    :type ctx: Dictionary
    :param ctx: The context dictionary to be used for situations
    where a more contextual configuration is meant to be used instead
    of the process wide global configuration.
    :rtype: Object
    :return: The value for the configuration with the requested
    name or the default value if no value was found.
    """

    configs = ctx["configs"] if ctx else CONFIGS
    cast = _cast_r(cast)
    value = configs.get(name, default)
    if cast and not value == None: value = cast(value)
    return value

def conf_prefix(prefix, ctx = None):
    configs = ctx["configs"] if ctx else CONFIGS
    configs_prefix = dict()
    for name, value in configs.items():
        if not name.startswith(prefix): continue
        configs_prefix[name] = value
    return configs_prefix

def conf_suffix(suffix, ctx = None):
    configs = ctx["configs"] if ctx else CONFIGS
    configs_suffix = dict()
    for name, value in configs.items():
        if not name.endswith(suffix): continue
        configs_suffix[name] = value
    return configs_suffix

def conf_s(name, value, ctx = None):
    configs = ctx["configs"] if ctx else CONFIGS
    configs[name] = value

def conf_r(name, ctx = None):
    configs = ctx["configs"] if ctx else CONFIGS
    if not name in configs: return
    del configs[name]

def conf_d(ctx = None):
    configs = ctx["configs"] if ctx else CONFIGS
    return configs

def conf_ctx():
    return dict(configs = dict(), config_f = dict())

def load(names = (FILE_NAME,), path = None, encoding = "utf-8", ctx = None):
    paths = []
    homes = get_homes()
    for home in homes:
        paths += [
            os.path.join(home),
            os.path.join(home, ".config"),
        ]
    paths += [sys.prefix]
    paths.append(path)
    for path in paths:
        for name in names:
            load_file(name = name, path = path, encoding = encoding, ctx = ctx)
    load_env(ctx = ctx)

def load_file(name = FILE_NAME, path = None, encoding = "utf-8", ctx = None):
    configs = ctx["configs"] if ctx else CONFIGS
    config_f = ctx["config_f"] if ctx else CONFIG_F

    if path: path = os.path.normpath(path)
    if path: file_path = os.path.join(path, name)
    else: file_path = name

    file_path = os.path.abspath(file_path)
    file_path = os.path.normpath(file_path)
    base_path = os.path.dirname(file_path)

    exists = os.path.exists(file_path)
    if not exists: return

    exists = file_path in config_f
    if exists: config_f.remove(file_path)
    config_f.append(file_path)

    file = open(file_path, "rb")
    try: data = file.read()
    finally: file.close()
    if not data: return

    data = data.decode(encoding)
    data_j = json.loads(data)

    _load_includes(base_path, data_j, encoding = encoding)

    for key, value in data_j.items():
        if not _is_valid(key): continue
        configs[key] = value

def load_env(ctx = None):
    configs = ctx["configs"] if ctx else CONFIGS

    config = dict(os.environ)
    homes = get_homes()

    for home in homes:
        _load_includes(home, config)

    for key, value in legacy.iteritems(config):
        if not _is_valid(key): continue
        configs[key] = value
        is_bytes = legacy.is_bytes(value)
        if not is_bytes: continue
        for encoding in ENV_ENCODINGS:
            try: value = value.decode(encoding)
            except UnicodeDecodeError: pass
            else: break
        configs[key] = value

def get_homes(
    file_path = HOME_FILE,
    default = "~",
    encoding = "utf-8",
    force_default = False
):
    global HOMES
    if HOMES: return HOMES

    HOMES = os.environ.get("HOMES", None)
    HOMES = HOMES.split(";") if HOMES else HOMES
    if not HOMES == None: return HOMES

    default = os.path.expanduser(default)
    default = os.path.abspath(default)
    default = os.path.normpath(default)
    HOMES = [default]

    file_path = os.path.expanduser(file_path)
    file_path = os.path.normpath(file_path)
    exists = os.path.exists(file_path)
    if not exists: return HOMES

    if not force_default: del HOMES[:]

    file = open(file_path, "rb")
    try: data = file.read()
    finally: file.close()

    data = data.decode("utf-8")
    data = data.strip()
    paths = data.split()

    for path in paths:
        path = path.strip()
        if not path: continue
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        path = os.path.normpath(path)
        HOMES.append(path)

    return HOMES

def _cast_r(cast):
    is_string = type(cast) in legacy.STRINGS
    if is_string: cast = __builtins__.get(cast, None)
    if not cast: return None
    return CASTS.get(cast, cast)

def _load_includes(base_path, config, encoding = "utf-8"):
    includes = ()

    for alias in IMPORT_NAMES:
        includes = config.get(alias, includes)

    if legacy.is_string(includes):
        includes = includes.split(";")

    for include in includes:
        load_file(
            name = include,
            path = base_path,
            encoding = encoding
        )

def _is_valid(key):
    if key in IMPORT_NAMES: return False
    return True

def _is_devel():
    """
    Simple debug/development level detection mechanism to be
    used at load time to determine if the system is running
    under a development (debug) environment.

    This function should not be used at runtime as there are
    other (more powerful) mechanisms to archive the same
    type of results.

    :rtype: bool
    :return: If the current environment is running under a
    development type level of traceability.
    """

    return conf("LEVEL", "INFO") in ("DEBUG",)

def _is_secure():
    """
    Simple secure variable that should be overriden only under
    very specific/critical operation that control if the current
    environment should hide information that would otherwise
    compromise some of the system's secrecy (eg: version, name, etc.)

    :rtype: bool
    :return: If the current environment is running under a
    secured type level of traceability.
    """

    return conf("SECURE", True, cast = bool)

load()
