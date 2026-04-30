// ─── Enums ────────────────────────────────────────────────────────────────────

export enum TipoTorneo {
  KNOCKOUT = "KNOCKOUT",
  ROUND_ROBIN = "ROUND_ROBIN",
  HYBRID = "HYBRID",
}

export enum CategoriaTorneo {
  PRIMARY = "PRIMARY",
  SECONDARY = "SECONDARY",
}

export enum EstadoTorneo {
  DRAFT = "DRAFT",
  REGISTRATION_OPEN = "REGISTRATION_OPEN",
  REGISTRATION_CLOSED = "REGISTRATION_CLOSED",
  IN_PROGRESS = "IN_PROGRESS",
  FINISHED = "FINISHED",
  CANCELLED = "CANCELLED",
}

// ─── Request ──────────────────────────────────────────────────────────────────

/** Body que se envía al backend en POST /api/torneos */
export interface CreateTournamentRequest {
  nombre: string;
  descripcion?: string;
  fecha_inicio: string;               // ISO date "YYYY-MM-DD"
  fecha_fin: string;
  fecha_inicio_inscripcion: string;
  fecha_fin_inscripcion: string;
  max_equipos: number;
  min_equipos: number;
  tipo_torneo: TipoTorneo;
  categorias_habilitadas: CategoriaTorneo[];
}

// ─── Response ─────────────────────────────────────────────────────────────────

/** Objeto torneo que devuelve el backend tras la creación (HTTP 201) */
export interface Tournament {
  id: string;
  nombre: string;
  descripcion: string;
  organizador_id: string;
  fecha_inicio: string;
  fecha_fin: string;
  fecha_inicio_inscripcion: string;
  fecha_fin_inscripcion: string;
  max_equipos: number;
  min_equipos: number;
  tipo_torneo: TipoTorneo;
  categorias_habilitadas: CategoriaTorneo[];
  estado: EstadoTorneo;
  created_at: string;
  updated_at: string;
}

// ─── Validation Error ─────────────────────────────────────────────────────────

// Estructura de error de validación que retorna el backend
export interface TournamentFieldError {
  campo: string;
  error: string;
}

// ─── Configuración del torneo (HU-GT-03) ─────────────────────────────────────────────────

export enum CriterioByeKO {
  RANKING = "RANKING",
  ALEATORIO = "ALEATORIO",
}

export enum CriterioDesempate {
  PUNTOS = "PUNTOS",
  DIFF_PUNTAJE = "DIFF_PUNTAJE",
  ENFRENTAMIENTO_DIRECTO = "ENFRENTAMIENTO_DIRECTO",
  PUNTAJE_FAVOR = "PUNTAJE_FAVOR",
  NOMBRE_ALFABETICO = "NOMBRE_ALFABETICO",
}

// Configuración si se elige el formato Knockout (eliminación directa)
export interface ConfigKnockout {
  semilla_habilitada: boolean;
  tercer_lugar: boolean;
  criterio_bye: CriterioByeKO;
}

// Configuración si se elige el formato Round Robin (todos contra todos)
export interface ConfigRoundRobin {
  num_vueltas: 1 | 2;
  puntos_victoria: number;
  puntos_empate: number;
  puntos_derrota: number;
  criterios_desempate: CriterioDesempate[];
}

// Configuración si se elige el formato Híbrido (fase de grupos y luego eliminación)
export interface ConfigHybrid {
  equipos_por_grupo: number;
  clasificados_por_grupo: number;
  num_vueltas_grupos: 1 | 2;
  formato_fase_final: "KNOCKOUT";
  tercer_lugar_final: boolean;
  criterios_desempate: CriterioDesempate[];
}

export type ConfigTorneo = ConfigKnockout | ConfigRoundRobin | ConfigHybrid;

// Petición para actualizar las reglas del torneo
export interface UpdateConfigRequest {
  config_torneo: ConfigTorneo;
}

// ─── Estructuras de los partidos (HU-GT-04) ───────────────────────────────────────────────────────

export enum EstadoPartido {
  PENDING = "PENDING",
  IN_PROGRESS = "IN_PROGRESS",
  FINISHED = "FINISHED",
  BYE = "BYE",
}

export enum FaseHibrido {
  GRUPOS = "GRUPOS",
  FINAL = "FINAL",
}

export interface Partido {
  id: string;
  torneo_id: string;
  ronda: number;
  posicion_en_ronda: number;
  equipo_local_id: string | null;
  equipo_visitante_id: string | null;
  es_bye: boolean;
  es_descanso: boolean;
  grupo_id: string | null;
  fase: FaseHibrido | null;
  estado: EstadoPartido;
  ganador_id: string | null;
  partido_siguiente_id: string | null;
  fecha_programada: string | null;
}

// ─── Estructuras de resultados (HU-GT-06) ───────────────────────────────────────────────────────

export enum EstadoResultado {
  PARTIAL = "PARTIAL",
  DEFINITIVE = "DEFINITIVE",
}

export enum TipoDatoCriterio {
  NUMERICO = "NUMERICO",
  BOOLEANO = "BOOLEANO",
}

export interface CriterioEvaluacion {
  id: string;
  torneo_id: string;
  nombre: string;
  descripcion?: string;
  tipo_dato: TipoDatoCriterio;
  peso_porcentual: number;
  valor_minimo?: number;
  valor_maximo?: number;
  mayor_es_mejor: boolean;
  orden: number;
}

export interface ResultadoPartido {
  id: string;
  partido_id: string;
  equipo_id: string;
  criterio_id: string;
  valor_registrado: number;
  valor_normalizado: number;
  estado_resultado: EstadoResultado;
  registrado_por: string;
  created_at: string;
  updated_at: string;
}

export interface RegisterResultRequest {
  criterio_id: string;
  equipo_id: string;
  valor_registrado: number;
  estado_resultado: EstadoResultado;
}

// ─── Estructuras para la tabla de posiciones y bracket (HU-GT-07) ──────────────────────────────────────────

export interface PosicionTabla {
  torneo_id: string;
  equipo_id: string;
  equipo_nombre?: string; // Nombre del equipo para mostrar en la interfaz
  grupo_id: string | null;
  partidos_jugados: number;
  victorias: number;
  empates: number;
  derrotas: number;
  puntos: number;
  puntaje_favor: number;
  puntaje_contra: number;
  diferencia_puntaje: number;
  posicion: number;
}

export enum Medalla {
  ORO = "ORO",
  PLATA = "PLATA",
  BRONCE = "BRONCE",
}

export interface RankingFinal {
  torneo_id: string;
  equipo_id: string;
  equipo_nombre?: string; // Nombre del equipo para facilitar la vista
  posicion_final: number;
  puntaje_total_acumulado: number;
  medalla: Medalla | null;
  mencion_especial: string | null;
}

