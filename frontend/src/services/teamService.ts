import { api } from "./api";
import type { Equipo, RegisterTeamRequest } from "../types/team";

// Función para registrar un equipo y sus participantes en un torneo específico
export async function registerTeam(
  torneoId: string,
  data: RegisterTeamRequest
): Promise<Equipo> {
  const response = await api.post<Equipo>(`/torneos/${torneoId}/equipos`, data);
  return response.data;
}
