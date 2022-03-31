from tests.utils import ok_response
from app.store import Store
import pytest
from tests.utils import check_empty_table_exists
from app.pharmacy.models import CategoryModel, MedicineModel, Medicine

from typing import Union


def dbobj2dt_category(cat: CategoryModel) -> dict:
    return {
        "id": cat.id,
        "title": cat.title
    }


def dbobj2dt_medicine(med: Union[MedicineModel, Medicine]) -> dict:
    return {
        "id": med.id,
        "vendor_code": med.vendor_code,
        "category_title": med.category_title,
        "title": med.title,
        "manufacturer": med.manufacturer,
        # "trade_price": med.trade_price,
        "price": med.price,
        # "price_offline": med.price_offline,
        "amount": med.amount,
        # "valid_until": med.valid_until
    }


class TestAdminAddCategory:
    async def test_unauthorized(self, cli, store):
        response = await cli.post(
            "/admin_add_category",
            json={
                "categories": [
                    {
                        "title": "Слабительное"
                    },
                    {
                        "title": "Жаропонижающее"
                    },
                    {
                        "title": "Сердечно-сосудистое"
                    }
                ]
            }
        )
        assert response.status == 401
        data = await response.json()
        assert data["error title"] == "unauthorized"

    async def test_categories_exists(self, authed_cli):
        await check_empty_table_exists(authed_cli, "categories")

    async def test_add_categories(self, cli, authed_cli, config):

        response = await authed_cli.post(
            "/admin_add_category",
            json={
                    "categories": [
                        {
                            "title": "Слабительное"
                        },
                        {
                            "title": "Жаропонижающее"
                        },
                        {
                            "title": "Сердечно-сосудистое"
                        }
                    ]
                }
        )
        assert response.status == 200
        commit_data = await CategoryModel.query.gino.all()
        data = await response.json()
        assert {
                   "status": "ok",
                   "data": [dbobj2dt_category(cat) for cat in commit_data]
               } == data

    async def test_repeating_categories(self, authed_cli, store: Store):
        response = await authed_cli.post(
            "/admin_add_category",
            json={
                "categories": [
                    {
                        "title": "Слабительное"
                    },
                    {
                        "title": "Слабительное"
                    },
                ]
            }
        )
        assert response.status == 500


class TestAdminAddMedicine:
    async def test_medicine_exists(self, cli):
        await check_empty_table_exists(cli, "medicine")

    async def test_unauthorized(self, cli):
        response = await cli.post(
            "/admin_add_new",
            json={
                "medicine": [
                    {
                        "vendor_code": '4759584298198',
                        "category_title": "Слабительное",
                        "title": "Гутталакс",
                        "manufacturer": "Институт де Ангели С.Р.Л.",
                        "trade_price": 100,
                        "amount": 3,
                        "valid_until": "2023/02/07"
                    },
                ]
            }
        )
        assert response.status == 401
        data = await response.json()
        assert data["error title"] == "unauthorized"

    async def test_add_medicine(self, authed_cli):
        response = await authed_cli.post(
            "/admin_add_new",
            json={
                "medicine": [
                    {
                        "vendor_code": '4759584298198',
                        "category_title": "Слабительное",
                        "title": "Гутталакс",
                        "manufacturer": "Институт де Ангели С.Р.Л.",
                        "trade_price": 100,
                        "amount": 3,
                        "valid_until": "2023/02/07"
                    },
                    {
                        "vendor_code": '45457435433819',
                        "category_title": "Жаропонижающее",
                        "title": "Панадол",
                        "manufacturer": "Глаксо Смит Кляйн",
                        "trade_price": 270,
                        "amount": 5,
                        "valid_until": "2022/05/19"
                    },
                    {
                        "vendor_code": '454574358438569',
                        "category_title": "Жаропонижающее",
                        "title": "Анальгин",
                        "manufacturer": "Фармстандарт",
                        "trade_price": 20,
                        "amount": 7,
                        "valid_until": "2022/10/19"
                    },
                    {
                        "vendor_code": '45457435843819',
                        "category_title": "Сердечно-сосудистое",
                        "title": "Метопролол",
                        "manufacturer": "Тева",
                        "trade_price": 40,
                        "amount": 3,
                        "valid_until": "2023/05/19"
                    },
                    {
                        "vendor_code": '45457325843819',
                        "category_title": "Слабительное",
                        "title": "Фитолакс",
                        "manufacturer": "Эвалар",
                        "trade_price": 300,
                        "amount": 2,
                        "valid_until": "2023/10/01"
                    },
                    {
                        "vendor_code": '43758457840594',
                        "category_title": "Сердечно-сосудистое",
                        "title": "Кардиомагнил",
                        "manufacturer": "Такеда",
                        "trade_price": 150,
                        "amount": 3,
                        "valid_until": "2023/10/09"
                    },
                    {
                        "vendor_code": '43758457270594',
                        "category_title": "Слабительное",
                        "title": "Фибралакс",
                        "manufacturer": "Эвалар",
                        "trade_price": 200,
                        "amount": 2,
                        "valid_until": "2022/05/19"
                    },
                    {
                        "vendor_code": '43758457840594',
                        "category_title": "Жаропонижающее",
                        "title": "Нурофен",
                        "manufacturer": "Рекитт Бенкизер",
                        "trade_price": 600,
                        "amount": 3,
                        "valid_until": "2023/05/19"
                    },
                    {
                        "vendor_code": '43758459240594',
                        "category_title": "Жаропонижающее",
                        "title": "Ибуклин",
                        "manufacturer": "Реддис",
                        "trade_price": 500,
                        "amount": 3,
                        "valid_until": "2022/07/20"
                    }
                ]
            }
        )
        assert response.status == 200
        commit_data = await MedicineModel.query.gino.all()
        data = await response.json()
        assert {
                   "status": "ok",
                   "data": [dbobj2dt_medicine(med) for med in commit_data]
               } == data



