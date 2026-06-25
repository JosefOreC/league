/* Tipos del módulo de Analítica (MVP3) — reflejan EXACTAMENTE el JSON
 * que devuelve el backend en /api/analitica/...
 * Fuente: analitica/infrastructure/adapters/input/api/analisis_views.py
 */

/* ── HU-AN-01 · Análisis Integral ─────────────────────────────────────────── */
export interface EquipoExtremo {
  equipo_id: string;
  nombre: string;
  puntaje_total: number;
  posicion_final: number;
  medalla: string | null;
}

export interface DistribucionCriterio {
  criterio_id: string;
  criterio_nombre: string;
  peso: number;
  promedio: number;
  maximo: number;
  minimo: number;
  desviacion_estandar: number;
}

export interface RankingItem {
  equipo_id?: string;
  equipo_nombre?: string;
  categoria?: string;
  posicion_final?: number;
  puntaje_total_acumulado?: number;
  medalla?: string | null;
  // alias tolerantes
  posicion?: number;
  nombre?: string;
  institucion?: string;
  puntaje_total?: number;
  [k: string]: unknown;
}

export interface AnalisisIntegralDTO {
  torneo_id: string;
  torneo_nombre: string;
  categoria_filtrada: string | null;
  metricas_globales: {
    total_equipos: number;
    total_partidos: number;
    puntaje_promedio_global: number;
    desviacion_estandar_global: number;
    puntaje_maximo: number;
    puntaje_minimo: number;
  };
  equipo_max: EquipoExtremo;
  equipo_min: EquipoExtremo;
  distribucion_criterios: DistribucionCriterio[];
  ranking_final: RankingItem[];
}

/* ── HU-AN-02 · Reporte Individual ────────────────────────────────────────── */
export interface PartidoDTO {
  partido_id: string;
  ronda: number;
  rival_id: string;
  rival_nombre: string;
  puntaje_equipo: number;
  puntaje_rival: number;
  ganador_id: string | null;
  es_victoria: boolean;
  fecha_programada: string | null;
}

export interface DetalleCriterioDTO {
  criterio_id: string;
  criterio_nombre: string;
  peso: number;
  promedio_equipo: number;
  maximo_equipo: number;
  minimo_equipo: number;
  promedio_torneo: number;
  comparativa_vs_promedio_pct: number;
}

export interface EvolucionRondaDTO {
  ronda: number;
  puntaje_ronda: number;
  puntaje_acumulado: number;
}

export interface ReporteIndividualDTO {
  torneo_id: string;
  torneo_nombre: string;
  equipo: {
    equipo_id: string;
    nombre: string;
    categoria: string;
    institucion: string;
    posicion_final: number;
    medalla: string | null;
  };
  resumen: {
    total_partidos_jugados: number;
    victorias: number;
    derrotas: number;
    puntaje_total_acumulado: number;
    promedio_puntaje_torneo: number;
    comparativa_vs_promedio_torneo_pct: number;
  };
  partidos: PartidoDTO[];
  detalle_criterios: DetalleCriterioDTO[];
  evolucion_por_ronda: EvolucionRondaDTO[];
}

/* ── HU-AN-04 · Tablero de Inteligencia ───────────────────────────────────── */
export interface TopEquipoDTO {
  equipo_id: string;
  equipo_nombre: string;
  posicion_actual: number;
  puntaje_acumulado: number;
  partidos_jugados: number;
  victorias: number;
  medalla: string | null;
}

export interface PartidoProximoDTO {
  partido_id: string;
  ronda: number;
  equipo_local_id: string;
  equipo_local_nombre: string;
  equipo_visitante_id: string;
  equipo_visitante_nombre: string;
  estado: string;
  fecha_programada: string | null;
  minutos_retraso: number | null;
}

export interface AlertaDTO {
  tipo: string;
  severidad: string;
  mensaje: string;
  entidad_ref_id: string | null;
  minutos_retraso: number | null;
}

export interface TableroInteligenciaDTO {
  torneo_id: string;
  torneo_nombre: string;
  estado_torneo: string;
  metricas: {
    total_equipos: number;
    total_partidos: number;
    partidos_finalizados: number;
    partidos_pendientes: number;
    partidos_en_progreso: number;
    porcentaje_avance: number;
  };
  top_3: TopEquipoDTO[];
  partidos_proximos: PartidoProximoDTO[];
  alertas_activas: AlertaDTO[];
}

/* ── HU-AN-08 · Panel Docente ─────────────────────────────────────────────── */
export interface CriterioPanelDTO {
  criterio_id: string;
  criterio_nombre: string;
  peso: number;
  promedio_equipo: number;
  promedio_torneo: number;
  percentil: number;
  maximo_torneo: number;
  minimo_torneo: number;
}

export interface RecomendacionDTO {
  criterio_id: string;
  criterio_nombre: string;
  tipo: string;
  percentil: number;
  descripcion: string;
  acciones_sugeridas: string[];
}

export interface PanelDocenteDTO {
  torneo_id: string;
  torneo_nombre: string;
  estado_panel: string;
  advertencia: string | null;
  docente: { docente_asesor_id: string; nombre: string };
  equipo: {
    equipo_id: string;
    nombre: string;
    posicion_final: number;
    medalla: string | null;
    puntaje_total_acumulado: number;
    total_partidos_jugados: number;
  };
  criterios: CriterioPanelDTO[];
  recomendaciones: RecomendacionDTO[];
}
