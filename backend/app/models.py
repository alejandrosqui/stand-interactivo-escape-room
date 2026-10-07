from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Experiencia(Base):
    __tablename__ = "experiencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(Text)
    instrucciones: Mapped[str] = mapped_column(Text)
    mision_inicial: Mapped[str] = mapped_column(Text)
    duracion_minutos: Mapped[int] = mapped_column(Integer)
    activa: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    creada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    actualizada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    desafios: Mapped[list["Desafio"]] = relationship(
        back_populates="experiencia", cascade="all, delete-orphan"
    )
    elementos_fisicos: Mapped[list["ElementoFisico"]] = relationship(
        back_populates="experiencia", cascade="all, delete-orphan"
    )
    partidas: Mapped[list["Partida"]] = relationship(back_populates="experiencia")


class Desafio(Base):
    __tablename__ = "desafios"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiencia_id: Mapped[int] = mapped_column(
        ForeignKey("experiencias.id", ondelete="CASCADE"), index=True
    )
    orden: Mapped[int] = mapped_column(Integer)
    tipo: Mapped[str] = mapped_column(String(20))
    titulo: Mapped[str] = mapped_column(String(120))
    consigna: Mapped[str] = mapped_column(Text)
    respuesta_correcta: Mapped[str] = mapped_column(String(200))
    pista: Mapped[str] = mapped_column(Text)
    puntos: Mapped[int] = mapped_column(Integer, default=100)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    experiencia: Mapped[Experiencia] = relationship(back_populates="desafios")
    elementos_fisicos: Mapped[list["ElementoFisico"]] = relationship(
        back_populates="desafio"
    )


class ElementoFisico(Base):
    __tablename__ = "elementos_fisicos"
    __table_args__ = (
        UniqueConstraint("experiencia_id", "codigo", name="uq_elemento_codigo_experiencia"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    experiencia_id: Mapped[int] = mapped_column(
        ForeignKey("experiencias.id", ondelete="CASCADE"), index=True
    )
    nombre: Mapped[str] = mapped_column(String(120))
    codigo: Mapped[str] = mapped_column(String(120))
    descripcion: Mapped[str] = mapped_column(Text)
    desafio_id: Mapped[int | None] = mapped_column(
        ForeignKey("desafios.id", ondelete="SET NULL"), nullable=True, index=True
    )

    experiencia: Mapped[Experiencia] = relationship(back_populates="elementos_fisicos")
    desafio: Mapped[Desafio | None] = relationship(back_populates="elementos_fisicos")


class Partida(Base):
    __tablename__ = "partidas"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiencia_id: Mapped[int] = mapped_column(
        ForeignKey("experiencias.id", ondelete="RESTRICT"), index=True
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    desafio_actual_id: Mapped[int | None] = mapped_column(
        ForeignKey("desafios.id", ondelete="SET NULL"), nullable=True
    )
    iniciada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finalizada_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    estado: Mapped[str] = mapped_column(String(30), default="en_curso", index=True)
    puntos: Mapped[int] = mapped_column(Integer, default=0)
    pistas_utilizadas: Mapped[int] = mapped_column(Integer, default=0)
    pistas_desafios: Mapped[str] = mapped_column(Text, default="")

    experiencia: Mapped[Experiencia] = relationship(back_populates="partidas")
    desafio_actual: Mapped[Desafio | None] = relationship()

