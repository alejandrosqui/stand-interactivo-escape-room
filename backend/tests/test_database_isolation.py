from pathlib import Path

from app.database import DEVELOPMENT_DATABASE_PATH, engine
from conftest import TEST_DATABASE_PATH


def test_pytest_usa_base_temporal_aislada():
    ruta_engine = Path(engine.url.database or "").resolve()

    assert ruta_engine == TEST_DATABASE_PATH
    assert ruta_engine != DEVELOPMENT_DATABASE_PATH
    assert ruta_engine.name == "test_stand.db"
    assert ruta_engine.parent != DEVELOPMENT_DATABASE_PATH.parent
