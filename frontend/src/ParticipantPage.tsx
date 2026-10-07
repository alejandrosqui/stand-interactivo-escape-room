import { FormEvent, useEffect, useState } from "react";

import { buscarExperiencia, consultarPartida, iniciarPartida, pedirPista, responderPartida } from "./api";
import type { ExperienciaPublica, Partida } from "./types";

type Props = { codigo: string };

function reloj(segundos: number) {
  return `${Math.floor(segundos / 60).toString().padStart(2, "0")}:${(segundos % 60).toString().padStart(2, "0")}`;
}

export function ParticipantPage({ codigo }: Props) {
  const [experiencia, setExperiencia] = useState<ExperienciaPublica | null>(null);
  const [partida, setPartida] = useState<Partida | null>(null);
  const [segundos, setSegundos] = useState(0);
  const [respuesta, setRespuesta] = useState("");
  const [error, setError] = useState("");
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    buscarExperiencia(codigo).then(setExperiencia).catch((e) => setError(e instanceof Error ? e.message : "No se pudo abrir la experiencia"));
  }, [codigo]);

  useEffect(() => {
    if (!partida || partida.estado !== "en_curso") return;
    setSegundos(partida.segundos_restantes);
    const visual = window.setInterval(() => setSegundos((actual) => Math.max(0, actual - 1)), 1000);
    const autoridad = window.setInterval(() => {
      void consultarPartida(partida.token).then((estado) => { setPartida(estado); setSegundos(estado.segundos_restantes); });
    }, 5000);
    return () => { window.clearInterval(visual); window.clearInterval(autoridad); };
  }, [partida?.token, partida?.estado, partida?.desafio?.id]);

  const comenzar = async () => {
    setOcupado(true); setError("");
    try { const nueva = await iniciarPartida(codigo); setPartida(nueva); setSegundos(nueva.segundos_restantes); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo iniciar la partida"); }
    finally { setOcupado(false); }
  };

  const responder = async (evento: FormEvent) => {
    evento.preventDefault(); if (!partida) return;
    setOcupado(true); setError("");
    try { const estado = await responderPartida(partida.token, respuesta); setPartida(estado); setSegundos(estado.segundos_restantes); if (estado.feedback?.startsWith("Respuesta correcta") || estado.estado === "completada") setRespuesta(""); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo validar la respuesta"); }
    finally { setOcupado(false); }
  };

  const pista = async () => {
    if (!partida) return;
    setOcupado(true);
    try { setPartida(await pedirPista(partida.token)); }
    catch (e) { setError(e instanceof Error ? e.message : "No se pudo obtener la pista"); }
    finally { setOcupado(false); }
  };

  if (error && !experiencia) return <main className="participant-shell center-state"><span className="signal">×</span><h1>Misión no disponible</h1><p>{error}</p><a className="ghost-button" href="/">Volver</a></main>;
  if (!experiencia) return <main className="participant-shell center-state"><span className="loader" /><p>Descifrando misión...</p></main>;

  const progreso = partida?.total_desafios ? Math.round((partida.desafios_resueltos / partida.total_desafios) * 100) : 0;
  return <main className="participant-shell">
    <div className="mission-progress"><span>{partida ? partida.estado.toUpperCase().replace("_", " ") : "INICIO"}</span><div><i style={{ width: `${progreso}%` }} /></div><span>{partida ? `${partida.desafios_resueltos} / ${partida.total_desafios}` : "LISTO"}</span></div>
    <section className="mission-hero"><span className="eyebrow">MISIÓN {experiencia.codigo}</span><h1>{experiencia.nombre}</h1><p className="lead">{experiencia.descripcion}</p><div className="mission-meta"><span>◷ {partida ? reloj(segundos) : `${experiencia.duracion_minutos} minutos`}</span><span>● {partida ? `${partida.puntos} puntos` : "Experiencia activa"}</span></div></section>
    {!partida && <><section className="panel instruction-panel"><span className="step">01</span><div><h2>Antes de comenzar</h2><p>{experiencia.instrucciones}</p></div></section><section className="mission-card"><span className="eyebrow">TU PRIMER OBJETIVO</span><h2>{experiencia.mision_inicial}</h2><button className="primary-button" disabled={ocupado} onClick={() => void comenzar()}>{ocupado ? "Iniciando..." : "Comenzar misión"}</button>{error && <p className="error-message">{error}</p>}</section></>}
    {partida?.estado === "en_curso" && partida.desafio && <section className="mission-card game-card"><div className="challenge-meta"><span className="eyebrow">DESAFÍO {partida.desafio.orden} · {partida.desafio.tipo.toUpperCase()}</span><span>{partida.desafio.puntos} pts</span></div><h2>{partida.desafio.titulo}</h2><p className="challenge-prompt">{partida.desafio.consigna}</p><form className="answer-form" onSubmit={responder}><label>{partida.desafio.tipo === "texto" ? "Tu respuesta" : "Código o identificador"}<input autoFocus required value={respuesta} onChange={(e) => setRespuesta(e.target.value)} placeholder={partida.desafio.tipo === "qr" ? "Escaneá o ingresá el código manualmente" : "Ingresá tu respuesta"} /></label><div className="form-actions"><button className="primary-button" disabled={ocupado}>Validar respuesta</button><button className="ghost-button" type="button" disabled={ocupado} onClick={() => void pista()}>Solicitar pista</button></div></form>{partida.feedback && <p className={partida.feedback.includes("incorrecta") ? "feedback error-message" : "feedback success-message"}>{partida.feedback}</p>}{partida.pista && <aside className="hint"><span className="eyebrow">PISTA</span><p>{partida.pista}</p></aside>}{error && <p className="error-message">{error}</p>}</section>}
    {partida && partida.estado !== "en_curso" && <section className="mission-card result-card"><span className="eyebrow">RESULTADO FINAL</span><h2>{partida.estado === "completada" ? "Misión completada" : "Tiempo agotado"}</h2><strong>{partida.puntos} puntos</strong><p>{partida.desafios_resueltos} de {partida.total_desafios} desafíos resueltos · {partida.pistas_utilizadas} pistas utilizadas</p><button className="ghost-button" onClick={() => {setPartida(null); setRespuesta("");}}>Volver al inicio</button></section>}
  </main>;
}
