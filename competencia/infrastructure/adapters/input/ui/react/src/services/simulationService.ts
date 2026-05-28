import { api } from "./api";
import {
  ConfigurarSimulacionRequest,
  EjecucionSimulacionResponse,
  PanelDocenteResponse,
  PracticaLibreRequest,
  PrediccionSimulacion,
  RetroalimentacionSimulacion,
  SimulacionSesion,
} from "../types/simulation";
import {
  mockConfigurarSimulacion,
  mockEjecutarSimulacion,
  mockIniciarPracticaLibre,
  mockObtenerPanelDocente,
  mockObtenerPrediccion,
  mockObtenerRetroalimentacion,
} from "./simulationService.mock";

/**
 * Mientras el backend de simulación no exista, usamos mocks.
 * Para apuntar al backend real: definir VITE_USE_MOCKS=false en .env.
 */
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== "false";

/** HU-SIM-01 — POST /api/simulacion/configurar */
export async function configurarSimulacion(
  payload: ConfigurarSimulacionRequest
): Promise<SimulacionSesion> {
  if (USE_MOCKS) return mockConfigurarSimulacion(payload);
  const response = await api.post<SimulacionSesion>("simulacion/configurar/", payload);
  return response.data;
}

/** HU-SIM-02 — POST /api/simulacion/:id/ejecutar */
export async function ejecutarSimulacion(
  simulacionId: string
): Promise<EjecucionSimulacionResponse> {
  if (USE_MOCKS) return mockEjecutarSimulacion(simulacionId);
  const response = await api.post<EjecucionSimulacionResponse>(
    `simulacion/${simulacionId}/ejecutar/`
  );
  return response.data;
}

/** HU-SIM-03 — GET /api/simulacion/:id/prediccion */
export async function obtenerPrediccion(
  simulacionId: string
): Promise<PrediccionSimulacion> {
  if (USE_MOCKS) return mockObtenerPrediccion(simulacionId);
  const response = await api.get<PrediccionSimulacion>(
    `simulacion/${simulacionId}/prediccion/`
  );
  return response.data;
}

/** HU-SIM-04 — GET /api/simulacion/panel?equipo_id=... */
export async function obtenerPanelDocente(
  equipoId: string
): Promise<PanelDocenteResponse> {
  if (USE_MOCKS) return mockObtenerPanelDocente(equipoId);
  const response = await api.get<PanelDocenteResponse>("simulacion/panel/", {
    params: { equipo_id: equipoId },
  });
  return response.data;
}

/** HU-SIM-05 — GET /api/simulacion/:id/retroalimentacion */
export async function obtenerRetroalimentacion(
  simulacionId: string
): Promise<RetroalimentacionSimulacion> {
  if (USE_MOCKS) return mockObtenerRetroalimentacion(simulacionId);
  const response = await api.get<RetroalimentacionSimulacion>(
    `simulacion/${simulacionId}/retroalimentacion/`
  );
  return response.data;
}

/** HU-SIM-06 — POST /api/simulacion/practica-libre */
export async function iniciarPracticaLibre(
  payload: PracticaLibreRequest
): Promise<EjecucionSimulacionResponse> {
  if (USE_MOCKS) return mockIniciarPracticaLibre(payload);
  const response = await api.post<EjecucionSimulacionResponse>(
    "simulacion/practica-libre/",
    payload
  );
  return response.data;
}
