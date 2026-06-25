import { useState } from "react";
import { useParams } from "react-router";
import { Download, Bot, Loader2, CheckCircle2, AlertTriangle } from "lucide-react";
import { PageHeader, viewColor } from "./shared/AnalyticsUI";
import { analyticsService } from "../../services/analyticsService";

/* HU-AN-06 — Certificados y Reconocimientos · /torneos/:id/certificados
 * Conectado a POST /api/analitica/torneos/:id/certificados/?tipo=PARTICIPACION|GANADOR
 * El endpoint devuelve un archivo (ZIP/PDF); aquí se dispara la descarga real.
 */

const TABS = ["Participación", "Ganadores"] as const;

function descargarBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

type Resultado =
  | { kind: "participacion"; total: number; excluidos: number }
  | { kind: "ganador"; medalla?: string; codigo?: string };

export function Certificados() {
  const { id = "" } = useParams();
  const [tab, setTab] = useState<(typeof TABS)[number]>("Participación");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resultado, setResultado] = useState<Resultado | null>(null);

  const generarParticipacion = async () => {
    setLoading(true); setError(""); setResultado(null);
    try {
      const r = await analyticsService.generarCertificados(id, "PARTICIPACION");
      descargarBlob(r.blob, `certificados_${id}.zip`);
      setResultado({ kind: "participacion", total: r.totalGenerados, excluidos: r.excluidosCount });
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const err = e as any;
      setError(err?.response?.data?.error || err?.message || "No se pudieron generar los certificados.");
    } finally {
      setLoading(false);
    }
  };

  const generarGanador = async () => {
    setLoading(true); setError(""); setResultado(null);
    try {
      // equipo campeón demo = "1"
      const r = await analyticsService.generarCertificados(id, "GANADOR", "1");
      descargarBlob(r.blob, `diploma_1.pdf`);
      setResultado({ kind: "ganador", medalla: r.medalla, codigo: r.codigo });
    } catch (e: unknown) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const err = e as any;
      setError(err?.response?.data?.error || err?.message || "No se pudo generar el diploma.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader title="Certificados y reconocimientos" />

      {/* Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200">
        <div className="flex gap-6">
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => { setTab(t); setResultado(null); setError(""); }}
              className={`-mb-px border-b-2 pb-3 text-sm font-medium transition-colors ${
                tab === t ? "border-indigo-600 text-indigo-600" : "border-transparent text-slate-400 hover:text-slate-600"
              }`}
            >
              {t} {tab === t && "✓"}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Panel de acción */}
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            {tab === "Participación" ? (
              <>
                <h2 className="text-base font-semibold text-slate-900">Certificados de participación</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Genera un PDF por cada participante <strong>autorizado</strong> y los empaqueta en un ZIP.
                  Los participantes sin autorización de datos quedan excluidos automáticamente.
                </p>
                <button
                  onClick={generarParticipacion}
                  disabled={loading}
                  className="mt-4 inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  style={{ backgroundColor: viewColor.indigo }}
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                  {loading ? "Generando ZIP…" : "Generar todos (ZIP)"}
                </button>
              </>
            ) : (
              <>
                <h2 className="text-base font-semibold text-slate-900">Diploma de ganador</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Genera el diploma en PDF del equipo campeón con su medalla y código de verificación.
                </p>
                <button
                  onClick={generarGanador}
                  disabled={loading}
                  className="mt-4 inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  style={{ backgroundColor: viewColor.indigo }}
                >
                  {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                  {loading ? "Generando PDF…" : "Generar diploma del campeón"}
                </button>
              </>
            )}

            {/* Resultado */}
            {resultado?.kind === "participacion" && (
              <div className="mt-4 flex items-start gap-2 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
                <CheckCircle2 className="h-5 w-5 shrink-0" />
                <span>
                  ZIP descargado. <strong>{resultado.total}</strong> certificados generados ·{" "}
                  <strong>{resultado.excluidos}</strong> excluidos por falta de autorización.
                </span>
              </div>
            )}
            {resultado?.kind === "ganador" && (
              <div className="mt-4 flex items-start gap-2 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
                <CheckCircle2 className="h-5 w-5 shrink-0" />
                <span>
                  Diploma descargado. Medalla: <strong>{resultado.medalla}</strong> · Código:{" "}
                  <span className="font-mono">{resultado.codigo}</span>
                </span>
              </div>
            )}
            {error && (
              <div className="mt-4 flex items-start gap-2 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                <AlertTriangle className="h-5 w-5 shrink-0" /> <span>{error}</span>
              </div>
            )}
          </div>
        </div>

        {/* Vista previa del certificado (plantilla visual) */}
        <div className="flex items-start justify-center">
          <div className="w-full rounded-lg p-8 text-center" style={{ backgroundColor: "#fefce8", border: `2px solid #d97706` }}>
            <p className="text-lg font-bold tracking-wide" style={{ color: "#ea580c" }}>
              CERTIFICADO DE {tab === "Participación" ? "PARTICIPACIÓN" : "RECONOCIMIENTO"}
            </p>
            <p className="text-xs text-slate-500">Torneo Regional de Robótica Educativa 2024</p>
            <div className="my-5 flex justify-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full" style={{ backgroundColor: viewColor.indigo }}>
                <Bot className="h-8 w-8 text-white" />
              </div>
            </div>
            <p className="text-sm text-slate-500">Se certifica la {tab === "Participación" ? "participación" : "distinción del equipo ganador"} en el</p>
            <p className="text-base font-semibold" style={{ color: viewColor.indigo }}>Torneo Regional de Robótica 2024</p>
            <p className="mt-6 text-[10px] text-slate-400">El documento oficial se genera y descarga con el botón de la izquierda.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
