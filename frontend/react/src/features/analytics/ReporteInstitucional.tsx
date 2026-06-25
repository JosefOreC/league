import { useParams, useSearchParams } from "react-router";
import {
  PageHeader,
  ExportPdfButton,
  KpiCardRow,
  Panel,
  AsyncBoundary,
  useAsyncData,
  medalEmoji,
  viewColor,
  sev,
} from "./shared/AnalyticsUI";
import { analyticsService } from "../../services/analyticsService";
import type { ReporteInstitucionalDTO, ReporteInstitucionalHistDTO } from "../../types/analytics";

/* HU-AN-03 — Reporte Institucional · /instituciones/:id/reporte
 * Conectado a GET /api/analitica/instituciones/:id/reporte/?torneo_id= y ?historico=true
 * El torneo del reporte actual se toma de ?torneo= (default "1").
 */

export function ReporteInstitucional() {
  const { id = "" } = useParams();
  const [sp] = useSearchParams();
  const torneoId = sp.get("torneo") || "1";

  const { data, status, errorMsg, errorCode, reload } = useAsyncData(
    async () => {
      const current = await analyticsService.getReporteInstitucional(id, torneoId);
      let hist: ReporteInstitucionalHistDTO | null = null;
      try {
        hist = await analyticsService.getReporteInstitucionalHistorico(id);
      } catch {
        hist = null; // puede no haber histórico (un solo torneo)
      }
      return { current, hist } as { current: ReporteInstitucionalDTO; hist: ReporteInstitucionalHistDTO | null };
    },
    [id, torneoId]
  );

  const inst = data?.current;
  const hist = data?.hist?.evolucion_historica ?? [];
  const maxHist = hist.length ? Math.max(...hist.map((h) => h.puntaje_promedio)) : 100;
  const mejora = hist.length >= 2 ? hist[hist.length - 1].puntaje_promedio - hist[0].puntaje_promedio : null;

  const kpis = inst
    ? [
        { label: "Equipos totales", value: inst.total_equipos_participantes, accentColor: viewColor.indigo },
        { label: "Mejor posición", value: `${inst.mejor_posicion_lograda}°`, accentColor: sev.gold },
        { label: "Prom. institucional", value: `${inst.puntaje_promedio_institucional.toFixed(1)}`, accentColor: sev.info },
        { label: "Criterio destacado", value: inst.criterio_mas_destacado || "—", accentColor: sev.success },
        { label: "Tipo", value: inst.tipo, accentColor: "#22c55e" },
        { label: "Torneos histórico", value: hist.length || 1, accentColor: "#f43f5e" },
      ]
    : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title={inst ? `Reporte institucional — ${inst.nombre_institucion}` : "Reporte institucional"}
        right={<ExportPdfButton label="PDF" variant="solid" accent={viewColor.indigo} />}
      />

      <AsyncBoundary
        status={status}
        errorMsg={errorMsg}
        errorCode={errorCode}
        onRetry={reload}
        loadingLabel="Cargando reporte institucional…"
        emptyLabel="Esta institución no tiene equipos en el torneo indicado."
      >
        {inst && (
          <>
            <Panel accentBar={sev.info}>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{inst.nombre_institucion}</h2>
                  <p className="mt-1 text-sm text-slate-500">Tipo: {inst.tipo} · Torneo: {inst.torneo_id}</p>
                </div>
                {hist.length > 0 && (
                  <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-600">
                    Histórico: {hist.length} torneos
                  </span>
                )}
              </div>
            </Panel>

            <KpiCardRow cards={kpis} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Panel title="Equipos en el torneo">
                <table className="w-full text-sm">
                  <thead className="text-xs uppercase text-slate-400">
                    <tr className="border-b border-slate-100">
                      <th className="py-2 text-left font-semibold">Equipo</th>
                      <th className="py-2 text-center font-semibold">Posición</th>
                      <th className="py-2 text-right font-semibold">Puntaje</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inst.posiciones_obtenidas.map((p, i) => (
                      <tr key={p.equipo_id} className="border-b border-slate-50" style={i === 0 ? { backgroundColor: "#fef3c7" } : undefined}>
                        <td className="py-2.5 font-semibold text-slate-900">{p.nombre_equipo}</td>
                        <td className="py-2.5 text-center text-slate-600">{p.posicion_final} {medalEmoji(p.posicion_final)}</td>
                        <td className="py-2.5 text-right font-bold" style={{ color: i === 0 ? sev.warning : "#334155" }}>
                          {p.puntaje_acumulado.toFixed(1)}
                        </td>
                      </tr>
                    ))}
                    {inst.posiciones_obtenidas.length === 0 && (
                      <tr><td colSpan={3} className="py-3 text-center text-xs text-slate-400">Sin equipos.</td></tr>
                    )}
                  </tbody>
                </table>
                <div className="mt-4">
                  <p className="mb-1 text-sm text-slate-600">
                    Puntaje promedio institucional: <strong className="text-slate-800">{inst.puntaje_promedio_institucional.toFixed(1)}</strong>
                  </p>
                </div>
              </Panel>

              <Panel title="Evolución histórica" subtitle="Puntaje promedio institucional por torneo">
                {hist.length > 0 ? (
                  <>
                    <div className="flex items-end justify-around gap-4 h-48 pt-4">
                      {hist.map((h, i) => (
                        <div key={h.torneo_id} className="flex flex-1 flex-col items-center justify-end">
                          <span className="mb-1 text-xs font-semibold text-slate-600">{h.puntaje_promedio.toFixed(1)}</span>
                          <div
                            className="w-full max-w-[64px] rounded-t-md"
                            style={{ height: `${(h.puntaje_promedio / maxHist) * 100}%`, backgroundColor: i === hist.length - 1 ? viewColor.indigo : "#a5b4fc" }}
                          />
                          <span className="mt-2 text-xs text-slate-400">{(h.fecha || "").slice(0, 4) || h.nombre_torneo}</span>
                        </div>
                      ))}
                    </div>
                    {mejora != null && (
                      <p className={`mt-3 text-center text-sm font-medium ${mejora >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {mejora >= 0 ? "↑ +" : "↓ "}{mejora.toFixed(1)} pts en {hist.length} torneos
                      </p>
                    )}
                  </>
                ) : (
                  <p className="text-sm text-slate-400">Solo hay un torneo registrado; aún no hay evolución histórica.</p>
                )}
              </Panel>
            </div>

            <Panel title="Observaciones institucionales" accentBar={sev.info}>
              <ul className="space-y-2 text-sm text-slate-600">
                <li>· La institución participó con {inst.total_equipos_participantes} equipo(s), logrando como mejor posición el {inst.mejor_posicion_lograda}°.</li>
                <li>· Su criterio más destacado fue: <strong>{inst.criterio_mas_destacado || "—"}</strong>.</li>
                {mejora != null && mejora >= 0 && <li>· Muestra una tendencia positiva sostenida de +{mejora.toFixed(1)} pts en su histórico.</li>}
              </ul>
            </Panel>
          </>
        )}
      </AsyncBoundary>
    </div>
  );
}
