from os import PathLike
from logging import Handler
from typing import Sequence, Type

from .bus import Bus
from .part import Part
from .cache import Cache
from .data import DataAdapter
from .session import Session
from .preferences import Preferences
from .asynchronous import AsyncManager
from .scheduler import SchedulerTask, JobFunction, Cron

class App:
    def __init__(
        self,
        name: str | None = ...,
        locales: Sequence[str] = ...,
        parts: Sequence[Type[Part]] = ...,
        level: str | int | None = ...,
        handlers: Sequence[Handler] | None = ...,
        service: bool = ...,
        safe: bool = ...,
        lazy: bool = ...,
        payload: bool = ...,
        cache_s: int = ...,
        cache_c: Type[Cache] = ...,
        preferences_c: Type[Preferences] = ...,
        bus_c: Type[Bus] = ...,
        session_c: Type[Session] = ...,
        adapter_c: Type[DataAdapter] = ...,
        manager_c: Type[AsyncManager] = ...,
    ): ...
    def start(self, refresh: bool = ...): ...
    def stop(self, refresh: bool = ...): ...
    def serve(
        self,
        server: str = ...,
        host: str = ...,
        port: int = ...,
        ipv6: bool = ...,
        ssl: bool = ...,
        key_file: PathLike[str] | None = ...,
        cer_file: PathLike[str] | None = ...,
        backlog: int = ...,
        threaded: bool = ...,
        conf: bool = ...,
        **kwargs
    ): ...
    def template(
        self,
        template: Template | PathLike[str] | str,
        content_type: str = ...,
        templates_path: PathLike[str] | str | None = ...,
        cache: bool = ...,
        detached: bool = ...,
        locale: str | None = ...,
        asynchronous: bool = ...,
        **kwargs
    ) -> str: ...
    def cron(
        self,
        job: JobFunction,
        cron: Cron,
        id: str | None = ...,
        description: str | None = ...,
    ) -> SchedulerTask: ...
    def is_loaded(self) -> bool: ...
    def is_parent(self) -> bool: ...
    def is_child(self) -> bool: ...
    def is_main(self) -> bool: ...
    def is_devel(self) -> bool: ...
    def is_running(self) -> bool: ...
    def is_started(self) -> bool: ...
    def is_stopped(self) -> bool: ...
    def url_for(
        self,
        type: str,
        filename: str | None = ...,
        prefix: str | None = ...,
        query: str | None = ...,
        params: str | None = ...,
        absolute: bool = ...,
        touch: bool = ...,
        session: bool = ...,
        compress: str | None = ...,
        base_url: str | None = ...,
        *args,
        **kwargs
    ) -> str | None: ...
    ...

class APIApp(App): ...
class WebApp(App): ...
class Template: ...

def get_app() -> App: ...
def get_name() -> str | None: ...
def get_base_path() -> PathLike[str] | None: ...
