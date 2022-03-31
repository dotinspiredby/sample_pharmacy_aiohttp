from aiohttp.web_exceptions import HTTPNotImplemented, HTTPNotFound

from app.web.app_ import View
from app.web.utils import json_response
from aiohttp_apispec import request_schema, response_schema, querystring_schema

from app.admin.schemes import AdminSchema, MedicineSetSchema, MedicineSchema, \
    CategoryScheme,  CategorySetScheme, RevenueSchema
from app.pharmacy.schemes import OrderNoSchema, OrderFullSchema

from app.admin.models import Admin
from app.web.mixins import AuthRequiredMixin
from aiohttp.web import HTTPForbidden, HTTPBadRequest

from aiohttp_session import new_session


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):

        login, password = self.data["login"], self.data["password"]
        admin = await self.store.admins.get_by_login(login)

        if not admin or not admin.is_password_valid(password):
            raise HTTPForbidden

        session = await new_session(self.request)
        created_admin = AdminSchema().dump(admin)
        session["admin"] = created_admin
        session["offline_cart"] = []

        return json_response(data=created_admin)

    @request_schema(AdminSchema)
    async def get(self):
        raise HTTPNotImplemented

    
class AdminAddNewCategory(AuthRequiredMixin, View):
    @request_schema(CategorySetScheme)
    @response_schema(CategorySetScheme, 200)
    async def post(self):
        category_set = self.data["categories"]

        list_of_added = await self.store.admins.add_categories(category_set)

        return json_response(data=[CategoryScheme().dump(cat) for cat in list_of_added])


class AdminAddNewItems(AuthRequiredMixin, View):
    @request_schema(MedicineSetSchema)
    @response_schema(MedicineSetSchema)
    async def post(self):
        medicine_set = self.data["medicine"]
        list_of_added = await self.store.admins.add_medicine_set(medicine_set)
        return json_response(data=[MedicineSchema().dump(med) for med in list_of_added])


class AdminViewOnlineOrder(AuthRequiredMixin, View):
    @request_schema(OrderNoSchema)
    @querystring_schema(OrderNoSchema)
    @response_schema(OrderFullSchema)
    async def get(self):
        order_no = self.data.get("order_no")
        order = await self.store.admins.find_and_view_order_by_no(order_no)
        if not order:
            raise HTTPNotFound
        return json_response(data=OrderFullSchema().dump(order))

    @request_schema(OrderNoSchema)
    @querystring_schema(OrderNoSchema)
    async def post(self):
        raise HTTPNotImplemented


class AdminExecuteOnlineOrder(AuthRequiredMixin, View):
    @querystring_schema(OrderNoSchema)
    @request_schema(OrderNoSchema)
    async def get(self):
        order_no = self.data.get("order_no")
        promo_rating_score = self.data.get("promo_rating_score", 0)

        order = await self.store.admins.find_and_view_order_by_no(order_no)
        if not order:
            raise HTTPNotFound
        if order.client.rating < promo_rating_score:
            raise HTTPBadRequest(reason="Incorrect promo_rating_score amount")

        if promo_rating_score > order.total_price:
            promo_rating_score = order.total_price - 1

        receipt = await self.store.admins.close_online_order(order_no, promo_rating_score)
        return json_response(data={"order": OrderFullSchema().dump(order),
                                   "receipt": RevenueSchema().dump(receipt)})

    @querystring_schema(OrderNoSchema)
    @request_schema(OrderNoSchema)
    async def post(self):
        raise HTTPNotImplemented


class AdminExecuteOfflineOrder(View):
    ...


