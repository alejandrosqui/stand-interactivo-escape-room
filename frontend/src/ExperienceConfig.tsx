import { FormEvent, useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";

import {
  guardarDesafio,
  guardarElemento,
  listarDesafios,
  listarElementos,
  modificarExperiencia,
  ordenarDesafios,
} from "./api";
import type { Desafio, DesafioDatos, ElementoFisico, ElementoFisicoDatos, Experiencia } from "./types";

const desafioVacio: DesafioDatos = {
  orden: 1, tipo: "texto", titulo: "", consigna: "", respuesta_correcta: "",
  pista: "", puntos: 100, activo: true,
};
const elementoVacio: ElementoFisicoDatos = {
  nombre: "", codigo: "", descripcion: "", desafio_id: null,
};

type Props = {
  experiencia: Experiencia;
  cerrar: () => void;
  actualizada: (experiencia: Experiencia) => void;
};

export function ExperienceConfig({ experiencia, cerrar, actualizada }: Props) {
  const [desafios, setDesafios] = useState<Desafio[]>([]);
  const [elementos, setElementos] = useState<ElementoFisico[]>([]);
  const [desafio, setDesafio] = useState<DesafioDatos>(desafioVacio);
  const [elemento, setElemento] = useState<ElementoFisicoDatos>(elementoVacio);
  const [editandoDesafio, setEditandoDesafio] = useState<number>();
  const [editandoElemento, setEditandoElemento] = useState<number>();
  const [duracion, setDuracion] = useState(experiencia.duracion_minutos);
  const [error, setError] = useState("");

  const cargar = async () => {
    const [nuevosDesafios, nuevosElementos] = await Promise.all([
      listarDesafios(experiencia.id), listarElementos(experiencia.id),
    ]);
    setDesafios(nuevosDesafios);
    setElementos(nuevosElementos);
    setDesafio((actual) => editandoDesafio ? actual : { ...actual, orden: nuevosDesafios.length + 1 });
  };

  useEffect(() => { void cargar().catch((e) => setError(e instanceof Error ? e.message : "No se pudo cargar")); }, [experiencia.id]);

  const guardarReto = async (evento: FormEvent) => {
    evento.preventDefault(); setError("");
    try {
      await guardarDesafio(experiencia.id, desafio, editandoDesafio);
      setEditandoDesafio(undefined); setDesafio({ ...desafioVacio, orden: desafios.length + (editandoDesafio ? 1 : 2) });
      await cargar();
    } catch (e) { setError(e instanceof Error ? e.message : "No se pudo guardar"); }
  };

  const guardarObjeto = async (evento: FormEvent) => {
    evento.preventDefault(); setError("");
    try {
      await guardarElemento(experiencia.id, elemento, editandoElemento);
      setEditandoElemento(undefined); setElemento(elementoVacio); await cargar();
    } catch (e) { setError(e instanceof Error ? e.message : "No se pudo guardar"); }
  };

  const mover = async (indice: number, direccion: -1 | 1) => {
    const destino = indice + direccion;
    if (destino < 0 || destino >= desafios.length) return;
    const ids = desafios.map((item) => item.id);
    [ids[indice], ids[destino]] = [ids[destino], ids[indice]];
    setDesafios(await ordenarDesafios(experiencia.id, ids));
  };

  const guardarDuracion = async () => {
    setError("");
    try {
      const resultado = await modificarExperiencia(experiencia.id, {
        nombre: experiencia.nombre,
        descripcion: experiencia.descripcion,
        instrucciones: experiencia.instrucciones,
        mision_inicial: experiencia.mision_inicial,
        duracion_minutos: duracion,
      });
      actualizada(resultado);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo guardar la duración");
    }
  };

  return <section className="config-band">
    <div className="config-header">
      <div><span className="eyebrow">CONFIGURACIÓN DE SECUENCIA</span><h2>{experiencia.nombre}</h2></div>
      <div className="config-toolbar">
        <label>Tiempo máximo
          <select value={duracion} onChange={(e) => setDuracion(Number(e.target.value))}>
            {[3, 4, 5, 6, 7].map((minutos) => <option key={minutos} value={minutos}>{minutos} minutos</option>)}
          </select>
        </label>
        <button className="primary-button small" disabled={duracion === experiencia.duracion_minutos} onClick={() => void guardarDuracion()}>Guardar tiempo</button>
        <button className="ghost-button" onClick={cerrar}>Cerrar</button>
      </div>
    </div>
    {error && <p className="error-message">{error}</p>}
    <div className="config-grid">
      <form className="panel form-panel" onSubmit={guardarReto}>
        <h3>{editandoDesafio ? "Editar desafío" : "Nuevo desafío"}</h3>
        <div className="field-row">
          <label>Orden<input type="number" min="1" value={desafio.orden} onChange={(e) => setDesafio({...desafio, orden: Number(e.target.value)})} /></label>
          <label>Tipo<select value={desafio.tipo} onChange={(e) => setDesafio({...desafio, tipo: e.target.value as DesafioDatos["tipo"]})}><option value="texto">Respuesta escrita</option><option value="codigo">Código</option><option value="qr">QR / identificador</option></select></label>
          <label>Puntos<input type="number" min="0" value={desafio.puntos} onChange={(e) => setDesafio({...desafio, puntos: Number(e.target.value)})} /></label>
        </div>
        <label>Título<input required minLength={3} value={desafio.titulo} onChange={(e) => setDesafio({...desafio, titulo: e.target.value})} /></label>
        <label>Consigna<textarea required minLength={3} value={desafio.consigna} onChange={(e) => setDesafio({...desafio, consigna: e.target.value})} /></label>
        <label>Respuesta válida<input required value={desafio.respuesta_correcta} onChange={(e) => setDesafio({...desafio, respuesta_correcta: e.target.value})} /></label>
        <label>Pista<textarea required value={desafio.pista} onChange={(e) => setDesafio({...desafio, pista: e.target.value})} /></label>
        <label className="check-label"><input type="checkbox" checked={desafio.activo} onChange={(e) => setDesafio({...desafio, activo: e.target.checked})} /> Desafío activo</label>
        <div className="form-actions"><button className="primary-button">Guardar desafío</button>{editandoDesafio && <button type="button" className="ghost-button" onClick={() => {setEditandoDesafio(undefined); setDesafio({...desafioVacio, orden: desafios.length + 1});}}>Cancelar</button>}</div>
      </form>
      <div className="challenge-list">
        <h3>Secuencia ({desafios.length})</h3>
        {desafios.map((item, indice) => <article className="panel compact-card" key={item.id}>
          <div><span className="code">{item.orden.toString().padStart(2, "0")} · {item.tipo.toUpperCase()}</span><h4>{item.titulo}</h4><p>{item.consigna}</p><small>{item.puntos} puntos · {item.activo ? "Activo" : "Inactivo"}</small></div>
          <div className="icon-actions"><button title="Subir" disabled={indice === 0} onClick={() => void mover(indice, -1)}>↑</button><button title="Bajar" disabled={indice === desafios.length - 1} onClick={() => void mover(indice, 1)}>↓</button><button title="Editar" onClick={() => {setEditandoDesafio(item.id); setDesafio(item);}}>Editar</button></div>
        </article>)}
        {!desafios.length && <p className="muted">Agregá el primer desafío de la secuencia.</p>}
      </div>
    </div>
    <div className="config-grid physical-grid">
      <form className="panel form-panel" onSubmit={guardarObjeto}>
        <h3>{editandoElemento ? "Editar elemento físico" : "Nuevo elemento físico"}</h3>
        <label>Nombre<input required minLength={2} value={elemento.nombre} onChange={(e) => setElemento({...elemento, nombre: e.target.value})} /></label>
        <label>Identificador / código<input required value={elemento.codigo} onChange={(e) => setElemento({...elemento, codigo: e.target.value})} /></label>
        <label>Descripción<textarea required value={elemento.descripcion} onChange={(e) => setElemento({...elemento, descripcion: e.target.value})} /></label>
        <label>Desafío vinculado<select value={elemento.desafio_id ?? ""} onChange={(e) => setElemento({...elemento, desafio_id: e.target.value ? Number(e.target.value) : null})}><option value="">Sin vincular</option>{desafios.map((item) => <option key={item.id} value={item.id}>{item.orden}. {item.titulo}</option>)}</select></label>
        <button className="primary-button">Guardar elemento</button>
      </form>
      <div className="challenge-list"><h3>Elementos físicos ({elementos.length})</h3>{elementos.map((item) => <article className="panel physical-card" key={item.id}><QRCodeSVG value={item.codigo} size={76} /><div><span className="code">{item.codigo}</span><h4>{item.nombre}</h4><p>{item.descripcion}</p></div><button className="ghost-button" onClick={() => {setEditandoElemento(item.id); setElemento(item);}}>Editar</button></article>)}</div>
    </div>
  </section>;
}
