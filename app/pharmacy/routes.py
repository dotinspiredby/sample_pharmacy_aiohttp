import typing

if typing.TYPE_CHECKING:
    from app.web.app_ import Application

from app.pharmacy.views import ListItemsView, MakeOnlineOrderView, \
    CancelOnlineOrderView, MakeNewClientView, EditClientView, \
    AddToCartView, DeleteFromCartView, FindMedicineByTitle, ClientLoginView


def setup_routes(app: "Application"):
    app.router.add_view("/registration", MakeNewClientView)  # ok
    app.router.add_view("/login", ClientLoginView)  # ok
    app.router.add_view("/edit_client", EditClientView)  # ok
    app.router.add_view("/list_items", ListItemsView)  # ok
    app.router.add_view("/search_by_title", FindMedicineByTitle)  # ok
    app.router.add_view("/make_order", MakeOnlineOrderView)
    app.router.add_view("/cancel_order", CancelOnlineOrderView)
    app.router.add_view("/add_to_cart", AddToCartView)  # ok
    app.router.add_view("/delete_from_cart", DeleteFromCartView)
