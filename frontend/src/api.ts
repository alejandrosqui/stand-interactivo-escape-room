import type {
  Desafio,
  DesafioDatos,
  ElementoFisico,
  ElementoFisicoDatos,
  Experiencia,
  ExperienciaDatos,
  ExperienciaPublica,
  Partida,
} from "./types";

const API_URL = (import.meta.env.VITE_API_URL ?? "/api").replace(/\/$/, "");

async function procesar<T>(respuesta: Response): Promise<T> {
  if (!respuesta.ok) {
    const error = await respuesta.json().catch(() => null);
    throw new Error(error?.detail ?? "No se pudo completar la operación");
  }
  return respuesta.json() as Promise<T>;
}

export async function listarExperiencias(): Promise<Experiencia[]> {
  return procesar(await fetch(`${API_URL}/experiencias`));
}

export async function crearExperiencia(
  datos: ExperienciaDatos,
): Promise<Experiencia> {
  return procesar(
    await fetch(`${API_URL}/experiencias`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    }),
  );
}

export async function modificarExperiencia(
  id: number,
  datos: ExperienciaDatos,
): Promise<Experiencia> {
  return procesar(
    await fetch(`${API_URL}/experiencias/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    }),
  );
}

export async function cambiarEstado(
  id: number,
  activa: boolean,
): Promise<Experiencia> {
  return procesar(
    await fetch(`${API_URL}/experiencias/${id}/estado`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ activa }),
    }),
  );
}

export async function buscarExperiencia(
  codigo: string,
): Promise<ExperienciaPublica> {
  return procesar(
    await fetch(`${API_URL}/publico/experiencias/${codigo}`),
  );
}

export async function listarDesafios(experienciaId: number): Promise<Desafio[]> {
  return procesar(await fetch(`${API_URL}/experiencias/${experienciaId}/desafios`));
}

export async function guardarDesafio(
  experienciaId: number,
  datos: DesafioDatos,
  id?: number,
): Promise<Desafio> {
  return procesar(await fetch(`${API_URL}/experiencias/${experienciaId}/desafios${id ? `/${id}` : ""}`, {
    method: id ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  }));
}

export async function ordenarDesafios(experienciaId: number, ids: number[]): Promise<Desafio[]> {
  return procesar(await fetch(`${API_URL}/experiencias/${experienciaId}/desafios/orden`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  }));
}

export async function listarElementos(experienciaId: number): Promise<ElementoFisico[]> {
  return procesar(await fetch(`${API_URL}/experiencias/${experienciaId}/elementos`));
}

export async function guardarElemento(
  experienciaId: number,
  datos: ElementoFisicoDatos,
  id?: number,
): Promise<ElementoFisico> {
  return procesar(await fetch(`${API_URL}/experiencias/${experienciaId}/elementos${id ? `/${id}` : ""}`, {
    method: id ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  }));
}

export async function iniciarPartida(codigo: string): Promise<Partida> {
  return procesar(await fetch(`${API_URL}/publico/experiencias/${codigo}/partidas`, { method: "POST" }));
}

export async function consultarPartida(token: string): Promise<Partida> {
  return procesar(await fetch(`${API_URL}/publico/partidas/${token}`));
}

export async function responderPartida(token: string, respuesta: string): Promise<Partida> {
  return procesar(await fetch(`${API_URL}/publico/partidas/${token}/respuestas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ respuesta }),
  }));
}

export async function pedirPista(token: string): Promise<Partida> {
  return procesar(await fetch(`${API_URL}/publico/partidas/${token}/pista`, { method: "POST" }));
}
