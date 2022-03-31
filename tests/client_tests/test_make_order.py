from datetime import datetime

from tests.utils import ok_response
from app.store import Store
import pytest
from tests.client_tests.test_client_register import dbobj2dt_client
from tests.admin_tests.test_admin_adding import dbobj2dt_medicine

from app.pharmacy.models import MedicineModel, OrderModel, ClientModel, MedicineInfoForOrder, CategoryModel, Category, \
    Medicine


def dbobj2dt_medicine_order(med: MedicineModel, order_amount) -> dict:
    return {
        "id": med.id,
        "vendor_code": med.vendor_code,
        "category_title": med.category_title,
        "title": med.title,
        "manufacturer": med.manufacturer,
        "price": med.price,
        "amount": order_amount,
    }


def dbobj2dt_category_full(cat: Category, cat_med: list[Medicine]) -> dict:
    return {
        "id": cat.id,
        "title": cat.title,
        "medicine": [dbobj2dt_medicine(med) for med in cat_med]
    }


def dbobj2dt_order(client: ClientModel, order: OrderModel, med_db: list[MedicineModel], amounts: list) -> dict:
    return {
        "id": order.id,
        "client": dbobj2dt_client(client),
        "medicine": [
            dbobj2dt_medicine_order(med_db[i], amounts[i])
            for i in range(len(med_db))
        ],
        "order_no": order.order_no,
        "total_price": order.total_price,
        "valid_until": order.valid_until.strftime("%Y/%m/%d"),
        "status": order.status
    }


class TestClientAddToCart:
    async def test_unauthorized(self, cli, store: Store,
                                medicine_1, medicine_2, medicine_3, medicine_4):
        response = await cli.post(
            "/add_to_cart?medicine_id=3&amount=1",
        )

        assert response.status == 401
        data = await response.json()
        assert data["error title"] == "unauthorized"

    async def test_success(self, authed_cli_client1, store: Store,
                           medicine_1, medicine_2, medicine_3,
                           medicine_4, medicine_5, medicine_6,
                           medicine_7, medicine_8, medicine_9):
        medicine_id = 1
        amount = 1
        response = await authed_cli_client1.post(
            f"/add_to_cart?medicine_id={medicine_id}&amount={amount}",
            json={
                "medicine_id": medicine_id,
                "amount": amount
            }
        )
        assert response.status == 200
        medicine_from_db = await MedicineModel.query.where(MedicineModel.id == medicine_id).gino.first()

        data = await response.json()
        assert data == ok_response([dbobj2dt_medicine_order(med=medicine_from_db, order_amount=amount)])

    async def test_multiple(self, authed_cli_client2, store: Store,
                            medicine_1, medicine_2, medicine_3,
                            medicine_4, medicine_5, medicine_6,
                            medicine_7, medicine_8, medicine_9):
        medicine_ids = [7, 6, 4]
        amounts = [2, 1, 2]

        response = await authed_cli_client2.post(
            f"/add_to_cart?medicine_id={medicine_ids[0]}&amount={amounts[0]}",
        )
        assert response.status == 200
        response_2 = await authed_cli_client2.post(
            f"/add_to_cart?medicine_id={medicine_ids[1]}&amount={amounts[1]}",
        )
        assert response_2.status == 200
        response_3 = await authed_cli_client2.post(
            f"/add_to_cart?medicine_id={medicine_ids[2]}&amount={amounts[2]}",
        )
        assert response_3.status == 200

        db_med_1 = await MedicineModel.query.where(MedicineModel.id == medicine_ids[0]).gino.first()
        db_med_2 = await MedicineModel.query.where(MedicineModel.id == medicine_ids[1]).gino.first()
        db_med_3 = await MedicineModel.query.where(MedicineModel.id == medicine_ids[2]).gino.first()

        data = await response_3.json()

        assert data == ok_response(
            [dbobj2dt_medicine_order(db_med_1, amounts[0]),
             dbobj2dt_medicine_order(db_med_2, amounts[1]),
             dbobj2dt_medicine_order(db_med_3, amounts[2])]
        )

    async def test_overbooking(self, authed_cli_client2, store: Store,
                               medicine_1, medicine_2, medicine_3,
                               medicine_4, medicine_5, medicine_6,
                               medicine_7, medicine_8, medicine_9):
        medicine_id = 7
        amount = 3
        response = await authed_cli_client2.post(
            f"/add_to_cart?medicine_id={medicine_id}&amount={amount}")
        assert response.status == 404
        data = await response.json()
        assert data["text"] == "Medicine not found or out of stock!"

    async def test_delete_from_cart(self, client_with_cart, store: Store):
        medicine_id = 7
        response = await client_with_cart.patch(
            f"/delete_from_cart?medicine_id={medicine_id}",
        )
        assert response.status == 200
        data = await response.json()
        assert 2 == len(data["data"])

    async def test_other_method_delete(self, client_with_cart, store: Store):
        medicine_id = 7
        response = await client_with_cart.post(
            f"/delete_from_cart?medicine_id={medicine_id}",
        )
        assert response.status == 405
        data = await response.json()
        assert data["error title"] == "not_implemented"


class TestClientMakeOrder:
    async def test_unauthorized(self, cli, store: Store):
        response = await cli.post(
            "/make_order"
        )
        assert response.status == 401
        data = await response.json()
        assert data["error title"] == "unauthorized"

    async def test_other_method_make_order(self, client_with_cart, store: Store):
        response = await client_with_cart.get(
            "/make_order"
        )
        assert response.status == 405
        data = await response.json()
        assert data["error title"] == "not_implemented"

    async def test_success(self, client_2, client_with_cart, medicine_ids, amounts, store: Store):
        response = await client_with_cart.post(
            "/make_order"
        )
        assert response.status == 200

        cli_from_db = await ClientModel.query.where(ClientModel.id == client_2.id).gino.first()
        order_id = 1
        medicine_db = [
            await MedicineModel.query.where(MedicineModel.id == med_id).gino.first()
            for med_id in medicine_ids
        ]
        order = await OrderModel.query.where(OrderModel.id == order_id).gino.first()  # pick order_no, price, date

        data = await response.json()
        assert ok_response(
            dbobj2dt_order(client=cli_from_db, order=order, med_db=medicine_db, amounts=amounts)
        ) == data

    async def test_empty_cart(self, client_2, authed_cli_client2):
        response = await authed_cli_client2.post(
            "/make_order"
        )
        assert response.status == 400
        data = await response.json()
        assert data["error title"] == "bad_request"
        assert data["text"] == "The cart is empty"


class TestClientCancelOrder:
    async def test_unauthorized(self, cli, store: Store):
        response = await cli.post(
            f"/cancel_order?order_no=1"
        )
        assert response.status == 401
        data = await response.json()
        assert data["error title"] == "unauthorized"

    async def test_other_method_make_order(self, client_order_no, authed_cli_client2, store: Store):
        response = await authed_cli_client2.get(
            f"/cancel_order?order_no={client_order_no}"
        )
        assert response.status == 405
        data = await response.json()
        assert data["error title"] == "not_implemented"

    async def test_success(self, client_order_no, authed_cli_client2, client_order_1, medicine_ids, amounts):
        medicine_db_before = [
            await MedicineModel.query.where(MedicineModel.id == med_id).gino.first()
            for med_id in medicine_ids
        ]

        response = await authed_cli_client2.post(
            f"/cancel_order?order_no={client_order_no}"
        )

        assert response.status == 200

        data = await response.json()
        assert data["data"] == f"ORDER canceled: order number {client_order_no}"

        order_info = await OrderModel.query.where(OrderModel.order_no == client_order_no).gino.all()
        assert order_info == []
        ordered_meds = await MedicineInfoForOrder.query.where(
            MedicineInfoForOrder.order_no == client_order_no).gino.all()
        assert ordered_meds == []

        medicine_db_after = [
            await MedicineModel.query.where(MedicineModel.id == med_id).gino.first()
            for med_id in medicine_ids
        ]

        for i in range(len(medicine_db_after)):
            assert medicine_db_after[i].amount == medicine_db_before[i].amount + amounts[i]
