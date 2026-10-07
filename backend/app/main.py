import os
import secrets
import string
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Desafio, ElementoFisico, Experiencia, Partida
from .schemas import (
    ExperienciaActualizar,
    ExperienciaCrear,
    ExperienciaEstado,
    ExperienciaPublica,
    ExperienciaSalida,
    DesafioActualizar,
    DesafioCrear,
    DesafioPublico,
    DesafioSalida,
    ElementoFisicoActualizar,
    ElementoFisicoCrear,
    ElementoFisicoSalida,
    OrdenDesafios,
    PartidaPublica,
    RespuestaPartida,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Stand interactivo API",
    version="0.1.0",
    description="API del mini escape room para eventos.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=os.getenv(
        "CORS_ORIGIN_REGEX",
        r"^http://(?:localhost|127\.0\.0\.1):\d+$",
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generar_codigo() -> str:
    alfabeto = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(6))


def obtener_experiencia(db: Session, experiencia_id: int) -> Experiencia:
    experiencia = db.get(Experiencia, experiencia_id)
    if experiencia is None:
        raise HTTPException(status_code=404, detail="Experiencia no encontrada")
    return experiencia


def obtener_desafio(db: Session, experiencia_id: int, desafio_id: int) -> Desafio:
    desafio = db.scalar(
        select(Desafio).where(
            Desafio.id == desafio_id, Desafio.experiencia_id == experiencia_id
        )
    )
    if desafio is None:
        raise HTTPException(status_code=404, detail="Desafío no encontrado")
    return desafio


def validar_desafio_elemento(db: Session, experiencia_id: int, desafio_id: int | None):
    if desafio_id is not None:
        obtener_desafio(db, experiencia_id, desafio_id)


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


def fecha_utc(fecha: datetime) -> datetime:
    return fecha.replace(tzinfo=timezone.utc) if fecha.tzinfo is None else fecha


def desafios_activos(db: Session, experiencia_id: int) -> list[Desafio]:
    return list(
        db.scalars(
            select(Desafio)
            .where(Desafio.experiencia_id == experiencia_id, Desafio.activo.is_(True))
            .order_by(Desafio.orden, Desafio.id)
        ).all()
    )


def controlar_tiempo(partida: Partida, db: Session) -> int:
    limite = partida.experiencia.duracion_minutos * 60
    transcurrido = int((ahora_utc() - fecha_utc(partida.iniciada_en)).total_seconds())
    restante = max(0, limite - transcurrido)
    if restante == 0 and partida.estado == "en_curso":
        partida.estado = "tiempo_agotado"
        partida.finalizada_en = ahora_utc()
        db.commit()
    return restante


def salida_partida(
    partida: Partida,
    db: Session,
    *,
    feedback: str | None = None,
    pista: str | None = None,
) -> PartidaPublica:
    restante = controlar_tiempo(partida, db)
    desafios = desafios_activos(db, partida.experiencia_id)
    actual = partida.desafio_actual if partida.estado == "en_curso" else None
    posicion = next((i for i, d in enumerate(desafios) if d.id == partida.desafio_actual_id), len(desafios))
    return PartidaPublica(
        token=partida.token,
        estado=partida.estado,
        puntos=partida.puntos,
        pistas_utilizadas=partida.pistas_utilizadas,
        segundos_restantes=restante,
        desafio=DesafioPublico.model_validate(actual, from_attributes=True) if actual else None,
        total_desafios=len(desafios),
        desafios_resueltos=len(desafios) if partida.estado == "completada" else posicion,
        feedback=feedback,
        pista=pista,
    )


def obtener_partida(db: Session, token: str) -> Partida:
    partida = db.scalar(select(Partida).where(Partida.token == token))
    if partida is None:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return partida


@app.get("/api/salud")
def salud() -> dict[str, str]:
    return {"estado": "ok", "version": app.version}


@app.get("/api/experiencias", response_model=list[ExperienciaSalida])
def listar_experiencias(db: Session = Depends(get_db)):
    return db.scalars(select(Experiencia).order_by(Experiencia.id.desc())).all()


@app.post(
    "/api/experiencias",
    response_model=ExperienciaSalida,
    status_code=status.HTTP_201_CREATED,
)
def crear_experiencia(datos: ExperienciaCrear, db: Session = Depends(get_db)):
    codigo = (datos.codigo or generar_codigo()).strip().upper()
    if db.scalar(select(Experiencia).where(Experiencia.codigo == codigo)):
        raise HTTPException(status_code=409, detail="El código ya está en uso")

    experiencia = Experiencia(
        **datos.model_dump(exclude={"codigo"}),
        codigo=codigo,
    )
    db.add(experiencia)
    db.commit()
    db.refresh(experiencia)
    return experiencia


@app.put("/api/experiencias/{experiencia_id}", response_model=ExperienciaSalida)
def modificar_experiencia(
    experiencia_id: int,
    datos: ExperienciaActualizar,
    db: Session = Depends(get_db),
):
    experiencia = obtener_experiencia(db, experiencia_id)
    for campo, valor in datos.model_dump().items():
        setattr(experiencia, campo, valor)
    db.commit()
    db.refresh(experiencia)
    return experiencia


@app.patch(
    "/api/experiencias/{experiencia_id}/estado",
    response_model=ExperienciaSalida,
)
def cambiar_estado(
    experiencia_id: int,
    datos: ExperienciaEstado,
    db: Session = Depends(get_db),
):
    experiencia = obtener_experiencia(db, experiencia_id)
    experiencia.activa = datos.activa
    db.commit()
    db.refresh(experiencia)
    return experiencia


@app.get(
    "/api/publico/experiencias/{codigo}",
    response_model=ExperienciaPublica,
)
def ver_experiencia_publica(codigo: str, db: Session = Depends(get_db)):
    experiencia = db.scalar(
        select(Experiencia).where(
            Experiencia.codigo == codigo.strip().upper(),
            Experiencia.activa.is_(True),
        )
    )
    if experiencia is None:
        raise HTTPException(
            status_code=404,
            detail="La experiencia no existe o todavía no está activa",
        )
    return experiencia


@app.get("/api/experiencias/{experiencia_id}/desafios", response_model=list[DesafioSalida])
def listar_desafios(experiencia_id: int, db: Session = Depends(get_db)):
    obtener_experiencia(db, experiencia_id)
    return db.scalars(
        select(Desafio).where(Desafio.experiencia_id == experiencia_id).order_by(Desafio.orden, Desafio.id)
    ).all()


@app.post("/api/experiencias/{experiencia_id}/desafios", response_model=DesafioSalida, status_code=201)
def crear_desafio(experiencia_id: int, datos: DesafioCrear, db: Session = Depends(get_db)):
    obtener_experiencia(db, experiencia_id)
    desafio = Desafio(experiencia_id=experiencia_id, **datos.model_dump())
    db.add(desafio)
    db.commit()
    db.refresh(desafio)
    return desafio


@app.put("/api/experiencias/{experiencia_id}/desafios/{desafio_id:int}", response_model=DesafioSalida)
def modificar_desafio(experiencia_id: int, desafio_id: int, datos: DesafioActualizar, db: Session = Depends(get_db)):
    desafio = obtener_desafio(db, experiencia_id, desafio_id)
    for campo, valor in datos.model_dump().items():
        setattr(desafio, campo, valor)
    db.commit()
    db.refresh(desafio)
    return desafio


@app.put("/api/experiencias/{experiencia_id}/desafios/orden", response_model=list[DesafioSalida])
def ordenar_desafios(experiencia_id: int, datos: OrdenDesafios, db: Session = Depends(get_db)):
    actuales = list(db.scalars(select(Desafio).where(Desafio.experiencia_id == experiencia_id)).all())
    if len(datos.ids) != len(set(datos.ids)) or set(datos.ids) != {d.id for d in actuales}:
        raise HTTPException(status_code=422, detail="Debe indicar todos los desafíos una sola vez")
    por_id = {d.id: d for d in actuales}
    for orden, desafio_id in enumerate(datos.ids, 1):
        por_id[desafio_id].orden = orden
    db.commit()
    return [por_id[i] for i in datos.ids]


@app.get("/api/experiencias/{experiencia_id}/elementos", response_model=list[ElementoFisicoSalida])
def listar_elementos(experiencia_id: int, db: Session = Depends(get_db)):
    obtener_experiencia(db, experiencia_id)
    return db.scalars(select(ElementoFisico).where(ElementoFisico.experiencia_id == experiencia_id).order_by(ElementoFisico.id)).all()


@app.post("/api/experiencias/{experiencia_id}/elementos", response_model=ElementoFisicoSalida, status_code=201)
def crear_elemento(experiencia_id: int, datos: ElementoFisicoCrear, db: Session = Depends(get_db)):
    obtener_experiencia(db, experiencia_id)
    validar_desafio_elemento(db, experiencia_id, datos.desafio_id)
    elemento = ElementoFisico(experiencia_id=experiencia_id, **datos.model_dump())
    elemento.codigo = elemento.codigo.strip().upper()
    db.add(elemento)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El identificador físico ya está en uso")
    db.refresh(elemento)
    return elemento


@app.put("/api/experiencias/{experiencia_id}/elementos/{elemento_id}", response_model=ElementoFisicoSalida)
def modificar_elemento(experiencia_id: int, elemento_id: int, datos: ElementoFisicoActualizar, db: Session = Depends(get_db)):
    elemento = db.scalar(select(ElementoFisico).where(ElementoFisico.id == elemento_id, ElementoFisico.experiencia_id == experiencia_id))
    if elemento is None:
        raise HTTPException(status_code=404, detail="Elemento físico no encontrado")
    validar_desafio_elemento(db, experiencia_id, datos.desafio_id)
    for campo, valor in datos.model_dump().items():
        setattr(elemento, campo, valor)
    elemento.codigo = elemento.codigo.strip().upper()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El identificador físico ya está en uso")
    db.refresh(elemento)
    return elemento


@app.post("/api/publico/experiencias/{codigo}/partidas", response_model=PartidaPublica, status_code=201)
def iniciar_partida(codigo: str, db: Session = Depends(get_db)):
    experiencia = db.scalar(select(Experiencia).where(Experiencia.codigo == codigo.strip().upper(), Experiencia.activa.is_(True)))
    if experiencia is None:
        raise HTTPException(status_code=404, detail="La experiencia no existe o todavía no está activa")
    desafios = desafios_activos(db, experiencia.id)
    if not desafios:
        raise HTTPException(status_code=409, detail="La experiencia no tiene desafíos activos")
    partida = Partida(
        experiencia_id=experiencia.id,
        token=secrets.token_urlsafe(24),
        desafio_actual_id=desafios[0].id,
        iniciada_en=ahora_utc(),
        estado="en_curso",
    )
    db.add(partida)
    db.commit()
    db.refresh(partida)
    return salida_partida(partida, db)


@app.get("/api/publico/partidas/{token}", response_model=PartidaPublica)
def consultar_partida(token: str, db: Session = Depends(get_db)):
    return salida_partida(obtener_partida(db, token), db)


@app.post("/api/publico/partidas/{token}/respuestas", response_model=PartidaPublica)
def responder_desafio(token: str, datos: RespuestaPartida, db: Session = Depends(get_db)):
    partida = obtener_partida(db, token)
    controlar_tiempo(partida, db)
    if partida.estado != "en_curso" or partida.desafio_actual is None:
        raise HTTPException(status_code=409, detail="La partida ya no admite respuestas")
    desafio = partida.desafio_actual
    respuesta = datos.respuesta.strip().casefold()
    valida = respuesta == desafio.respuesta_correcta.strip().casefold()
    if desafio.tipo in {"codigo", "qr"}:
        codigos = db.scalars(select(ElementoFisico.codigo).where(ElementoFisico.desafio_id == desafio.id)).all()
        valida = valida or respuesta in {codigo.strip().casefold() for codigo in codigos}
    if not valida:
        return salida_partida(partida, db, feedback="Respuesta incorrecta. Revisá las pistas e intentá nuevamente.")
    partida.puntos += desafio.puntos
    desafios = desafios_activos(db, partida.experiencia_id)
    indice = next(i for i, item in enumerate(desafios) if item.id == desafio.id)
    if indice + 1 < len(desafios):
        partida.desafio_actual_id = desafios[indice + 1].id
        feedback = "Respuesta correcta. Avanzaste al siguiente desafío."
    else:
        partida.desafio_actual_id = None
        partida.estado = "completada"
        partida.finalizada_en = ahora_utc()
        feedback = "Misión completada."
    db.commit()
    db.refresh(partida)
    return salida_partida(partida, db, feedback=feedback)


@app.post("/api/publico/partidas/{token}/pista", response_model=PartidaPublica)
def solicitar_pista(token: str, db: Session = Depends(get_db)):
    partida = obtener_partida(db, token)
    controlar_tiempo(partida, db)
    if partida.estado != "en_curso" or partida.desafio_actual is None:
        raise HTTPException(status_code=409, detail="La partida ya no admite pistas")
    usados = {int(item) for item in partida.pistas_desafios.split(",") if item}
    desafio = partida.desafio_actual
    if desafio.id not in usados:
        usados.add(desafio.id)
        partida.pistas_utilizadas += 1
        partida.pistas_desafios = ",".join(str(item) for item in sorted(usados))
        db.commit()
    return salida_partida(partida, db, pista=desafio.pista)
