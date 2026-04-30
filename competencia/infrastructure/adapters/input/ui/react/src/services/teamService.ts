import { api } from "./api";
import type { Equipo, RegisterTeamRequest } from "../types/team";

// Función para registrar un equipo y sus participantes en un torneo específico
export async function registerTeam(
  torneoId: string,
  data: RegisterTeamRequest
): Promise<Equipo> {
  // Adaptar el payload al formato que espera InscribeTeamUseCase
  const payload = {
    team: {
      name: data.nombre,
      category: data.categoria,
      nivel_tecnico_declarado: data.nivel_tecnico_declarado,
      // Enviamos los objetos completos para que el backend pueda crearlos si no existen
      institution: {
        name: data.institucion.nombre,
        type: data.institucion.tipo,
        city: data.institucion.ciudad,
        country: data.institucion.pais,
      },
      docente_asesor: data.docente_asesor,
      representante_id: data.docente_asesor.id || "", 
    },
    participants: data.participantes.map(p => ({
      ...p,
      birth_date: "2000-01-01", 
    }))
  };

  const response = await api.post<Equipo>(`competencia/torneo/${torneoId}/inscribir/`, payload);
  return response.data;
}

export async function getTeamsByTournament(torneoId: string): Promise<Equipo[]> {
  const response = await api.get<Equipo[]>(`competencia/torneo/${torneoId}/equipos/`);
  return response.data;
}

export async function approveTeam(teamId: string): Promise<Equipo> {
  const response = await api.post<Equipo>(`competencia/equipo/${teamId}/aprobar/`);
  return response.data;
}

export async function rejectTeam(teamId: string): Promise<Equipo> {
  const response = await api.post<Equipo>(`competencia/equipo/${teamId}/rechazar/`);
  return response.data;
}

