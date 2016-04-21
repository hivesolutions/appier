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

from . import api
from . import async
from . import base
from . import cache
from . import compress
from . import config
from . import controller
from . import data
from . import defines
from . import exceptions
from . import export
from . import geo
from . import git
from . import http
from . import legacy
from . import log
from . import meta
from . import model
from . import mongo
from . import observer
from . import part
from . import redisdb
from . import request
from . import scheduler
from . import serialize
from . import session
from . import settings
from . import smtp
from . import structures
from . import typesf
from . import util
from . import validation

from .api import Api, OAuthApi, OAuth1Api, OAuth2Api
from .async import AsyncManager, SimpleManager, QueueManager
from .base import APP, LEVEL, NAME, VERSION, PLATFORM, API_VERSION, BUFFER_SIZE, MAX_LOG_SIZE,\
    MAX_LOG_COUNT, App, APIApp, WebApp, get_app, get_name, get_base_path, get_request,\
    get_session, get_model, get_controller, get_adapter, get_manager, get_logger, get_level, is_devel, is_safe
from .cache import Cache, MemoryCache
from .compress import Compress
from .config import conf, conf_prefix, conf_s
from .controller import Controller
from .data import DataAdapter, MongoAdapter, TinyAdapter, Collection, MongoCollection, TinyCollection
from .defines import ITERABLES, MOBILE_REGEX, MOBILE_PREFIX_REGEX, BODY_REGEX, TAG_REGEX,\
    EMAIL_REGEX, WINDOWS_LOCALE
from .exceptions import AppierException, OperationalError, SecurityError, AssertionError,\
    ValidationError, NotFoundError, NotImplementedError, BaseInternalError, ValidationInternalError,\
    ValidationMultipleError, HTTPError, APIError, APIAccessError, OAuthAccessError
from .export import ExportManager, MongoEncoder
from .geo import GeoResolver
from .git import Git
from .http import get, post, put, delete
from .log import MemoryHandler, ThreadFormatter, rotating_handler, smtp_handler, in_signature
from .meta import Ordered, Indexed
from .model import Model, LocalModel, Field, link, operation, field
from .mongo import Mongo, get_connection, get_db, drop_db, object_id, dumps
from .observer import Observable
from .part import Part
from .redisdb import Redis
from .request import CODE_STRINGS, Request, MockRequest
from .scheduler import Scheduler
from .serialize import serialize_csv, serialize_ics, build_encoder
from .session import Session, MockSession, MemorySession, FileSession, RedisSession, ClientSession
from .settings import DEBUG, USERNAME, PASSWORD
from .smtp import message, message_base, message_netius, smtp_engine, multipart, plain,\
    html, header
from .structures import OrderedDict
from .typesf import Type, File, Files, ImageFile, ImageFiles, image, images, Reference,\
    reference, References, references
from .util import is_iterable, is_mobile, email_parts, email_mime, email_name, email_base,\
    obfuscate, request_json, get_object, resolve_alias, page_types, find_types, norm_object,\
    set_object, leafs, gen_token, html_to_text, camel_to_underscore, camel_to_readable, quote,\
    unquote, base_name, base_name_m, parse_cookie, parse_multipart, decode_params, load_form,\
    check_login, ensure_login, dict_merge, private, ensure, delayed, route, error_handler,\
    exception_handler, before_request, after_request, is_detached, sanitize, verify, execute,\
    ctx_locale, FileTuple, BaseThread, JSONEncoder
from .validation import validate, validate_b, validate_e, safe, eq, gt, gte, lt, lte, not_null,\
    not_empty, not_false, is_in, is_simple, is_email, is_url, is_regex, field_eq, field_gt,\
    field_gte, field_lt, field_lte, string_gt, string_lt, string_eq, equals, not_past, not_duplicate,\
    all_different, no_self

from .mongo import get_connection as get_mongo
from .mongo import get_db as get_mongo_db
from .mongo import drop_db as drop_mongo_db
from .mongo import dumps as dumps_mongo
from .mongo import object_id as object_id_mongo
from .redisdb import get_connection as get_redis
from .redisdb import dumps as dumps_redis

HTTPError = exceptions.HTTPError
