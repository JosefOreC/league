import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { ArrowLeft, FlaskConical, Loader2, FileText } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import {
  analizarComponentes,
  analizarProgramacion,
  getAnalisisPrevios,
  getRetosTorneo,
} from "../../services/simulationService";
import {
  CasoReto,
  type AnalisisEntregaResponse,
  type RetoTorneo,
} from "../../types/simulation";

const TABS: { caso: CasoReto; label: string }[] = [
  { caso: CasoReto.PROGRAMACION, label: "Programación" },
  { caso: CasoReto.COMPONENTES, label: "Componentes" },
];

export function RetoAnalyzer() {
  const { tournamentId } = useParams<{ tournamentId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [caso, setCaso] = useState<CasoReto>(CasoReto.PROGRAMACION);
  const [retos, setRetos] = useState<RetoTorneo[]>([]);
  const [selectedRetoId, setSelectedRetoId] = useState<string>("");
  const [content, setContent] = useState("");
  const [historial, setHistorial] = useState<AnalisisEntregaResponse[]>([]);
  const [analysisResult, setAnalysisResult] = useState<AnalisisEntregaResponse | null>(null);

  const [isLoadingRetos, setIsLoadingRetos] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const selectedReto = retos.find((r) => r.id === selectedRetoId) ?? null;

  // Cargar retos del caso activo
  useEffect(() => {
    if (!tournamentId) return;
    setIsLoadingRetos(true);
    getRetosTorneo(tournamentId, caso)
      .then((data) => {
        setRetos(data);
        setSelectedRetoId(data[0]?.id ?? "");
      })
      .finally(() => setIsLoadingRetos(false));
  }, [tournamentId, caso]);

  // Cargar análisis previos
  useEffect(() => {
    if (!tournamentId || !user?.id) return;
    getAnalisisPrevios(user.id, tournamentId)
      .then((prev) => setHistorial(prev.filter((a) => a.caso === caso)))
      .catch(() => setHistorial([]));
  }, [tournamentId, user?.id, caso]);

  async function handleAnalyze() {
    if (!selectedReto || !content || !tournamentId || !user?.id) return;
    setIsAnalyzing(true);
    try {
      const result =
        caso === CasoReto.PROGRAMACION
          ? await analizarProgramacion({
              reto_id: selectedReto.id,
              participante_id: user.id,
              torneo_id: tournamentId,
              codigo_fuente: content,
            })
          : await analizarComponentes({
              reto_id: selectedReto.id,
              participante_id: user.id,
              torneo_id: tournamentId,
              descripcion_solucion: content,
            });
      setAnalysisResult(result);
      const prev = await getAnalisisPrevios(user.id, tournamentId);
      setHistorial(prev.filter((a) => a.caso === caso));
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate(`/dashboard/simulaciones/torneo/${tournamentId}`)}
          className="text-sm text-slate-500 hover:text-slate-700 inline-flex items-center mb-3"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver al torneo
        </button>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-xl text-purple-600">
            <FlaskConical size={22} />
          </div>
          Analizador de Retos
        </h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200">
        {TABS.map((t) => (
          <button
            key={t.caso}
            onClick={() => {
              setCaso(t.caso);
              setContent("");
              setAnalysisResult(null);
            }}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              caso === t.caso
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Selector de reto + textarea */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 space-y-4">
        {isLoadingRetos ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          </div>
        ) : retos.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-6">
            No hay retos disponibles para este caso.
          </p>
        ) : (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Reto</label>
              <select
                value={selectedRetoId}
                onChange={(e) => setSelectedRetoId(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {retos.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.titulo}
                  </option>
                ))}
              </select>
            </div>

            {selectedReto && (
              <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
                <p className="text-sm text-slate-600 mb-2">{selectedReto.descripcion}</p>
                <p className="text-xs text-slate-500">
                  Criterios:{" "}
                  {selectedReto.criterios_evaluacion
                    .map((c) => `${c.nombre} ${c.peso}%`)
                    .join(" · ")}
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                {caso === CasoReto.PROGRAMACION ? "Código fuente" : "Descripción de la solución"}
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder={
                  caso === CasoReto.PROGRAMACION
                    ? "Pega aquí el código fuente del robot"
                    : "Describe la solución de hardware/componentes"
                }
                rows={10}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none font-mono"
              />
            </div>

            <div className="flex justify-end">
              <button
                onClick={handleAnalyze}
                disabled={!selectedReto || !content || isAnalyzing}
                className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 inline-flex items-center disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analizando...
                  </>
                ) : (
                  <>Analizar entrega →</>
                )}
              </button>
            </div>
          </>
        )}
      </div>

      {/* Resultado del análisis */}
      {analysisResult && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Resultado del análisis</h2>
            <span className="text-2xl font-bold text-blue-600">
              {analysisResult.puntaje_total_simulado.toFixed(1)}
              <span className="text-sm text-slate-400 font-normal"> / 100</span>
            </span>
          </div>

          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wider text-slate-500 border-b border-slate-200">
                <th className="py-2">Criterio</th>
                <th className="py-2 text-center">Puntos</th>
                <th className="py-2 text-center">Máx.</th>
                <th className="py-2 w-1/3">Progreso</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {analysisResult.calificaciones_por_criterio.map((c, i) => {
                const pct = c.max_puntos > 0 ? (c.puntos / c.max_puntos) * 100 : 0;
                return (
                  <tr key={i}>
                    <td className="py-2.5 font-medium text-slate-900">{c.criterio}</td>
                    <td className="py-2.5 text-center text-slate-700">{c.puntos}</td>
                    <td className="py-2.5 text-center text-slate-500">{c.max_puntos}</td>
                    <td className="py-2.5">
                      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <blockquote className="border-l-4 border-blue-400 bg-blue-50 pl-4 py-2 text-sm text-blue-800 italic">
            {analysisResult.observacion_general}
          </blockquote>
        </div>
      )}

      {/* Análisis previos */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
          <FileText className="h-5 w-5 mr-2 text-slate-500" />
          Análisis previos
        </h2>
        {historial.length === 0 ? (
          <p className="text-sm text-slate-500">Aún no hay análisis previos para este caso.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {historial.map((a) => (
              <li key={a.id} className="py-3 flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium text-slate-900">
                    {retos.find((r) => r.id === a.reto_id)?.titulo ?? a.reto_id}
                  </span>
                  <span className="text-xs text-slate-400 ml-2">
                    {new Date(a.creado_en).toLocaleDateString("es-PE", {
                      day: "2-digit",
                      month: "short",
                    })}
                  </span>
                </div>
                <span className="text-sm font-semibold text-slate-700">
                  {a.puntaje_total_simulado.toFixed(1)} / 100
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
