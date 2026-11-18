import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / 'reunify_demo.sqlite3'
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH.as_posix()}')


def make_engine(url: str, enforce_foreign_keys: bool = True):
    engine = create_engine(url, connect_args={'check_same_thread': False} if url.startswith('sqlite') else {})
    if engine.dialect.name == 'sqlite' and enforce_foreign_keys:
        # Runtime connections enforce foreign keys. Alembic batch migrations opt
        # out (enforce_foreign_keys=False) so SQLite table rebuilds can drop and
        # recreate referenced tables without tripping constraints on existing rows.
        @event.listens_for(engine, 'connect')
        def enable_foreign_keys(connection, _):
            connection.execute('PRAGMA foreign_keys=ON')
    return engine


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass
