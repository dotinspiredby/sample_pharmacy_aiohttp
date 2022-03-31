from dataclasses import dataclass
import yaml

import typing
if typing.TYPE_CHECKING:
    from app.web.app_ import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    login: str
    password: str


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"


@dataclass
class Config:
    session: SessionConfig = None
    admin: AdminConfig = None
    database: DatabaseConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as file:
        raw_config = yaml.safe_load(file)

        app.config = Config(
            session=SessionConfig(
                key=raw_config["session"]["key"]),
            admin=AdminConfig(
                login=raw_config["admin"]["login"],
                password=raw_config["admin"]["password"]
            ),
            database=DatabaseConfig(
                host=raw_config["database"]["host"],
                port=raw_config["database"]["port"],
                user=raw_config["database"]["user"],
                password=raw_config["database"]["password"],
                database=raw_config["database"]["database"]
            )
        )
