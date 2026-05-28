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
// Endpoint: POST /api/ia/analizar   Body: { texto }
export async function analizarTexto(texto: string): Promise<AnalisisIAResponse> {
  const response = await api.post<AnalisisIAResponse>("ia/analizar", { texto });
  return response.data;
}

// Solicitamos a la IA que recomiende la dificultad basándose en los equipos inscritos
export async function recomendarDificultad(torneoId: string): Promise<RecomendacionDificultadResponse> {
  const response = await api.post<RecomendacionDificultadResponse>("ia/recomendar-dificultad", { torneo_id: torneoId });
  return response.data;
}

// Solicitamos a la IA que recomiende el formato del torneo basándose en el contexto
export async function recomendarFormato(torneoId: string, objetivo?: string, dias?: number): Promise<RecomendacionFormatoResponse> {
  const payload: any = { torneo_id: torneoId };
  if (objetivo) payload.objetivo_declarado = objetivo;
  if (dias) payload.tiempo_disponible_dias = dias;

  const response = await api.post<RecomendacionFormatoResponse>("ia/recomendar-formato", payload);
  return response.data;
}

// Solicitamos a la IA que genere reglas operativas contextualizadas
export async function generarReglasOperativas(torneoId: string): Promise<ReglaOperativa[]> {
  const response = await api.post<ReglaOperativa[]>("ia/generar-reglas", { torneo_id: torneoId });
  return response.data;
}

// Solicitamos a la IA que genere criterios de evaluación / rúbricas (HU-IA-05)
export async function generarCriteriosEvaluacion(payload: {
  torneo_id: string;
  tipo_torneo: string;
  nivel: string | number;
  categoria: string;
  descripcion?: string;
}): Promise<{ sesion_ia_id: string; criterios: CriterioEvaluacionIA[]; total_pesos: number }> {
  const response = await api.post("ia/generar-criterios", payload);
  return response.data;
}

// Actualizamos el peso de un criterio específico
export async function actualizarPesoCriterio(criterioId: string, peso: number): Promise<any> {
  const response = await api.put(`ia/criterios/${criterioId}`, { peso_porcentual: peso });
  return response.data;
}

// Confirmamos los criterios de una sesión
export async function confirmarCriterios(sesionIaId: string): Promise<any> {
  const response = await api.post(`ia/criterios/${sesionIaId}/confirmar`);
  return response.data;
}

// Respondemos a una recomendación generada por la IA (HU-IA-06)
export async function responderRecomendacion(recomendacionId: string, payload: AccionRecomendacionRequest): Promise<void> {
  // Nota: Este endpoint no parece estar en ia_urls.py, se mantiene como referencia
  await api.patch(`ia/recomendaciones/${recomendacionId}`, payload);
}
