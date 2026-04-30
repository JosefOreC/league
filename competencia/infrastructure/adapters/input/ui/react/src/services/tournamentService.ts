import { api } from "./api";
import type {
  CreateTournamentRequest,
  Tournament,
  UpdateConfigRequest,
} from "../types/tournament";

/**
 * Crea un nuevo torneo, enviando el formato JSON que espera el backend.
 * (POST /competencia/create_tournament o /competencia/create/)
 */
export async function createTournament(data: CreateTournamentRequest): Promise<Tournament> {
  // Adaptar el payload del frontend al formato exacto de la HU-GT-02
  const payload = {
    name: data.nombre,
    description: data.descripcion || "",
    // Fechas de competencia (ISO 8601)
    date_start: `${data.fecha_inicio}T09:00:00`,
    date_end: `${data.fecha_fin}T18:00:00`,
    // CAPA DE TRADUCCIÓN: UI (PRIMARY/SECONDARY) -> Backend (explorador/innovador)
    category: data.categorias_habilitadas[0] === CategoriaTorneo.PRIMARY ? "explorador" : "innovador",
    // Limites de equipos
    max_teams: Number(data.max_equipos),
  };

  console.log("[TournamentService] Payload final para el backend:", payload);
  
  console.log("[TournamentService] Enviando petición POST a:", api.defaults.baseURL + "/competencia/create/");
  const response = await api.post<Tournament>("/competencia/create/", payload);
  console.log("[TournamentService] Respuesta recibida:", response.status, response.data);
  return response.data;
}

/**
 * Configura las reglas, el tipo de torneo y la evaluación.
 * (PUT /competencia/config_tournament_rules/{id}/)
 */
export async function configTournamentRules(id: string, payload: any): Promise<Tournament> {
  console.log(`[tournamentService] Configurando reglas para torneo ${id}`);
  const response = await api.put<Tournament>(`/competencia/torneo/${id}/rules/`, payload);
  return response.data;
}

/**
 * Pasa a revisión un torneo (Human In The Loop o revisión por organizadores)
 * (POST /competencia/review_tournament/{id}/)
 */
export async function reviewTournament(id: string): Promise<Tournament> {
  const response = await api.post<Tournament>(`/competencia/torneo/${id}/review/`);
  return response.data;
}

/**
 * Abre las inscripciones del torneo.
 * (POST /competencia/open_registrations/{id}/)
 */
export async function openRegistrations(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Abriendo inscripciones para torneo ${id}`);
  const response = await api.post<Tournament>(`/competencia/torneo/${id}/open-registrations/`);
  return response.data;
}

/**
 * Cierra las inscripciones del torneo.
 * (POST /competencia/close_registrations/{id}/)
 */
export async function closeRegistrations(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Cerrando inscripciones para torneo ${id}`);
  const response = await api.post<Tournament>(`/competencia/torneo/${id}/close-registrations/`);
  return response.data;
}

/**
 * Inicia el torneo y genera los fixtures automáticamente.
 * (POST /competencia/start_tournament/{id}/)
 */
export async function startTournament(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Iniciando torneo ${id}`);
  const response = await api.post<Tournament>(`/competencia/torneo/${id}/start/`);
  return response.data;
}

/**
 * Cancela el torneo.
 * (POST /competencia/cancel_tournament/{id}/)
 */
export async function cancelTournament(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Cancelando torneo ${id}`);
  const response = await api.post<Tournament>(`/competencia/torneo/${id}/cancel/`);
  return response.data;
}

// ----------------------------------------------------------------------
// Consultas Generales (GET)
// ----------------------------------------------------------------------

export async function getTournaments(): Promise<Tournament[]> {
  const response = await api.get<Tournament[]>("/competencia/all/");
  return response.data;
}

export async function getTournamentById(id: string): Promise<Tournament> {
  const response = await api.get<Tournament>(`/competencia/torneo/${id}/`);
  return response.data;
}

// ----------------------------------------------------------------------
// Resultados / Gestión de Partidos (Para futuras HU)
// ----------------------------------------------------------------------

export async function registerMatchResults(
  torneoId: string,
  partidoId: string,
  resultados: import("../types/tournament").RegisterResultRequest[]
): Promise<import("../types/tournament").ResultadoPartido[]> {
  const response = await api.post(`/torneos/${torneoId}/partidos/${partidoId}/resultados/`, { resultados });
  return response.data;
}

export async function finalizeMatch(
  torneoId: string,
  partidoId: string
): Promise<void> {
  await api.post(`/torneos/${torneoId}/partidos/${partidoId}/finalizar/`);
}

export async function getTournamentStandings(
  torneoId: string
): Promise<import("../types/tournament").PosicionTabla[]> {
  const response = await api.get(`/torneos/${torneoId}/tabla-posiciones/`);
  return response.data;
}

export async function getTournamentBracket(
  torneoId: string
): Promise<import("../types/tournament").Partido[]> {
  const response = await api.get(`/torneos/${torneoId}/bracket/`);
  return response.data;
}
