import gino
from gino.api import Gino
from app.store.database.gino_ import db
from hashlib import sha256

from typing import Optional, List
from sqlalchemy.engine.url import URL
from sqlalchemy import and_, or_

from .gino_ import db

from .buisness_logic import price_markup_, edit_rating

from random import randint

from datetime import datetime, timedelta, date

import typing
from app.admin.models import AdminModel

if typing.TYPE_CHECKING:
    from app.web.app_ import Application

    from app.pharmacy.models import ClientModel, CategoryModel, \
        MedicineModel, OrderModel, RevenueModel, MedicineInfoForOrder
    from app.pharmacy.models import Client, Category, Medicine, ClientOrder, Revenue


class Database:

    def __init__(self, app: "Application"):
        self.app = app
        self.db: Optional[Gino] = None

    async def connect(self, *_, **kwargs):
        self._engine = await gino.create_engine(
            URL(
                drivername="asyncpg",
                host=self.app.config.database.host,
                port=self.app.config.database.port,
                username=self.app.config.database.user,
                password=self.app.config.database.password,
                database=self.app.config.database.database,
            ),
            min_size=1,
            max_size=1,
        )
        self.db = db
        self.db.bind = self._engine
        await self.db.gino.create_all()

    async def disconnect(self, *_, **kwargs):
        ...
        # await self.db.pop_bind().close()

    ############################################
    # ALL DATABASE QUERY OPERATIONS ADMIN      #
    ############################################

    @property
    async def admin_empty(self) -> bool:
        from app.admin.models import AdminModel
        counter = self.db.func.count(AdminModel.id)
        total = await self.db.select([counter]).gino.scalar()
        return total == 0

    async def create_new_admin(self, login: str, password: str) -> "AdminModel":
        admin = await AdminModel.create(login=login, password=str(sha256(password.encode()).hexdigest()))
        return admin

    async def get_by_login(self, login: str) -> "AdminModel":
        res = await AdminModel.query.where(AdminModel.login == login).gino.first()
        return res

    async def add_new_category(self, title: str) -> "CategoryModel":
        from app.pharmacy.models import CategoryModel
        category = await CategoryModel.create(title=title)
        return category

    async def add_new_medicine(self, vendor_code: str, category_title: str,
                               title: str, manufacturer: str, price: float, amount: int) -> "MedicineModel":
        from app.pharmacy.models import MedicineModel

        medicine = await MedicineModel.create(vendor_code=vendor_code,
                                              category_title=category_title,
                                              title=title, manufacturer=manufacturer, trade_price=price,
                                              price=price_markup_(price, online=True),
                                              price_offline=price_markup_(price, online=False),
                                              amount=amount
                                              )
        return medicine

    async def find_order_by_order_no(self, order_no: str) -> "OrderModel":
        from app.pharmacy.models import OrderModel
        result = await OrderModel.query.where(OrderModel.order_no == order_no).gino.first()
        return result

    async def search_online_order(self, order_no: str):
        from app.pharmacy.models import MedicineModel, MedicineInfoForOrder, OrderModel

        medicine_info = await MedicineInfoForOrder.outerjoin(
            MedicineModel, and_(
                MedicineModel.title == MedicineInfoForOrder.title,
                MedicineModel.id == MedicineInfoForOrder.medicine_id)
        ).select().where(MedicineInfoForOrder.order_no == order_no).gino.load(
            MedicineInfoForOrder.distinct(MedicineInfoForOrder.id).load(add_item=MedicineModel.load())
        ).all()
        # print([item.medicine_info for item in medicine_info])

        # привязать медикаменты по заказу к инфам по медикаментам

        # order_info = (await OrderModel.outerjoin(
        #     MedicineInfoForOrder, OrderModel.order_no == MedicineInfoForOrder.order_no
        # ).select().where(OrderModel.order_no == order_no).gino.load(
        #     OrderModel.distinct(OrderModel.order_no).load(add_to_cart=MedicineInfoForOrder.load())
        # ).all())[0]

        order_info = await OrderModel.outerjoin(
            MedicineInfoForOrder, OrderModel.order_no == MedicineInfoForOrder.order_no
        ).select().where(OrderModel.order_no == order_no).gino.load(
            OrderModel.distinct(OrderModel.order_no).load(add_to_cart=MedicineInfoForOrder.load())
        ).first()

        # print(order_info.medicine)
        return order_info, medicine_info

    async def close_online_order(self, order_no: str, promo_rating_score: int) -> tuple["RevenueModel", "ClientModel"]:
        from app.pharmacy.models import OrderModel, RevenueModel
        order = await OrderModel.query.where(OrderModel.order_no == order_no).gino.first()
        client = await self.search_client_by_id(order.client_id)
        await OrderModel.update.values(status="PAYED").where(OrderModel.order_no == order_no).gino.status()

        revenue = await RevenueModel.create(order_no=order.order_no, sum=order.total_price-promo_rating_score)

        await client.update(rating=client.rating-int(promo_rating_score)).apply()  # if score applied for discount
        # subtract score

        # await client.update(rating=edit_rating(client.rating, order.total_price)).apply()
        await client.update(rating=edit_rating(client.rating, revenue.sum)).apply()
        return revenue, client

    ############################################
    # ALL DATABASE QUERY OPERATIONS CLIENT     #
    ############################################

    async def create_new_client(self, name: str,
                                password: str,
                                phone: Optional[str] = " ",
                                email: Optional[str] = " "
                                ) -> "ClientModel":
        from app.pharmacy.models import ClientModel
        client = await ClientModel.create(
            name=name,
            password=str(sha256(password.encode()).hexdigest()),
            phone=phone,
            email=email,
            rating=0)
        return client

    async def search_client_by_id(self, id_: int) -> "ClientModel":
        from app.pharmacy.models import ClientModel
        return await ClientModel.query.where(ClientModel.id == id_).gino.first()

    async def search_client_by_phone_or_email(self, phone: str, email: str) -> List["ClientModel"]:
        from app.pharmacy.models import ClientModel
        return await ClientModel.query.where(
            or_(
                ClientModel.phone == phone, ClientModel.email == email)
        ).gino.all()

    async def search_client_by_phone_or_email_(self, phone: Optional[str] = "", email: Optional[str] = "") \
            -> "ClientModel":
        from app.pharmacy.models import ClientModel
        return await ClientModel.query.where(
            or_(
                ClientModel.phone == phone, ClientModel.email == email)
        ).gino.first()

    async def search_client_by_phone_email(self, phone: str, email: str) -> "ClientModel":
        from app.pharmacy.models import ClientModel
        return await ClientModel.query.where(
            and_(
                ClientModel.phone == phone, ClientModel.email == email)
        ).gino.first()

    async def search_client_by_email(self, email: str) -> "ClientModel":
        from app.pharmacy.models import ClientModel
        return await ClientModel.query.where(ClientModel.email == email).gino.all()[0]

    async def patch_client(self, client: "Client") -> "ClientModel":
        from app.pharmacy.models import ClientModel
        client_from_db = await self.search_client_by_id(client.id)

        await client_from_db.update(name=client.name, email=client.email, phone=client.phone).apply()
        return client_from_db

    async def check_category(self, category: str) -> bool:
        from app.pharmacy.models import CategoryModel
        result = await CategoryModel.query.where(CategoryModel.title == category).gino.all()

        return result != []

    async def browse_categories(self, category: Optional[str] = None):
        from app.pharmacy.models import CategoryModel, MedicineModel
        if not category:
            return await CategoryModel.outerjoin(MedicineModel, CategoryModel.title == MedicineModel.category_title) \
                .select().gino.load(
                CategoryModel.distinct(CategoryModel.id).load(add_item=MedicineModel.load())
            ).all()

        return await CategoryModel.outerjoin(MedicineModel, CategoryModel.title == MedicineModel.category_title) \
            .select() \
            .where(CategoryModel.title == category).gino.load(
            CategoryModel.distinct(CategoryModel.title).load(add_item=MedicineModel.load())
        ).all()

    async def search_medicine_by_title(self, title: str) -> List["MedicineModel"]:
        from app.pharmacy.models import MedicineModel
        results = await MedicineModel.query.where(
            and_(
                MedicineModel.title == title, MedicineModel.amount != 0)
        ).order_by(MedicineModel.price).gino.all()
        return results

    async def search_medicine_by_id_and_amount(self, id_: int, amount: int) -> Optional["MedicineModel"]:
        from app.pharmacy.models import MedicineModel
        results = await MedicineModel.query.where(
            and_(
                MedicineModel.id == id_, MedicineModel.amount >= amount)
        ).order_by(MedicineModel.price).gino.first()
        return results

    async def make_online_order(self, client_id: int, cart: list[dict]) -> Optional["OrderModel"]:
        from app.pharmacy.models import OrderModel, MedicineModel, MedicineInfoForOrder
        online_order: OrderModel = await OrderModel.create(client_id=client_id,
                                                           order_no=str(randint(1, 2 ** 32)),
                                                           status="PENDING",
                                                           total_price=0,
                                                           valid_until=datetime.now() + timedelta(days=5))
        for medicine in cart:
            item: MedicineModel = await MedicineModel.query.where(and_(
                MedicineModel.id == medicine["id"],
                MedicineModel.title == medicine["title"],
                MedicineModel.vendor_code == str(medicine["vendor_code"]),
                MedicineModel.manufacturer == medicine["manufacturer"],
                MedicineModel.amount >= medicine["amount"])).gino.first()

            medicine_entry = await MedicineInfoForOrder.create(
                order_no=online_order.order_no,
                title=item.title,
                medicine_id=item.id,
                amount_booked=medicine["amount"],
                price_booked=medicine["price"]
            )
            online_order.add_to_cart(medicine_entry)
            online_order.add_to_cart_info(item)

            await item.update(amount=item.amount - medicine["amount"]).apply()

        await online_order.update(total_price=online_order.price).apply()
        return online_order

    async def cancel_order(self, order_no: str):
        from app.pharmacy.models import OrderModel, MedicineInfoForOrder, MedicineModel
        order = await OrderModel.query.where(
            OrderModel.order_no == order_no
        ).gino.first()
        medicine_booked = await MedicineInfoForOrder.query.where(
            MedicineInfoForOrder.order_no == order_no
        ).gino.all()

        for medicine in medicine_booked:
            med_info_in_stock = await MedicineModel.query.where(
                and_(
                    MedicineModel.title == medicine.title,
                    MedicineModel.id == medicine.medicine_id
                )
            ).gino.first()
            await med_info_in_stock.update(amount=med_info_in_stock.amount+medicine.amount_booked).apply()

        await order.delete()

    ############################################
    # DATABASE CLEANING OPERATION              #
    ############################################

    async def clean_outdated_orders(self):
        from app.pharmacy.models import OrderModel

        orders = await OrderModel.query.where(
            OrderModel.valid_until < datetime.now()
        ).gino.all()

        for order in orders:
            await order.delete()
