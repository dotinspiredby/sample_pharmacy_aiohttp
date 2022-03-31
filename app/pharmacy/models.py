from dataclasses import dataclass, field
from typing import Optional
from hashlib import sha256
from typing import List

from app.store.database.gino_ import db
from datetime import date

@dataclass
class Medicine:
    id: int
    vendor_code: str
    category_title: str
    title: str
    price: float
    manufacturer: Optional[str] = None
    amount: Optional[int] = None


@dataclass
class Category:
    id: int
    title: str
    medicine: Optional[list[Medicine]] = None


@dataclass
class Client:
    id: int
    name: str
    rating: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    cart: list = field(default_factory=list)

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]):
        return cls(id=int(session["client"]["id"]),
                   name=session["client"]["name"],
                   rating=session["client"]["rating"],
                   phone=session["client"]["phone"],
                   email=session["client"]["email"],
                   cart=session["cart"]
                   )

    def find_existing_item_amount_by_id(self, id_: int) -> int:
        for each in self.cart:
            if each["id"] == id_:
                return each["amount"]
        return 0

    def add_item_to_request_cart(self, item: dict):
        for each in self.cart:
            if each["id"] == item["id"]:
                each["amount"] = item["amount"]
                return
        self.cart.append(item)

    def delete_item_from_cart(self, item_id: int):
        for each in self.cart:
            if each["id"] == item_id:
                self.cart.remove(each)
                break

    def add_to_cart(self, session: Optional[dict]):
        if len(session["cart"]) != 0:
            self.cart.append(session["cart"])


@dataclass
class ClientOrder:
    id: int
    client: Client
    medicine: list[Medicine]
    order_no: str
    total_price: float
    valid_until: date
    status: Optional[str] = None


@dataclass
class Revenue:
    order_no: str
    sum: float


class CategoryModel(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(), nullable=False, unique=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._medicine_prods: List["MedicineModel"] = []

    @property
    def medicine(self) -> List["MedicineModel"]:
        return self._medicine_prods

    def add_item(self, item: Optional["MedicineModel"]):
        if item:
            self._medicine_prods.append(item)


class MedicineModel(db.Model):
    __tablename__ = "medicine"

    id = db.Column(db.Integer(), primary_key=True)
    vendor_code = db.Column(db.String(), nullable=False)
    category_title = db.Column(db.ForeignKey("categories.title", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(), nullable=False, unique=True)
    manufacturer = db.Column(db.String())
    trade_price = db.Column(db.Float(), nullable=False)
    amount = db.Column(db.Integer(), nullable=False)

    price = db.Column(db.Float(), nullable=True)
    price_offline = db.Column(db.Float(), nullable=True)


class ClientModel(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer())


class OrderModel(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer(), primary_key=True)
    client_id = db.Column(db.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    # medicine: list[Medicine]
    order_no = db.Column(db.String(), nullable=False, unique=True)
    status = db.Column(db.String(), nullable=False)
    total_price = db.Column(db.Float())
    valid_until = db.Column(db.DateTime())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._medicine: List[MedicineModel] = []
        self._medicine_info: List["MedicineInfoForOrder"] = []
        self._total_price: int = 0

    @property
    def medicine(self) -> List["MedicineInfoForOrder"]:
        return self._medicine

    @property
    def medicine_info(self) -> List[MedicineModel]:
        return self._medicine_info

    @property
    def price(self) -> int:
        return self._total_price

    def add_to_cart(self, item: Optional["MedicineInfoForOrder"]):
        if item:
            self._medicine.append(item)
            self._total_price += item.amount_booked*item.price_booked

    def add_to_cart_info(self, item: Optional["MedicineModel"]):
        if item:
            self._medicine_info.append(item)


class MedicineInfoForOrder(db.Model):
    __tablename__ = "booked_medicine"

    id = db.Column(db.Integer(), primary_key=True)
    order_no = db.Column(db.ForeignKey("orders.order_no", ondelete="CASCADE"), nullable=False)
    medicine_id = db.Column(db.ForeignKey("medicine.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.ForeignKey("medicine.title", ondelete="CASCADE"), nullable=False)
    amount_booked = db.Column(db.Integer(), nullable=False)
    price_booked = db.Column(db.Float(), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._medicine_info: List[MedicineModel] = []

    @property
    def medicine_info(self) -> List[MedicineModel]:
        return self._medicine_info

    def add_item(self, item: Optional[MedicineModel]):
        if item:
            self._medicine_info.append(item)


class RevenueModel(db.Model):
    __tablename__ = "revenue"

    id = db.Column(db.Integer(), primary_key=True)
    order_no = db.Column(db.ForeignKey("orders.order_no", ondelete="CASCADE"), nullable=False)
    sum = db.Column(db.Float())


