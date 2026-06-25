import { useState } from "react";
import { useParams } from "react-router";
import {
  PageHeader,
  ExportPdfButton,
  ExportPdfOutline,
  KpiCardRow,
  Panel,
  HBar,
  AlertaBadge,
  medalFromText,
  useAsyncData,
  AsyncBoundary,
  viewColor,
  sev,
} from "./shared/AnalyticsUI";
import { analyticsService } from "../../services/analyticsService";

/* HU-AN-01 — Análisis Integral del Torneo · /torneos/:id/analisis-integral
 * Conectado a GET /api/analitica/torneos/:id/analisis-integral/
 */

export function AnalisisIntegral() {
  const { id = "" } = useParams();
  const [categoria, setCategoria] = useState<string>("TODAS");

  const { data, status, errorMsg, errorCode, reload } = useAsyncData(
    () => analyticsService.getAnalisisIntegral(id, categoria === "TODAS" ? undefined : categoria),
    [id, categoria]
  );

  const m = data?.metricas_globales;
  const kpis = m
    ? [
        { label: "Total equipos", value: m.total_equipos, accentColor: viewColor.indigo },
        { label: "Partidos jugados", value: m.total_partidos, accentColor: sev.success },
        { label: "Puntaje promedio", value: m.puntaje_promedio_global.toFixed(1), accentColor: sev.info },
        { label: "Desv. estándar", value: m.desviacion_estandar_global.toFixed(1), accentColor: sev.warning },
        { label: "Puntaje máximo", value: m.puntaje_maximo.toFixed(1), accentColor: "#22c55e" },
        { label: "Puntaje mínimo", value: m.puntaje_minimo.toFixed(1), accentColor: "#f43f5e" },
      ]
    : [];

  const ranking = (data?.ranking_final ?? []).slice(0, 5);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title={data?.torneo_nombre || "Análisis integral del torneo"}
        subtitle="Análisis integral del torneo"
        right={
          <>
            <ExportPdfOutline />
            <ExportPdfButton label="PDF" variant="solid" accent="#1e293b" />
          </>
        }
      />

      <AsyncBoundary
        status={status}
        errorMsg={errorMsg}
        errorCode={errorCode}
        onRetry={reload}
        loadingLabel="Cargando análisis integral…"
        emptyLabel="Este torneo aún no tiene resultados para analizar."
      >
        {data && (
          <>
            <KpiCardRow cards={kpis} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Panel
                title="Distribución por criterio de evaluación"
                subtitle="Puntaje promedio normalizado [0–100]"
                right={
                  <select
                    value={categoria}
                    onChange={(e) => setCategoria(e.target.value)}
                    className="h-9 rounded-md border border-slate-300 px-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="SECONDARY">SECONDARY</option>
                    <option value="PRIMARY">PRIMARY</option>
                    <option value="TODAS">Todas</option>
                  </select>
                }
              >
                <div className="space-y-3">
                  {data.distribucion_criterios.map((c) => (
                    <HBar key={c.criterio_id} label={c.criterio_nombre} value={Number(c.promedio.toFixed(1))} color={viewColor.indigo} />
                  ))}
                  {data.distribucion_criterios.length === 0 && (
                    <p className="text-sm text-slate-400">Sin criterios registrados.</p>
                  )}
                </div>
              </Panel>

              <Panel title="Ranking final del torneo" subtitle="Top 5 equipos por puntaje acumulado">
                <table className="w-full text-sm">
                  <thead className="text-xs uppercase text-slate-400">
                    <tr className="border-b border-slate-100">
                      <th className="py-2 text-left font-semibold">Pos</th>
                      <th className="py-2 text-left font-semibold">Equipo</th>
                      <th className="py-2 text-left font-semibold">Institución</th>
                      <th className="py-2 text-right font-semibold">Puntaje</th>
                      <th className="py-2 text-center font-semibold"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {ranking.map((r, i) => {
                      const pos = Number(r.posicion_final ?? r.posicion ?? i + 1);
                      const nombre = String(r.equipo_nombre ?? r.nombre ?? r.equipo_id ?? "—");
                      const inst = String(r.categoria ?? r.institucion ?? "");
                      const pts = Number(r.puntaje_total_acumulado ?? r.puntaje_total ?? 0);
                      return (
                        <tr key={String(r.equipo_id ?? i)} className="border-b border-slate-50" style={pos === 1 ? { backgroundColor: "#fef3c7" } : undefined}>
                          <td className="py-2.5 font-bold text-slate-700">{pos}</td>
                          <td className="py-2.5 font-semibold text-slate-900">{nombre}</td>
                          <td className="py-2.5 text-slate-500">{inst}</td>
                          <td className="py-2.5 text-right font-bold text-slate-800">{pts.toFixed(1)}</td>
                          <td className="py-2.5 text-center">{medalFromText(r.medalla) || (pos <= 3 ? ["🥇", "🥈", "🥉"][pos - 1] : "")}</td>
                        </tr>
                      );
                    })}
                    {ranking.length === 0 && (
                      <tr>
                        <td colSpan={5} className="py-4 text-center text-sm text-slate-400">Sin ranking disponible.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </Panel>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Panel accentBar={sev.warning}>
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Equipo con mayor puntaje acumulado</p>
                <p className="mt-2 text-2xl font-bold" style={{ color: sev.warning }}>
                  {data.equipo_max.nombre} {medalFromText(data.equipo_max.medalla)}
                </p>
                <div className="mt-4 flex items-baseline gap-2">
                  <span className="text-sm text-slate-500">Puntaje acumulado</span>
                  <span className="text-xl font-bold" style={{ color: sev.warning }}>
                    {data.equipo_max.puntaje_total.toFixed(1)} pts
                  </span>
                </div>
                <p className="mt-1 text-sm text-slate-500">Posición final: {data.equipo_max.posicion_final}°</p>
              </Panel>

              <Panel title="Alertas del análisis">
                <div className="space-y-2">
                  <AlertaBadge type="success" text={`Cobertura de resultados sobre ${m?.total_partidos ?? 0} partidos`} />
                  {m && m.desviacion_estandar_global > 15 && (
                    <AlertaBadge type="warning" text={`Alta varianza global (σ=${m.desviacion_estandar_global.toFixed(1)})`} />
                  )}
                  <AlertaBadge
                    type="info"
                    text={`Equipo con menor puntaje: ${data.equipo_min.nombre} (${data.equipo_min.puntaje_total.toFixed(1)})`}
                  />
                </div>
              </Panel>
            </div>
          </>
        )}
      </AsyncBoundary>
    </div>
  );
}
