from typing import List

import pytest
from aiohttp.test_utils import TestClient

from app.pharmacy.models import ClientOrder, ClientModel


@pytest.fixture
def medicine_ids():
    return [7, 6, 4]


@pytest.fixture
def amounts():
    return [2, 1, 2]


@pytest.fixture
async def client_with_cart(store, client_2, authed_cli_client2,
                           medicine_1, medicine_2, medicine_3,
                           medicine_4, medicine_5, medicine_6,
                           medicine_7, medicine_8, medicine_9) -> TestClient:
    medicine_ids = [7, 6, 4]
    amounts = [2, 1, 2]

    response = await authed_cli_client2.post(
        f"/add_to_cart?medicine_id={medicine_ids[0]}&amount={amounts[0]}",
    )

    response_2 = await authed_cli_client2.post(
        f"/add_to_cart?medicine_id={medicine_ids[1]}&amount={amounts[1]}",
    )

    response_3 = await authed_cli_client2.post(
        f"/add_to_cart?medicine_id={medicine_ids[2]}&amount={amounts[2]}",
    )
    yield authed_cli_client2


@pytest.fixture
async def client_order_1(store, client_2, authed_cli_client2,
                         medicine_1, medicine_2, medicine_3,
                         medicine_4, medicine_5, medicine_6,
                         medicine_7, medicine_8, medicine_9
                         ) -> ClientOrder:
    medicine_ids = [7, 6, 4]
    amounts = [2, 1, 2]

    response = await authed_cli_client2.post(
        f"/add_to_cart?medicine_id={medicine_ids[0]}&amount={amounts[0]}",
    )

    response_2 = await authed_cli_client2.post(
        f"/add_to_cart?medicine_id={medicine_ids[1]}&amount={amounts[1]}",
    )

    response_3 = await authed_cli_client2.post(
        f"/add_to_cart?medicine_id={medicine_ids[2]}&amount={amounts[2]}",
    )
    cart = (await response_3.json())["data"]
    order = await store.pharmacy.make_online_order(client_id=client_2.id, cart=cart)
    yield order


@pytest.fixture
def client_order_no(client_order_1):
    return client_order_1.order_no


@pytest.fixture
async def client_order_2(store, client_2, client_2_with_rating, authed_cli_client2, medicine_10):
    medicine_id = 1
    amount = 1

    response = await authed_cli_client2.post(
        f"/add_to_cart?medicine_id={medicine_id}&amount={amount}",
    )
    cart = (await response.json())["data"]
    order = await store.pharmacy.make_online_order(client_id=client_2.id, cart=cart)
    yield order


@pytest.fixture
def client_order2_no(client_order_2):
    return client_order_2.order_no
