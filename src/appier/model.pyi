from typing import Any, Callable, Self, Sequence
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
    @property
    def identity(self) -> Any: ...
    ...

class Field:
    def __init__(self, *args, **kwargs): ...

def link(
    name: str | None = ...,
    description: str | None = ...,
    parameters: tuple = ...,
    context: bool = ...,
    devel: bool = ...,
) -> Callable[[Callable], Callable]: ...
def operation(
    name: str | None = ...,
    description: str | None = ...,
    parameters: tuple = ...,
    kwargs: dict[str, Any] | None = ...,
    factory: bool = ...,
    level: int = ...,
    devel: bool = ...,
) -> Callable[[Callable], Callable]: ...

field = Field
