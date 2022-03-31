import typing
from logging import getLogger

from typing import Optional, List

from app.pharmacy.models import MedicineInfoForOrder, Medicine, MedicineModel

if typing.TYPE_CHECKING:
    from app.web.app_ import Application

from datetime import datetime


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self.logger = getLogger("Base Accessor")
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    def inform_about_connection(self):
        self.logger.info(f"Connected to GINO, TIMESTAMP: {datetime.now()}, gino init {self.app.database.db}")

    def inform_about_disconnection(self):
        self.logger.info(f"Disconnected from GINO: {datetime.now()}, {self.app.database.db}")

    async def connect(self, app: "Application"):
        if self.app.database.db is None:
            await self.app.database.connect()
        self.inform_about_connection()
        return

    async def disconnect(self, app: "Application"):
        if self.app.database.db is not None:
            await self.app.database.disconnect()
        self.inform_about_disconnection()
        return

    def send_medicine_list(self, results: typing.List[Optional[MedicineModel]]) -> typing.List[Medicine]:
        return [
            Medicine(id=item.id, vendor_code=item.vendor_code,
                     category_title=item.category_title, title=item.title,
                     manufacturer=item.manufacturer, price=item.price, amount=item.amount)
            for item in results
        ]
