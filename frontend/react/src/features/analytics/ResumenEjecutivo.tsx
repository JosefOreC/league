import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router";
import { RefreshCw, Copy, Check } from "lucide-react";
import { PageHeader, Panel, AsyncBoundary, viewColor } from "./shared/AnalyticsUI";
import type { AsyncStatus } from "./shared/AnalyticsUI";
import { analyticsService } from "../../services/analyticsService";
import type { ResumenEjecutivoDTO } from "../../types/analytics";

/* HU-AN-07 — Resumen Ejecutivo Automático · /torneos/:id/resumen-ejecutivo
 * Conectado a POST /api/analitica/torneos/:id/resumen-ejecutivo/?tono=
 */

const TEAL = viewColor.teal;
const TONOS = [
  { key: "DIVULGATIVO", label: "Divulgativo" },
  { key: "FORMAL", label: "Formal" },
  { key: "CELEBRATORIO", label: "Celebratorio" },
];

// Resalta dentro del texto los valores de las métricas inyectadas
function renderConHighlights(texto: string, valores: string[]) {
  if (valores.length === 0) return texto;
  const escaped = valores.filter(Boolean).map((v) => v.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const re = new RegExp(`(${escaped.join("|")})`, "g");
  return texto.split(re).map((part, i) =>
    escaped.some((e) => new RegExp(`^${e}$`).test(part)) ? (
      <span key={i} className="font-semibold" style={{ color: TEAL }}>{part}</span>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}

export function ResumenEjecutivo() {
  const { id = "" } = useParams();
  const [tono, setTono] = useState("DIVULGATIVO");
  const [data, setData] = useState<ResumenEjecutivoDTO | null>(null);
  const [status, setStatus] = useState<AsyncStatus>("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [errorCode, setErrorCode] = useState<number | undefined>();
  const [copied, setCopied] = useState(false);

  const generar = useCallback(
    (tonoSel: string) => {
      setStatus("loading");
      analyticsService
        .generarResumenEjecutivo(id, tonoSel)
        .then((d) => {
          setData(d);
          setStatus("ok");
        })
        .catch((err: unknown) => {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const e = err as any;
          setErrorCode(e?.response?.status);
          setErrorMsg(e?.response?.data?.error || e?.response?.data?.detail || e?.message || "Error al generar el resumen.");
          setStatus("error");
        });
    },
    [id]
  );

  useEffect(() => { generar("DIVULGATIVO"); }, [generar]);

  const copiar = () => {
    if (data?.resumen_texto) {
      navigator.clipboard?.writeText(data.resumen_texto);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const m = data?.metricas_usadas;
  const chips = m
    ? [
        m.total_equipos != null ? `${m.total_equipos} equipos` : "",
        m.total_instituciones != null ? `${m.total_instituciones} instituciones` : "",
        m.total_participantes != null ? `${m.total_participantes} participantes` : "",
        m.campeon_nombre ? `Campeón: ${m.campeon_nombre}` : "",
        m.puntaje_campeon != null ? `Top: ${Number(m.puntaje_campeon).toFixed(1)} pts` : "",
      ].filter(Boolean)
    : [];

  // valores literales a resaltar en el texto
  const valoresResaltar = m
    ? [
        String(m.total_equipos ?? ""),
        String(m.total_instituciones ?? ""),
        String(m.total_participantes ?? ""),
        String(m.campeon_nombre ?? ""),
      ].filter((v) => v && v !== "undefined")
    : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader title="Resumen ejecutivo automático" accent={TEAL} />

      {/* Configuración de tono */}
      <div className="flex flex-wrap items-center gap-6 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-500">Tono del resumen:</span>
          {TONOS.map((t) => (
            <button
              key={t.key}
              onClick={() => { setTono(t.key); generar(t.key); }}
              disabled={status === "loading"}
              className="rounded-md border px-3 py-1.5 text-xs font-semibold transition-colors disabled:opacity-50"
              style={tono === t.key ? { borderColor: TEAL, color: TEAL, backgroundColor: `${TEAL}10` } : { borderColor: "#e2e8f0", color: "#94a3b8" }}
            >
              {t.label} {tono === t.key && "✓"}
            </button>
          ))}
        </div>
        {data && <span className="text-sm text-slate-400">Versión {data.version}</span>}
        <button
          onClick={() => generar(tono)}
          disabled={status === "loading"}
          className="ml-auto inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
          style={{ backgroundColor: TEAL }}
        >
          <RefreshCw className={`h-4 w-4 ${status === "loading" ? "animate-spin" : ""}`} /> Regenerar resumen
        </button>
      </div>

      {/* Métricas inyectadas */}
      {chips.length > 0 && (
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="mb-2 text-sm font-medium text-slate-600">Datos inyectados al modelo:</p>
          <div className="flex flex-wrap gap-2">
            {chips.map((c) => (
              <span key={c} className="rounded-full px-3 py-1 text-xs font-medium" style={{ backgroundColor: "#ccfbf1", color: TEAL }}>{c}</span>
            ))}
          </div>
          {data && (
            <p className="mt-2 text-xs text-slate-400">{data.num_palabras} palabras · Tono {data.tono} · v{data.version}</p>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Panel title="Texto generado" accentBar={TEAL}>
            <AsyncBoundary
              status={status}
              errorMsg={errorMsg}
              errorCode={errorCode}
              onRetry={() => generar(tono)}
              loadingLabel="Generando resumen…"
              emptyLabel="No se pudo generar el resumen."
            >
              {data && (
                <p className="text-sm leading-7 text-slate-700 whitespace-pre-line">
                  {renderConHighlights(data.resumen_texto, valoresResaltar)}
                </p>
              )}
            </AsyncBoundary>
          </Panel>
        </div>

        <Panel title="Análisis del texto">
          {data ? (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-slate-200 p-3">
                  <p className="text-[10px] uppercase text-slate-400">Palabras</p>
                  <p className="text-xl font-bold text-slate-700">{data.num_palabras}</p>
                </div>
                <div className="rounded-lg border border-slate-200 p-3">
                  <p className="text-[10px] uppercase text-slate-400">Versión</p>
                  <p className="text-xl font-bold" style={{ color: viewColor.indigo }}>{data.version}</p>
                </div>
              </div>

              <p className="mt-4 mb-2 text-xs font-semibold uppercase text-slate-400">Datos citados</p>
              <div className="space-y-2">
                {chips.map((c) => (
                  <div key={c} className="flex items-start gap-2 rounded-md bg-green-50 px-3 py-1.5 text-xs text-green-700">
                    <span>✓</span><span>{c}</span>
                  </div>
                ))}
              </div>

              <p className="mt-4 mb-2 text-xs font-semibold uppercase text-slate-400">Exportar resumen</p>
              <button onClick={copiar} className="inline-flex items-center gap-2 rounded-md border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50">
                {copied ? <Check className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
                {copied ? "Copiado" : "Copiar texto"}
              </button>
            </>
          ) : (
            <p className="text-sm text-slate-400">Genera un resumen para ver el análisis.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
