from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class ExperienciaBase(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    descripcion: str = Field(min_length=10, max_length=1000)
    instrucciones: str = Field(min_length=10, max_length=1000)
    mision_inicial: str = Field(min_length=5, max_length=1000)
    duracion_minutos: int = Field(ge=3, le=7)


class ExperienciaCrear(ExperienciaBase):
    codigo: str | None = Field(default=None, min_length=4, max_length=12)


class ExperienciaActualizar(ExperienciaBase):
    pass


class ExperienciaEstado(BaseModel):
    activa: bool


class ExperienciaSalida(ExperienciaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    activa: bool
    creada_en: datetime
    actualizada_en: datetime


class ExperienciaPublica(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    codigo: str
    nombre: str
    descripcion: str
    instrucciones: str
    mision_inicial: str
    duracion_minutos: int


TipoDesafio = Literal["texto", "codigo", "qr"]


class DesafioBase(BaseModel):
    orden: int = Field(ge=1)
    tipo: TipoDesafio
    titulo: str = Field(min_length=3, max_length=120)
    consigna: str = Field(min_length=3, max_length=1000)
    respuesta_correcta: str = Field(min_length=1, max_length=200)
    pista: str = Field(min_length=1, max_length=1000)
    puntos: int = Field(ge=0, le=10000)
    activo: bool = True


class DesafioCrear(DesafioBase):
    pass


class DesafioActualizar(DesafioBase):
    pass


class DesafioSalida(DesafioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiencia_id: int


class OrdenDesafios(BaseModel):
    ids: list[int] = Field(min_length=1)


class ElementoFisicoBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    codigo: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(min_length=1, max_length=1000)
    desafio_id: int | None = None


class ElementoFisicoCrear(ElementoFisicoBase):
    pass


class ElementoFisicoActualizar(ElementoFisicoBase):
    pass


class ElementoFisicoSalida(ElementoFisicoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiencia_id: int


class DesafioPublico(BaseModel):
    id: int
    orden: int
    tipo: TipoDesafio
    titulo: str
    consigna: str
    puntos: int


class PartidaPublica(BaseModel):
    token: str
    estado: str
    puntos: int
    pistas_utilizadas: int
    segundos_restantes: int
    desafio: DesafioPublico | None
    total_desafios: int
    desafios_resueltos: int
    feedback: str | None = None
    pista: str | None = None


class RespuestaPartida(BaseModel):
    respuesta: str = Field(min_length=1, max_length=200)

