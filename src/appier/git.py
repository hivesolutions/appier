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

from . import util
from . import common
from . import legacy
from . import exceptions

class Git(object):

    @classmethod
    def is_git(cls, path = None):
        path = path or common.base().get_base_path()
        try: result = util.execute(["git", "status"], path = path)
        except OSError: return False
        code = result["code"]
        return code == 0

    @classmethod
    def clone(cls, url, path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "clone", url], path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def fetch(cls, flags = [], path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "fetch"] + flags, path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def pull(cls, flags = [], path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "pull"] + flags, path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def push(cls, flags = [], path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "push"] + flags, path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def commit(cls, message = "Update", flags = [], path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "commit", "-m", message] + flags, path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def checkout(cls, branch = "master", flags = [], path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "checkout", branch] + flags, path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def add(cls, target = "*", flags = [], path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "add", target] + flags, path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def add_upstream(cls, url, name = "upstream", path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "remote", "add", name, url], path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def config(cls, key, value, _global = True, path = None, raise_e = True):
        path = path or common.base().get_base_path()
        result = util.execute(
            ["git", "config", "--global" if _global else "", key, value],
            path = path
        )
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        return message

    @classmethod
    def get_config(cls, key, _global = True, path = None, raise_e = False):
        path = path or common.base().get_base_path()
        result = util.execute(
            ["git", "config", "--global" if _global else "", "--get", key],
            path = path
        )
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        value = message.strip()
        return value

    @classmethod
    def get_branches(cls, names = False, path = None, raise_e = False):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "branch"], path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        branches = message.strip()
        branches = branches.split("\n")
        branches = [(value.lstrip("* "), value.startswith("*")) for value in branches]
        if names: branches = [branch[0] for branch in branches]
        return branches

    @classmethod
    def get_branch(cls, path = None, raise_e = False):
        path = path or common.base().get_base_path()
        branches = cls.get_branches(path = path, raise_e = raise_e)
        for branch, selected in branches:
            if not selected: continue
            return branch
        return None

    @classmethod
    def get_commit(cls, path = None, raise_e = False):
        path = path or common.base().get_base_path()
        result = util.execute(["git", "rev-parse", "HEAD"], path = path)
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        commit = message.strip()
        return commit

    @classmethod
    def get_origin(cls, path = None, raise_e = False):
        path = path or common.base().get_base_path()
        result = util.execute(
            ["git", "config", "--get", "remote.origin.url"],
            path = path
        )
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        origin = message.strip()
        origin = cls.safe_origin(origin)
        return origin

    @classmethod
    def get_repo_path(cls, path = None, raise_e = False):
        path = path or common.base().get_base_path()
        result = util.execute(
            ["git", "rev-parse", "--show-toplevel"],
            path = path
        )
        if cls._wrap_error(result, raise_e = raise_e): return None
        message = result.get("stdout", "")
        repo_path = message.strip()
        return repo_path

    @classmethod
    def safe_origin(cls, origin, display_l = 3):
        parse = legacy.urlparse(origin)
        safe_l = []
        if parse.scheme: safe_l.append(parse.scheme + "://")
        if parse.username: safe_l.append(parse.username)
        if parse.password:
            obfuscated = util.obfuscate(parse.password)
            safe_l.append(":" + obfuscated)
        if parse.username: safe_l.append("@")
        if parse.hostname: safe_l.append(parse.hostname)
        if parse.path: safe_l.append(parse.path)
        return "".join(safe_l)

    @classmethod
    def norm_origin(cls, origin, prefix = "https://"):
        if origin.startswith(("http://", "https://")): return origin
        if origin.endswith(".git"): origin = origin[:-4]
        origin = origin.replace(":", "/")
        origin = prefix + origin
        return origin

    @classmethod
    def parse_origin(cls, origin, safe = True):
        parse = legacy.urlparse(origin)
        if safe and not parse.scheme:
            origin = cls.norm_origin(origin)
            return cls.parse_origin(origin, safe = False)
        scheme = parse.scheme if parse.scheme else "ssh"
        username = parse.username if parse.username else None
        password = parse.password if parse.password else None
        hostname = parse.hostname if parse.hostname else None
        path = parse.path if parse.path else None
        return dict(
            scheme = scheme,
            username = username,
            password = password,
            hostname = hostname,
            path = path
        )

    @classmethod
    def _wrap_error(cls, result, raise_e = False):
        code = result["code"]
        if code == 0: return False
        if raise_e:
            raise exceptions.OperationalError(
                message = result.get("stderr", "") or\
                    result.get("stdout", "")
            )
        return True
