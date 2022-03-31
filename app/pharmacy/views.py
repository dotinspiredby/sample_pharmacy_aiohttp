from aiohttp_session import new_session, get_session

from app.web.app_ import View
from app.web.utils import json_response
from app.web.mixins import AuthRequiredMixinClient

from aiohttp_apispec import request_schema, response_schema, querystring_schema

from .models import Client
from .schemes import ClientRegistrationSchema, ClientSchema, \
    MedicineByCategory, TitleSchema, MedicineSetSchema, OrderNoSchema, MedicineIdSchema, OrderFullSchema, \
    MedicineSchema, CategorySchemeTwo, MultipleCategoriesSchema

from aiohttp.web_exceptions import HTTPConflict, HTTPForbidden, HTTPNotFound, HTTPBadRequest, HTTPNotImplemented


class MakeNewClientView(View):
    @request_schema(ClientRegistrationSchema)
    @response_schema(ClientRegistrationSchema)
    async def post(self):
        name, phone, email, password = self.data["name"], self.data["phone"], self.data["email"], self.data["password"]

        clients = await self.store.pharmacy.find_by_credentials(phone=phone, email=email)
        if clients:
            raise HTTPConflict(reason="Phone or email already used")

        created_client = await self.store.pharmacy.create_new_account(
            name=name, password=password, phone=phone, email=email)

        return json_response(data=ClientRegistrationSchema().dump(created_client))

    @request_schema(ClientRegistrationSchema)
    async def get(self):
        raise HTTPNotImplemented


class ClientLoginView(View):
    @request_schema(ClientSchema)
    @response_schema(ClientRegistrationSchema)
    async def post(self):
        # phone, email, password = self.data["phone"], self.data["email"],
        password = self.data["password"]
        client = await self.store.pharmacy.find_by_email_and_phone(phone=self.data.get("phone"),
                                                                   email=self.data.get("email"))

        if not client or not client.is_password_valid(password):
            raise HTTPForbidden

        session = await new_session(self.request)
        client_data = ClientRegistrationSchema().dump(client)
        session["client"] = client_data
        session["cart"] = []

        return json_response(data=client_data)

    @request_schema(ClientSchema)
    async def get(self):
        raise HTTPNotImplemented


class EditClientView(AuthRequiredMixinClient, View):
    @request_schema(ClientRegistrationSchema)
    @response_schema(ClientRegistrationSchema)
    async def patch(self):
        client_id = self.request.client.id
        # TODO: можно прикрутить значения из куки, на которых замены не было

        name, phone, email, password = self.data.get("name"), self.data.get("phone"), \
                                       self.data.get("email"), self.data.get("password")

        client_dataclass = Client(id=int(client_id), name=name, phone=phone,
                                  email=email, password=password)
        new_data = await self.store.pharmacy.edit_client_data(client_dataclass)

        if not new_data:
            raise HTTPConflict(reason="Phone or email already used")

        return json_response(data=ClientRegistrationSchema().dump(new_data))


class ListItemsView(View):
    @request_schema(CategorySchemeTwo)
    @querystring_schema(CategorySchemeTwo)
    @response_schema(MultipleCategoriesSchema)
    async def get(self):
        data = await self.store.pharmacy.browse_categories(self.data.get("title"))

        if not data:
            raise HTTPNotFound(reason="Category not found!")

        return json_response(
            data=MultipleCategoriesSchema().dump(
                {
                    "categories": data,
                }
            )
        )


class FindMedicineByTitle(View):
    @request_schema(TitleSchema)
    @querystring_schema(TitleSchema)
    @response_schema(MedicineSetSchema)
    async def get(self):
        # title = self.data["title"]

        data = await self.store.pharmacy.search_by_title(self.data.get("title"))

        if not data:
            raise HTTPNotFound(reason="Title not found!")

        return json_response(data=MedicineSetSchema().dump(
            {
                "medicine": data,
            }
        )
        )


class AddToCartView(AuthRequiredMixinClient, View):
    @querystring_schema(MedicineIdSchema)
    @request_schema(MedicineIdSchema)
    @response_schema(MedicineSetSchema)
    async def post(self):
        med_id = self.data.get("medicine_id")
        amount = self.data.get("amount")
        existing_amount = self.request.client.find_existing_item_amount_by_id(med_id)
        data = await self.store.pharmacy.search_by_id_and_amount(id_=med_id,
                                                                 amount_requested=amount,
                                                                 amount_already=existing_amount)
        if not data:
            raise HTTPNotFound(reason="Medicine not found or out of stock!")

        session = await get_session(self.request)

        self.request.client.add_item_to_request_cart(MedicineSchema().dump(data))

        session["cart"] = self.request.client.cart
        return json_response(data=self.request.client.cart)


class DeleteFromCartView(AuthRequiredMixinClient, View):
    @querystring_schema(MedicineIdSchema)
    @request_schema(MedicineIdSchema)
    @response_schema(MedicineSetSchema)
    async def patch(self):
        med_cart_id = self.data.get("medicine_id")

        self.request.client.delete_item_from_cart(med_cart_id)

        session = await get_session(self.request)
        # try:
        #     session["cart"].pop(med_cart_id)
        # except ValueError:
        #     ...

        session["cart"] = self.request.client.cart

        return json_response(data=self.request.client.cart)

    @querystring_schema(MedicineIdSchema)
    @request_schema(MedicineIdSchema)
    async def post(self):
        raise HTTPNotImplemented


class MakeOnlineOrderView(AuthRequiredMixinClient, View):
    @response_schema(OrderFullSchema)
    async def post(self):

        client = self.request.client.id
        cart = self.request.client.cart

        if len(cart) == 0:
            raise HTTPBadRequest(reason="The cart is empty")

        cart_check = await self.store.pharmacy.check_amount_for_cart_before_order(cart)
        if not cart_check:
            raise HTTPBadRequest(reason="Sorry, some items became out of stock.")

        order = await self.store.pharmacy.make_online_order(client, cart)

        return json_response(data=OrderFullSchema().dump(order))

    async def get(self):
        raise HTTPNotImplemented


class CancelOnlineOrderView(AuthRequiredMixinClient, View):
    @request_schema(OrderNoSchema)
    @querystring_schema(OrderNoSchema)
    async def post(self):
        order_no = self.data.get("order_no")

        data = await self.store.pharmacy.cancel_online_order(order_no)

        if not data:
            raise HTTPNotFound(reason="Order not found!")

        return json_response(data=data)

    @querystring_schema(OrderNoSchema)
    @request_schema(OrderNoSchema)
    async def get(self):
        raise HTTPNotImplemented
