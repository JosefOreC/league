import { api } from "./api";
import type {
  TelemetriaPredictivaRequest,
  PrediccionTelemetriaResponse,
  HistorialPrediccion,
  RetoTorneo,
  CasoReto,
  AnalisisProgramacionRequest,
  AnalisisComponentesRequest,
  AnalisisEntregaResponse,
  SimulationContext,
  SimulationResult,
  RunSimulationRequest,
} from "../types/simulation";

// 3.1  POST /api/simulacion/predecir/
export async function predecirTelemetria(
  payload: TelemetriaPredictivaRequest
): Promise<PrediccionTelemetriaResponse> {
  const { data } = await api.post<PrediccionTelemetriaResponse>("simulacion/predecir/", payload);
  return data;
}

// 3.2  GET /api/simulacion/historial/<participante_id>/
export async function getHistorialPredicciones(
  participanteId: number
): Promise<HistorialPrediccion[]> {
  const { data } = await api.get<HistorialPrediccion[]>(`simulacion/historial/${participanteId}/`);
  return data;
}

// 3.3  GET /api/simulacion/retos/<torneo_id>/?caso=...
export async function getRetosTorneo(
  torneoId: string,
  caso?: CasoReto
): Promise<RetoTorneo[]> {
  const url = caso
    ? `simulacion/retos/${torneoId}/?caso=${caso}`
    : `simulacion/retos/${torneoId}/`;
  const { data } = await api.get<RetoTorneo[]>(url);
  return data;
}

// 3.4  POST /api/simulacion/analisis/programacion/
export async function analizarProgramacion(
  payload: AnalisisProgramacionRequest
): Promise<AnalisisEntregaResponse> {
  const { data } = await api.post<AnalisisEntregaResponse>("simulacion/analisis/programacion/", payload);
  return data;
}

// 3.5  POST /api/simulacion/analisis/componentes/
export async function analizarComponentes(
  payload: AnalisisComponentesRequest
): Promise<AnalisisEntregaResponse> {
  const { data } = await api.post<AnalisisEntregaResponse>("simulacion/analisis/componentes/", payload);
  return data;
}

// 3.6  GET /api/simulacion/analisis/<participante_id>/<torneo_id>/
export async function getAnalisisPrevios(
  participanteId: string,
  torneoId: string
): Promise<AnalisisEntregaResponse[]> {
  const { data } = await api.get<AnalisisEntregaResponse[]>(
    `simulacion/analisis/${participanteId}/${torneoId}/`
  );
  return data;
}

// 3.7  GET /api/simulacion/torneo/<tournament_id>/contexto/
export async function getSimulationContext(
  tournamentId: string
): Promise<SimulationContext> {
  const { data } = await api.get<SimulationContext>(`simulacion/torneo/${tournamentId}/contexto/`);
  return data;
}

// 3.8  POST /api/simulacion/torneo/<tournament_id>/ejecutar/
export async function runSimulation(
  tournamentId: string,
  payload: RunSimulationRequest
): Promise<SimulationResult> {
  const { data } = await api.post<SimulationResult>(
    `simulacion/torneo/${tournamentId}/ejecutar/`,
    payload
  );
  return data;
}
