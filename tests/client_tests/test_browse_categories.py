from tests.utils import ok_response
from app.store import Store
import pytest

from tests.admin_tests.test_admin_adding import dbobj2dt_medicine
from app.pharmacy.models import MedicineModel, Category, Medicine


def dbobj2dt_category_full(cat: Category, cat_med: list[Medicine]) -> dict:
    return {
        "id": cat.id,
        "title": cat.title,
        "medicine": [dbobj2dt_medicine(med) for med in cat_med]
    }


class TestCommonBrowseCategories:
    async def test_success_no_cat(self, cli, store: Store, category_1, category_2, category_3,
                                  medicine_1, medicine_2, medicine_3,
                                  medicine_4):
        response = await cli.get(
            "/list_items",
            json={}
        )
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {
                "categories": [
                    dbobj2dt_category_full(cat=category_1[0], cat_med=medicine_1),
                    dbobj2dt_category_full(cat=category_2[0], cat_med=[medicine_2[0], medicine_3[0]]),
                    dbobj2dt_category_full(cat=category_3[0], cat_med=medicine_4)
                ]
            }
        )

    async def test_success_cat_filter(self, cli, store: Store, category_1, category_2, category_3,
                                      medicine_1, medicine_2, medicine_3,
                                      medicine_4):
        response = await cli.get(
            f"/list_items?title={category_2[0].title}",
            json={
                "title": category_2[0].title
            }
        )
        assert response.status == 200
        data = await response.json()
        assert data == ok_response(
            {
                "categories": [
                    dbobj2dt_category_full(cat=category_2[0], cat_med=[medicine_2[0], medicine_3[0]])
                ]
            }
        )

    async def test_cat_not_found(self, cli, store: Store, category_1, category_2, category_3,
                                 medicine_1, medicine_2, medicine_3,
                                 medicine_4):
        response = await cli.get(
            f"/list_items?title=Что-то",
        )
        assert response.status == 404
        data = await response.json()
        assert data["error title"] == "not_found"
        assert data["text"] == "Category not found!"


class TestCommonSearchByTitle:
    async def test_success(self, cli, store: Store, category_1, category_2, category_3,
                           medicine_1, medicine_2, medicine_3,
                           medicine_4):
        response = await cli.get(
            f"/search_by_title?title={medicine_1[0].title}"
        )
        medicine_from_db = await MedicineModel.query.where(MedicineModel.id == medicine_1[0].id).gino.first()
        assert response.status == 200
        data = await response.json()

        assert data == ok_response(
            {
                "medicine": [dbobj2dt_medicine(medicine_from_db)]
            }
        )

    async def test_not_found(self, cli, store: Store, category_1, category_2, category_3,
                             medicine_1, medicine_2, medicine_3,
                             medicine_4):
        response = await cli.get(
            f"/search_by_title?title=Something"
        )
        assert response.status == 404
        data = await response.json()
        assert data["error title"] == "not_found"
        assert data["text"] == "Title not found!"

