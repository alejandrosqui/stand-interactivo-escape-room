import { useEffect, useState } from "react";

import { buscarExperiencia } from "./api";
import type { ExperienciaPublica } from "./types";

type Props = { codigo: string };

export function ParticipantPage({ codigo }: Props) {
  const [experiencia, setExperiencia] = useState<ExperienciaPublica | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    buscarExperiencia(codigo)
      .then(setExperiencia)
      .catch((e) =>
        setError(e instanceof Error ? e.message : "No se pudo abrir la experiencia"),
      );
  }, [codigo]);

  if (error) {
    return (
      <main className="participant-shell center-state">
        <span className="signal">×</span>
        <h1>Misión no disponible</h1>
        <p>{error}</p>
        <a className="ghost-button" href="/">Volver</a>
      </main>
    );
  }

  if (!experiencia) {
    return (
      <main className="participant-shell center-state">
        <span className="loader" />
        <p>Descifrando misión…</p>
      </main>
    );
  }

  return (
    <main className="participant-shell">
      <div className="mission-progress">
        <span>INICIO</span>
        <div><i /></div>
        <span>01 / 01</span>
      </div>
      <section className="mission-hero">
        <span className="eyebrow">MISIÓN {experiencia.codigo}</span>
        <h1>{experiencia.nombre}</h1>
        <p className="lead">{experiencia.descripcion}</p>
        <div className="mission-meta">
          <span>◷ {experiencia.duracion_minutos} minutos</span>
          <span>● Experiencia activa</span>
        </div>
      </section>
      <section className="panel instruction-panel">
        <span className="step">01</span>
        <div>
          <h2>Antes de comenzar</h2>
          <p>{experiencia.instrucciones}</p>
        </div>
      </section>
      <section className="mission-card">
        <span className="eyebrow">TU PRIMER OBJETIVO</span>
        <h2>{experiencia.mision_inicial}</h2>
        <button className="primary-button">Comenzar misión</button>
      </section>
    </main>
  );
}

