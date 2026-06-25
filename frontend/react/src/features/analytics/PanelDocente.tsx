import { useParams } from "react-router";
import {
  PageHeader,
  KpiCardRow,
  Panel,
  PercentilGlobalBar,
  AsyncBoundary,
  useAsyncData,
  medalFromText,
  viewColor,
  sev,
} from "./shared/AnalyticsUI";
import { analyticsService } from "../../services/analyticsService";

/* HU-AN-08 — Panel de Retroalimentación Docente · /torneos/:id/equipos/:eid/panel-docente
 * Conectado a GET /api/analitica/torneos/:id/equipos/:eid/panel-docente/
 */

const NAVY = viewColor.navy;

const TIPO_COLOR: Record<string, string> = {
  PRACTICA_DIRIGIDA: "#3b82f6",
  PRÁCTICA_DIRIGIDA: "#3b82f6",
  RECURSO: "#8b5cf6",
  METODOLOGIA: "#16a34a",
  METODOLOGÍA: "#16a34a",
};

export function PanelDocente() {
  const { id = "", eid = "" } = useParams();
  const { data, status, errorMsg, errorCode, reload } = useAsyncData(
    () => analyticsService.getPanelDocente(id, eid),
    [id, eid]
  );

  const eq = data?.equipo;
  const preliminar = (data?.estado_panel || "").toUpperCase().includes("PRELIM");

  // ordenar criterios por promedio del equipo para fortalezas (top) y debilidad (bottom)
  const criterios = [...(data?.criterios ?? [])].sort((a, b) => b.promedio_equipo - a.promedio_equipo);
  const fortalezas = criterios.slice(0, 3);
  const debil = criterios[criterios.length - 1];

  const avgPercentil = criterios.length
    ? Math.round(criterios.reduce((s, c) => s + c.percentil, 0) / criterios.length)
    : 0;

  const kpis = eq
    ? [
        { label: "Puntaje acumulado", value: eq.puntaje_total_acumulado.toFixed(1), accentColor: sev.info },
        { label: "Partidos", value: eq.total_partidos_jugados, accentColor: sev.success },
        { label: "Percentil global", value: `${avgPercentil}°`, accentColor: viewColor.indigo },
        { label: "Posición final", value: `${eq.posicion_final}°`, accentColor: sev.warning },
        { label: "Medalla", value: eq.medalla ? `${medalFromText(eq.medalla)} ${eq.medalla}` : "—", accentColor: sev.gold, wide: true },
      ]
    : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title={data ? `Panel de retroalimentación — ${data.docente.nombre || "Docente"}` : "Panel de retroalimentación"}
        accent={NAVY}
        right={
          <button className="inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold text-white" style={{ backgroundColor: NAVY }}>
            Exportar PDF
          </button>
        }
      />

      <AsyncBoundary
        status={status}
        errorMsg={errorMsg}
        errorCode={errorCode}
        onRetry={reload}
        loadingLabel="Cargando panel docente…"
        emptyLabel="Aún no hay retroalimentación disponible para este equipo."
      >
        {data && eq && (
          <>
            <Panel>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{eq.nombre}</h2>
                  <p className="mt-1 text-sm text-slate-500">Docente: {data.docente.nombre}</p>
                </div>
                <div className="flex gap-2">
                  {eq.medalla && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-700">
                      {medalFromText(eq.medalla)} Posición {eq.posicion_final}°
                    </span>
                  )}
                  {preliminar ? (
                    <span className="inline-flex items-center gap-1 rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-orange-700">⏳ Panel PRELIMINAR</span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-xs font-bold text-green-700">✓ Panel DEFINITIVO</span>
                  )}
                </div>
              </div>
              {preliminar && data.advertencia && (
                <p className="mt-3 rounded-md bg-orange-50 px-3 py-2 text-xs text-orange-700">⏳ {data.advertencia}</p>
              )}
            </Panel>

            <KpiCardRow cards={kpis} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Panel title="Fortalezas detectadas" subtitle="Top 3 criterios con mayor puntaje promedio">
                <div className="space-y-3">
                  {fortalezas.map((f, i) => (
                    <div key={f.criterio_id} className="rounded-lg bg-slate-50 p-3" style={{ borderLeft: `4px solid ${["#15803d", "#16a34a", "#4ade80"][i] || "#4ade80"}` }}>
                      <p className="text-sm font-semibold text-slate-800">{f.criterio_nombre}</p>
                      <p className="text-xs text-slate-500">Promedio: {f.promedio_equipo.toFixed(1)} · Percentil: {f.percentil}°</p>
                      <p className="mt-1 text-xs font-medium text-green-600">
                        {f.promedio_equipo >= f.promedio_torneo ? "+" : ""}{(f.promedio_equipo - f.promedio_torneo).toFixed(1)} pts vs. torneo ({f.promedio_torneo.toFixed(1)})
                      </p>
                    </div>
                  ))}
                  {debil && fortalezas.length > 0 && debil.criterio_id !== fortalezas[0].criterio_id && (
                    <div className="rounded-lg border-t border-dashed border-slate-200 pt-3">
                      <p className="text-sm font-semibold text-slate-800">{debil.criterio_nombre}</p>
                      <p className="mt-1 text-xs font-medium text-amber-600">
                        {debil.promedio_equipo.toFixed(1)} — menor del equipo (torneo {debil.promedio_torneo.toFixed(1)})
                      </p>
                    </div>
                  )}
                  {criterios.length === 0 && <p className="text-sm text-slate-400">Sin criterios evaluados.</p>}
                </div>
              </Panel>

              <Panel title="Recomendaciones pedagógicas" subtitle="Generadas automáticamente por el sistema">
                <div className="space-y-3">
                  {data.recomendaciones.map((r, i) => {
                    const color = TIPO_COLOR[r.tipo.toUpperCase()] || "#6366f1";
                    return (
                      <div key={i} className="rounded-lg bg-white p-3 shadow-sm" style={{ borderLeft: `4px solid ${color}` }}>
                        <p className="text-[10px] font-bold uppercase tracking-wide" style={{ color }}>{r.tipo.replace(/_/g, " ")}</p>
                        <p className="text-sm font-semibold text-slate-800">{r.criterio_nombre}</p>
                        <p className="mt-0.5 text-xs text-slate-500">{r.descripcion}</p>
                        {r.acciones_sugeridas?.length > 0 && (
                          <ul className="mt-1 list-disc pl-4 text-xs text-slate-500">
                            {r.acciones_sugeridas.map((a, j) => <li key={j}>{a}</li>)}
                          </ul>
                        )}
                      </div>
                    );
                  })}
                  {data.recomendaciones.length === 0 && <p className="text-sm text-slate-400">Sin recomendaciones.</p>}
                </div>
              </Panel>

              <Panel title="Percentil global">
                <PercentilGlobalBar
                  percentil={avgPercentil}
                  accent={NAVY}
                  caption={
                    <div>
                      <p>Posición: percentil {avgPercentil}° del torneo</p>
                      <p className="font-medium text-green-600">Mejor que {avgPercentil}% de los equipos</p>
                    </div>
                  }
                />
              </Panel>
            </div>

            <div className="rounded-xl p-5" style={{ backgroundColor: "#eff6ff" }}>
              <p className="text-sm text-slate-700">
                <span className="font-semibold">Nota del sistema: </span>
                {preliminar
                  ? "Este panel es PRELIMINAR — el torneo sigue en curso y los datos son parciales."
                  : "Este panel es DEFINITIVO. El torneo ha finalizado y los datos reflejan el desempeño completo del equipo."}
              </p>
            </div>
          </>
        )}
      </AsyncBoundary>
    </div>
  );
}
