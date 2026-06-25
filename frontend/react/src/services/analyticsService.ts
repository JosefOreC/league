import { api } from "./api";
import type {
  AnalisisIntegralDTO,
  ReporteIndividualDTO,
  TableroInteligenciaDTO,
  PanelDocenteDTO,
  ReporteInstitucionalDTO,
  ReporteInstitucionalHistDTO,
  SugerenciasResponse,
  ResumenEjecutivoDTO,
} from "../types/analytics";

/* Servicio de Analítica (MVP3) — consume /api/analitica/...
 * El token JWT lo inyecta automáticamente el interceptor de api.ts
 */
export const analyticsService = {
  // HU-AN-01
  getAnalisisIntegral: (torneoId: string, categoria?: string) =>
    api
      .get<AnalisisIntegralDTO>(`analitica/torneos/${torneoId}/analisis-integral/`, {
        params: categoria ? { categoria } : undefined,
      })
      .then((r) => r.data),

  // HU-AN-02
  getReporteIndividual: (torneoId: string, equipoId: string) =>
    api
      .get<ReporteIndividualDTO>(
        `analitica/torneos/${torneoId}/equipos/${equipoId}/reporte-individual/`
      )
      .then((r) => r.data),

  // HU-AN-04
  getTableroInteligencia: (torneoId: string) =>
    api
      .get<TableroInteligenciaDTO>(`analitica/torneos/${torneoId}/tablero-inteligencia/`)
      .then((r) => r.data),

  // HU-AN-08
  getPanelDocente: (torneoId: string, equipoId: string) =>
    api
      .get<PanelDocenteDTO>(
        `analitica/torneos/${torneoId}/equipos/${equipoId}/panel-docente/`
      )
      .then((r) => r.data),

  // HU-AN-03 — reporte de un torneo específico
  getReporteInstitucional: (instId: string, torneoId: string) =>
    api
      .get<ReporteInstitucionalDTO>(`analitica/instituciones/${instId}/reporte/`, {
        params: { torneo_id: torneoId },
      })
      .then((r) => r.data),

  // HU-AN-03 — evolución histórica (multi-torneo)
  getReporteInstitucionalHistorico: (instId: string) =>
    api
      .get<ReporteInstitucionalHistDTO>(`analitica/instituciones/${instId}/reporte/`, {
        params: { historico: "true" },
      })
      .then((r) => r.data),

  // HU-AN-05
  getSugerencias: (torneoId: string) =>
    api
      .get<SugerenciasResponse>(`analitica/torneos/${torneoId}/sugerencias/`)
      .then((r) => r.data),

  // HU-AN-07 (POST — genera una nueva versión)
  generarResumenEjecutivo: (torneoId: string, tono: string) =>
    api
      .post<ResumenEjecutivoDTO>(
        `analitica/torneos/${torneoId}/resumen-ejecutivo/`,
        {},
        { params: { tono } }
      )
      .then((r) => r.data),

  // HU-AN-06 (POST — descarga archivo ZIP/PDF). Devuelve el blob + metadatos de cabeceras.
  generarCertificados: (torneoId: string, tipo: "PARTICIPACION" | "GANADOR", equipoId?: string) =>
    api
      .post(
        `analitica/torneos/${torneoId}/certificados/`,
        {},
        { params: { tipo, ...(equipoId ? { equipo_id: equipoId } : {}) }, responseType: "blob" }
      )
      .then((r) => ({
        blob: r.data as Blob,
        totalGenerados: Number(r.headers["x-total-generados"] ?? 0),
        excluidosCount: Number(r.headers["x-excluidos-count"] ?? 0),
        medalla: r.headers["x-medalla"] as string | undefined,
        codigo: r.headers["x-codigo-verificacion"] as string | undefined,
      })),
};
