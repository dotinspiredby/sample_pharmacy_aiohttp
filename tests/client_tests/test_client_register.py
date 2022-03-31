from tests.utils import ok_response
from app.store import Store
import pytest
from typing import Union

from app.pharmacy.models import ClientModel, Client


def dbobj2dt_client(client: Union[ClientModel, Client]) -> dict:
    return {
        "id": client.id,
        "name": client.name,
        "phone": client.phone,
        "email": client.email,
        # "password": client.password,
        "rating": client.rating
    }


class TestClientRegistration:
    async def test_registration(self, cli, store):
        response = await cli.post(
            "/registration",
            json={
                    "name": "Иванов Иван Иванович",
                    "phone": "+79126693582",
                    "email": "user.test@smth.ru",
                    "password": "hellotest2"
                }
        )
        assert response.status == 200
        commit_data = await ClientModel.query.gino.first()
        data = await response.json()
        assert ok_response(dbobj2dt_client(commit_data)) == data

    async def test_registration_missing_item(self, cli, store):
        response = await cli.post(
            "/registration",
            json={
                "name": "Иванов Иван Иванович",
                "phone": "+79126693582",
                "email": "user.test@smth.ru",
                # "password": "hellotest2"
            }
        )
        assert response.status == 400
        data = await response.json()
        assert data["error title"] == "bad_request"
        assert data["data"]["password"][0] == "Missing data for required field."

    async def test_registration_already_existing_phone(self, cli, store, client_1: Client):
        pseudo_new_client = {"name": "Иванова Анна Ивановна",
                             "phone": client_1.phone,
                             "email": "user.test@smth2.ru",
                             "password": "hellotest2"}
        response = await cli.post(
            "/registration", json=pseudo_new_client
        )
        assert response.status == 409
        data = await response.json()
        assert data["error title"] == "conflict"
        assert data["text"] == "Phone or email already used"

    async def test_registration_already_existing_email(self, cli, store, client_1: Client):
        pseudo_new_client = {"name": "Иванова Анна Ивановна",
                             "phone": "+79156693582",
                             "email": client_1.email,
                             "password": "hellotest2"}
        response = await cli.post(
            "/registration", json=pseudo_new_client
        )
        assert response.status == 409
        data = await response.json()
        assert data["error title"] == "conflict"
        assert data["text"] == "Phone or email already used"

