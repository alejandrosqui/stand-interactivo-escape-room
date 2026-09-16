from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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

