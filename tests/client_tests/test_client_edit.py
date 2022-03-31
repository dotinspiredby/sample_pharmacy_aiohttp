from tests.utils import ok_response
from .test_client_register import dbobj2dt_client
from app.store import Store
import pytest

from app.pharmacy.models import ClientModel, Client


class TestClientEditInfo:
    async def test_unauthorized(self, cli, store: Store):
        response = await cli.patch(
            "/edit_client",
            json={
                "name": "First Name Last Name",
                "phone": "+74839293673",
                "email": "user.test@smth3.ru",
                "password": "hello"
            }
        )
        assert response.status == 401
        data = await response.json()
        assert data["error title"] == "unauthorized"

    async def test_success(self, authed_cli_client2, store: Store):
        response = await authed_cli_client2.patch(
            "/edit_client",
            json={
                "name": "First Name Last Name",
                "phone": "+74839293673",
                "email": "user.test@smth3.ru",
                "password": "hello"
            }
        )
        assert response.status == 200
        commit_data = await ClientModel.query.where(ClientModel.name == "First Name Last Name").gino.first()
        data = await response.json()
        assert data == ok_response(dbobj2dt_client(commit_data))

    async def test_edit_already_existing_phone(self, authed_cli_client2, client_1, store: Store):
        response = await authed_cli_client2.patch(
            "/edit_client",
            json={
                "name": "First Name Last Name",
                "phone": client_1.phone,
                "email": "user.test@smth3.ru",
                "password": "hello"
            }
        )
        assert response.status == 409
        data = await response.json()
        assert data["error title"] == "conflict"
        assert data["text"] == "Phone or email already used"

    async def test_edit_already_existing_email(self, authed_cli_client2, client_1, store: Store):
        response = await authed_cli_client2.patch(
            "/edit_client",
            json={
                "name": "First Name Last Name",
                "phone": "+74839293673",
                "email": client_1.email,
                "password": "hello"
            }
        )
        assert response.status == 409
        data = await response.json()
        assert data["error title"] == "conflict"
        assert data["text"] == "Phone or email already used"
