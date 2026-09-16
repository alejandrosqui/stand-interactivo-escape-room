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

