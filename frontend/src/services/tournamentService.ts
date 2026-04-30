import { api } from "./api";
import type {
  CreateTournamentRequest,
  Tournament,
  UpdateConfigRequest,
} from "../types/tournament";

// Crea un nuevo torneo, iniciará en estado de borrador (DRAFT)
export async function createTournament(data: CreateTournamentRequest): Promise<Tournament> {
  const response = await api.post<Tournament>("/torneos", data);
  return response.data;
}

// Publica el torneo para abrir la fase de inscripciones
export async function publishTournament(id: string): Promise<Tournament> {
  const response = await api.post<Tournament>(`/torneos/${id}/publicar`);
  return response.data;
}

// Obtiene la lista de torneos disponibles para el usuario
export async function getTournaments(): Promise<Tournament[]> {
  const response = await api.get<Tournament[]>("/torneos");
  return response.data;
}

// Obtiene la información detallada de un torneo por su identificador
export async function getTournamentById(id: string): Promise<Tournament> {
  const response = await api.get<Tournament>(`/torneos/${id}`);
  return response.data;
}

// Guarda la configuración del torneo (solo permitido en estado DRAFT)
export async function updateTournamentConfig(
  id: string,
  data: UpdateConfigRequest
): Promise<Tournament> {
  const response = await api.patch<Tournament>(`/torneos/${id}/config`, data);
  return response.data;
}

// Inicia el torneo y genera los fixtures automáticamente
export async function startTournament(id: string): Promise<void> {
  await api.post(`/torneos/${id}/iniciar`);
}

// Registra los resultados parciales ingresados por el juez
export async function registerMatchResults(
  torneoId: string,
  partidoId: string,
  resultados: import("../types/tournament").RegisterResultRequest[]
): Promise<import("../types/tournament").ResultadoPartido[]> {
  const response = await api.post(`/torneos/${torneoId}/partidos/${partidoId}/resultados`, { resultados });
  return response.data;
}

// Cierra el partido definitivamente y calcula al ganador
export async function finalizeMatch(
  torneoId: string,
  partidoId: string
): Promise<void> {
  await api.post(`/torneos/${torneoId}/partidos/${partidoId}/finalizar`);
}

// Obtiene la tabla de posiciones actualizada del torneo
export async function getTournamentStandings(
  torneoId: string
): Promise<import("../types/tournament").PosicionTabla[]> {
  const response = await api.get(`/torneos/${torneoId}/tabla-posiciones`);
  return response.data;
}

// Obtiene el árbol de enfrentamientos o bracket actualizado
export async function getTournamentBracket(
  torneoId: string
): Promise<import("../types/tournament").Partido[]> {
  const response = await api.get(`/torneos/${torneoId}/bracket`);
  return response.data;
}

