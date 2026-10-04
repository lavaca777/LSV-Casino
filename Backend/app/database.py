from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia FastAPI que provee una sesión de BD por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea todas las tablas definidas en los modelos (dev)."""
    from app import models  # noqa: F401  importa los modelos para registrarlos en Base

    Base.metadata.create_all(bind=engine)
    _run_light_migrations()


def _run_light_migrations() -> None:
    """Añade columnas nuevas a tablas ya existentes.

    `create_all` no modifica tablas que ya existen, y el proyecto no usa
    migraciones formales (Alembic). Estas sentencias idempotentes mantienen
    la BD de desarrollo al día tanto para devs nuevos como existentes.
    """
    migrations = [
        "ALTER TABLE game_sessions ADD COLUMN IF NOT EXISTS balance_after NUMERIC(12, 2) NOT NULL DEFAULT 0",
    ]
    with engine.begin() as conn:
        for statement in migrations:
            conn.execute(text(statement))
