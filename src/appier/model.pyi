#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2024 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2024 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

from typing import Callable, Self, Sequence
from .base import App

class Model:
    owner: App

    @classmethod
    def singleton(
        cls,
        model: Self | None = ...,
        form: bool = ...,
        safe: bool = ...,
        build: bool = ...,
        *args,
        **kwargs
    ) -> Self | None: ...
    @classmethod
    def get(cls, *args, **kwargs) -> Self | None: ...
    @classmethod
    def find(cls, *args, **kwargs) -> Sequence[Self]: ...
    @classmethod
    def validate(cls) -> list[Callable]: ...
    @classmethod
    def _name(cls) -> str: ...
    def save(
        self,
        validate: bool = ...,
        verify: bool = ...,
        is_new: bool | None = ...,
        increment_a: bool | None = ...,
        immutables_a: bool | None = ...,
        pre_validate: bool = ...,
        pre_save: bool = ...,
        pre_create: bool = ...,
        pre_update: bool = ...,
        post_validate: bool = ...,
        post_save: bool = ...,
        post_create: bool = ...,
        post_update: bool = ...,
        before_callbacks: Sequence[Callable[[Self], None]] = ...,
        after_callbacks: Sequence[Callable[[Self], None]] = ...,
    ) -> Self: ...
    ...

class Field:
    def __init__(self, *args, **kwargs): ...

field = Field
