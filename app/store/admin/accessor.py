import typing

from typing import Optional, List
from logging import getLogger

from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin
from app.pharmacy.models import Revenue, ClientOrder, Client, Medicine, Category, MedicineInfoForOrder

if typing.TYPE_CHECKING:
    from app.web.app_ import Application


from datetime import datetime

from app.store.database.gino_ import db


class AdminAccessor(BaseAccessor):

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.logger = getLogger("Admin Accessor")

    async def connect(self, app: "Application"):
        await super().connect(app)
        await self.create_admin_on_start(
            login=app.config.admin.login, password=app.config.admin.password
        )
        # await app.database.connect()

    async def get_by_login(self, login: str) -> Optional[Admin]:
        """finds the admin by login"""
        raw_data = await self.app.database.get_by_login(login)
        if raw_data:
            return Admin(id=raw_data.id, login=raw_data.login, password=raw_data.password)
        return None

    async def create_admin_on_start(self, login: str, password: str) -> Optional[Admin]:
        if await self.app.database.admin_empty:

            admin = await self.app.database.create_new_admin(login=login, password=password)

            # inner log for creation
            self.logger.info(f"ADMIN added: "
                             f"{admin.id}, {admin.login}, {admin.password},"
                             f"TIMESTAMP: {datetime.now()}")

            return Admin(id=1, login=login, password=password)
        self.logger.info(f"ADMIN ALREADY EXISTS: "
                         f"TIMESTAMP: {datetime.now()}")

    async def create_admin(self, login: str, password: str) -> Optional[Admin]:
        """creates the admin account"""
        admin_from_db = await self.app.database.create_new_admin(login=login, password=password)
        self.logger.info(f"NEW PROVISOR added: "
                         f"{admin_from_db.id}, {admin_from_db.login}, {admin_from_db.password},"
                         f"TIMESTAMP: {datetime.now()}")
        return Admin(id=admin_from_db.id, login=admin_from_db.login)

    async def add_categories(self, category_set: list[dict]) -> List[Category]:
        result = []
        for item in category_set:
            title = item["title"]
            item_ = await self.app.database.add_new_category(title=title)
            # try:
            #
            # except:
            #     item_ = await self.app.database.add_new_category(title=str(title + "_"))
            result.append(Category(id=item_.id, title=item_.title))

            self.logger.info(f"NEW CATEGORY added: "
                             f"{item_.id}, {item_.title},"
                             f"TIMESTAMP: {datetime.now()}")
        return result

    async def add_medicine_set(self, medicine_set: list[dict]) -> List[Medicine]:
        result = []
        for item in medicine_set:
            vendor_code = str(item["vendor_code"])
            category_title = item["category_title"]
            title = item["title"]
            manufacturer = item["manufacturer"]
            trade_price = item["trade_price"]
            amount = item["amount"]
            valid_until = item["valid_until"]
            try:
                item_ = await self.app.database.add_new_medicine(vendor_code, category_title, title,
                                                                manufacturer, trade_price, amount)
            except:
                category = await self.app.database.add_new_category(category_title)
                item_ = await self.app.database.add_new_medicine(vendor_code, category_title, title,
                                                                 manufacturer, trade_price, amount)
            result.append(Medicine(id=item_.id, vendor_code=item_.vendor_code,
                                   category_title=item_.category_title, title=item_.title,
                                   manufacturer=item_.manufacturer, price=item_.price, amount=item_.amount))

            self.logger.info(f"NEW MEDICINE added: "
                             f"id {item_.id}, vendor code {item_.vendor_code}, category {item_.category_title}, "
                             f" title {item_.title}, made by {item_.manufacturer}, "
                             f"trade price {item_.price}, amount {item_.amount} "
                             f"TIMESTAMP: {datetime.now()}")

        return result

    async def close_online_order(self, order_no: str, promo_rating_score: int) -> Revenue:
        """execute the online order when client already payed"""

        revenue, client = await self.app.database.close_online_order(order_no=order_no,
                                                                     promo_rating_score=promo_rating_score)

        return Revenue(order_no=revenue.order_no, sum=revenue.sum)

    async def execute_offline_order(self):
        ...

    def send_medicine_list_for_order(self, results: List[Optional[MedicineInfoForOrder]]
                                     ) -> List[Medicine]:
        result = [
            Medicine(id=item.medicine_info[0].id, vendor_code=item.medicine_info[0].vendor_code,
                     category_title=item.medicine_info[0].category_title,
                     title=item.medicine_info[0].title, manufacturer=item.medicine_info[0].manufacturer,
                     price=item.price_booked, amount=item.amount_booked)
            for item in results
        ]
        # print(result)
        return result

    async def find_and_view_order_by_no(self, order_no) -> Optional[ClientOrder]:
        order, medicine = await self.app.database.search_online_order(order_no=order_no)
        if not order:
            return None
        client_data = await self.app.database.search_client_by_id(order.client_id)
        return ClientOrder(
            id=order.id,
            client=Client(id=client_data.id, name=client_data.name,
                          phone=client_data.phone, email=client_data.email, rating=client_data.rating),
            medicine=self.send_medicine_list_for_order(results=medicine),
            order_no=order.order_no,
            status=order.status,
            total_price=order.total_price,
            valid_until=order.valid_until
        )
