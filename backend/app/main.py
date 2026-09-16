import secrets
import string
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Experiencia
from .schemas import (
    ExperienciaActualizar,
    ExperienciaCrear,
    ExperienciaEstado,
    ExperienciaPublica,
    ExperienciaSalida,
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
    allow_origins=["http://localhost:5173"],
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
