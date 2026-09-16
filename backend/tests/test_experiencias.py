def datos_experiencia():
    return {
        "codigo": "MISION1",
        "nombre": "El código perdido",
        "descripcion": "Encontrá el código oculto dentro del stand.",
        "instrucciones": "Escaneá las pistas y resolvé la misión sin mover objetos.",
        "mision_inicial": "Buscá el cartel que contiene el primer símbolo.",
        "duracion_minutos": 5,
    }


def test_crear_modificar_y_activar_experiencia(client):
    creada = client.post("/api/experiencias", json=datos_experiencia())
    assert creada.status_code == 201
    assert creada.json()["activa"] is False

    actualizada = datos_experiencia()
    actualizada["nombre"] = "El código patagónico"
    respuesta = client.put("/api/experiencias/1", json=actualizada)
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "El código patagónico"

    activada = client.patch("/api/experiencias/1/estado", json={"activa": True})
    assert activada.status_code == 200
    assert activada.json()["activa"] is True


def test_solo_una_experiencia_activa_es_publica(client):
    client.post("/api/experiencias", json=datos_experiencia())

    inactiva = client.get("/api/publico/experiencias/MISION1")
    assert inactiva.status_code == 404

    client.patch("/api/experiencias/1/estado", json={"activa": True})
    publica = client.get("/api/publico/experiencias/MISION1")
    assert publica.status_code == 200
    assert publica.json()["duracion_minutos"] == 5
    assert publica.json()["mision_inicial"].startswith("Buscá")


def test_rechaza_duracion_fuera_del_alcance(client):
    datos = datos_experiencia()
    datos["duracion_minutos"] = 10
    respuesta = client.post("/api/experiencias", json=datos)
    assert respuesta.status_code == 422

