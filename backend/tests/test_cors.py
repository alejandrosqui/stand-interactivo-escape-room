import pytest


@pytest.mark.parametrize(
    "origen",
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
    ],
)
def test_preflight_cors_acepta_origenes_locales_de_vite(client, origen):
    respuesta = client.options(
        "/api/experiencias",
        headers={
            "Origin": origen,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == origen


def test_cors_rechaza_origen_no_local(client):
    respuesta = client.options(
        "/api/experiencias",
        headers={
            "Origin": "https://sitio-no-autorizado.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert respuesta.status_code == 400
