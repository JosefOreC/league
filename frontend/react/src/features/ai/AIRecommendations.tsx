import { useState } from "react";
import {
  BrainCircuit,
  Sparkles,
  AlertCircle,
  CheckCircle,
  Loader2,
  ChevronRight,
  Cpu,
  BarChart3,
} from "lucide-react";
import { generarCriteriosEvaluacion, actualizarPesoCriterio, confirmarCriterios } from "../../services/aiService";
import { getTournaments } from "../../services/tournamentService";
import { CriterioEvaluacionIA } from "../../types/ai";
import { Tournament, EstadoTorneo } from "../../types/tournament";
import axios from "axios";

type Nivel = "BASICO" | "INTERMEDIO" | "AVANZADO";

export function AIRecommendations() {
  const [torneos, setTorneos] = useState<Tournament[]>([]);
  const [loadingTorneos, setLoadingTorneos] = useState(false);

  // HU-IA-05: Generación de Criterios
  const [selectedTorneoId, setSelectedTorneoId] = useState("");
  const [nivel, setNivel] = useState<Nivel>("BASICO");
  const [isGenerating, setIsGenerating] = useState(false);
  const [sesionId, setSesionId] = useState<string | null>(null);
  const [criterios, setCriterios] = useState<CriterioEvaluacionIA[]>([]);
  const [isConfirming, setIsConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const selectedTorneo = torneos.find(t => t.id === selectedTorneoId);
  const totalPesos = criterios.reduce((sum, c) => sum + c.peso_porcentual, 0);

  const loadTorneos = async () => {
    setLoadingTorneos(true);
    try {
      const data = await getTournaments();
      // Solo torneos activos donde se pueden configurar criterios
      setTorneos(data.filter(t =>
        t.state === EstadoTorneo.DRAFT ||
        t.state === EstadoTorneo.IN_REVIEW
      ));
    } catch {
      setError("No se pudieron cargar los torneos.");
    } finally {
      setLoadingTorneos(false);
    }
  };

  // Cargar torneos al montar si el selector está vacío
  const handleLoadTorneos = () => {
    if (torneos.length === 0) loadTorneos();
  };

  const handleGenerarCriterios = async () => {
    if (!selectedTorneoId || !selectedTorneo) return;
    setError(null);
    setSuccess(null);
    setIsGenerating(true);
    setCriterios([]);
    setSesionId(null);
    try {
      // tipo_torneo viene anidado en config_tournament.type
      const tipoTorneo = selectedTorneo.config_tournament?.type || "knockout";
      const result = await generarCriteriosEvaluacion({
        torneo_id: selectedTorneoId,
        tipo_torneo: tipoTorneo.toUpperCase(),
        nivel,
        categoria: (selectedTorneo.category || "explorador").toUpperCase(),
        descripcion: selectedTorneo.description,
      });
      setSesionId(result.sesion_ia_id);
      setCriterios(result.criterios);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || "Error al generar criterios.");
      } else {
        setError("Error de conexión con el servidor de IA.");
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePesoChange = async (criterioId: string, nuevoPeso: number) => {
    try {
      await actualizarPesoCriterio(criterioId, nuevoPeso);
      setCriterios(prev => prev.map(c =>
        c.id === criterioId ? { ...c, peso_porcentual: nuevoPeso } : c
      ));
    } catch {
      // Actualización optimista ya aplicada, error silencioso para UX fluida
    }
  };

  const handleConfirmarCriterios = async () => {
    if (!sesionId) return;
    if (Math.abs(totalPesos - 100) > 0.5) {
      setError(`La suma de pesos debe ser 100%. Actualmente es ${totalPesos.toFixed(1)}%.`);
      return;
    }
    setError(null);
    setIsConfirming(true);
    try {
      await confirmarCriterios(sesionId);
      setSuccess("✅ Criterios de evaluación confirmados y aplicados al torneo correctamente.");
      setCriterios([]);
      setSesionId(null);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || "Error al confirmar criterios.");
      } else {
        setError("Error de conexión.");
      }
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
          <BrainCircuit className="h-6 w-6 text-purple-600 mr-2" />
          Inteligencia Artificial
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Asistente inteligente para generar y configurar criterios de evaluación para tus torneos.
        </p>
      </div>

      {/* Alertas */}
      {error && (
        <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm">
          <AlertCircle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}
      {success && (
        <div className="flex items-center gap-3 p-3 rounded-md bg-green-50 border border-green-300 text-green-700 text-sm">
          <CheckCircle size={16} className="shrink-0" />
          <span>{success}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Panel izquierdo: Configuración */}
        <div className="lg:col-span-1 space-y-5">
          <div className="bg-gradient-to-br from-purple-900 to-indigo-900 text-white rounded-2xl p-6 shadow-lg">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="h-5 w-5 text-purple-300" />
              <h2 className="font-semibold text-purple-100">Generador de Rúbricas</h2>
            </div>
            <p className="text-xs text-purple-300 mb-5 leading-relaxed">
              Selecciona un torneo y el nivel de exigencia. La IA generará criterios de evaluación balanceados con pesos automáticos.
            </p>

            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-purple-200">Torneo</label>
                <select
                  className="flex h-10 w-full rounded-md border border-purple-600 bg-purple-800/50 text-white px-3 py-2 text-sm focus:ring-purple-400 focus:border-purple-400"
                  value={selectedTorneoId}
                  onClick={handleLoadTorneos}
                  onChange={e => setSelectedTorneoId(e.target.value)}
                >
                  <option value="">
                    {loadingTorneos ? "Cargando torneos..." : "Seleccione un torneo..."}
                  </option>
                  {torneos.map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-purple-200">Nivel de Exigencia</label>
                <select
                  className="flex h-10 w-full rounded-md border border-purple-600 bg-purple-800/50 text-white px-3 py-2 text-sm"
                  value={nivel}
                  onChange={e => setNivel(e.target.value as Nivel)}
                >
                  <option value="BASICO">Básico (Explorador)</option>
                  <option value="INTERMEDIO">Intermedio (Innovador)</option>
                  <option value="AVANZADO">Avanzado (Constructor)</option>
                </select>
              </div>

              <button
                onClick={handleGenerarCriterios}
                disabled={!selectedTorneoId || isGenerating}
                className="w-full inline-flex items-center justify-center rounded-md text-sm font-semibold bg-purple-500 hover:bg-purple-400 text-white h-10 px-4 disabled:opacity-50 transition-colors shadow-sm"
              >
                {isGenerating ? (
                  <><Loader2 size={14} className="animate-spin mr-2" />Generando...</>
                ) : (
                  <><Cpu size={14} className="mr-2" />Generar Criterios IA</>
                )}
              </button>
            </div>
          </div>

          {/* Info del torneo seleccionado */}
          {selectedTorneo && (
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm text-sm space-y-2">
              <h3 className="font-semibold text-slate-800 text-xs uppercase tracking-wide">Torneo Seleccionado</h3>
              <p className="font-medium text-slate-900">{selectedTorneo.name}</p>
              <div className="flex gap-2">
                <span className="px-2 py-0.5 rounded-full text-xs bg-blue-100 text-blue-700 capitalize">{selectedTorneo.category}</span>
                <span className="px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-600 capitalize">{selectedTorneo.state}</span>
              </div>
            </div>
          )}
        </div>

        {/* Panel derecho: Resultados */}
        <div className="lg:col-span-2">
          {criterios.length === 0 && !isGenerating ? (
            <div className="bg-white border border-dashed border-slate-300 rounded-2xl p-12 text-center flex flex-col items-center justify-center h-full min-h-[350px]">
              <BarChart3 className="h-12 w-12 text-slate-300 mb-4" />
              <h3 className="text-slate-500 font-medium mb-2">Sin criterios generados</h3>
              <p className="text-slate-400 text-sm max-w-xs">
                Selecciona un torneo y haz clic en "Generar Criterios IA" para obtener una rúbrica de evaluación personalizada.
              </p>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
                <div>
                  <h2 className="font-semibold text-slate-900">Criterios Sugeridos por IA</h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Sesión: <code className="bg-slate-100 px-1 rounded text-purple-600">{sesionId?.slice(0, 8)}…</code>
                  </p>
                </div>
                <span className={`text-xs font-bold px-3 py-1.5 rounded-full border ${
                  Math.abs(totalPesos - 100) < 0.5
                    ? "bg-green-100 text-green-700 border-green-200"
                    : "bg-red-100 text-red-700 border-red-200"
                }`}>
                  Σ Pesos: {totalPesos.toFixed(1)}%
                </span>
              </div>

              <div className="divide-y divide-slate-50">
                {criterios.map((c, i) => (
                  <div key={c.id} className="p-4 hover:bg-slate-50/50 transition-colors">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-xs font-bold">
                        {i + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-4 mb-1">
                          <h3 className="font-semibold text-slate-900 text-sm">{c.nombre}</h3>
                          <div className="flex items-center gap-2 shrink-0">
                            <label className="text-xs text-slate-500">Peso %:</label>
                            <input
                              type="number"
                              step="1"
                              min="0"
                              max="100"
                              value={c.peso_porcentual}
                              onChange={e => handlePesoChange(c.id, parseFloat(e.target.value) || 0)}
                              className="w-20 text-center rounded-md border border-slate-300 px-2 py-1 text-sm focus:ring-purple-500 focus:border-purple-500"
                            />
                          </div>
                        </div>
                        <p className="text-xs text-slate-500 mb-2">{c.descripcion}</p>
                        <div className="flex items-center gap-4 text-xs text-slate-400">
                          <span>Rango: [{c.valor_minimo ?? 0} – {c.valor_maximo ?? 100}]</span>
                          <span>Mayor es mejor: {c.mayor_es_mejor ? "✓" : "✗"}</span>
                          <span className="px-1.5 py-0.5 bg-slate-100 rounded capitalize">{c.tipo_dato}</span>
                        </div>
                        {/* Barra de peso visual */}
                        <div className="mt-2 w-full bg-slate-100 rounded-full h-1.5">
                          <div
                            className="bg-purple-500 h-1.5 rounded-full transition-all"
                            style={{ width: `${Math.min(c.peso_porcentual, 100)}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
                <p className="text-xs text-slate-500">
                  {Math.abs(totalPesos - 100) < 0.5
                    ? "✅ Pesos balanceados. Puedes confirmar."
                    : `⚠ Ajusta los pesos para que sumen 100% (faltan ${(100 - totalPesos).toFixed(1)}%).`
                  }
                </p>
                <button
                  onClick={handleConfirmarCriterios}
                  disabled={isConfirming || Math.abs(totalPesos - 100) > 0.5}
                  className="inline-flex items-center gap-2 px-5 py-2 rounded-md bg-purple-600 text-white text-sm font-semibold hover:bg-purple-700 disabled:opacity-50 transition-colors shadow-sm"
                >
                  {isConfirming ? <Loader2 size={14} className="animate-spin" /> : <ChevronRight size={14} />}
                  Confirmar Criterios
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
