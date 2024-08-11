import os
from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Load environment variables from .env file
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Construct the database URL using environment variables and URL object
database_url = f"mysql+mysqldb://{os.getenv("MYSQL_USER")}:{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}/{os.getenv("MYSQL_DB")}"
config.set_main_option("sqlalchemy.url", str(database_url))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from app.models import (
    user, role, permission, role_permission,
    direct_chat, group_chat, group_user_role,
    token_blacklist, post
)

# Combine all SQLAlchemy model metadata
target_metadata = [
    user.Base.metadata,
    role.Base.metadata,
    permission.Base.metadata,
    role_permission.Base.metadata,
    direct_chat.Base.metadata,
    group_chat.Base.metadata,
    group_user_role.Base.metadata,
    token_blacklist.Base.metadata,
    post.Base.metadata,
]

# # Setup to collect metadata from all SQLAlchemy models
# def get_target_metadata():
#     """Function to collect all metadata from individual SQLAlchemy model files."""
#     metadata = []
#     for meta in target_metadata:
#         metadata.append(meta)
#     return metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
