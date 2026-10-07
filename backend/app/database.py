import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT_DATABASE_PATH = (PROJECT_ROOT / "stand_interactivo.db").resolve()
DEFAULT_DATABASE_URL = f"sqlite+pysqlite:///{DEVELOPMENT_DATABASE_PATH.as_posix()}"


def normalizar_database_url(valor: str) -> URL:
    url = make_url(valor)
    if url.get_backend_name() != "sqlite" or not url.database or url.database == ":memory:":
        return url

    ruta = Path(url.database)
    if not ruta.is_absolute():
        ruta = PROJECT_ROOT / ruta
    return url.set(database=str(ruta.resolve()))


DATABASE_URL = normalizar_database_url(os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))

if os.getenv("APP_ENV") == "test":
    if DATABASE_URL.get_backend_name() != "sqlite" or not DATABASE_URL.database:
        raise RuntimeError("Los tests deben usar una base SQLite aislada")
    ruta_test = Path(DATABASE_URL.database).resolve()
    if ruta_test == DEVELOPMENT_DATABASE_PATH or ruta_test.name == "stand_interactivo.db":
        raise RuntimeError("Pytest no puede usar la base de desarrollo stand_interactivo.db")

engine_options: dict[str, object] = {"pool_pre_ping": True}
if DATABASE_URL.get_backend_name() == "sqlite":
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

