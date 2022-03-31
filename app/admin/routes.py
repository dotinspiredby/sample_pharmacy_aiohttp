import typing
if typing.TYPE_CHECKING:
    from app.web.app_ import Application

from app.admin.views import AdminAddNewItems, \
    AdminExecuteOnlineOrder, AdminExecuteOfflineOrder, \
    AdminAddNewCategory, AdminViewOnlineOrder


def setup_routes(app: "Application"):
    from app.admin.views import AdminLoginView

    app.router.add_view("/admin_login", AdminLoginView)  # ok
    app.router.add_view("/admin_add_new", AdminAddNewItems)  # ok
    app.router.add_view("/admin_add_category", AdminAddNewCategory)  # ok
    app.router.add_view("/admin_view_client_order", AdminViewOnlineOrder)  # ok
    app.router.add_view("/admin_execute_online_order", AdminExecuteOnlineOrder)  # ok
    app.router.add_view("/admin_execute_offline_order", AdminExecuteOfflineOrder)
