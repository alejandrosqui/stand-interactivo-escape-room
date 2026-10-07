from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Partida


def crear_experiencia(client):
    respuesta = client.post(
        "/api/experiencias",
        json={
            "codigo": "ESCAPE2",
            "nombre": "Secuencia del stand",
            "descripcion": "Una secuencia física y digital para resolver.",
            "instrucciones": "Resolvé cada desafío antes de que termine el tiempo.",
            "mision_inicial": "Encontrá el primer código escondido.",
            "duracion_minutos": 3,
        },
    )
    assert respuesta.status_code == 201
    client.patch("/api/experiencias/1/estado", json={"activa": True})


def crear_desafio(client, orden, titulo, respuesta, tipo="texto"):
    resultado = client.post(
        "/api/experiencias/1/desafios",
        json={
            "orden": orden,
            "tipo": tipo,
            "titulo": titulo,
            "consigna": f"Resolvé {titulo}",
            "respuesta_correcta": respuesta,
            "pista": f"Pista para {titulo}",
            "puntos": orden * 100,
            "activo": True,
        },
    )
    assert resultado.status_code == 201
    return resultado.json()


def preparar_partida(client):
    crear_experiencia(client)
    primero = crear_desafio(client, 1, "Primer desafío", "PATAGONIA")
    segundo = crear_desafio(client, 2, "Segundo desafío", "QR-42", "qr")
    inicio = client.post("/api/publico/experiencias/ESCAPE2/partidas")
    assert inicio.status_code == 201
    return primero, segundo, inicio.json()


def afirmar_sin_solucion(datos):
    texto = str(datos).casefold()
    assert "respuesta_correcta" not in texto
    assert "patagonia" not in texto
    assert "qr-42" not in texto


def test_crear_y_ordenar_desafios(client):
    crear_experiencia(client)
    primero = crear_desafio(client, 2, "Uno", "A")
    segundo = crear_desafio(client, 1, "Dos", "B")

    ordenados = client.put(
        "/api/experiencias/1/desafios/orden",
        json={"ids": [primero["id"], segundo["id"]]},
    )

    assert ordenados.status_code == 200
    assert [item["orden"] for item in ordenados.json()] == [1, 2]
    assert [item["id"] for item in ordenados.json()] == [primero["id"], segundo["id"]]


def test_iniciar_partida_entrega_primer_desafio_sin_respuesta(client):
    primero, _, partida = preparar_partida(client)

    assert partida["estado"] == "en_curso"
    assert partida["desafio"]["id"] == primero["id"]
    assert partida["total_desafios"] == 2
    assert partida["segundos_restantes"] > 0
    afirmar_sin_solucion(partida)


def test_respuesta_incorrecta_no_avanza(client):
    primero, _, partida = preparar_partida(client)
    respuesta = client.post(
        f"/api/publico/partidas/{partida['token']}/respuestas",
        json={"respuesta": "incorrecta"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["desafio"]["id"] == primero["id"]
    assert respuesta.json()["puntos"] == 0
    assert "incorrecta" in respuesta.json()["feedback"].casefold()
    afirmar_sin_solucion(respuesta.json())


def test_respuesta_correcta_avanza_y_codigo_fisico_finaliza(client):
    _, segundo, partida = preparar_partida(client)
    elemento = client.post(
        "/api/experiencias/1/elementos",
        json={
            "nombre": "Placa QR",
            "codigo": "FISICO-99",
            "descripcion": "Placa ubicada en el stand.",
            "desafio_id": segundo["id"],
        },
    )
    assert elemento.status_code == 201

    avance = client.post(
        f"/api/publico/partidas/{partida['token']}/respuestas",
        json={"respuesta": "  patagonia  "},
    )
    assert avance.status_code == 200
    assert avance.json()["desafio"]["id"] == segundo["id"]
    assert avance.json()["puntos"] == 100

    final = client.post(
        f"/api/publico/partidas/{partida['token']}/respuestas",
        json={"respuesta": "fisico-99"},
    )
    assert final.status_code == 200
    assert final.json()["estado"] == "completada"
    assert final.json()["desafio"] is None
    assert final.json()["puntos"] == 300
    afirmar_sin_solucion(final.json())


def test_solicitar_pista_cuenta_una_vez(client):
    _, _, partida = preparar_partida(client)
    url = f"/api/publico/partidas/{partida['token']}/pista"

    primera = client.post(url)
    segunda = client.post(url)

    assert primera.status_code == 200
    assert primera.json()["pista"] == "Pista para Primer desafío"
    assert segunda.json()["pistas_utilizadas"] == 1
    afirmar_sin_solucion(primera.json())


def test_tiempo_agotado_impide_responder(client):
    _, _, partida = preparar_partida(client)
    with SessionLocal() as db:
        registro = db.scalar(select(Partida).where(Partida.token == partida["token"]))
        registro.iniciada_en = datetime.now(timezone.utc) - timedelta(minutes=4)
        db.commit()

    estado = client.get(f"/api/publico/partidas/{partida['token']}")
    respuesta = client.post(
        f"/api/publico/partidas/{partida['token']}/respuestas",
        json={"respuesta": "PATAGONIA"},
    )

    assert estado.status_code == 200
    assert estado.json()["estado"] == "tiempo_agotado"
    assert estado.json()["segundos_restantes"] == 0
    assert estado.json()["desafios_resueltos"] == 0
    assert respuesta.status_code == 409
    afirmar_sin_solucion(estado.json())
