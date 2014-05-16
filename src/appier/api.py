#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2014 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import logging

from appier import base
from appier import http
from appier import observer
from appier import exceptions

class Api(observer.Observable):
    """
    Abstract and top level api class that should be used
    as the foundation for the creation of api clients.

    This class should offer a set of services so that a
    concrete api implementation should not be concerned
    with issues like: logging, building and destruction.
    """

    def __init__(self, owner = None, *args, **kwargs):
        observer.Observable.__init__(self, *args, **kwargs)
        self.owner = owner or base.APP

    def get(self, url, headers = None, **kwargs):
        self.build(headers, kwargs)
        return self.request(
            http.get,
            url,
            params = kwargs,
            headers = headers
        )

    def post(
        self,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        **kwargs
    ):
        self.build(headers, kwargs)
        return self.request(
            http.post,
            url,
            params = kwargs,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers
        )

    def put(
        self,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        **kwargs
    ):
        self.build(headers, kwargs)
        return self.request(
            http.put,
            url,
            params = kwargs,
            data = data,
            data_j = data_j,
            data_m = data_m,
            headers = headers
        )

    def delete(self, url, headers = None, **kwargs):
        self.build(headers, kwargs)
        return self.request(
            http.delete,
            url,
            params = kwargs,
            headers = headers
        )

    def request(self, method, *args, **kwargs):
        return method(*args, **kwargs)

    def build(self, headers, kwargs):
        pass

    @property
    def logger(self):
        if self.owner: return self.owner.logger
        else: return logging.getLogger()

class OAuth2Api(Api):

    def request(self, method, *args, **kwargs):
        try: result = method(*args, **kwargs)
        except exceptions.HTTPError:
            raise exceptions.OAuthAccessError(
                message = "Problems using access token found must re-authorize"
            )
            raise
        return result

    def build(self, headers, kwargs):
        token = kwargs.get("token", True)
        if token: kwargs["access_token"] = self.get_access_token()
        if "token" in kwargs: del kwargs["token"]

    def get_access_token(self):
        if self.access_token: return self.access_token
        raise exceptions.OAuthAccessError(
            message = "No access token found must re-authorize"
        )
