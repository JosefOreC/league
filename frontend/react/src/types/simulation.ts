// ─── Enums ────────────────────────────────────────────────────────────────────
export enum CasoReto {
  PROGRAMACION = "PROGRAMACION",
  COMPONENTES = "COMPONENTES",
}

// ─── 2.1 Telemetría predictiva (POST /predecir, GET /historial) ────────────────
export interface TelemetriaPredictivaRequest {
  participante_id: number;
  torneo_id: number;
  tiempo_estimado: number;
  complejidad_codigo: number; // 1..10
  colisiones_historicas: number;
  telemetria_velocidad_prom: number;
  telemetria_errores: number;
}

export interface PrediccionTelemetriaResponse {
  id: number;
  puntaje_estimado: number;
  tiempo_probable_fin: number;
  rmse_validacion: number;
  modelo_version: string; // "v1"
}

export interface HistorialPrediccion {
  id: number;
  torneo_id: number;
  tiempo_estimado: number;
  complejidad_codigo: number;
  colisiones_historicas: number;
  telemetria_json: {
    velocidad_promedio: number;
    errores: number;
  };
  puntaje_estimado: number | null;
  tiempo_probable_fin: number | null;
  rmse_validacion: number | null;
  creado_en: string; // ISO timestamp
  modelo_version: string;
  es_oficial: boolean;
}

// ─── 2.2 Retos del torneo (GET /retos) ─────────────────────────────────────────
export interface CriterioRetoIA {
  nombre: string;
  peso: number; // porcentaje
}

export interface RetoTorneo {
  id: string;
  torneo_id: string;
  titulo: string;
  descripcion: string;
  caso: CasoReto;
  criterios_evaluacion: CriterioRetoIA[];
}

// ─── 2.3 Análisis de entrega (POST /analisis/{programacion|componentes}) ───────
export interface AnalisisProgramacionRequest {
  reto_id: string;
  participante_id: string;
  torneo_id: string;
  codigo_fuente: string;
}

export interface AnalisisComponentesRequest {
  reto_id: string;
  participante_id: string;
  torneo_id: string;
  descripcion_solucion: string;
}

export interface CalificacionCriterio {
  criterio: string;
  puntos: number;
  max_puntos: number;
}

export interface AnalisisEntregaResponse {
  id: string;
  caso: CasoReto;
  reto_id: string;
  puntaje_total_simulado: number;
  calificaciones_por_criterio: CalificacionCriterio[];
  observacion_general: string;
  creado_en: string;
}

// ─── 2.4 Contexto + ejecución de simulación (GET /contexto, POST /ejecutar) ─────
export interface SimulationContextTournament {
  id: string;
  name: string;
  state: string;
  category: string;
}

export interface SimulationContextTeam {
  id: string;
  name: string;
  nivel_tecnico_declarado: string;
  participants_count: number;
}

export interface SimulationCriterion {
  id: string;
  name: string;
  description: string;
  peso: number;
  min_qualification: number;
  max_qualification: number;
}

export interface SimulationContext {
  tournament: SimulationContextTournament;
  team: SimulationContextTeam;
  criterios: SimulationCriterion[];
}

export interface CriterionScore {
  criterio_id: string;
  nombre: string;
  peso: number;
  valor_simulado: number;
  valor_normalizado: number;
  en_rango: boolean;
}

// IMPORTANTE: posicion_estimada es un OBJETO ANIDADO, no un escalar
export interface PosicionEstimada {
  posicion_estimada: number;
  total_equipos: number;
  percentil: number;
}

export interface StrengthOrWeakness {
  criterio_id: string;
  nombre: string;
  valor_normalizado: number;
  motivo?: string;
}

export interface SimulationFeedback {
  resumen: string;
  recomendaciones: string[];
  sin_mejoras_criticas?: boolean;
}

export interface SimulationResult {
  simulation_id: string;
  scores: CriterionScore[];
  puntaje_total: number;
  posicion_estimada: PosicionEstimada; // anidado
  fortalezas: StrengthOrWeakness[];
  debilidades: StrengthOrWeakness[];
  retroalimentacion: SimulationFeedback;
}

export interface RunSimulationRequest {
  entregable: string;
}
