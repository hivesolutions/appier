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

from . import amqp
from . import api
from . import asynchronous
from . import base
from . import bus
from . import cache
from . import component
from . import compress
from . import config
from . import controller
from . import crypt
from . import data
from . import defines
from . import exceptions
from . import execution
from . import export
from . import extra
from . import geo
from . import git
from . import http
from . import legacy
from . import log
from . import meta
from . import mock
from . import model
from . import mongo
from . import observer
from . import part
from . import preferences
from . import queuing
from . import redisdb
from . import request
from . import scheduler
from . import serialize
from . import session
from . import settings
from . import smtp
from . import storage
from . import structures
from . import typesf
from . import util
from . import validation

from .amqp import AMQP
from .api import API, OAuthAPI, OAuth1API, OAuth2API
from .asynchronous import ASYNC_HEADER, AsyncManager, SimpleManager, QueueManager, AwaitWrapper, CoroutineWrapper,\
    AyncgenWrapper, await_wrap, await_yield, ensure_generator, is_coroutine, is_coroutine_object, is_coroutine_native,\
    to_coroutine, wrap_silent, unavailable, is_neo, Future, coroutine, wakeup, sleep, wait, notify, build_future,\
    ensure_async, header_a, ensure_a
from .base import APP, LEVEL, NAME, VERSION, PLATFORM, IDENTIFIER_SHORT, IDENTIFIER_LONG, IDENTIFIER,\
    API_VERSION, BUFFER_SIZE, MAX_LOG_SIZE, MAX_LOG_COUNT, App, APIApp, WebApp, Template, get_app, get_name,\
    get_base_path, get_cache, get_preferences, get_bus, get_request, get_session, get_model, get_controller, get_part,\
    get_adapter, get_manager, get_logger, get_level, is_loaded, is_devel, is_safe, to_locale, on_exit
from .bus import Bus, MemoryBus, RedisBus
from .cache import Cache, MemoryCache, FileCache, RedisCache, SerializedCache
from .component import Component
from .compress import Compress
from .config import conf, conf_prefix, conf_suffix, conf_s, conf_r, conf_d, conf_ctx
from .controller import Controller
from .crypt import Cipher, RC4, Spritz
from .data import DataAdapter, MongoAdapter, TinyAdapter, Collection, MongoCollection, TinyCollection
from .defines import ITERABLES, MOBILE_REGEX, TABLET_REGEX, MOBILE_PREFIX_REGEX, BODY_REGEX, TAG_REGEX,\
    EMAIL_REGEX, BROWSER_INFO, OS_INFO, WINDOWS_LOCALE, SLUG_PERMUTATIONS
from .exceptions import AppierException, OperationalError, SecurityError, AssertionError,\
    ValidationError, NotFoundError, NotImplementedError, BaseInternalError, ValidationInternalError,\
    ValidationMultipleError, HTTPError, APIError, APIAccessError, OAuthAccessError
from .execution import ExecutionThread, background, insert_work, interval_work, seconds_work,\
    minutes_work, hourly_work, daily_work, weekly_work, monthly_work, seconds_eval, minutes_eval,\
    hourly_eval, daily_eval, weekly_eval, monthly_eval
from .export import ExportManager
from .extra import get_a, post_a, put_a, delete_a, patch_a, get_w, post_w, put_w, delete_w, patch_w
from .geo import GeoResolver
from .git import Git
from .http import file_g, get_f, get, post, put, delete, HTTPResponse
from .log import MemoryHandler, BaseFormatter, ThreadFormatter, DummyLogger, rotating_handler, smtp_handler,\
    in_signature
from .meta import Ordered, Indexed
from .mock import MockObject, MockResponse, MockApp
from .model import Model, LocalModel, Field, link, operation, view, field, type_d, is_unset
from .mongo import Mongo, MongoEncoder, get_connection, reset_connection, get_db, drop_db, object_id, dumps
from .observer import Observable
from .part import Part
from .preferences import Preferences, MemoryPreferences, FilePreferences, RedisPreferences
from .queuing import Queue, MemoryQueue, MultiprocessQueue, AMQPQueue
from .redisdb import Redis
from .request import CODE_STRINGS, Request, MockRequest
from .scheduler import Scheduler
from .serialize import serialize_csv, serialize_ics, build_encoder
from .session import Session, MockSession, MemorySession, FileSession, RedisSession, ClientSession
from .settings import DEBUG, USERNAME, PASSWORD
from .smtp import message, message_base, message_netius, smtp_engine, multipart, plain,\
    html, header
from .storage import StorageEngine, BaseEngine, FsEngine
from .structures import OrderedDict, LazyDict, LazyValue, GeneratorFile, lazy_dict, lazy
from .typesf import AbstractType, Type, File, Files, ImageFile, ImageFiles, image, images, Reference,\
    reference, References, references, Encrypted, encrypted, secure
from .util import is_iterable, is_mobile, is_tablet, is_browser, is_bot, browser_info, email_parts, email_mime,\
    email_name, email_base, date_to_timestamp, obfuscate, import_pip, ensure_pip, install_pip, install_pip_s,\
    request_json, get_context, get_object, resolve_alias, page_types, find_types, norm_object, set_object, leafs,\
    gather_errors, gen_token, html_to_text, camel_to_underscore, camel_to_readable, underscore_to_readable, quote,\
    unquote, unescape, split_unescape, call_safe, base_name, base_name_m, is_content_type, parse_content_type, parse_cookie,\
    parse_multipart, decode_params, load_form, check_login, check_token, check_tokens, ensure_login, get_tokens_m,\
    to_tokens_m, dict_merge, cached, private, ensure, delayed, route, error_handler, exception_handler, before_request,\
    after_request, is_detached, sanitize, verify, verify_equal, verify_not_equal, execute, ctx_locale, ctx_request,\
    FileTuple, BaseThread, JSONEncoder
from .validation import validate, validate_b, validate_e, safe, eq, gt, gte, lt, lte, not_null, not_empty, not_false,\
    is_in, is_upper, is_lower, is_simple, is_email, is_url, is_regex, field_eq, field_gt, field_gte, field_lt,\
    field_lte, string_gt, string_lt, string_eq, equals, not_past, not_duplicate, all_different, no_self

from .amqp import get_connection as get_amqp
from .amqp import properties as properties_amqp
from .mongo import get_connection as get_mongo
from .mongo import get_db as get_mongo_db
from .mongo import drop_db as drop_mongo_db
from .mongo import object_id as object_id_mongo
from .mongo import dumps as dumps_mongo
from .mongo import serialize as serialize_mongo
from .mongo import directions as directions_mongo
from .redisdb import get_connection as get_redis
from .redisdb import dumps as dumps_redis

HTTPError = exceptions.HTTPError
