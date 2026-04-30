// ─── Enums ────────────────────────────────────────────────────────────────────

export enum TipoTorneo {
  KNOCKOUT = "KNOCKOUT",
  ROUND_ROBIN = "ROUND_ROBIN",
  HYBRID = "HYBRID",
}

export enum CategoriaTorneo {
  EXPLORADOR = "explorador",
  INNOVADOR = "innovador",
  CONSTRUCTOR = "constructor",
}

export enum EstadoTorneo {
  DRAFT = "draft",
  IN_REVIEW = "in_review",
  REGISTRATION_OPEN = "registration_open",
  REGISTRATION_CLOSED = "registration_closed",
  IN_PROGRESS = "in_progress",
  FINISHED = "finalized",
  CANCELLED = "cancelled",
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
  name: string;
  description: string;
  creator_user_id: string;
  date_start: string;
  date_end: string;
  state: EstadoTorneo;
  category: CategoriaTorneo;
  created_at?: string;
  updated_at?: string;
  tournament_rule?: any;
  tournament_evaluation?: any;
  config_tournament?: any;
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
  seed_enabled: boolean;
  third_place: boolean;
  best_of: number;
}

// Configuración si se elige el formato Round Robin (todos contra todos)
export interface ConfigRoundRobin {
  num_rounds: number;
  point_to_victory: number;
  point_to_draw: number;
  point_to_defeat: number;
  tie_breaking_criteria: string[];
}

// Configuración si se elige el formato Híbrido (fase de grupos y luego eliminación)
export interface ConfigHybrid {
  teams_for_group: number;
  classified_by_group: number;
  num_rounds: number;
  final_format: string;
  third_place: boolean;
}

export type ConfigTorneo = ConfigKnockout | ConfigRoundRobin | ConfigHybrid;

// Petición para actualizar las reglas del torneo (HU-GT-03)
export interface UpdateConfigRequest {
  tournament_rule: {
    id?: string;
    min_members: number;
    max_members: number;
    min_teams: number;
    max_teams: number;
    access_type: "public" | "private";
    validation_list: string[];
    date_start_inscription: string | null;
    date_end_inscription: string | null;
  };
  tournament_config: {
    type: "knockout" | "round_robin" | "hybrid";
    config: ConfigTorneo;
  };
  tournament_evaluation: {
    criterias: Array<{
      id?: string;
      name: string;
      description: string;
      min_value: number;
      max_value: number;
      value: number;
    }>;
  };
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

