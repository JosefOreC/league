import { api } from "./api";
import type {
  AnalisisIntegralDTO,
  ReporteIndividualDTO,
  TableroInteligenciaDTO,
  PanelDocenteDTO,
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
};
