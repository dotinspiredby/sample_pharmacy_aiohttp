from tests.utils import ok_response
from .test_client_register import dbobj2dt_client
from app.store import Store
import pytest

from app.pharmacy.models import ClientModel, Client


class TestClientLoginView:
    async def test_success_1(self, cli, client_1):
        response = await cli.post(
            "/login",
            json={
                "email": client_1.email,
                "phone": client_1.phone,
                "password": "hellotest2"
            }
        )
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            dbobj2dt_client(client_1)
        )

    async def test_success_2(self, cli, client_1):
        response = await cli.post(
            "/login",
            json={
                "email": client_1.email,
                # "phone": client_1.phone,
                "password": "hellotest2"
            }
        )
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            dbobj2dt_client(client_1)
        )

    async def test_success_3(self, cli, client_1):
        response = await cli.post(
            "/login",
            json={
                # "email": client_1.email,
                "phone": client_1.phone,
                "password": "hellotest2"
            }
        )
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            dbobj2dt_client(client_1)
        )

    async def test_no_login(self, cli, client_1):
        response = await cli.post(
            "/login",
            json={
                # "email": client_1.email,
                # "phone": client_1.phone,
                "password": "hellotest2"
            }
        )
        assert response.status == 403
        data = await response.json()
        assert data["error title"] == "forbidden"

    async def test_invalid_credentials(self, cli, client_1):
        response = await cli.post(
            "/login",
            json={
                "email": client_1.email,
                "phone": client_1.phone,
                "password": "blabla"
            }
        )
        assert response.status == 403
        data = await response.json()
        assert data["error title"] == "forbidden"

    async def test_different_method(self, cli, client_1):
        resp = await cli.get(
            "/login",
            json={
                "email": client_1.email,
                "phone": client_1.phone,
                "password": "hellotest2"
            }
        )
        assert resp.status == 405
        data = await resp.json()
        assert data["error title"] == "not_implemented"
