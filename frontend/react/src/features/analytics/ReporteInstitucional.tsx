import { PageHeader, ExportPdfButton, KpiCardRow, Panel, medalEmoji, viewColor, sev } from "./shared/AnalyticsUI";

/* HU-AN-03 — Reporte Institucional · /instituciones/:id/reporte */

const KPIS = [
  { label: "Equipos totales", value: 3, accentColor: viewColor.indigo },
  { label: "Mejor posición", value: "1°", accentColor: sev.gold },
  { label: "Prom. institucional", value: "82.6 pts", accentColor: sev.info },
  { label: "Criterio destacado", value: "Precisión nav.", accentColor: sev.success },
  { label: "Medallas", value: "🥇🥈", accentColor: sev.gold },
  { label: "Participantes", value: "12 est.", accentColor: "#f43f5e" },
];

const EQUIPOS = [
  { equipo: "RoboChampions", cat: "SECONDARY", pos: 1, puntaje: 94.7 },
  { equipo: "RoboChampions Jr.", cat: "PRIMARY", pos: 4, puntaje: 78.2 },
  { equipo: "San Ramón Bots", cat: "SECONDARY", pos: 7, puntaje: 74.9 },
];

const HIST = [
  { anio: "2022", valor: 65.0 },
  { anio: "2023", valor: 74.1 },
  { anio: "2024", valor: 82.6 },
];

export function ReporteInstitucional() {
  const maxHist = 100;
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Reporte institucional — I.E. San Ramón"
        right={<ExportPdfButton label="PDF" variant="solid" accent={viewColor.indigo} />}
      />

      {/* InstitucionIdentityCard */}
      <Panel accentBar={sev.info}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-900">I.E. San Ramón</h2>
            <p className="mt-1 text-sm text-slate-500">Tipo: PÚBLICA · Ciudad: Huancayo · Junín, PE</p>
          </div>
          <div className="flex gap-2">
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">Histórico: 3 torneos</span>
            <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-600">2022–2024</span>
          </div>
        </div>
      </Panel>

      <KpiCardRow cards={KPIS} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Panel title="Equipos en torneo actual (2024)">
          <table className="w-full text-sm">
            <thead className="text-xs uppercase text-slate-400">
              <tr className="border-b border-slate-100">
                <th className="py-2 text-left font-semibold">Equipo</th>
                <th className="py-2 text-left font-semibold">Categoría</th>
                <th className="py-2 text-center font-semibold">Posición</th>
                <th className="py-2 text-right font-semibold">Puntaje</th>
              </tr>
            </thead>
            <tbody>
              {EQUIPOS.map((e, i) => (
                <tr key={e.equipo} className="border-b border-slate-50" style={i === 0 ? { backgroundColor: "#fef3c7" } : undefined}>
                  <td className="py-2.5 font-semibold text-slate-900">{e.equipo}</td>
                  <td className="py-2.5">
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">{e.cat}</span>
                  </td>
                  <td className="py-2.5 text-center text-slate-600">
                    {e.pos} {medalEmoji(e.pos)}
                  </td>
                  <td className="py-2.5 text-right font-bold" style={{ color: i === 0 ? sev.warning : "#334155" }}>
                    {e.puntaje}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-4">
            <p className="mb-1 text-sm text-slate-600">
              Puntaje promedio institucional 2024: <strong className="text-slate-800">82.6 pts</strong>
            </p>
            <div className="h-3 w-full rounded-full bg-slate-100">
              <div className="h-3 rounded-full" style={{ width: "82.6%", backgroundColor: viewColor.indigo }} />
            </div>
          </div>
        </Panel>

        <Panel title="Evolución histórica (2022–2024)" subtitle="Puntaje promedio institucional por torneo">
          <div className="flex items-end justify-around gap-4 h-48 pt-4">
            {HIST.map((h, i) => (
              <div key={h.anio} className="flex flex-1 flex-col items-center justify-end">
                <span className="mb-1 text-xs font-semibold text-slate-600">{h.valor}</span>
                <div
                  className="w-full max-w-[64px] rounded-t-md"
                  style={{
                    height: `${(h.valor / maxHist) * 100}%`,
                    backgroundColor: i === HIST.length - 1 ? viewColor.indigo : "#a5b4fc",
                  }}
                />
                <span className="mt-2 text-xs text-slate-400">{h.anio}</span>
              </div>
            ))}
          </div>
          <p className="mt-3 text-center text-sm font-medium text-green-600">↑ +17.6 pts de mejora en 3 torneos</p>
        </Panel>
      </div>

      <Panel title="Observaciones y recomendaciones institucionales" accentBar={sev.info}>
        <ul className="space-y-2 text-sm text-slate-600 list-none">
          <li>· La institución muestra tendencia positiva sostenida en los últimos tres torneos.</li>
          <li>· El equipo RoboChampions logró el primer lugar con 94.7 pts.</li>
          <li>· Los equipos PRIMARY presentan margen de mejora en Robustez del sistema.</li>
        </ul>
        <div className="mt-4 flex items-start gap-2 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <span>⚠️</span>
          <span>
            <strong>Recomendación:</strong> Reforzar talleres de programación defensiva y robustez en categorías de primaria.
          </span>
        </div>
      </Panel>
    </div>
  );
}
