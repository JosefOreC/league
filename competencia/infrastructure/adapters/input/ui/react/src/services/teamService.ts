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
      institution_id: data.institucion.id,
      nivel_tecnico_declarado: data.nivel_tecnico_declarado,
      // Estos IDs deberían venir del contexto de la sesión o ser creados previamente
      representante_id: data.docente_asesor.id || "", 
      docente_asesor_id: data.docente_asesor.id || "",
    },
    participants: data.participantes.map(p => ({
      ...p,
      birth_date: "2000-01-01", // Valor temporal si no viene en el form, ya que el backend lo requiere
    }))
  };

  const response = await api.post<Equipo>(`competencia/torneo/${torneoId}/inscribir/`, payload);
  return response.data;
}
