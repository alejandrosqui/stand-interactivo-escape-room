import os
import tempfile
from pathlib import Path

_directorio_test = tempfile.TemporaryDirectory(prefix="stand_interactivo_pytest_")
TEST_DATABASE_PATH = (Path(_directorio_test.name) / "test_stand.db").resolve()
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DATABASE_PATH.as_posix()}"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, DEVELOPMENT_DATABASE_PATH, engine
from app.main import app


def verificar_base_aislada():
    ruta_engine = Path(engine.url.database or "").resolve()
    if ruta_engine != TEST_DATABASE_PATH:
        raise RuntimeError(f"La base de test no es la temporal esperada: {ruta_engine}")
    if ruta_engine == DEVELOPMENT_DATABASE_PATH or ruta_engine.name == "stand_interactivo.db":
        raise RuntimeError("Se bloqueó una operación destructiva sobre la base de desarrollo")


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    _directorio_test.cleanup()


@pytest.fixture(autouse=True)
def base_limpia():
    verificar_base_aislada()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    verificar_base_aislada()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

