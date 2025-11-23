from typing import Any

URL: str
TIMEOUT: int
connection: Any | None

class AMQP:
    url: str | None
    _connection: Any | None
    def __init__(self, url: str | None = ...): ...
    def get_connection(self, url: str | None = ..., timeout: int = ...) -> Any: ...

def get_connection(url: str = ..., timeout: int = ...) -> Any: ...
def properties(*args, **kwargs) -> Any: ...
