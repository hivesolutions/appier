from typing import Any, Callable, Coroutine

class ASGIApp:
    _asgi: ASGIApp | None
    server_version: str | None
    _server: Any | None
    @classmethod
    async def asgi_entry(
        cls,
        scope: dict[str, Any],
        receive: Callable[[], Coroutine[Any, Any, dict[str, Any]]],
        send: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None: ...
    def serve_uvicorn(self, host: str, port: int, **kwargs) -> None: ...
    def serve_hypercorn(
        self,
        host: str,
        port: int,
        ssl: bool = ...,
        key_file: str | None = ...,
        cer_file: str | None = ...,
        **kwargs
    ) -> None: ...
    def serve_daphne(self, host: str, port: int, **kwargs) -> None: ...
    async def send(self, data: Any, content_type: str | None = ...) -> Any: ...
    async def app_asgi(self, *args, **kwargs) -> Any: ...
    async def application_asgi(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Coroutine[Any, Any, dict[str, Any]]],
        send: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None: ...
    async def asgi_lifespan(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Coroutine[Any, Any, dict[str, Any]]],
        send: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None: ...
    async def asgi_http(
        self,
        scope: dict[str, Any],
        receive: Callable[[], Coroutine[Any, Any, dict[str, Any]]],
        send: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None: ...
    async def _build_start_response(
        self,
        ctx: dict[str, Any],
        send: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> Callable[[str, list[tuple[str, str]]], None]: ...
    async def _build_sender(
        self,
        ctx: dict[str, Any],
        send: Callable[[dict[str, Any]], Coroutine[Any, Any, None]],
        start_response: Callable[[str, list[tuple[str, str]]], None],
    ) -> Callable[[Any], Coroutine[Any, Any, None]]: ...
    async def _build_body(
        self,
        receive: Callable[[], Coroutine[Any, Any, dict[str, Any]]],
        max_size: int = ...,
    ) -> Any: ...
    async def _build_environ(
        self,
        scope: dict[str, Any],
        body: Any,
        sender: Callable[[Any], Coroutine[Any, Any, None]],
    ) -> dict[str, Any]: ...
    def _ensure_start(
        self,
        ctx: dict[str, Any],
        start_response: Callable[[str, list[tuple[str, str]]], None],
    ) -> None: ...

def build_asgi(app_cls: type[ASGIApp]) -> Callable: ...
def build_asgi_i(app: ASGIApp) -> Callable: ...
