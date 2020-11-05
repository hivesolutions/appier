#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2020 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2020 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import imp

import email.header

import email.mime.text
import email.mime.multipart
import email.mime.application

from . import config
from . import legacy

def message(
    sender,
    receivers,
    contents,
    host = None,
    port = 25,
    username = None,
    password = None,
    stls = False,
    safe = True
):
    """
    Create a new message.

    Args:
        sender: (todo): write your description
        receivers: (str): write your description
        contents: (todo): write your description
        host: (str): write your description
        port: (int): write your description
        username: (str): write your description
        password: (str): write your description
        stls: (str): write your description
        safe: (bool): write your description
    """
    is_contents = isinstance(contents, legacy.STRINGS)
    if not is_contents: contents = contents.as_string()
    if safe:
        contents = contents.replace("\r\n", "\n")
        contents = contents.replace("\n", "\r\n")
    engine = smtp_engine()
    helo_host = config.conf("SMTP_HELO_HOST", None)
    method = globals()["message_" + engine]
    return method(
        sender,
        receivers,
        contents,
        host = host,
        port = port,
        username = username,
        password = password,
        stls = stls,
        helo_host = helo_host
    )

def message_base(
    sender,
    receivers,
    contents,
    host = None,
    port = 25,
    username = None,
    password = None,
    stls = False,
    helo_host = None,
    *args,
    **kwargs
):
    """
    Create a base.

    Args:
        sender: (todo): write your description
        receivers: (str): write your description
        contents: (str): write your description
        host: (str): write your description
        port: (int): write your description
        username: (str): write your description
        password: (str): write your description
        stls: (todo): write your description
        helo_host: (str): write your description
    """
    pass

def message_netius(
    sender,
    receivers,
    contents,
    host = None,
    port = 25,
    username = None,
    password = None,
    stls = False,
    helo_host = None,
    *args,
    **kwargs
):
    """
    Create a message to a netius.

    Args:
        sender: (todo): write your description
        receivers: (todo): write your description
        contents: (todo): write your description
        host: (str): write your description
        port: (int): write your description
        username: (str): write your description
        password: (str): write your description
        stls: (todo): write your description
        helo_host: (todo): write your description
    """
    import netius.clients
    smtp_client = netius.clients.SMTPClient(auto_close = True, host = helo_host)
    smtp_client.message(
        [sender],
        receivers,
        contents,
        host = host,
        port = port,
        username = username,
        password = password,
        stls = stls
    )

def smtp_engine():
    """
    Returns the smtp engine.

    Args:
    """
    try: imp.find_module("netius")
    except ImportError: return "base"
    return "netius"

def multipart():
    """
    Multipart mime

    Args:
    """
    return email.mime.multipart.MIMEMultipart("alternative")

def plain(contents, encoding = "utf-8"):
    """
    Convert plain text to plaintext.

    Args:
        contents: (str): write your description
        encoding: (str): write your description
    """
    return email.mime.text.MIMEText(contents, "plain", encoding)

def html(contents, encoding = "utf-8"):
    """
    Convert an html.

    Args:
        contents: (str): write your description
        encoding: (str): write your description
    """
    return email.mime.text.MIMEText(contents, "html", encoding)

def application(contents, name = "unnamed"):
    """
    Gets an application.

    Args:
        contents: (str): write your description
        name: (str): write your description
    """
    return email.mime.application.MIMEApplication(contents, Name = name)

def header(value, encoding = "utf-8", encode = True):
    """
    Encode a header.

    Args:
        value: (todo): write your description
        encoding: (str): write your description
        encode: (str): write your description
    """
    header = email.header.Header(value, encoding)
    if encode: header = header.encode()
    return header
