from tests.utils import ok_response
from app.store import Store
import pytest

from app.pharmacy.models import MedicineModel, OrderModel, ClientModel, RevenueModel

from tests.client_tests.test_make_order import dbobj2dt_order

from app.store.database.buisness_logic import edit_rating


def dbobj2dt_revenue(rev: RevenueModel):
    return {
        "order_no": rev.order_no,
        "sum": rev.sum
    }


class TestAdminViewClientOrder:
    async def test_unauthorized(self, cli, client_order_1, client_2, store: Store):
        response = await cli.get(
            f"/admin_view_client_order?order_no={client_order_1.order_no}",
            json={
                "order_no": client_order_1.order_no
            }
        )
        assert response.status == 401
        data = await response.json()
        assert data["error title"] == "unauthorized"

    async def test_not_found(self, client_order_no, authed_cli, store: Store):
        order_no = str(int(client_order_no) + 1)

        response = await authed_cli.get(
            f"/admin_view_client_order?order_no={order_no}&promo_rating_score=0"
        )
        assert response.status == 404
        data = await response.json()
        assert data["error title"] == "not_found"

    async def test_invalid_method(self, client_order_no, authed_cli, client_2, store: Store):
        response = await authed_cli.post(
            f"/admin_view_client_order?order_no={client_order_no}"
        )
        assert response.status == 405
        data = await response.json()
        assert data["error title"] == "not_implemented"

    async def test_success(self, client_order_1, client_order_no, authed_cli, medicine_ids, amounts,
                           client_2, store: Store):
        response = await authed_cli.get(
            f"/admin_view_client_order?order_no={client_order_no}&promo_rating_score=0",
        )
        assert response.status == 200

        cli_from_db = await ClientModel.query.where(ClientModel.id == client_2.id).gino.first()
        medicine_db = [
            await MedicineModel.query.where(MedicineModel.id == med_id).gino.first()
            for med_id in medicine_ids
        ]
        order = await OrderModel.query.where(OrderModel.order_no == client_order_no).gino.first()

        data = await response.json()

        assert ok_response(
            dbobj2dt_order(client=cli_from_db, order=order, med_db=medicine_db, amounts=amounts)
        ) == data


class TestAdminExecuteClientOnlineOrder:
    async def test_unauthorized(self, cli, client_order_1, client_2, store: Store):
        response = await cli.get(
            f"/admin_execute_online_order?order_no={client_order_1.order_no}"
        )
        assert response.status == 401
        data = await response.json()
        assert data["error title"] == "unauthorized"

    async def test_not_found(self, client_order_no, authed_cli, store: Store):
        order_no = str(int(client_order_no) + 1)
        response = await authed_cli.get(
            f"/admin_execute_online_order?order_no={order_no}&promo_rating_score=0"
        )
        assert response.status == 404
        data = await response.json()
        assert data["error title"] == "not_found"

    async def test_invalid_method(self, client_order_no, authed_cli, client_2, store: Store):
        response = await authed_cli.post(
            f"/admin_execute_online_order?order_no={client_order_no}"
        )
        assert response.status == 405
        data = await response.json()
        assert data["error title"] == "not_implemented"

    async def test_success(self, client_order_1, client_order_no, authed_cli, medicine_ids, amounts,
                           client_2, store: Store):
        cli_from_db = await ClientModel.query.where(ClientModel.id == client_2.id).gino.first()

        medicine_db = [
            await MedicineModel.query.where(MedicineModel.id == med_id).gino.first()
            for med_id in medicine_ids
        ]
        order_not_payed = await OrderModel.query.where(OrderModel.order_no == client_order_no).gino.first()

        response = await authed_cli.get(
            f"/admin_execute_online_order?order_no={client_order_no}&promo_rating_score=0"
        )
        assert response.status == 200

        revenue_db = await RevenueModel.query.where(RevenueModel.order_no == client_order_no).gino.first()

        expected_new_rating = edit_rating(rating=cli_from_db.rating, sum_=revenue_db.sum)

        data = await response.json()

        assert ok_response(
            {
                "order": dbobj2dt_order(client=cli_from_db, order=order_not_payed, med_db=medicine_db, amounts=amounts),
                "receipt": dbobj2dt_revenue(revenue_db)
            }
        ) == data

        order_payed = await OrderModel.query.where(OrderModel.order_no == client_order_no).gino.first()
        client_upd_rating = await ClientModel.query.where(ClientModel.id == client_2.id).gino.first()

        assert order_payed.status == "PAYED"
        assert client_upd_rating.rating == expected_new_rating

    async def test_prs_more_than_rating_bad_request(self, client_2_with_rating, client_order_2, client_order2_no,
                                                    client_2_rating,
                                                    authed_cli):
        response = await authed_cli.get(
            f"/admin_execute_online_order?order_no={client_order_2.order_no}&promo_rating_score={client_2_rating + 1}"
        )
        assert response.status == 400
        data = await response.json()
        assert data["error title"] == "bad_request"
        assert data["text"] == "Incorrect promo_rating_score amount"

    async def test_apply_rating_score_success(self, client_2_with_rating, client_order_1, client_order_no,
                                              client_2_rating, authed_cli):
        order_info = await OrderModel.query.where(OrderModel.order_no == client_order_no).gino.first()
        expected_sum_payed = order_info.total_price - client_2_rating

        response = await authed_cli.get(
            f"/admin_execute_online_order?order_no={client_order_1.order_no}&promo_rating_score={client_2_rating}"
        )
        assert response.status == 200
        data = await response.json()

        assert data["data"]["receipt"]["sum"] == expected_sum_payed

    async def test_rating_more_than_sum(self, client_2, client_2_with_rating, client_order_2, client_order2_no,
                                        client_2_rating, authed_cli):
        order_info = await OrderModel.query.where(OrderModel.order_no == client_order2_no).gino.first()

        expected_sum_payed = 1
        total_price = order_info.total_price
        temp_rating = int(total_price - 1)
        expected_rating = edit_rating(temp_rating, 1)

        response = await authed_cli.get(
            f"/admin_execute_online_order?order_no={client_order2_no}&promo_rating_score={client_2_rating}"
        )
        assert response.status == 200
        data = await response.json()

        assert data["data"]["receipt"]["sum"] == expected_sum_payed

        client_form_db = await ClientModel.query.where(ClientModel.id == client_2.id).gino.first()
        assert client_form_db.rating == expected_rating



