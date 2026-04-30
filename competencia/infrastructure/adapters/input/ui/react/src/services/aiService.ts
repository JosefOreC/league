import { api } from "./api";
import { 
  AnalisisIAResponse, 
  RecomendacionDificultadResponse, 
  RecomendacionFormatoResponse, 
  ReglaOperativa,
  CriterioEvaluacionIA,
  AccionRecomendacionRequest
} from "../types/ai";

// Enviamos un texto descriptivo a la IA para que extraiga los parámetros del torneo
export async function analizarTexto(texto: string): Promise<AnalisisIAResponse> {
  const response = await api.post<AnalisisIAResponse>("/ia/analizar", { texto });
  return response.data;
}

// Solicitamos a la IA que recomiende la dificultad basándose en los equipos inscritos
export async function recomendarDificultad(torneoId: string): Promise<RecomendacionDificultadResponse> {
  const response = await api.post<RecomendacionDificultadResponse>("/ia/recomendar-dificultad", { torneo_id: torneoId });
  return response.data;
}

// Solicitamos a la IA que recomiende el formato del torneo basándose en el contexto
export async function recomendarFormato(torneoId: string, objetivo?: string, dias?: number): Promise<RecomendacionFormatoResponse> {
  const payload: any = { torneo_id: torneoId };
  if (objetivo) payload.objetivo_declarado = objetivo;
  if (dias) payload.tiempo_disponible_dias = dias;
  
  const response = await api.post<RecomendacionFormatoResponse>("/ia/recomendar-formato", payload);
  return response.data;
}

// Solicitamos a la IA que genere reglas operativas contextualizadas
export async function generarReglasOperativas(torneoId: string): Promise<ReglaOperativa[]> {
  const response = await api.post<ReglaOperativa[]>("/ia/generar-reglas", { torneo_id: torneoId });
  return response.data;
}

// Solicitamos a la IA que genere criterios de evaluación / rúbricas (HU-IA-05)
export async function generarCriteriosEvaluacion(torneoId: string): Promise<CriterioEvaluacionIA[]> {
  const response = await api.post<CriterioEvaluacionIA[]>("/ia/generar-criterios", { torneo_id: torneoId });
  return response.data;
}

// Respondemos a una recomendación generada por la IA (HU-IA-06)
export async function responderRecomendacion(recomendacionId: string, payload: AccionRecomendacionRequest): Promise<void> {
  await api.patch(`/ia/recomendaciones/${recomendacionId}`, payload);
}
