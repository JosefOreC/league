// ─── Enums ────────────────────────────────────────────────────────────────────

export enum EstadoSimulacion {
  CONFIGURADA = "CONFIGURADA",
  COMPLETADA = "COMPLETADA",
}

export enum NivelDificultad {
  PRINCIPIANTE = "PRINCIPIANTE",
  INTERMEDIO = "INTERMEDIO",
  AVANZADO = "AVANZADO",
  RETO_EXTREMO = "RETO_EXTREMO",
}

export enum FormatoSimulacion {
  KNOCKOUT = "KNOCKOUT",
  ROUND_ROBIN = "ROUND_ROBIN",
  HYBRID = "HYBRID",
}

// ─── Requests ─────────────────────────────────────────────────────────────────

/** HU-SIM-01 — POST /api/simulacion/configurar */
export interface ConfigurarSimulacionRequest {
  torneo_id: string;
  nivel_dificultad: NivelDificultad;
  num_equipos_simulados: number;
  formato: FormatoSimulacion;
}

/** HU-SIM-06 — POST /api/simulacion/practica-libre */
export interface PracticaLibreRequest {
  nivel_dificultad: NivelDificultad;
  formato: FormatoSimulacion;
  num_equipos: number;
}

// ─── Responses ────────────────────────────────────────────────────────────────

/** Sesión creada tras configurar (HU-SIM-01) o tras práctica libre (HU-SIM-06) */
export interface SimulacionSesion {
  simulacion_id: string;
  torneo_id: string | null;            // null en práctica libre
  equipo_id: string | null;            // null en práctica libre sin equipo
  nivel_dificultad: NivelDificultad;
  num_equipos_simulados: number;
  formato: FormatoSimulacion;
  estado: EstadoSimulacion;
  es_practica_libre: boolean;
  created_at: string;
}

/** Resultado de un enfrentamiento simulado (HU-SIM-02) */
export interface EnfrentamientoSimulado {
  equipo_local_id: string;
  equipo_visitante_id: string;
  puntaje_estimado_local: number;
  puntaje_estimado_visitante: number;
  posicion_estimada: number;
  nivel_confianza: number;              // 0.0 – 1.0
}

/** Resumen devuelto por POST /api/simulacion/:id/ejecutar (HU-SIM-02) */
export interface EjecucionSimulacionResponse {
  simulacion_id: string;
  estado: EstadoSimulacion;
  enfrentamientos: EnfrentamientoSimulado[];
  duracion_ms: number;
}

/** Item de fortaleza o debilidad (HU-SIM-03) */
export interface CriterioDesempeno {
  criterio_id: string;
  criterio_nombre: string;
  puntaje_porcentaje: number;           // 0 – 100
  recomendacion_mejora: string;
}

/** GET /api/simulacion/:id/prediccion (HU-SIM-03) */
export interface PrediccionSimulacion {
  simulacion_id: string;
  posicion_estimada: number;
  puntaje_total_estimado: number;
  margen_error: number;                 // ± posiciones
  nivel_confianza: number;              // 0.0 – 1.0
  fortalezas: CriterioDesempeno[];      // criterios con puntaje ≥ 75 %
  debilidades: CriterioDesempeno[];     // criterios con puntaje < 50 %
  advertencia?: string;                 // presente si nivel_confianza < 0.60
}

/** Item del panel del docente (HU-SIM-04) */
export interface SimulacionPanelItem {
  simulacion_id: string;
  fecha: string;                        // ISO
  posicion_estimada: number;
  puntaje_total: number;
  nivel_confianza: number;
}

/** Punto del gráfico de evolución (HU-SIM-04) */
export interface PuntoEvolucion {
  fecha: string;                        // ISO
  puntaje: number;
}

/** GET /api/simulacion/panel?equipo_id=... */
export interface PanelDocenteResponse {
  equipo_id: string;
  equipo_nombre?: string;
  simulaciones: SimulacionPanelItem[];
  evolucion: PuntoEvolucion[];
  mensaje?: string;                     // p. ej. "Este equipo aún no ha realizado simulaciones"
}

/**
 * GET /api/simulacion/:id/retroalimentacion (HU-SIM-05)
 *
 * La HU original tiene los criterios de aceptación copiados de la HU-SIM-04.
 * Esta forma es una propuesta tentativa hasta que el equipo aclare el contrato.
 */
export interface RetroalimentacionCriterio {
  criterio_id: string;
  criterio_nombre: string;
  puntaje_obtenido: number;
  puntaje_esperado: number;
  gap: number;                          // puntaje_esperado - puntaje_obtenido
  accion_recomendada: string;
}

export interface RetroalimentacionSimulacion {
  simulacion_id: string;
  resumen: string;
  criterios: RetroalimentacionCriterio[];
  generado_at: string;
}

// ─── Errores ──────────────────────────────────────────────────────────────────

export interface SimulacionError {
  error: string;
}
