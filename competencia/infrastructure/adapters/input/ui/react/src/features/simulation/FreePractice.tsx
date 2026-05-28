import { useState } from "react";
import {
  Gamepad2,
  Play,
  Loader2,
  AlertCircle,
  Trophy,
} from "lucide-react";
import { toast } from "sonner";
import {
  EjecucionSimulacionResponse,
  FormatoSimulacion,
  NivelDificultad,
  PracticaLibreRequest,
} from "../../types/simulation";
import { iniciarPracticaLibre } from "../../services/simulationService";

const NIVEL_LABEL: Record<NivelDificultad, string> = {
  [NivelDificultad.PRINCIPIANTE]: "Principiante",
  [NivelDificultad.INTERMEDIO]: "Intermedio",
  [NivelDificultad.AVANZADO]: "Avanzado",
  [NivelDificultad.RETO_EXTREMO]: "Reto Extremo",
};

const FORMATO_LABEL: Record<FormatoSimulacion, string> = {
  [FormatoSimulacion.KNOCKOUT]: "Knockout",
  [FormatoSimulacion.ROUND_ROBIN]: "Round Robin",
  [FormatoSimulacion.HYBRID]: "Híbrido",
};

export function FreePractice() {
  const [formData, setFormData] = useState<PracticaLibreRequest>({
    nivel_dificultad: NivelDificultad.PRINCIPIANTE,
    formato: FormatoSimulacion.ROUND_ROBIN,
    num_equipos: 4,
  });

  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<EjecucionSimulacionResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.num_equipos < 2 || formData.num_equipos > 15) {
      setError("El número de equipos debe estar entre 2 y 15.");
      return;
    }

    setIsRunning(true);
    setResultado(null);
    try {
      const res = await iniciarPracticaLibre(formData);
      setResultado(res);
      toast.success("Práctica completada — no afecta estadísticas oficiales");
    } catch {
      setError("Ocurrió un error al ejecutar la práctica.");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
          <Gamepad2 className="mr-3 h-7 w-7 text-blue-600" />
          Práctica Libre
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Entrena con simulaciones sin estar inscrito en un torneo. Los resultados no afectan estadísticas oficiales.
        </p>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <p className="text-sm text-amber-800">
          <strong>Modo práctica</strong> · estas simulaciones no se guardan en el historial oficial del equipo ni aparecen en el panel del docente de torneos.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Nivel de dificultad
            </label>
            <select
              value={formData.nivel_dificultad}
              onChange={(e) =>
                setFormData((p) => ({ ...p, nivel_dificultad: e.target.value as NivelDificultad }))
              }
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Object.values(NivelDificultad).map((n) => (
                <option key={n} value={n}>
                  {NIVEL_LABEL[n]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Formato
            </label>
            <select
              value={formData.formato}
              onChange={(e) =>
                setFormData((p) => ({ ...p, formato: e.target.value as FormatoSimulacion }))
              }
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Object.values(FormatoSimulacion).map((f) => (
                <option key={f} value={f}>
                  {FORMATO_LABEL[f]}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Número de equipos (2 – 15)
          </label>
          <input
            type="number"
            min={2}
            max={15}
            value={formData.num_equipos}
            onChange={(e) => setFormData((p) => ({ ...p, num_equipos: Number(e.target.value) }))}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex justify-end pt-2 border-t border-slate-100">
          <button
            type="submit"
            disabled={isRunning}
            className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 inline-flex items-center disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isRunning ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Ejecutando...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Iniciar práctica
              </>
            )}
          </button>
        </div>
      </form>

      {resultado && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900 flex items-center">
              <Trophy className="h-5 w-5 mr-2 text-blue-600" />
              Resultados de la práctica
            </h2>
            <span className="text-xs text-slate-500">
              {resultado.enfrentamientos.length} enfrentamientos · {(resultado.duracion_ms / 1000).toFixed(1)}s
            </span>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wider text-slate-500 border-b border-slate-200">
                <th className="px-6 py-3">Rival</th>
                <th className="px-6 py-3 text-center">Mi puntaje</th>
                <th className="px-6 py-3 text-center">Rival</th>
                <th className="px-6 py-3 text-center">Confianza</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {resultado.enfrentamientos.map((e, idx) => {
                const gane = e.puntaje_estimado_local > e.puntaje_estimado_visitante;
                return (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="px-6 py-3 text-slate-700">Equipo rival #{idx + 1}</td>
                    <td className={`px-6 py-3 text-center font-semibold ${gane ? "text-green-700" : "text-slate-700"}`}>
                      {e.puntaje_estimado_local}
                    </td>
                    <td className={`px-6 py-3 text-center ${!gane ? "text-red-700 font-semibold" : "text-slate-700"}`}>
                      {e.puntaje_estimado_visitante}
                    </td>
                    <td className="px-6 py-3 text-center text-slate-600">
                      {Math.round(e.nivel_confianza * 100)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
