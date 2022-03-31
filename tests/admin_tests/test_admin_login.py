from tests.utils import ok_response
from app.store import Store
import pytest

from hashlib import sha256


class TestAdminLoginView:
    async def test_create_on_startup(self, store: Store, config):

        admin = await store.admins.get_by_login(config.admin.login)
        assert admin is not None
        assert admin.login == config.admin.login
        assert admin.password == str(sha256(config.admin.password.encode()).hexdigest())
        assert admin.id == 1

    async def test_success(self, cli, config):
        response = await cli.post(
            "/admin_login",
            json={
                "login": config.admin.login,
                "password": config.admin.password
            }
        )
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {
                "id": 1,
                "login": config.admin.login
            }
        )

    async def test_no_login(self, cli, config):
        response = await cli.post(
            "/admin_login",
            json={
                "password": config.admin.password,
            }
        )
        assert response.status == 400
        data = await response.json()
        assert data["error title"] == "bad_request"
        assert data["data"]["login"][0] == "Missing data for required field."

    async def test_invalid_data(self, cli):
        response = await cli.post(
            "/admin_login",
            json={
                "login": "invalid",
                "password": "invalid"
            },
        )
        assert response.status == 403
        data = await response.json()
        assert data["error title"] == "forbidden"

    async def test_different_method(self, cli):
        resp = await cli.get(
            "/admin_login",
            json={
                "login": "qwerty",
                "password": "qwerty",
            },
        )
        assert resp.status == 405
        data = await resp.json()
        assert data["error title"] == "not_implemented"
