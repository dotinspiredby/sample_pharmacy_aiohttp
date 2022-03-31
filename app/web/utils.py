from aiohttp.web import json_response as aio_json_resp
from aiohttp.web_response import Response

from typing import Any, Optional, Union


def json_response(data: Any = None, status: str = "ok") -> Response:
    if not data:
        data = {}
    return aio_json_resp(
        data={
            "status": status,
            "data": data
        }
    )


def error_response(
        http_status: int,
        status: str = "Exception",
        message: Optional[str] = "",
        data: Optional[Union[dict, list]] = None,
):
    if not data:
        data = {}
    return aio_json_resp(
        status=http_status,
        data={
            "error title": status,
            "text": message,
            "data": data
        },
    )
