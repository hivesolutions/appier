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

import util

class Part(object):
    """
    Abstract top level class for the "part" module infra-structure
    should implement the base method for the proper working of a
    part and raise exception for mandatory methods.
    """

    def __init__(self, owner = None):
        self.owner = owner

    def __getattr__(self, name):
        if self.owner and hasattr(self.owner, name):
            return getattr(self.owner, name)
        raise AttributeError("'%s' not found" % name)

    def name(self):
        cls = self.__class__
        cls_name = cls.__name__
        name = util.camel_to_underscore(cls_name)
        if name.endswith("_part"): name = name[:-5]
        return name

    def routes(self):
        return []

class AdminPart(Part):
    pass

class CaptchaPart(Part):
    """
    Modular part class that provides the required infra-structure
    for the generation and management of a captcha image.

    Should be used with proper knowledge of the inner workings of
    the captcha mechanism to avoid any security problems.

    @see: http://en.wikipedia.org/wiki/CAPTCHA
    """

    def routes(self):
        return [
            (("GET",), re.compile("^/captcha/image$"), self.image)
        ]

    def image(self):
        return ""

    def generate(self, value = None, width = 300, height = 50, letter_count = 5):
        # retrieves the plugin path
        #plugin_path = plugin_manager.get_plugin_path_by_id(self.plugin.id)
        # tenho de sacar aki um recurso self.resource_path(

        import PIL

        # creates the resources path from the "base" plugin path
        #resources_path = plugin_path + "/" + RESOURCES_PATH

        value = value or self._generate_string(letter_count = letter_count)
        font = self._get_font()
        pattern = self._get_pattern()

        image = PIL.Image.new("RGBA", (width, height), (255, 255, 255, 255))
        self._fill_pattern(image, pattern)
        self._draw_text(image, font, value)

        buffer = cStringIO.StringIO()
        image.save(buffer, "jpeg")
        buffer.seek(0)
        return (value, buffer)

    def generate_data(self, *args, **kwargs):
        value, buffer = self.generate(*args, **kwargs)
        data = buffer.read()
        return (value, data)

    def _draw_text(self, image, text_font, string_value, rotate = True):
        import PIL.Image
        import PIL.ImageDraw

        # retrieves the image width and height
        image_width, image_height = image.size

        # creates a text image
        text_image = PIL.Image.new("RGBA", (image_width, image_height), (255, 255, 255, 0))

        # creates the text draw (temporary) from the text image
        text_draw = PIL.ImageDraw.Draw(text_image)

        # in case the rotate flag is set
        if rotate:
            # draws the text into the text image in rotate mode
            text_size = self._draw_text_rotate(text_image, text_font, string_value)
        else:
            # draws the text into the text image in simple mode mode
            text_size = self._draw_text_simple(text_draw, text_font, string_value)

        # unpacks the text size retrieving the text width and height
        text_width, text_height = text_size

        # calculates the initial text x position
        initial_text_x = (image_width / 2) - (text_width / 2)

        # calculates the initial text y position
        initial_text_y = (image_height / 2) - (text_height / 2)

        # paste text image with the mask into the image
        image.paste(text_image, (initial_text_x, initial_text_y), text_image)

    def _draw_text_simple(self, text_draw, text_font, string_value):
        # draw the text to the text draw
        text_draw.text((0, 0), string_value, font = text_font, fill = (220, 220, 220))

        # retrieves the text size from the text font
        text_size = text_font.getsize(string_value)

        # returns the text size
        return text_size

    def _draw_text_rotate(self, text_image, text_font, string_value):
        import PIL.Image
        import PIL.ImageDraw

        # start the current letter x position
        current_letter_x = 0

        # start the maximum letter height
        maximum_letter_height = 0

        # iterates over all the letters in the string value
        for letter_value in string_value:
            # retrieves the letter width and height from the text font
            letter_width, letter_height = text_font.getsize(letter_value)

            # creates a letter image
            letter_image = PIL.Image.new("RGBA", (letter_width, letter_height), (255, 255, 255, 0))

            # creates the letter draw (temporary) from the letter image
            letter_draw = PIL.ImageDraw.Draw(letter_image)

            # draw the text to the text draw
            letter_draw.text((0, 0), letter_value, font = text_font, fill = (220, 220, 220))

            # generates a random rotation angle
            rotation = random.randint(-45, 45)

            # rotates the text image
            letter_image = letter_image.rotate(rotation, PIL.Image.BICUBIC, 1)

            # retrieves the letter image width and height
            letter_image_width, letter_image_height = letter_image.size

            # paste letter image with the mask into the image
            text_image.paste(letter_image, (current_letter_x, 0), letter_image)

            # increments the current letter z position
            # with the letter width
            current_letter_x += letter_image_width

            # in case the current letter image height is the largest
            if letter_image_height > maximum_letter_height:
                # sets the maximum letter height as the
                # current letter image height
                maximum_letter_height = letter_image_height

        # creates the string value size tuple
        size = (current_letter_x, maximum_letter_height)

        # returns the string value size tuple
        return size

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
        import PIL.ImageFont #@todo depois tenho de fazer um getter

        fonts_path = os.path.join(self.res_path, "static", "fonts")
        name = name or self._random_path(fonts_path, (".ttf", ".otf"))

        font_path = os.path.join(fonts_path, name)
        font = PIL.ImageFont.truetype(font_path, size)
        return font

    def _get_pattern(self, name = None):
        import PIL.Image

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

part = CaptchaPart()
print part.name()
