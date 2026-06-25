import { useState } from "react";
import { RefreshCw, Download, Copy, Check } from "lucide-react";
import { PageHeader, ExportPdfButton, Panel, viewColor } from "./shared/AnalyticsUI";

/* HU-AN-07 — Resumen Ejecutivo Automático (NLP) · /torneos/:id/resumen-ejecutivo */

const TEAL = viewColor.teal;
const TONOS = ["Divulgativo", "Formal", "Celebratorio"] as const;

const CHIPS = ["12 equipos", "7 instituciones", "48 participantes", "Campeón: RoboChampions", "Puntaje top: 94.7 pts"];

// El texto generado, con tokens [resaltados] para los datos inyectados
const SEGMENTS: { text: string; hl?: boolean }[] = [
  { text: "El Torneo Regional de Robótica Educativa 2024 congregó a " },
  { text: "12 equipos", hl: true },
  { text: " provenientes de " },
  { text: "7 instituciones educativas", hl: true },
  { text: " de la región Junín, reuniendo a " },
  { text: "48 participantes", hl: true },
  { text: " en una jornada de innovación y competencia. La organización coronó como campeón al equipo " },
  { text: "RoboChampions", hl: true },
  { text: " de la I.E. San Ramón, que acumuló un puntaje de " },
  { text: "94.7 puntos", hl: true },
  { text: " sobre 100, destacándose en precisión de navegación y robustez del sistema. " },
  { text: "El certamen evidenció un nivel técnico sobresaliente y consolida a la región como referente en robótica escolar." },
];

export function ResumenEjecutivo() {
  const [tono, setTono] = useState<(typeof TONOS)[number]>("Divulgativo");
  const [dirty, setDirty] = useState(false);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const regenerar = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setDirty(false);
    }, 1500);
  };

  const copiar = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Resumen ejecutivo automático — Torneo Regional 2024"
        accent={TEAL}
        right={<ExportPdfButton label="PDF" variant="solid" accent={TEAL} />}
      />

      {/* Configuración */}
      <div className="flex flex-wrap items-center gap-6 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-500">Tono del resumen:</span>
          {TONOS.map((t) => (
            <button
              key={t}
              onClick={() => {
                setTono(t);
                setDirty(true);
              }}
              className="rounded-md border px-3 py-1.5 text-xs font-semibold transition-colors"
              style={tono === t ? { borderColor: TEAL, color: TEAL, backgroundColor: `${TEAL}10` } : { borderColor: "#e2e8f0", color: "#94a3b8" }}
            >
              {t} {tono === t && "✓"}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-500">Versión:</span>
          <input readOnly value={1} className="h-8 w-12 rounded-md border border-slate-200 text-center text-sm" />
          <span className="text-sm text-slate-400">de 1</span>
        </div>
        <button
          onClick={regenerar}
          disabled={!dirty || loading}
          className="ml-auto inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
          style={{ backgroundColor: TEAL }}
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} /> Regenerar resumen
        </button>
      </div>

      {/* DatosInyectadosBar */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="mb-2 text-sm font-medium text-slate-600">Datos inyectados al modelo:</p>
        <div className="flex flex-wrap gap-2">
          {CHIPS.map((c) => (
            <span key={c} className="rounded-full px-3 py-1 text-xs font-medium" style={{ backgroundColor: "#ccfbf1", color: TEAL }}>
              {c}
            </span>
          ))}
        </div>
        <p className="mt-2 text-xs text-slate-400">431 palabras · Generado: 18 dic 2024 14:52 h</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* TextoGeneradoPanel */}
        <div className="lg:col-span-2">
          <Panel title="Texto generado" accentBar={TEAL}>
            {loading ? (
              <div className="space-y-3 animate-pulse">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-4 rounded bg-slate-100" style={{ width: `${85 - i * 6}%` }} />
                ))}
              </div>
            ) : (
              <p className="text-sm leading-7 text-slate-700">
                {SEGMENTS.map((s, i) =>
                  s.hl ? (
                    <span key={i} className="font-semibold" style={{ color: TEAL }}>
                      {s.text}
                    </span>
                  ) : (
                    <span key={i}>{s.text}</span>
                  )
                )}
              </p>
            )}
          </Panel>
        </div>

        {/* AnalisisTextoPanel */}
        <Panel title="Análisis del texto">
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-lg border border-slate-200 p-3">
              <p className="text-[10px] uppercase text-slate-400">Palabras</p>
              <p className="text-xl font-bold text-slate-700">431</p>
            </div>
            <div className="rounded-lg border border-slate-200 p-3">
              <p className="text-[10px] uppercase text-slate-400">Párrafos</p>
              <p className="text-xl font-bold" style={{ color: viewColor.indigo }}>
                4
              </p>
            </div>
          </div>

          <p className="mt-4 mb-2 text-xs font-semibold uppercase text-slate-400">Datos citados en el texto</p>
          <div className="space-y-2">
            {[
              "12 equipos, 7 instituciones, 48 estudiantes",
              "RoboChampions — 94.7 pts",
              "Criterio destacado: Precisión (87.2)",
              "Alerta Robustez: σ = 18.4",
            ].map((c) => (
              <div key={c} className="flex items-start gap-2 rounded-md bg-green-50 px-3 py-1.5 text-xs text-green-700">
                <span>✓</span>
                <span>{c}</span>
              </div>
            ))}
          </div>

          <p className="mt-4 mb-2 text-xs font-semibold uppercase text-slate-400">Historial de versiones</p>
          <div className="space-y-2">
            <div className="rounded-md px-3 py-2 text-xs font-medium text-white" style={{ backgroundColor: TEAL }}>
              v1 · {tono} · 14:52 h (actual)
            </div>
            <div className="rounded-md bg-slate-100 px-3 py-2 text-xs font-medium text-slate-400">
              v2 disponible tras regenerar
            </div>
          </div>

          <p className="mt-4 mb-2 text-xs font-semibold uppercase text-slate-400">Exportar resumen</p>
          <div className="flex gap-2">
            <button className="inline-flex items-center gap-2 rounded-md px-3 py-2 text-xs font-semibold text-white" style={{ backgroundColor: TEAL }}>
              <Download className="h-4 w-4" /> PDF completo
            </button>
            <button onClick={copiar} className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50">
              {copied ? <Check className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
              {copied ? "Copiado" : "Copiar texto"}
            </button>
          </div>
        </Panel>
      </div>
    </div>
  );
}
