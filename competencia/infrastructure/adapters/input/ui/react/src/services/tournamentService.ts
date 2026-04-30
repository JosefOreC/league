import { api } from "./api";
import {
  CreateTournamentRequest,
  Tournament,
  UpdateConfigRequest,
  CategoriaTorneo,
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
    category: data.categorias_habilitadas[0] || CategoriaTorneo.EXPLORADOR,
    // Limites de equipos
    max_teams: Number(data.max_equipos),
  };

  console.log("[TournamentService] Payload final para el backend:", payload);

  console.log("[TournamentService] Enviando petición POST a:", api.defaults.baseURL + "competencia/create/");
  const response = await api.post<Tournament>("competencia/create/", payload);
  console.log("[TournamentService] Respuesta recibida:", response.status, response.data);
  return response.data;
}

/**
 * Configura las reglas, el tipo de torneo y la evaluación.
 * (PUT /api/competencia/torneo/{id}/rules/)
 */
export async function configTournamentRules(id: string, payload: UpdateConfigRequest): Promise<Tournament> {
  console.log(`[tournamentService] Configurando reglas para torneo ${id}`);
  const response = await api.put<Tournament>(`competencia/torneo/${id}/rules/`, payload);
  return response.data;
}

/**
 * Pasa a revisión un torneo (Human In The Loop o revisión por organizadores)
 * (POST /competencia/review_tournament/{id}/)
 */
export async function reviewTournament(id: string): Promise<Tournament> {
  const response = await api.post<Tournament>(`competencia/torneo/${id}/review/`);
  return response.data;
}

/**
 * Vuelve el torneo a estado borrador.
 * (POST /api/competencia/torneo/{id}/draft/)
 * Nota: Verificar si este endpoint existe en el backend, por ahora se mantiene la firma.
 */
export async function backToDraft(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Volviendo a borrador torneo ${id}`);
  const response = await api.post<Tournament>(`competencia/torneo/${id}/draft/`);
  return response.data;
}

/**
 * Abre las inscripciones del torneo.
 * (POST /competencia/open_registrations/{id}/)
 */
export async function openRegistrations(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Abriendo inscripciones para torneo ${id}`);
  const response = await api.post<Tournament>(`competencia/torneo/${id}/open-registrations/`);
  return response.data;
}

/**
 * Cierra las inscripciones del torneo.
 * (POST /competencia/close_registrations/{id}/)
 */
export async function closeRegistrations(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Cerrando inscripciones para torneo ${id}`);
  const response = await api.post<Tournament>(`competencia/torneo/${id}/close-registrations/`);
  return response.data;
}

/**
 * Inicia el torneo y genera los fixtures automáticamente.
 * (POST /competencia/start_tournament/{id}/)
 */
export async function startTournament(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Iniciando torneo ${id}`);
  const response = await api.post<Tournament>(`competencia/torneo/${id}/start/`);
  return response.data;
}

/**
 * Cancela el torneo.
 * (POST /competencia/cancel_tournament/{id}/)
 */
export async function cancelTournament(id: string): Promise<Tournament> {
  console.log(`[tournamentService] Cancelando torneo ${id}`);
  const response = await api.post<Tournament>(`competencia/torneo/${id}/cancel/`);
  return response.data;
}

/**
 * Genera los fixtures del torneo (HU-GT-04).
 */
export async function generateFixtures(id: string): Promise<any> {
  console.log(`[tournamentService] Generando fixtures para torneo ${id}`);
  const response = await api.post(`competencia/torneo/${id}/generar-fixtures/`);
  return response.data;
}

// ----------------------------------------------------------------------
// Consultas Generales (GET)
// ----------------------------------------------------------------------

export async function getTournaments(): Promise<Tournament[]> {
  const response = await api.get<Tournament[]>("competencia/all/");
  return response.data;
}

export async function getTournamentById(id: string): Promise<Tournament> {
  const response = await api.get<Tournament>(`competencia/torneo/${id}/`);
  return response.data;
}

// ----------------------------------------------------------------------
// Resultados / Gestión de Partidos (Para futuras HU)
// ----------------------------------------------------------------------

export async function registerMatchResults(
  torneoId: string,
  partidoId: string,
  resultados: any
): Promise<any> {
  if (!torneoId) throw new Error("ID de torneo no encontrado");
  console.log(`[tournamentService] Registrando resultados para partido ${partidoId} en torneo ${torneoId}`);
  const response = await api.post(`competencia/partido/${partidoId}/resultado/`, { results: resultados });
  return response.data;
}

/**
 * Finaliza un partido y calcula al ganador (HU-GT-06).
 */
export async function finalizeMatch(
  partidoId: string
): Promise<any> {
  console.log(`[tournamentService] Finalizando partido ${partidoId}`);
  // El backend maneja el cálculo del ganador en register_match_result, 
  // pero podemos tener un endpoint dedicado si fuera necesario.
  // Por ahora, usamos el de resultados con una bandera o similar si el backend lo soporta,
  // o simplemente devolvemos éxito si el flujo ya está cubierto.
  const response = await api.post(`competencia/partido/${partidoId}/resultado/`, { finalize: true });
  return response.data;
}

export async function getTournamentStandings(
  torneoId: string
): Promise<import("../types/tournament").PosicionTabla[]> {
  if (!torneoId) return [];
  const response = await api.get(`competencia/torneo/${torneoId}/posiciones/`);
  return response.data;
}

export async function getTournamentBracket(
  torneoId: string
): Promise<import("../types/tournament").Partido[]> {
  // Nota: Este endpoint no parece estar en urls.py todavía, se usará el de posiciones o uno futuro.
  const response = await api.get(`competencia/torneo/${torneoId}/posiciones/`);
  return response.data;
}
