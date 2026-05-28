import {
  ConfigurarSimulacionRequest,
  EjecucionSimulacionResponse,
  EstadoSimulacion,
  PanelDocenteResponse,
  PracticaLibreRequest,
  PrediccionSimulacion,
  RetroalimentacionSimulacion,
  SimulacionSesion,
} from "../types/simulation";

/**
 * Mock service para la Épica 3 (Simulación).
 * Devuelve datos realistas mientras el backend no exista.
 * Toggle con VITE_USE_MOCKS=true (default si la variable no está definida).
 */

// ─── Almacén en memoria ──────────────────────────────────────────────────────

interface StoredSimulacion extends SimulacionSesion {
  ejecucion?: EjecucionSimulacionResponse;
}

const SIMULACIONES = new Map<string, StoredSimulacion>();
let seq = 1;

function nuevaId(): string {
  return `sim-${String(seq++).padStart(4, "0")}`;
}

function delay<T>(value: T, ms = 600): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

// ─── Catálogos simulados ─────────────────────────────────────────────────────

const CRITERIOS = [
  { id: "cr-1", nombre: "Precisión de movimiento" },
  { id: "cr-2", nombre: "Velocidad de ejecución" },
  { id: "cr-3", nombre: "Resolución de obstáculos" },
  { id: "cr-4", nombre: "Trabajo en equipo" },
  { id: "cr-5", nombre: "Estrategia de juego" },
  { id: "cr-6", nombre: "Manejo de tiempo" },
];

const RECOMENDACIONES_FORTALEZA: Record<string, string> = {
  "cr-1": "Mantén las rutinas de calibración antes de cada partida.",
  "cr-2": "Sigue practicando con tiempos cronometrados, vas muy bien.",
  "cr-3": "Tu lectura de obstáculos es sólida; comparte la técnica con el equipo.",
  "cr-4": "La sincronía del equipo es destacable; documéntenla como buena práctica.",
  "cr-5": "Tu planeamiento estratégico es de los más fuertes del grupo.",
  "cr-6": "Gestión de tiempo impecable; mantén el ritmo en eliminatorias.",
};

const RECOMENDACIONES_DEBILIDAD: Record<string, string> = {
  "cr-1": "Refuerza ejercicios de control fino con el robot en pistas reducidas.",
  "cr-2": "Trabaja sprints de 30 s para mejorar velocidad de respuesta.",
  "cr-3": "Practica escenarios con obstáculos móviles imprevistos.",
  "cr-4": "Sesiones de comunicación dirigida pueden mejorar la coordinación.",
  "cr-5": "Estudia partidas previas para anticipar movimientos del rival.",
  "cr-6": "Ensayos cronometrados ayudarán a evitar penalizaciones por tiempo.",
};

// ─── Generadores ─────────────────────────────────────────────────────────────

function generarEnfrentamientos(num: number) {
  return Array.from({ length: num }, (_, i) => ({
    equipo_local_id: "equipo-propio",
    equipo_visitante_id: `equipo-rival-${i + 1}`,
    puntaje_estimado_local: Math.round(60 + Math.random() * 35),
    puntaje_estimado_visitante: Math.round(45 + Math.random() * 40),
    posicion_estimada: i + 1,
    nivel_confianza: Math.round((0.65 + Math.random() * 0.3) * 100) / 100,
  }));
}

function generarPrediccion(simulacionId: string, num: number, tieneHistorial = true): PrediccionSimulacion {
  const confianza = tieneHistorial
    ? Math.round((0.7 + Math.random() * 0.25) * 100) / 100
    : Math.round((0.4 + Math.random() * 0.15) * 100) / 100;

  const puntajesPorCriterio = CRITERIOS.map((c) => ({
    criterio_id: c.id,
    criterio_nombre: c.nombre,
    puntaje_porcentaje: Math.round(25 + Math.random() * 70),
    recomendacion_mejora: "",
  }));

  const fortalezas = puntajesPorCriterio
    .filter((c) => c.puntaje_porcentaje >= 75)
    .map((c) => ({ ...c, recomendacion_mejora: RECOMENDACIONES_FORTALEZA[c.criterio_id] }));

  const debilidades = puntajesPorCriterio
    .filter((c) => c.puntaje_porcentaje < 50)
    .map((c) => ({ ...c, recomendacion_mejora: RECOMENDACIONES_DEBILIDAD[c.criterio_id] }));

  const prediccion: PrediccionSimulacion = {
    simulacion_id: simulacionId,
    posicion_estimada: Math.max(1, Math.round(Math.random() * num)),
    puntaje_total_estimado: Math.round(550 + Math.random() * 250),
    margen_error: Math.max(1, Math.round(2 + Math.random() * 2)),
    nivel_confianza: confianza,
    fortalezas,
    debilidades,
  };

  if (confianza < 0.6) {
    prediccion.advertencia =
      "Predicción con datos limitados. Participa en más simulaciones para mejorar la precisión.";
  }

  return prediccion;
}

function generarRetroalimentacion(simulacionId: string): RetroalimentacionSimulacion {
  return {
    simulacion_id: simulacionId,
    resumen:
      "El equipo muestra buen desempeño general, con áreas claras de oportunidad en velocidad y estrategia.",
    criterios: CRITERIOS.map((c) => {
      const esperado = 75 + Math.round(Math.random() * 15);
      const obtenido = Math.round(40 + Math.random() * 50);
      return {
        criterio_id: c.id,
        criterio_nombre: c.nombre,
        puntaje_obtenido: obtenido,
        puntaje_esperado: esperado,
        gap: Math.max(0, esperado - obtenido),
        accion_recomendada:
          obtenido < 50
            ? RECOMENDACIONES_DEBILIDAD[c.id]
            : "Mantén el ritmo actual y refuerza con repeticiones cronometradas.",
      };
    }),
    generado_at: new Date().toISOString(),
  };
}

function generarPanelDocente(equipoId: string): PanelDocenteResponse {
  if (SIMULACIONES.size === 0) {
    // Sembrar algunas simulaciones de ejemplo para que el coach vea datos
    const ahora = Date.now();
    for (let i = 4; i >= 0; i--) {
      const id = nuevaId();
      const fecha = new Date(ahora - i * 4 * 24 * 60 * 60 * 1000).toISOString();
      SIMULACIONES.set(id, {
        simulacion_id: id,
        torneo_id: "torneo-demo",
        equipo_id: equipoId,
        nivel_dificultad: "INTERMEDIO" as any,
        num_equipos_simulados: 6,
        formato: "ROUND_ROBIN" as any,
        estado: EstadoSimulacion.COMPLETADA,
        es_practica_libre: false,
        created_at: fecha,
      });
    }
  }

  const sims = Array.from(SIMULACIONES.values())
    .filter((s) => s.equipo_id === equipoId && !s.es_practica_libre)
    .sort((a, b) => (b.created_at > a.created_at ? 1 : -1));

  return {
    equipo_id: equipoId,
    equipo_nombre: "Equipo Robotix Junior",
    simulaciones: sims.map((s, idx) => ({
      simulacion_id: s.simulacion_id,
      fecha: s.created_at,
      posicion_estimada: Math.max(1, ((idx * 3) % 8) + 1),
      puntaje_total: 600 + Math.round(Math.random() * 200),
      nivel_confianza: Math.round((0.7 + Math.random() * 0.25) * 100) / 100,
    })),
    evolucion: sims
      .slice()
      .reverse()
      .map((s, idx) => ({
        fecha: s.created_at,
        puntaje: 550 + idx * 35 + Math.round(Math.random() * 50),
      })),
    mensaje: sims.length === 0 ? "Este equipo aún no ha realizado simulaciones" : undefined,
  };
}

// ─── Funciones públicas ──────────────────────────────────────────────────────

export async function mockConfigurarSimulacion(
  payload: ConfigurarSimulacionRequest
): Promise<SimulacionSesion> {
  const id = nuevaId();
  const sesion: StoredSimulacion = {
    simulacion_id: id,
    torneo_id: payload.torneo_id,
    equipo_id: "equipo-propio",
    nivel_dificultad: payload.nivel_dificultad,
    num_equipos_simulados: payload.num_equipos_simulados,
    formato: payload.formato,
    estado: EstadoSimulacion.CONFIGURADA,
    es_practica_libre: false,
    created_at: new Date().toISOString(),
  };
  SIMULACIONES.set(id, sesion);
  return delay(sesion, 500);
}

export async function mockEjecutarSimulacion(
  simulacionId: string
): Promise<EjecucionSimulacionResponse> {
  const sesion = SIMULACIONES.get(simulacionId);
  if (!sesion) {
    throw { response: { status: 404, data: { error: "Simulación no encontrada" } } };
  }
  if (sesion.estado === EstadoSimulacion.COMPLETADA) {
    throw {
      response: {
        status: 409,
        data: {
          error:
            "Esta simulación ya fue ejecutada. Cree una nueva sesión para volver a simular",
        },
      },
    };
  }

  const enfrentamientos = generarEnfrentamientos(sesion.num_equipos_simulados);
  const ejecucion: EjecucionSimulacionResponse = {
    simulacion_id: simulacionId,
    estado: EstadoSimulacion.COMPLETADA,
    enfrentamientos,
    duracion_ms: 2400 + Math.round(Math.random() * 1500),
  };

  sesion.estado = EstadoSimulacion.COMPLETADA;
  sesion.ejecucion = ejecucion;
  SIMULACIONES.set(simulacionId, sesion);
  return delay(ejecucion, 2500);
}

export async function mockObtenerPrediccion(
  simulacionId: string
): Promise<PrediccionSimulacion> {
  const sesion = SIMULACIONES.get(simulacionId);
  if (!sesion) {
    throw { response: { status: 404, data: { error: "Simulación no encontrada" } } };
  }
  return delay(generarPrediccion(simulacionId, sesion.num_equipos_simulados), 500);
}

export async function mockObtenerPanelDocente(equipoId: string): Promise<PanelDocenteResponse> {
  return delay(generarPanelDocente(equipoId), 500);
}

export async function mockObtenerRetroalimentacion(
  simulacionId: string
): Promise<RetroalimentacionSimulacion> {
  return delay(generarRetroalimentacion(simulacionId), 500);
}

export async function mockIniciarPracticaLibre(
  payload: PracticaLibreRequest
): Promise<EjecucionSimulacionResponse> {
  const id = nuevaId();
  const sesion: StoredSimulacion = {
    simulacion_id: id,
    torneo_id: null,
    equipo_id: null,
    nivel_dificultad: payload.nivel_dificultad,
    num_equipos_simulados: payload.num_equipos,
    formato: payload.formato,
    estado: EstadoSimulacion.COMPLETADA,
    es_practica_libre: true,
    created_at: new Date().toISOString(),
  };

  const enfrentamientos = generarEnfrentamientos(payload.num_equipos);
  const ejecucion: EjecucionSimulacionResponse = {
    simulacion_id: id,
    estado: EstadoSimulacion.COMPLETADA,
    enfrentamientos,
    duracion_ms: 1800 + Math.round(Math.random() * 1200),
  };

  sesion.ejecucion = ejecucion;
  SIMULACIONES.set(id, sesion);
  return delay(ejecucion, 2000);
}
