from typing import Optional
from logging import getLogger
from app.base.base_accessor import BaseAccessor
from app.pharmacy.models import *

from typing import List
from datetime import datetime
import typing

if typing.TYPE_CHECKING:
    from app.web.app_ import Application
    from app.pharmacy.models import Client

from app.store.database.gino_ import db


class PharmacyAccessor(BaseAccessor):

    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.logger = getLogger("Pharmacy Accessor")

    async def connect(self, app: "Application"):
        await super().connect(app)

    async def create_new_account(self, name: str,
                                 password: str,
                                 phone: str,
                                 email: str
                                 ) -> Client:

        client_from_db = await self.app.database.create_new_client(name, password, phone, email)
        self.logger.info(f"NEW CLIENT added: "
                         f"{client_from_db.id}, {client_from_db.name}, "
                         f"{client_from_db.email}, {client_from_db.phone}"
                         f"TIMESTAMP: {datetime.now()}")
        return Client(id=client_from_db.id, name=client_from_db.name,  password=client_from_db.password,
                      phone=client_from_db.phone, email=client_from_db.email, rating=client_from_db.rating)

    async def find_by_email_and_phone(self, phone: str, email: str) -> Optional[Client]:
        client_from_db = await self.app.database.search_client_by_phone_or_email_(phone=phone, email=email)
        # print(client_from_db.id, client_from_db.name)
        if client_from_db:
            return Client(id=client_from_db.id, name=client_from_db.name, password=client_from_db.password,
                          phone=client_from_db.phone, email=client_from_db.email, rating=client_from_db.rating)
        return None

    async def find_by_credentials(self, phone: str, email: str) -> Optional[List[Client]]:
        existing_clients = await self.app.database.search_client_by_phone_or_email(phone, email)
        if existing_clients:
            return [Client(id=client_from_db.id, name=client_from_db.name, password=client_from_db.password,
                           phone=client_from_db.phone, email=client_from_db.email, rating=client_from_db.rating)
                    for client_from_db in existing_clients]
        return None

    async def edit_client_data(self, client: Client) -> Optional[Client]:
        for_repeating_credentials = await self.find_by_credentials(phone=client.phone, email=client.email)
        if for_repeating_credentials:
            """ на случай, если имеил и телефон тот же только у самого пользователя"""
            for each in for_repeating_credentials:
                if each.id != client.id:
                    return None
        updated = await self.app.database.patch_client(client)
        # TODO: DATACLASS!!!
        # return updated
        return Client(id=updated.id, name=updated.name, password=updated.password,
                      phone=updated.phone, email=updated.email, rating=updated.rating)

    def send_medicine_list(self, results: List[Optional[MedicineModel]]) -> List[Medicine]:
        return [
            Medicine(id=item.id, vendor_code=item.vendor_code,
                     category_title=item.category_title, title=item.title,
                     manufacturer=item.manufacturer, price=item.price, amount=item.amount)
            for item in results
        ]

    async def browse_categories(self, category: Optional[str] = None):
        if category:

            category_exists = await self.app.database.check_category(category)
            if not category_exists:
                return None
        result = await self.app.database.browse_categories(category)
        return [
            Category(id=item.id, title=item.title, medicine=[
                Medicine(id=med.id, vendor_code=med.vendor_code,
                         category_title=med.category_title, title=med.title,
                         price=med.price, manufacturer=med.manufacturer, amount=med.amount) for med in item.medicine
            ])
            for item in result
        ]

    # async def search_medicine(self, category: Optional[str] = None) -> List[Medicine]:
    #     results = await self.app.database.browse_categories(category)
    #     return self.send_medicine_list(results)

    async def search_by_title(self, title: str) -> Optional[List[Medicine]]:
        results = await self.app.database.search_medicine_by_title(title)
        if results:
            return self.send_medicine_list(results)
        return None

    async def search_by_id_and_amount(self, id_: int, amount_requested: int, amount_already: int) -> Optional[Medicine]:
        result = await self.app.database.search_medicine_by_id_and_amount(id_, amount=amount_already + amount_requested)
        if result:
            return Medicine(id=result.id, vendor_code=result.vendor_code,
                            category_title=result.category_title, title=result.title,
                            manufacturer=result.manufacturer, price=result.price,
                            amount=amount_requested
                            )
        return None

    async def check_amount_for_cart_before_order(self, cart: List[dict]) -> bool:
        for medicine in cart:
            medicine_from_db = await self.app.database.search_medicine_by_id_and_amount(id_=medicine["id"],
                                                                                        amount=medicine["amount"])
            if not medicine_from_db:
                return False
        return True

    def send_medicine_list_for_order(self, results: List[Optional[MedicineInfoForOrder]],
                                     results_info: List[Optional[MedicineModel]]) -> List[Medicine]:
        return [
            Medicine(id=results_info[i].id, vendor_code=results_info[i].vendor_code,
                     category_title=results_info[i].category_title,
                     title=results_info[i].title, manufacturer=results_info[i].manufacturer,
                     price=results[i].price_booked, amount=results[i].amount_booked)
            for i in range(len(results))
        ]

    async def make_online_order(self, client_id: int, cart: list[dict]):
        client_data = await self.app.database.search_client_by_id(client_id)
        order = await self.app.database.make_online_order(client_id, cart)

        self.logger.info(f"NEW ORDER added: "
                         f"order number {order.id}, "
                         f"client id {order.client_id}, "
                         f"total price {order.total_price}, "
                         f"valid till {order.valid_until} "
                         # f"items {self.send_medicine_list_for_order(
                         # results_info=order.medicine_info, results=order.medicine)}"
                         f"TIMESTAMP: {datetime.now()}")

        return ClientOrder(
            id=order.id,
            client=Client(id=client_data.id, name=client_data.name,
                          phone=client_data.phone, email=client_data.email, rating=client_data.rating),
            medicine=self.send_medicine_list_for_order(results_info=order.medicine_info, results=order.medicine),
            order_no=order.order_no,
            status=order.status,
            total_price=order.total_price,
            valid_until=order.valid_until
        )

    async def cancel_online_order(self, order_no: str):
        order = await self.app.database.find_order_by_order_no(order_no)
        if order:
            await self.app.database.cancel_order(order_no)
            self.logger.info(f"ORDER canceled: "
                             f"order number {order_no}, "
                             f"TIMESTAMP: {datetime.now()}")
            return f"ORDER canceled: order number {order_no}"
        return None
