import typing

from app.store.database.database import Database

if typing.TYPE_CHECKING:
    from app.web.app_ import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.admin.accessor import AdminAccessor
        from app.store.pharmacy.accessor import PharmacyAccessor

        self.pharmacy = PharmacyAccessor(app)
        self.admins = AdminAccessor(app)


def setup_store(app: "Application"):

    app.database = Database(app)
    app.store = Store(app)

    # app.on_startup.append(app.database.connect)
    # app.on_startup.append(app.store.admins.connect)
    # app.on_shutdown.append(app.database.disconnect)
    # app.on_shutdown.append(app.store.admins.disconnect)


