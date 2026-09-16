import type {
  Experiencia,
  ExperienciaDatos,
  ExperienciaPublica,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

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
