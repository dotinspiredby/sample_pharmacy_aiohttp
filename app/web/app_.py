from typing import Optional
from aiohttp.web import Application as Aio_app
from aiohttp.web import Request as Aio_request
from aiohttp.web import View as Aio_view

from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from .config import Config
from .config import setup_config
from .logger import setup_logging
from .middlewares import setup_middlewares
from .routes import setup_routes
from ..admin.models import Admin
from ..pharmacy.models import Client
from ..store import setup_store, Store, Database


class Application(Aio_app):
    config: Optional[Config] = None
    store: Optional[Store] = None
    database: Optional[Database] = None


class Request(Aio_request):
    admin: Optional[Admin] = None
    client: Optional[Client] = None

    @property
    def app(self) -> Application:
        return super().app()


class View(Aio_view):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


def setup_app(config_path: str) -> Application:
    app = Application()
    setup_config(app=app, config_path=config_path)
    setup_logging(app)
    setup_store(app)
    session_setup(app, EncryptedCookieStorage(app.config.session.key))
    setup_routes(app)
    setup_aiohttp_apispec(
        app=app,
        title="Sample Pharmacy Booking System",
        url="/docs/json",
        swagger_path="/docs"
    )
    setup_middlewares(app)

    return app
