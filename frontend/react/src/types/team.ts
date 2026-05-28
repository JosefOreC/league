// Enum para el nivel técnico declarado por el equipo
export enum NivelTecnico {
  BASICO = "BASICO",
  INTERMEDIO = "INTERMEDIO",
  AVANZADO = "AVANZADO",
}

// Enum para el estado de la inscripción del equipo
export enum EstadoInscripcion {
  PENDIENTE = "PENDIENTE",
  APROBADO = "APROBADO",
  RECHAZADO = "RECHAZADO",
}

// Enum para el tipo de institución educativa
export enum TipoInstitucion {
  PUBLICA = "PUBLICA",
  PRIVADA = "PRIVADA",
  CONCERTADA = "CONCERTADA",
}

// Estructura de datos para la institución a la que pertenece el equipo
export interface Institucion {
  id?: string;
  nombre: string;
  tipo: TipoInstitucion;
  ciudad: string;
  pais: string;
}

// Estructura de datos para el docente que asesora al equipo
export interface DocenteAsesor {
  id?: string;
  nombre_completo: string;
  email: string;
  telefono: string;
  institucion_id?: string;
}

// Estructura de datos para un participante individual
export interface Participante {
  id?: string;
  nombres: string;
  apellidos: string;
  edad: number;
  grado_academico: string;
  rol_en_equipo?: string;
  documento_identidad: string;
  autorizacion_datos: boolean;
}

// Interfaz principal para el Equipo
export interface Equipo {
  id: string;
  tournament_id: string;
  name: string;
  category: string;
  institution_id: string;
  nivel_tecnico_declarado: NivelTecnico;
  estado_inscripcion: EstadoInscripcion;
  fecha_inscripcion: string;
  representante_id: string;
  docente_asesor_id: string;
  participants?: Participante[];
}

// Formato de los datos que se envían para registrar un nuevo equipo
export interface RegisterTeamRequest {
  nombre: string;
  categoria: string;
  nivel_tecnico_declarado: NivelTecnico;
  institucion: Institucion;
  docente_asesor: DocenteAsesor;
  participantes: Participante[];
}
