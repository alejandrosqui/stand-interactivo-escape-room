export type ExperienciaDatos = {
  nombre: string;
  descripcion: string;
  instrucciones: string;
  mision_inicial: string;
  duracion_minutos: number;
};

export type Experiencia = ExperienciaDatos & {
  id: number;
  codigo: string;
  activa: boolean;
  creada_en: string;
  actualizada_en: string;
};

export type ExperienciaPublica = ExperienciaDatos & {
  codigo: string;
};

export type TipoDesafio = "texto" | "codigo" | "qr";

export type DesafioDatos = {
  orden: number;
  tipo: TipoDesafio;
  titulo: string;
  consigna: string;
  respuesta_correcta: string;
  pista: string;
  puntos: number;
  activo: boolean;
};

export type Desafio = DesafioDatos & { id: number; experiencia_id: number };

export type ElementoFisicoDatos = {
  nombre: string;
  codigo: string;
  descripcion: string;
  desafio_id: number | null;
};

export type ElementoFisico = ElementoFisicoDatos & {
  id: number;
  experiencia_id: number;
};

export type DesafioPublico = {
  id: number;
  orden: number;
  tipo: TipoDesafio;
  titulo: string;
  consigna: string;
  puntos: number;
};

export type Partida = {
  token: string;
  estado: "en_curso" | "completada" | "tiempo_agotado";
  puntos: number;
  pistas_utilizadas: number;
  segundos_restantes: number;
  desafio: DesafioPublico | null;
  total_desafios: number;
  desafios_resueltos: number;
  feedback: string | null;
  pista: string | null;
};

