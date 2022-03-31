import json
import typing
from .utils import error_response as error_json_response

from aiohttp.web_exceptions import HTTPUnprocessableEntity, HTTPBadRequest, HTTPNotImplemented, \
    HTTPUnauthorized, HTTPForbidden, HTTPNotFound, HTTPConflict, HTTPInternalServerError

from aiohttp.web_middlewares import middleware
# this is for decorator

from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session

from ..pharmacy.models import Client

if typing.TYPE_CHECKING:
    from .app_ import Application, Request

from app.admin.models import Admin


@middleware
async def auth_middleware(request: "Request", handler: callable):
    session = await get_session(request)
    if session:
        try:
            request.admin = Admin.from_session(session)
        except KeyError:
            request.client = Client.from_session(session)

    return await handler(request)


HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text)
        )
    except HTTPBadRequest as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
        )
    except HTTPNotImplemented as e:
        return error_json_response(
            http_status=405,
            status=HTTP_ERROR_CODES[405],
            message=e.reason
        )
    except HTTPUnauthorized as e:
        return error_json_response(
            http_status=401,
            status=HTTP_ERROR_CODES[401],
            message=e.reason
        )
    except HTTPForbidden as e:
        return error_json_response(
            http_status=403,
            status=HTTP_ERROR_CODES[403],
            message=e.reason
        )
    except HTTPNotFound as e:
        try:
            return error_json_response(
                http_status=404,
                status=HTTP_ERROR_CODES[404],
                message=e.reason,
                data=request.client.cart
            )
        except AttributeError:
            return error_json_response(
                http_status=404,
                status=HTTP_ERROR_CODES[404],
                message=e.reason
            )
    except HTTPConflict as e:
        return error_json_response(
            http_status=409,
            status=HTTP_ERROR_CODES[409],
            message=e.reason,

        )
    except HTTPInternalServerError as e:
        return error_json_response(
            http_status=500,
            status=HTTP_ERROR_CODES[500],
            message=e.reason
        )


def setup_middlewares(app: "Application"):
    app.middlewares.append(auth_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
