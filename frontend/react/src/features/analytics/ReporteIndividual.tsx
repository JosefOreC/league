import { useParams } from "react-router";
import {
  PageHeader,
  ExportPdfButton,
  Panel,
  PercentilGlobalBar,
  EvolucionRondaChart,
  AsyncBoundary,
  useAsyncData,
  medalFromText,
  viewColor,
  sev,
} from "./shared/AnalyticsUI";
import { analyticsService } from "../../services/analyticsService";

/* HU-AN-02 — Reporte Individual · /torneos/:id/equipos/:eid/reporte-individual
 * Conectado a GET /api/analitica/torneos/:id/equipos/:eid/reporte-individual/
 */

function Chip({ label, value, positive }: { label: string; value: string; positive?: boolean }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2">
      <p className="text-[10px] uppercase tracking-wide text-slate-400">{label}</p>
      <p className={`text-lg font-bold ${positive === undefined ? "text-slate-800" : positive ? "text-green-600" : "text-red-600"}`}>{value}</p>
    </div>
  );
}

export function ReporteIndividual() {
  const { id = "", eid = "" } = useParams();
  const { data, status, errorMsg, errorCode, reload } = useAsyncData(
    () => analyticsService.getReporteIndividual(id, eid),
    [id, eid]
  );

  const eq = data?.equipo;
  const res = data?.resumen;
  const diff = res ? res.comparativa_vs_promedio_torneo_pct : 0;

  // percentil aproximado a partir de la comparativa (solo visual)
  const percentil = res
    ? Math.max(1, Math.min(99, Math.round(50 + diff)))
    : 0;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title={eq ? `Reporte individual — ${eq.nombre}` : "Reporte individual"}
        right={<ExportPdfButton label="PDF" variant="solid" accent={viewColor.indigo} />}
      />

      <AsyncBoundary
        status={status}
        errorMsg={errorMsg}
        errorCode={errorCode}
        onRetry={reload}
        loadingLabel="Cargando reporte del equipo…"
        emptyLabel="Este equipo aún no tiene datos de desempeño."
      >
        {data && eq && res && (
          <>
            <Panel>
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-xl font-bold text-slate-900">{eq.nombre}</h2>
                    {eq.medalla && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-700">
                        {medalFromText(eq.medalla)} {eq.medalla}
                      </span>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-slate-500">
                    {eq.institucion} · Categoría {eq.categoria}
                  </p>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <Chip label="Posición final" value={`${eq.posicion_final}°`} />
                  <Chip label="Puntaje acum." value={res.puntaje_total_acumulado.toFixed(1)} />
                  <Chip label="Victorias" value={`${res.victorias}/${res.total_partidos_jugados}`} />
                  <Chip label="vs. promedio" value={`${diff >= 0 ? "+" : ""}${diff.toFixed(1)}%`} positive={diff >= 0} />
                </div>
              </div>
            </Panel>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Panel title="Evolución por ronda" subtitle="Puntaje por ronda vs. promedio del torneo">
                {data.evolucion_por_ronda.length > 1 ? (
                  <EvolucionRondaChart
                    values={data.evolucion_por_ronda.map((e) => Number(e.puntaje_ronda.toFixed(1)))}
                    promedio={Number(res.promedio_puntaje_torneo.toFixed(1))}
                    color={viewColor.indigo}
                  />
                ) : (
                  <p className="text-sm text-slate-400">Datos insuficientes para graficar la evolución.</p>
                )}
              </Panel>

              <Panel title="Detalle por criterio — Comparativa vs. torneo">
                <div className="mb-3 flex gap-4 text-xs text-slate-500">
                  <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-sm" style={{ backgroundColor: viewColor.indigo }} /> Equipo</span>
                  <span className="flex items-center gap-1.5"><span className="inline-block h-3 w-3 rounded-sm bg-slate-300" /> Torneo</span>
                </div>
                <div className="space-y-4">
                  {data.detalle_criterios.map((c) => (
                    <div key={c.criterio_id}>
                      <p className="mb-1 text-sm text-slate-600">{c.criterio_nombre}</p>
                      <div className="flex items-center gap-2">
                        <div className="h-3 flex-1 rounded-full bg-slate-100">
                          <div className="h-3 rounded-full" style={{ width: `${c.promedio_equipo}%`, backgroundColor: viewColor.indigo }} />
                        </div>
                        <span className="w-12 text-right text-xs font-semibold text-slate-700">{c.promedio_equipo.toFixed(1)}</span>
                      </div>
                      <div className="mt-1 flex items-center gap-2">
                        <div className="h-3 flex-1 rounded-full bg-slate-100">
                          <div className="h-3 rounded-full bg-slate-300" style={{ width: `${c.promedio_torneo}%` }} />
                        </div>
                        <span className="w-12 text-right text-xs font-semibold text-slate-400">{c.promedio_torneo.toFixed(1)}</span>
                      </div>
                    </div>
                  ))}
                  {data.detalle_criterios.length === 0 && <p className="text-sm text-slate-400">Sin criterios.</p>}
                </div>
              </Panel>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Panel title="Percentil global">
                <PercentilGlobalBar
                  percentil={percentil}
                  caption={
                    <div className="space-y-1">
                      <p className="flex justify-between">
                        <span>Puntaje equipo: <strong className="text-slate-700">{res.puntaje_total_acumulado.toFixed(1)}</strong></span>
                        <span>Promedio torneo: <strong className="text-slate-700">{res.promedio_puntaje_torneo.toFixed(1)}</strong></span>
                      </p>
                      <p className={`font-medium ${diff >= 0 ? "text-green-600" : "text-red-600"}`}>
                        {diff >= 0 ? "+" : ""}{diff.toFixed(1)}% respecto al promedio general
                      </p>
                    </div>
                  }
                />
              </Panel>

              <Panel title="Partidos disputados">
                <table className="w-full text-sm">
                  <thead className="text-xs uppercase text-slate-400">
                    <tr className="border-b border-slate-100">
                      <th className="py-2 text-left font-semibold">Ronda</th>
                      <th className="py-2 text-left font-semibold">Rival</th>
                      <th className="py-2 text-center font-semibold">Marcador</th>
                      <th className="py-2 text-right font-semibold">Resultado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.partidos.map((p) => (
                      <tr key={p.partido_id} className="border-b border-slate-50">
                        <td className="py-2.5 text-slate-500">R{p.ronda}</td>
                        <td className="py-2.5 font-medium text-slate-800">{p.rival_nombre}</td>
                        <td className="py-2.5 text-center text-slate-600">{p.puntaje_equipo} - {p.puntaje_rival}</td>
                        <td className={`py-2.5 text-right font-semibold ${p.es_victoria ? "text-green-600" : "text-red-500"}`}>
                          {p.es_victoria ? "Victoria" : "Derrota"}
                        </td>
                      </tr>
                    ))}
                    {data.partidos.length === 0 && (
                      <tr><td colSpan={4} className="py-3 text-center text-xs text-slate-400">Sin partidos registrados.</td></tr>
                    )}
                  </tbody>
                </table>
              </Panel>
            </div>

            {/* MencionEspecialBanner — derivado de la comparativa */}
            <div className="rounded-xl p-5" style={{ backgroundColor: "#fef9c3" }}>
              <p className="text-sm">
                <span className="font-semibold text-slate-700">Resumen: </span>
                <span className="font-semibold" style={{ color: sev.warning }}>
                  {eq.nombre} terminó en la posición {eq.posicion_final}° con {res.puntaje_total_acumulado.toFixed(1)} pts ({res.victorias} victorias).
                </span>
              </p>
            </div>
          </>
        )}
      </AsyncBoundary>
    </div>
  );
}
