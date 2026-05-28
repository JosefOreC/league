import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import axios from "axios";
import { toast } from "sonner";
import {
  Sparkles,
  ArrowLeft,
  Loader2,
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  MessageSquare,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { getSimulationContext, runSimulation } from "../../services/simulationService";
import type { SimulationContext, SimulationResult } from "../../types/simulation";

function barColor(valor: number): string {
  if (valor >= 70) return "#16a34a"; // verde
  if (valor >= 40) return "#d97706"; // ámbar
  return "#dc2626"; // rojo
}

export function SimulationEditor() {
  const { tournamentId } = useParams<{ tournamentId: string }>();
  const navigate = useNavigate();

  const [context, setContext] = useState<SimulationContext | null>(null);
  const [entregable, setEntregable] = useState("");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const charCount = entregable.length;
  const canSubmit = charCount >= 100 && !isExecuting;

  useEffect(() => {
    if (!tournamentId) return;
    getSimulationContext(tournamentId)
      .then(setContext)
      .catch((err) => {
        if (axios.isAxiosError(err) && err.response?.status === 403) {
          setError("No tienes un equipo aprobado en este torneo.");
        } else if (axios.isAxiosError(err) && err.response?.status === 404) {
          toast.error("Torneo no encontrado");
          setTimeout(() => navigate("/dashboard/simulaciones"), 1500);
        } else {
          setError("No se pudo cargar el contexto de la simulación.");
        }
      })
      .finally(() => setIsLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tournamentId]);

  async function handleExecute() {
    if (!canSubmit || !tournamentId) return;
    setIsExecuting(true);
    try {
      const data = await runSimulation(tournamentId, { entregable });
      setResult(data);
      if (data.puntaje_total >= 80) {
        // @ts-expect-error — canvas-confetti no incluye tipos
        void import("canvas-confetti").then((m) =>
          m.default({ particleCount: 80, spread: 70, origin: { y: 0.6 } })
        );
      }
      setTimeout(
        () => document.getElementById("resultado")?.scrollIntoView({ behavior: "smooth" }),
        60
      );
    } finally {
      setIsExecuting(false);
    }
  }

  // ── Loading ──────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="h-12 w-12 text-blue-500 animate-spin" />
        <p className="text-slate-500 font-medium">Cargando contexto...</p>
      </div>
    );
  }

  // ── Error 403 (sin equipo aprobado) ────────────────────────────────────────
  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        <div className="bg-red-50 border border-red-200 rounded-2xl p-12 text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-700 font-medium mb-6">{error}</p>
          <button
            onClick={() => navigate("/dashboard/simulaciones")}
            className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 inline-flex items-center"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Volver a Mis Simulaciones
          </button>
        </div>
      </div>
    );
  }

  if (!context) return null;

  const sumaPesos = context.criterios.reduce((acc, c) => acc + c.peso, 0);

  const dataChart = result?.scores.map((s) => ({
    nombre: s.nombre.length > 18 ? s.nombre.slice(0, 18) + "…" : s.nombre,
    valor_normalizado: s.valor_normalizado,
  }));

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate("/dashboard/simulaciones")}
          className="text-sm text-slate-500 hover:text-slate-700 inline-flex items-center mb-3"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a Mis Simulaciones
        </button>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-xl text-purple-600">
            <Sparkles size={22} />
          </div>
          Simulación de entregable
        </h1>
        <p className="text-sm text-slate-500 mt-1 ml-1">
          {context.tournament.name} · {context.team.name}
        </p>
      </div>

      {/* Editor: criterios + entregable */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Criterios oficiales */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">📋 Criterios oficiales</h2>
          <div className="space-y-3">
            {context.criterios.map((c) => (
              <div key={c.id} className="border border-slate-100 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-slate-900">{c.name}</span>
                  <span className="text-sm font-bold text-blue-600">{c.peso}%</span>
                </div>
                {c.description && <p className="text-xs text-slate-500 mb-1">{c.description}</p>}
                <p className="text-xs text-slate-400">
                  Rango: {c.min_qualification} – {c.max_qualification}
                </p>
              </div>
            ))}
          </div>
          <p className="text-sm text-slate-500 mt-4 pt-3 border-t border-slate-100">
            Suma de pesos: <span className="font-semibold text-slate-700">{sumaPesos}%</span>
          </p>
        </div>

        {/* Entregable */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 flex flex-col">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">📝 Tu entregable</h2>
          <textarea
            value={entregable}
            onChange={(e) => setEntregable(e.target.value)}
            placeholder="Describe el entregable de tu equipo (mínimo 100 caracteres)..."
            rows={10}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none flex-1"
          />
          <div className="flex items-center justify-between mt-2">
            <span className={`text-xs ${charCount < 100 ? "text-red-600" : "text-slate-500"}`}>
              {charCount} / mín. 100 caracteres
            </span>
          </div>
          {charCount > 0 && charCount < 100 && (
            <p className="text-xs text-red-600 mt-1">
              El entregable debe tener al menos 100 caracteres.
            </p>
          )}
          <button
            onClick={handleExecute}
            disabled={!canSubmit}
            className="mt-4 px-4 py-2.5 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 inline-flex items-center justify-center disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isExecuting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Ejecutando...
              </>
            ) : (
              <>
                Ejecutar simulación
                <Sparkles className="h-4 w-4 ml-2" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Resultado embebido */}
      {result && (
        <div id="resultado" className="space-y-6 scroll-mt-6">
          {/* KPI cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">
              <p className="text-xs font-medium text-slate-500 mb-1">Puntaje</p>
              <p className="text-2xl font-bold text-slate-900">
                {result.puntaje_total.toFixed(2)}
                <span className="text-sm text-slate-400 font-normal"> / 100</span>
              </p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">
              <p className="text-xs font-medium text-slate-500 mb-1">Posición</p>
              <p className="text-2xl font-bold text-slate-900">
                {result.posicion_estimada.posicion_estimada}
                <span className="text-sm text-slate-400 font-normal">
                  {" "}
                  / {result.posicion_estimada.total_equipos}
                </span>
              </p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">
              <p className="text-xs font-medium text-slate-500 mb-1">Percentil</p>
              <p className="text-2xl font-bold text-slate-900">
                {result.posicion_estimada.percentil}%
              </p>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">
              <p className="text-xs font-medium text-slate-500 mb-1">Equipos</p>
              <p className="text-2xl font-bold text-slate-900">
                {result.posicion_estimada.total_equipos}
              </p>
            </div>
          </div>

          {/* Gráfico por criterio */}
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">📊 Puntaje por criterio</h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dataChart} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="nombre" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "white",
                      border: "1px solid #e2e8f0",
                      borderRadius: "8px",
                    }}
                  />
                  <Bar dataKey="valor_normalizado" radius={[4, 4, 0, 0]}>
                    {dataChart?.map((d, i) => (
                      <Cell key={i} fill={barColor(d.valor_normalizado)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Fortalezas / Debilidades */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                <CheckCircle2 className="h-5 w-5 mr-2 text-green-600" />
                Fortalezas
              </h2>
              {result.fortalezas.length === 0 ? (
                <p className="text-sm text-slate-500">Sin fortalezas destacadas.</p>
              ) : (
                <ul className="space-y-3">
                  {result.fortalezas.map((f) => (
                    <li key={f.criterio_id} className="border-l-4 border-green-500 pl-4">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-slate-900">{f.nombre}</span>
                        <span className="text-sm font-bold text-green-700">
                          {f.valor_normalizado}%
                        </span>
                      </div>
                      {f.motivo && <p className="text-sm text-slate-600 mt-0.5">{f.motivo}</p>}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-amber-600" />
                Debilidades
              </h2>
              {result.debilidades.length === 0 ? (
                <p className="text-sm text-slate-500">Sin debilidades críticas.</p>
              ) : (
                <ul className="space-y-3">
                  {result.debilidades.map((d) => (
                    <li key={d.criterio_id} className="border-l-4 border-amber-500 pl-4">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-slate-900">{d.nombre}</span>
                        <span className="text-sm font-bold text-amber-700">
                          {d.valor_normalizado}%
                        </span>
                      </div>
                      {d.motivo && <p className="text-sm text-slate-600 mt-0.5">{d.motivo}</p>}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Retroalimentación */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h2 className="text-base font-semibold text-blue-900 mb-2 flex items-center">
              <MessageSquare className="h-5 w-5 mr-2" />
              Retroalimentación
            </h2>
            <p className="text-sm text-blue-800 mb-3">{result.retroalimentacion.resumen}</p>
            {result.retroalimentacion.sin_mejoras_criticas ? (
              <p className="text-sm text-green-700 font-medium">
                ¡Excelente! No hay mejoras críticas pendientes.
              </p>
            ) : (
              <ul className="list-disc list-inside space-y-1 text-sm text-blue-800">
                {result.retroalimentacion.recomendaciones.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => {
                setResult(null);
                setEntregable("");
              }}
              className="px-4 py-2 text-sm text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
            >
              Nueva simulación
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
