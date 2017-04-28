#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2017 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import hmac
import uuid
import time
import base64
import hashlib
import logging

from . import base
from . import http
from . import legacy
from . import observer
from . import exceptions

class Api(observer.Observable):
    """
    Abstract and top level api class that should be used
    as the foundation for the creation of api clients.

    This class should offer a set of services so that a
    concrete api implementation should not be concerned
    with issues like: logging, building and destruction.
    """

    SINGLETON = None

    def __init__(self, owner = None, *args, **kwargs):
        observer.Observable.__init__(self, *args, **kwargs)
        self.owner = owner or base.APP
        if not hasattr(self, "auth_callback"): self.auth_callback = None

    @classmethod
    def singleton(cls, *args, **kwargs):
        callback = kwargs.pop("scallback", None)
        if cls.SINGLETON: return cls.SINGLETON
        cls.SINGLETON = cls(*args, **kwargs)
        if callback: callback(cls.SINGLETON)
        return cls.SINGLETON

    def get(
        self,
        url,
        headers = None,
        params = None,
        handle = None,
        silent = None,
        redirect = None,
        timeout = None,
        callback = True,
        **kwargs
    ):
        headers = headers or dict()
        params = params or kwargs
        auth_callback = self.auth_callback if callback else None
        self.build(
            "GET",
            url,
            headers = headers,
            params = params,
            kwargs = kwargs
        )
        return self.request(
            http.get,
            url,
            params = params,
            headers = headers,
            handle = handle,
            silent = silent,
            redirect = redirect,
            timeout = timeout,
            auth_callback = auth_callback
        )

    def post(
        self,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        handle = None,
        silent = None,
        redirect = None,
        timeout = None,
        callback = True,
        **kwargs
    ):
        headers = headers or dict()
        params = params or kwargs
        auth_callback = self.auth_callback if callback else None
        self.build(
            "POST",
            url,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers,
            params = params,
            mime = mime,
            kwargs = kwargs
        )
        return self.request(
            http.post,
            url,
            params = params,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers,
            mime = mime,
            handle = handle,
            silent = silent,
            redirect = redirect,
            timeout = timeout,
            auth_callback = auth_callback
        )

    def put(
        self,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        handle = None,
        silent = None,
        redirect = None,
        timeout = None,
        callback = True,
        **kwargs
    ):
        headers = headers or dict()
        params = params or kwargs
        auth_callback = self.auth_callback if callback else None
        self.build(
            "PUT",
            url,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers,
            params = params,
            mime = mime,
            kwargs = kwargs
        )
        return self.request(
            http.put,
            url,
            params = params,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers,
            mime = mime,
            handle = handle,
            silent = silent,
            redirect = redirect,
            timeout = timeout,
            auth_callback = auth_callback
        )

    def delete(
        self,
        url,
        headers = None,
        params = None,
        handle = None,
        silent = None,
        redirect = None,
        timeout = None,
        callback = True,
        **kwargs
    ):
        headers = headers or dict()
        params = params or kwargs
        auth_callback = self.auth_callback if callback else None
        self.build(
            "DELETE",
            url,
            headers = headers,
            params = params,
            kwargs = kwargs
        )
        return self.request(
            http.delete,
            url,
            params = params,
            headers = headers,
            handle = handle,
            silent = silent,
            redirect = redirect,
            timeout = timeout,
            auth_callback = auth_callback
        )

    def patch(
        self,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        handle = None,
        silent = None,
        redirect = None,
        timeout = None,
        callback = True,
        **kwargs
    ):
        headers = headers or dict()
        params = params or kwargs
        auth_callback = self.auth_callback if callback else None
        self.build(
            "PATCH",
            url,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers,
            params = params,
            mime = mime,
            kwargs = kwargs
        )
        return self.request(
            http.patch,
            url,
            params = params,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers,
            mime = mime,
            handle = handle,
            silent = silent,
            redirect = redirect,
            timeout = timeout,
            auth_callback = auth_callback
        )

    def request(self, method, *args, **kwargs):
        try: result = method(*args, **kwargs)
        except exceptions.HTTPError as exception:
            self.handle_error(exception)
        else: return result

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        pass

    def handle_error(self, error):
        raise

    @property
    def logger(self):
        if self.owner: return self.owner.logger
        else: return logging.getLogger()

class OAuthApi(Api):
    """
    Abstract class for the implementation of oauth based
    infra-structure, should expose a series of utilities
    for the authentication using oauth.

    A direct fallback mode should be support so that dual
    api clients are allowed and may be able to interact.
    """

    DIRECT_MODE = 1
    """ The direct mode where a complete access is allowed
    to the client by providing the "normal" credentials to
    it and ensuring a complete authentication """

    OAUTH_MODE = 2
    """ The oauth client mode where the set of permissions
    (scope) is authorized on behalf on an already authenticated
    user using a web agent (recommended mode) """

    UNSET_MODE = 3
    """ The unset client mode for situations where the client
    exists but not enough information is provided to it so that
    it knows how to interact with the server side (detached client) """

    def __init__(self, *args, **kwargs):
        Api.__init__(self, *args, **kwargs)
        self.mode = OAuthApi.OAUTH_MODE

    def handle_error(self, error):
        raise exceptions.OAuthAccessError(
            message = "Problems using access token found must re-authorize",
            original = error
        )

    def is_direct(self):
        return self.mode == OAuthApi.DIRECT_MODE

    def is_oauth(self):
        return self.mode == OAuthApi.OAUTH_MODE

    def _get_mode(self):
        return OAuthApi.OAUTH_MODE

class OAuth1Api(OAuthApi):

    def __init__(self, *args, **kwargs):
        OAuthApi.__init__(self, *args, **kwargs)
        self.oauth_token = None
        self.oauth_token_secret = None

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        if not self.is_oauth(): return
        auth = kwargs.pop("auth", True)
        if auth: self.auth_header(method, url, headers, kwargs)

    def auth_header(self, method, url, headers, kwargs, sign_method = "HMAC-SHA1"):
        if not sign_method == "HMAC-SHA1": raise exceptions.NotImplementedError()

        if not self.client_key: raise exceptions.SecurityError(
            message = "No client key defined, mandatory"
        )
        if not self.client_secret: raise exceptions.SecurityError(
            message = "No client secret defined, mandatory"
        )

        oauth_callback = kwargs.pop("oauth_callback", None)

        params = []

        encoded = http._quote(kwargs, safe = "~")
        items = encoded.items()
        params.extend(items)

        unique = str(uuid.uuid4())
        oauth_nonce = unique.replace("-", "")
        oauth_timestamp = str(int(time.time()))

        authorization = dict(
            oauth_nonce = oauth_nonce,
            oauth_signature_method = sign_method,
            oauth_timestamp = oauth_timestamp,
            oauth_consumer_key = self.client_key,
            oauth_version = "1.0"
        )
        if self.oauth_token: authorization["oauth_token"] = self.oauth_token
        if oauth_callback: authorization["oauth_callback"] = oauth_callback

        encoded = http._quote(authorization, safe = "~")
        items = encoded.items()
        params.extend(items)
        params.sort()

        signature_base = "&".join(["%s=%s" % (key, value) for key, value in params])
        signature_extra = "&".join([
            legacy.quote(method, safe = "~"),
            legacy.quote(url, safe = "~"),
            legacy.quote(signature_base, safe = "~")
        ])

        if self.oauth_token_secret: key = "%s&%s" % (self.client_secret, self.oauth_token_secret)
        else: key = "%s&" % self.client_secret

        if legacy.is_unicode(key): key = key.encode("utf-8")
        if legacy.is_unicode(signature_extra): signature_extra = signature_extra.encode("utf-8")

        oauth_signature = hmac.new(key, signature_extra, hashlib.sha1).digest()
        oauth_signature = base64.b64encode(oauth_signature)
        oauth_signature = legacy.str(oauth_signature)

        authorization["oauth_signature"] = oauth_signature
        authorization = http._quote(authorization, safe = "~")
        authorization = authorization.items()
        authorization = ["%s=\"%s\"" % (key, value) for key, value in authorization]

        authorization_s = ", ".join(authorization)
        authorization_s = "OAuth %s" % authorization_s

        headers["Authorization"] = authorization_s

class OAuth2Api(OAuthApi):

    def __init__(self, *args, **kwargs):
        OAuthApi.__init__(self, *args, **kwargs)
        self.access_token = None

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        if not self.is_oauth(): return
        token = kwargs.pop("token", True)
        if token and "param" in self.oauth_types:
            kwargs["access_token"] = self.get_access_token()
        if token and "header" in self.oauth_types:
            headers["Authorization"] = "Bearer %s" % self.get_access_token()

    def get_access_token(self):
        if self.access_token: return self.access_token
        raise exceptions.OAuthAccessError(
            message = "No access token found must re-authorize"
        )

    @property
    def oauth_types(self):
        return ("param", "header")
