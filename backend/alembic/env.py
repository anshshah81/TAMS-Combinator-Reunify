from alembic import context
from app.db import Base, DATABASE_URL, make_engine
from app import models  # noqa: F401: register tables

config = context.config
target_metadata = Base.metadata
url = config.attributes.get('database_url', DATABASE_URL)

if context.is_offline_mode():
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True,
                      render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = make_engine(url, enforce_foreign_keys=False)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata,
                          compare_type=True, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
