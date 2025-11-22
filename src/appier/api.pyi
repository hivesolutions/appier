from typing import Any, Callable, Self

from .base import App
from .observer import Observable

class API(Observable):
    SINGLETON: Self | None
    owner: App
    auth_callback: Callable | None
    def __init__(self, owner: App = ..., *args, **kwargs): ...
    @classmethod
    def singleton(cls, *args, **kwargs) -> Self: ...
    def get(
        self,
        url: str,
        headers: dict[str, Any] | None = ...,
        params: dict[str, Any] | None = ...,
        handle: bool | None = ...,
        silent: bool | None = ...,
        redirect: bool | None = ...,
        timeout: int | float | None = ...,
        callback: bool = ...,
        extra: dict[str, Any] | None = ...,
        **kwargs
    ) -> Any: ...
    def post(
        self,
        url: str,
        data: Any = ...,
        data_j: Any = ...,
        data_m: Any = ...,
        headers: dict[str, Any] | None = ...,
        params: dict[str, Any] | None = ...,
        mime: str | None = ...,
        handle: bool | None = ...,
        silent: bool | None = ...,
        redirect: bool | None = ...,
        timeout: int | float | None = ...,
        callback: bool = ...,
        extra: dict[str, Any] | None = ...,
        **kwargs
    ) -> Any: ...
    def put(
        self,
        url: str,
        data: Any = ...,
        data_j: Any = ...,
        data_m: Any = ...,
        headers: dict[str, Any] | None = ...,
        params: dict[str, Any] | None = ...,
        mime: str | None = ...,
        handle: bool | None = ...,
        silent: bool | None = ...,
        redirect: bool | None = ...,
        timeout: int | float | None = ...,
        callback: bool = ...,
        extra: dict[str, Any] | None = ...,
        **kwargs
    ) -> Any: ...
    def delete(
        self,
        url: str,
        headers: dict[str, Any] | None = ...,
        params: dict[str, Any] | None = ...,
        handle: bool | None = ...,
        silent: bool | None = ...,
        redirect: bool | None = ...,
        timeout: int | float | None = ...,
        callback: bool = ...,
        extra: dict[str, Any] | None = ...,
        **kwargs
    ) -> Any: ...
    def patch(
        self,
        url: str,
        data: Any = ...,
        data_j: Any = ...,
        data_m: Any = ...,
        headers: dict[str, Any] | None = ...,
        params: dict[str, Any] | None = ...,
        mime: str | None = ...,
        handle: bool | None = ...,
        silent: bool | None = ...,
        redirect: bool | None = ...,
        timeout: int | float | None = ...,
        callback: bool = ...,
        extra: dict[str, Any] | None = ...,
        **kwargs
    ) -> Any: ...
    def request(self, method: Callable, *args, **kwargs) -> Any: ...
    def build( # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        method: str,
        url: str,
        data: Any = ...,
        data_j: Any = ...,
        data_m: Any = ...,
        headers: dict[str, Any] | None = ...,
        params: dict[str, Any] | None = ...,
        mime: str | None = ...,
        kwargs: dict[str, Any] | None = ...,
    ) -> None: ...
    def handle_error(self, error: Exception) -> None: ...
    @property
    def logger(self) -> Any: ...

class OAuthAPI(API):
    DIRECT_MODE: int
    OAUTH_MODE: int
    UNSET_MODE: int
    mode: int
    def __init__(self, *args, **kwargs): ...
    def handle_error(self, error: Exception) -> None: ...
    def is_direct(self) -> bool: ...
    def is_oauth(self) -> bool: ...
    def _get_mode(self) -> int: ...

class OAuth1API(OAuthAPI):
    oauth_token: str | None
    oauth_token_secret: str | None
    client_key: str | None
    client_secret: str | None
    def __init__(self, *args, **kwargs): ...
    def build(
        self,
        method: str,
        url: str,
        data: Any = ...,
        data_j: Any = ...,
        data_m: Any = ...,
        headers: dict[str, Any] | None = ...,
        params: dict[str, Any] | None = ...,
        mime: str | None = ...,
        kwargs: dict[str, Any] | None = ...,
    ) -> None: ...
    def auth_header(
        self,
        method: str,
        url: str,
        headers: dict[str, Any],
        kwargs: dict[str, Any],
        sign_method: str = ...,
    ) -> None: ...
    @property
    def auth_default(self) -> bool: ...

class OAuth2API(OAuthAPI):
    access_token: str | None
    def __init__(self, *args, **kwargs): ...
    def build(
        self,
        method: str,
        url: str,
        data: Any = ...,
        data_j: Any = ...,
        data_m: Any = ...,
        headers: dict[str, Any] | None = ...,
        params: dict[str, Any] | None = ...,
        mime: str | None = ...,
        kwargs: dict[str, Any] | None = ...,
    ) -> None: ...
    def get_access_token(self) -> str: ...
    @property
    def oauth_types(self) -> tuple[str, ...]: ...
    @property
    def oauth_param(self) -> str: ...
    @property
    def token_default(self) -> bool: ...
