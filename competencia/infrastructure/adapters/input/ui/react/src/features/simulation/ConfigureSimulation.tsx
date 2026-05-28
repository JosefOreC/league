import { useState } from "react";
import { useNavigate } from "react-router";
import { FlaskConical, Save, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import {
  ConfigurarSimulacionRequest,
  FormatoSimulacion,
  NivelDificultad,
} from "../../types/simulation";
import { configurarSimulacion } from "../../services/simulationService";

const TORNEOS_DISPONIBLES = [
  { id: "torneo-001", nombre: "Robotix Cup 2026 — Fase regional" },
  { id: "torneo-002", nombre: "Liga STEM Junín — Eliminatorias" },
  { id: "torneo-003", nombre: "Campeonato Escolar de Robótica El Tambo" },
];

const NIVEL_LABEL: Record<NivelDificultad, string> = {
  [NivelDificultad.PRINCIPIANTE]: "Principiante",
  [NivelDificultad.INTERMEDIO]: "Intermedio",
  [NivelDificultad.AVANZADO]: "Avanzado",
  [NivelDificultad.RETO_EXTREMO]: "Reto Extremo",
};

const FORMATO_LABEL: Record<FormatoSimulacion, string> = {
  [FormatoSimulacion.KNOCKOUT]: "Knockout (eliminación directa)",
  [FormatoSimulacion.ROUND_ROBIN]: "Round Robin (todos contra todos)",
  [FormatoSimulacion.HYBRID]: "Híbrido (grupos + eliminación)",
};

export function ConfigureSimulation() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState<ConfigurarSimulacionRequest>({
    torneo_id: TORNEOS_DISPONIBLES[0].id,
    nivel_dificultad: NivelDificultad.INTERMEDIO,
    num_equipos_simulados: 6,
    formato: FormatoSimulacion.ROUND_ROBIN,
  });

  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.num_equipos_simulados < 2 || formData.num_equipos_simulados > 15) {
      setError("El número de equipos rivales debe estar entre 2 y 15.");
      return;
    }

    setIsSaving(true);
    try {
      const sesion = await configurarSimulacion(formData);
      toast.success("Simulación configurada correctamente");
      navigate(`/dashboard/simulacion/${sesion.simulacion_id}/ejecutar`);
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setError("Solo equipos aprobados pueden acceder a simulaciones.");
      } else {
        setError("Ocurrió un error al configurar la simulación.");
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
          <FlaskConical className="mr-3 h-7 w-7 text-blue-600" />
          Configurar Simulación
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Diseña un escenario de práctica para que tu equipo entrene en condiciones similares al torneo real.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Torneo al que pertenece tu equipo
          </label>
          <select
            value={formData.torneo_id}
            onChange={(e) => setFormData((p) => ({ ...p, torneo_id: e.target.value }))}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {TORNEOS_DISPONIBLES.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nombre}
              </option>
            ))}
          </select>
        </div>

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
              Formato del torneo
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
            Número de equipos rivales simulados (2 – 15)
          </label>
          <input
            type="number"
            min={2}
            max={15}
            value={formData.num_equipos_simulados}
            onChange={(e) =>
              setFormData((p) => ({
                ...p,
                num_equipos_simulados: Number(e.target.value),
              }))
            }
            className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="px-4 py-2 text-sm text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isSaving}
            className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 inline-flex items-center disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <Save className="h-4 w-4 mr-2" />
            {isSaving ? "Configurando..." : "Configurar y continuar"}
          </button>
        </div>
      </form>
    </div>
  );
}
