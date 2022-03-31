from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
from dotenv import load_dotenv
import yaml
from app.web.config import Config, \
    SessionConfig, AdminConfig, DatabaseConfig

from app.store.database.gino_ import db
# print(os.path.abspath("config.yml"))
config_path = os.path.abspath("config.yml")

with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)
    app_config = Config(
        session=SessionConfig(
            key=cfg["session"]["key"],
        ),
        admin=AdminConfig(
            login=cfg["admin"]["login"],
            password=cfg["admin"]["password"],
        ),
        # database=DatabaseConfig(**raw_config["database"]),
        database=DatabaseConfig(
            host=cfg["database"]["host"],
            port=cfg["database"]["port"],
            user=cfg["database"]["user"],
            password=cfg["database"]["password"],
            database=cfg["database"]["database"]
        )
    )


def set_sql_alchemy_url(user: str, password: str, host: str, port: int, db: str):
    config.set_main_option("sqlalchemy.url", f"postgres://{user}:{password}@{host}:{port}/{db}")


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = db


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    set_sql_alchemy_url(app_config.database.user, app_config.database.password,
                        app_config.database.host, app_config.database.port,
                        app_config.database.database)
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    set_sql_alchemy_url(app_config.database.user, app_config.database.password,
                        app_config.database.host, app_config.database.port,
                        app_config.database.database)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
