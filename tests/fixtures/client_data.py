from typing import List

import pytest

from app.pharmacy.models import Client, ClientModel


@pytest.fixture
async def client_1(store) -> Client:
    client = await store.pharmacy.create_new_account(
        name="Иванов Иван Иванович",
        phone="+79126693582",
        email="user.test@smth.ru",
        password="hellotest2"
    )
    yield client


@pytest.fixture
async def client_2(store) -> Client:
    client = await store.pharmacy.create_new_account(
        name="Иванова Анна Ивановна",
        phone="+79156693582",
        email="user.test@smth2.ru",
        password="hellotest2"
    )
    yield client


@pytest.fixture
def client_2_rating():
    return 8


@pytest.fixture
async def client_2_with_rating(store, client_2, client_2_rating):
    client_from_db = await ClientModel.query.where(ClientModel.id == client_2.id).gino.first()
    await client_from_db.update(rating=client_2_rating).apply()
    yield client_from_db

