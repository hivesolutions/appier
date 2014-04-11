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

import os
import re
import random
import cStringIO

import appier.base

try:
    import PIL.Image
    import PIL.ImageDraw
    import PIL.ImageFont
except:
    pass

class CaptchaPart(appier.base.Part):
    """
    Modular part class that provides the required infra-structure
    for the generation and management of a captcha image.

    Should be used with proper knowledge of the inner workings of
    the captcha mechanism to avoid any security problems.

    @see: http://en.wikipedia.org/wiki/CAPTCHA
    """

    def routes(self):
        return [
            (("GET",), re.compile("^/captcha$"), self.image),
            (("GET",), re.compile("^/captcha/validate$"), self.validate),
        ]

    def image(self):
        value, data = self.generate_data()
        self.session["captcha"] = value
        self.request.set_content_type("image/jpeg")
        return data

    def validate(self):
        value = self.field("value")
        self.verify(value)

    def generate(
        self,
        value = None,
        width = 300,
        height = 80,
        letter_count = 5,
        rotate = True
    ):
        value = value or self._generate_string(letter_count = letter_count)
        font = self._get_font()
        pattern = self._get_pattern()

        image = PIL.Image.new("RGBA", (width, height), (255, 255, 255, 255))
        self._fill_pattern(image, pattern)
        self._draw_text(image, font, value, rotate = rotate)

        buffer = cStringIO.StringIO()
        image.save(buffer, "jpeg")
        buffer.seek(0)
        return (value, buffer)

    def generate_data(self, *args, **kwargs):
        value, buffer = self.generate(*args, **kwargs)
        data = buffer.read()
        return (value, data)

    def verify(self, value):
        captcha = self.session.get("captcha", None)
        if captcha: del self.session["captcha"]
        if not captcha: raise appier.base.SecurityError(
            message = "No captcha available",
            error_code = 401
        )
        if not value == captcha: raise appier.base.SecurityError(
            message = "Invalid captcha value",
            error_code = 401
        )

    def _draw_text(self, image, font, value, rotate = True):
        image_width, image_height = image.size
        text = PIL.Image.new("RGBA", (image_width, image_height), (255, 255, 255, 0))
        draw = PIL.ImageDraw.Draw(text)

        if rotate: size = self._draw_text_rotate(text, font, value)
        else: size = self._draw_text_simple(draw, font, value)

        text_width, text_height = size
        initial_text_x = (image_width / 2) - (text_width / 2)
        initial_text_y = (image_height / 2) - (text_height / 2)

        image.paste(text, (initial_text_x, initial_text_y), text)

    def _draw_text_simple(self, draw, font, value):
        draw.text((0, 0), value, font = font, fill = (220, 220, 220))
        return font.getsize(value)

    def _draw_text_rotate(self, image, font, value):
        has_offset = hasattr(font, "getoffset")

        current_letter_x = 0
        maximum_letter_height = 0

        for letter in value:
            letter_width, letter_height = font.getsize(letter)
            if has_offset: offset_width, offset_height = font.getoffset(letter)
            else: offset_width, offset_height = (0, 0)
            letter_width += offset_width
            letter_height += offset_height

            letter_image = PIL.Image.new("RGBA", (letter_width, letter_height), (255, 255, 255, 0))
            letter_draw = PIL.ImageDraw.Draw(letter_image)
            letter_draw.text((0, 0), letter, font = font, fill = (220, 220, 220))
            rotation = random.randint(-45, 45)

            letter_image = letter_image.rotate(rotation, PIL.Image.BICUBIC, 1)
            letter_image_width, letter_image_height = letter_image.size

            image.paste(letter_image, (current_letter_x, 0), letter_image)

            current_letter_x += letter_image_width

            if letter_image_height < maximum_letter_height: continue
            maximum_letter_height = letter_image_height

        return (current_letter_x, maximum_letter_height)

    def _fill_pattern(self, image, pattern):
        image_width, image_height = image.size
        pattern_width, pattern_height = pattern.size

        current_pattern_y = 0

        while current_pattern_y < image_height:
            current_pattern_x = 0

            while current_pattern_x < image_width:
                image.paste(pattern, (current_pattern_x, current_pattern_y))
                current_pattern_x += pattern_width

            current_pattern_y += pattern_height

    def _get_font(self, name = None, size = 36):
        fonts_path = os.path.join(self.res_path, "static", "fonts")
        name = name or self._random_path(fonts_path, (".ttf", ".otf"))

        font_path = os.path.join(fonts_path, name)
        font = PIL.ImageFont.truetype(font_path, size)
        return font

    def _get_pattern(self, name = None):
        patterns_path = os.path.join(self.res_path, "static", "patterns")
        name = name or self._random_path(patterns_path, (".jpg", ".jpeg"))

        pattern_path = os.path.join(patterns_path, name)
        pattern = PIL.Image.open(pattern_path)
        return pattern

    def _generate_string(self, letter_count = 5):
        buffer = []

        for _index in range(letter_count):
            letter = random.randint(97, 122)
            buffer.append(chr(letter))

        value = "".join(buffer)
        return value

    def _random_path(self, path, extensions = []):
        paths = os.listdir(path)
        paths = [value for value in paths if os.path.splitext(value)[1] in extensions]
        paths_length = len(paths)
        file_index = random.randint(0, paths_length - 1)
        return paths[file_index]
