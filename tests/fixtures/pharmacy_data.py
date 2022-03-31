from typing import List

import pytest

from app.pharmacy.models import Category, Medicine


@pytest.fixture
async def category_1(store) -> List[Category]:
    categories = await store.admins.add_categories(
        category_set=[
            {
                "title": "Слабительное"
            },
        ]
    )
    yield categories


@pytest.fixture
async def category_2(store) -> List[Category]:
    categories = await store.admins.add_categories(
        category_set=[
            {
                "title": "Жаропонижающее"
            },
        ]
    )
    yield categories


@pytest.fixture
async def category_3(store) -> List[Category]:
    categories = await store.admins.add_categories(
        category_set=[
            {
                "title": "Сердечно-сосудистое"
            }
        ]
    )
    yield categories


@pytest.fixture
async def medicine_1(store, category_1) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 4759584298198,
                "category_title": category_1[0].title,
                "title": "Гутталакс",
                "manufacturer": "Институт де Ангели С.Р.Л.",
                "trade_price": 100,
                "amount": 3,
                "valid_until": "2023/02/07"
            },
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_2(store, category_2) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 45457435433819,
                "category_title": category_2[0].title,
                "title": "Панадол",
                "manufacturer": "Глаксо Смит Кляйн",
                "trade_price": 270,
                "amount": 5,
                "valid_until": "2022/05/19"
            },
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_3(store, category_2) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 454574358438569,
                "category_title": category_2[0].title,
                "title": "Анальгин",
                "manufacturer": "Фармстандарт",
                "trade_price": 20,
                "amount": 7,
                "valid_until": "2022/10/19"
            },
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_4(store, category_3) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 45457435843819,
                "category_title": category_3[0].title,
                "title": "Метопролол",
                "manufacturer": "Тева",
                "trade_price": 40,
                "amount": 3,
                "valid_until": "2023/05/19"
            },
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_5(store, category_1) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 45457325843819,
                "category_title": category_1[0].title,
                "title": "Фитолакс",
                "manufacturer": "Эвалар",
                "trade_price": 300,
                "amount": 2,
                "valid_until": "2023/10/01"
            },
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_6(store, category_3) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 43758457840594,
                "category_title": category_3[0].title,
                "title": "Кардиомагнил",
                "manufacturer": "Такеда",
                "trade_price": 150,
                "amount": 3,
                "valid_until": "2023/10/09"
            },
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_7(store, category_1) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 43758457270594,
                "category_title": category_1[0].title,
                "title": "Фибралакс",
                "manufacturer": "Эвалар",
                "trade_price": 200,
                "amount": 2,
                "valid_until": "2022/05/19"
            },
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_8(store, category_2) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 43758457840594,
                "category_title": category_2[0].title,
                "title": "Нурофен",
                "manufacturer": "Рекитт Бенкизер",
                "trade_price": 600,
                "amount": 3,
                "valid_until": "2023/05/19"
            },
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_9(store, category_2) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 43758459240594,
                "category_title": category_2[0].title,
                "title": "Ибуклин",
                "manufacturer": "Реддис",
                "trade_price": 500,
                "amount": 3,
                "valid_until": "2022/07/20"
            }
        ]
    )
    yield medicine


@pytest.fixture
async def medicine_10(store, category_2) -> List[Medicine]:
    medicine = await store.admins.add_medicine_set(
        medicine_set=[
            {
                "vendor_code": 43758459243794,
                "category_title": category_2[0].title,
                "title": "Парацетамол",
                "manufacturer": "Татхимфарм",
                "trade_price": 5,
                "amount": 3,
                "valid_until": "2025/07/20"
            }
        ]
    )
    yield medicine

