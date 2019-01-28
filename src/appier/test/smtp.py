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

import unittest

import appier

class SMTPTest(unittest.TestCase):

    def test_plain(self):
        address_mime = appier.email_mime("João Magalhães <joamag@hive.pt>")

        mime = appier.plain("Hello World")
        mime["Subject"] = "Hello World"
        mime["From"] = address_mime
        mime["To"] = ", ".join([address_mime])

        result = mime.as_string()
        self.assertEqual(result, "Content-Type: text/plain; charset=\"utf-8\"\n\
MIME-Version: 1.0\n\
Content-Transfer-Encoding: base64\n\
Subject: Hello World\n\
From: =?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>\n\
To: =?utf-8?q?Jo=C3=A3o_Magalh=C3=A3es?= <joamag@hive.pt>\n\
\n\
SGVsbG8gV29ybGQ=\n")
