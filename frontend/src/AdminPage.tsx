import { FormEvent, useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";

import {
  cambiarEstado,
  crearExperiencia,
  listarExperiencias,
  modificarExperiencia,
} from "./api";
import type { Experiencia, ExperienciaDatos } from "./types";
import { ExperienceConfig } from "./ExperienceConfig";

const vacia: ExperienciaDatos = {
  nombre: "",
  descripcion: "",
  instrucciones: "",
  mision_inicial: "",
  duracion_minutos: 5,
};

export function AdminPage() {
  const [experiencias, setExperiencias] = useState<Experiencia[]>([]);
  const [formulario, setFormulario] = useState<ExperienciaDatos>(vacia);
  const [editando, setEditando] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [configurando, setConfigurando] = useState<Experiencia | null>(null);

  const cargar = async () => {
    try {
      setExperiencias(await listarExperiencias());
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo cargar");
    }
  };

  useEffect(() => {
    void cargar();
  }, []);

  const guardar = async (evento: FormEvent) => {
    evento.preventDefault();
    setGuardando(true);
    setError("");
    try {
      if (editando) {
        await modificarExperiencia(editando, formulario);
      } else {
        await crearExperiencia(formulario);
      }
      setFormulario(vacia);
      setEditando(null);
      await cargar();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo guardar");
    } finally {
      setGuardando(false);
    }
  };

  const editar = (experiencia: Experiencia) => {
    setEditando(experiencia.id);
    setFormulario({
      nombre: experiencia.nombre,
      descripcion: experiencia.descripcion,
      instrucciones: experiencia.instrucciones,
      mision_inicial: experiencia.mision_inicial,
      duracion_minutos: experiencia.duracion_minutos,
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const alternar = async (experiencia: Experiencia) => {
    await cambiarEstado(experiencia.id, !experiencia.activa);
    await cargar();
  };

  return (
    <main className="admin-shell">
      <header className="page-header">
        <div>
          <span className="eyebrow">CONTROL DE MISIÓN</span>
          <h1>Experiencias del stand</h1>
          <p>Creá, configurá y publicá la secuencia del evento.</p>
        </div>
        <a className="ghost-button" href="/">Vista participante</a>
      </header>

      {configurando ? (
        <ExperienceConfig
          experiencia={configurando}
          cerrar={() => setConfigurando(null)}
          actualizada={(experiencia) => {
            setConfigurando(experiencia);
            void cargar();
          }}
        />
      ) : (
      <section className="admin-grid">
        <form className="panel form-panel" onSubmit={guardar}>
          <div className="section-heading">
            <span className="step">01</span>
            <div>
              <h2>{editando ? "Editar experiencia" : "Nueva experiencia"}</h2>
              <p>Duración permitida: entre 3 y 7 minutos.</p>
            </div>
          </div>

          <label>
            Nombre
            <input
              required
              minLength={3}
              value={formulario.nombre}
              onChange={(e) =>
                setFormulario({ ...formulario, nombre: e.target.value })
              }
              placeholder="Ej. El código patagónico"
            />
          </label>
          <label>
            Descripción
            <textarea
              required
              minLength={10}
              value={formulario.descripcion}
              onChange={(e) =>
                setFormulario({ ...formulario, descripcion: e.target.value })
              }
              placeholder="¿Qué propuesta verá el visitante?"
            />
          </label>
          <label>
            Instrucciones
            <textarea
              required
              minLength={10}
              value={formulario.instrucciones}
              onChange={(e) =>
                setFormulario({ ...formulario, instrucciones: e.target.value })
              }
              placeholder="Indicaciones breves y claras"
            />
          </label>
          <label>
            Misión inicial
            <textarea
              required
              minLength={5}
              value={formulario.mision_inicial}
              onChange={(e) =>
                setFormulario({ ...formulario, mision_inicial: e.target.value })
              }
              placeholder="La primera misión que recibe el participante"
            />
          </label>
          <label>
            Duración estimada
            <select
              value={formulario.duracion_minutos}
              onChange={(e) =>
                setFormulario({
                  ...formulario,
                  duracion_minutos: Number(e.target.value),
                })
              }
            >
              {[3, 4, 5, 6, 7].map((minutos) => (
                <option key={minutos} value={minutos}>
                  {minutos} minutos
                </option>
              ))}
            </select>
          </label>

          {error && <p className="error-message">{error}</p>}

          <div className="form-actions">
            <button className="primary-button" disabled={guardando}>
              {guardando ? "Guardando…" : editando ? "Guardar cambios" : "Crear experiencia"}
            </button>
            {editando && (
              <button
                className="ghost-button"
                type="button"
                onClick={() => {
                  setEditando(null);
                  setFormulario(vacia);
                }}
              >
                Cancelar
              </button>
            )}
          </div>
        </form>

        <section className="experience-list">
          <div className="section-heading">
            <span className="step">02</span>
            <div>
              <h2>Publicación</h2>
              <p>Activá una experiencia y probala desde su QR.</p>
            </div>
          </div>

          {experiencias.length === 0 && (
            <div className="panel empty-state">
              <span>◇</span>
              <p>Todavía no creaste ninguna experiencia.</p>
            </div>
          )}

          {experiencias.map((experiencia) => {
            const url = `${window.location.origin}/experiencia/${experiencia.codigo}`;
            return (
              <article className="panel experience-card" key={experiencia.id}>
                <div className="card-copy">
                  <div className="status-row">
                    <span className={experiencia.activa ? "badge active" : "badge"}>
                      {experiencia.activa ? "ACTIVA" : "BORRADOR"}
                    </span>
                    <span className="code">{experiencia.codigo}</span>
                  </div>
                  <h3>{experiencia.nombre}</h3>
                  <p>{experiencia.descripcion}</p>
                  <span className="duration">{experiencia.duracion_minutos} min</span>
                  <div className="card-actions">
                    <button className="ghost-button" onClick={() => editar(experiencia)}>
                      Editar
                    </button>
                    <button
                      className="primary-button small"
                      onClick={() => void alternar(experiencia)}
                    >
                      {experiencia.activa ? "Desactivar" : "Activar"}
                    </button>
                    <button className="ghost-button" onClick={() => setConfigurando(experiencia)}>
                      Configurar secuencia
                    </button>
                  </div>
                </div>
                <div className="qr-box">
                  <QRCodeSVG value={url} size={112} level="M" />
                  <a href={url} target="_blank" rel="noreferrer">Abrir</a>
                </div>
              </article>
            );
          })}
        </section>
      </section>
      )}
    </main>
  );
}

