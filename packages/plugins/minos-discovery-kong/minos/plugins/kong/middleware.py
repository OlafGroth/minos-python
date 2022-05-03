from collections.abc import (
    Awaitable,
    Callable,
)
from typing import (
    Optional,
)

from minos.networks import (
    REQUEST_USER_CONTEXT_VAR,
    HttpRequest,
    Request,
    Response,
)


async def middleware(request: Request, inner: Callable[[Request], Awaitable[Optional[Response]]]) -> Optional[Response]:
    """Parse headers for http request and set Minos user from Kong headers.

    :param request: The request containing the data.
    :param inner: The inner handling function to be executed.
    :return: The response generated by the inner handling function.
    """
    token = None
    try:
        if isinstance(request, HttpRequest):
            if (user_uuid := request.headers.get("X-Consumer-Custom-ID")) is not None:
                request.headers["user"] = user_uuid
                token = REQUEST_USER_CONTEXT_VAR.set(user_uuid)
        response = await inner(request)
    finally:
        if token:
            REQUEST_USER_CONTEXT_VAR.reset(token)

    return response
