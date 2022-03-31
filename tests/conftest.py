from .fixtures import *  # Do not remove this line!
import os
from unittest.mock import AsyncMock
import pytest
from aiohttp.test_utils import TestClient, loop_context

from app.store import Store
from app.web.app_ import setup_app
from app.web.config import Config
from app.store import Database
import sqlalchemy
import logging


@pytest.fixture(scope="session")
def loop():
    with loop_context() as _loop:
        yield _loop


@pytest.fixture(scope="session")
def server():
    app = setup_app(
        config_path=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "config.yml"
        )
    )
    app.on_startup.clear()
    app.on_shutdown.clear()

    app.database = Database(app)

    app.on_startup.append(app.database.connect)
    app.on_startup.append(app.store.admins.connect)
    app.on_shutdown.append(app.database.disconnect)
    app.on_shutdown.append(app.store.admins.disconnect)

    return app


@pytest.fixture
def store(server) -> Store:
    return server.store


@pytest.fixture(autouse=True, scope="function")
async def clear_db(server):
    yield
    db = server.database.db
    for table in db.sorted_tables:
        if table.name != "admins":
            await db.status(db.text(f"TRUNCATE {table.name} CASCADE"))
            try:
                row = await db.status(
                    db.text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1")
                )
            except Exception:
                pass


@pytest.fixture
def config(server) -> Config:
    return server.config


@pytest.fixture(autouse=True)
def cli(aiohttp_client, loop, server) -> TestClient:
    return loop.run_until_complete(aiohttp_client(server))


@pytest.fixture
async def authed_cli(cli, config) -> TestClient:
    await cli.post(
        "/admin_login",
        data={
            "login": config.admin.login,
            "password": config.admin.password,
        },
    )
    yield cli


@pytest.fixture
async def authed_cli_client1(cli, config, client_1, client_2) -> TestClient:
    await cli.post(
        "/login",
        data={
            "phone": client_1.phone,
            "password": "hellotest2"
        }
    )
    yield cli


@pytest.fixture
async def authed_cli_client2(cli, config, client_1, client_2) -> TestClient:
    await cli.post(
        "/login",
        data={
            "email": client_2.email,
            "password": "hellotest2"
        }
    )
    yield cli




