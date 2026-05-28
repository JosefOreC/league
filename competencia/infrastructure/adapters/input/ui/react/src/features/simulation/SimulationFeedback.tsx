import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { FileText, Loader2, ArrowLeft } from "lucide-react";
import { RetroalimentacionSimulacion } from "../../types/simulation";
import { obtenerRetroalimentacion } from "../../services/simulationService";

function colorGap(gap: number) {
  if (gap === 0) return "bg-green-100 text-green-700";
  if (gap <= 15) return "bg-yellow-100 text-yellow-700";
  return "bg-red-100 text-red-700";
}

export function SimulationFeedback() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [retro, setRetro] = useState<RetroalimentacionSimulacion | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    obtenerRetroalimentacion(id)
      .then(setRetro)
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!retro) {
    return <p className="text-center text-slate-500 py-12">No se pudo cargar la retroalimentación.</p>;
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
            <FileText className="mr-3 h-7 w-7 text-blue-600" />
            Retroalimentación Detallada
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Reporte automático generado el {new Date(retro.generado_at).toLocaleString("es-PE")}.
          </p>
        </div>
        <button
          onClick={() => navigate(`/dashboard/simulacion/${id}/prediccion`)}
          className="px-3 py-2 text-sm text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 inline-flex items-center"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Volver a predicción
        </button>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h2 className="text-base font-semibold text-blue-900 mb-2">Resumen ejecutivo</h2>
        <p className="text-sm text-blue-800">{retro.resumen}</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
          <h2 className="text-lg font-semibold text-slate-900">Desempeño por criterio</h2>
        </div>
        <table className="w-full">
          <thead>
            <tr className="text-left text-xs uppercase tracking-wider text-slate-500 border-b border-slate-200">
              <th className="px-6 py-3">Criterio</th>
              <th className="px-6 py-3 text-center">Obtenido</th>
              <th className="px-6 py-3 text-center">Esperado</th>
              <th className="px-6 py-3 text-center">Gap</th>
              <th className="px-6 py-3">Acción recomendada</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {retro.criterios.map((c) => (
              <tr key={c.criterio_id} className="hover:bg-slate-50">
                <td className="px-6 py-4 font-medium text-slate-900">{c.criterio_nombre}</td>
                <td className="px-6 py-4 text-center text-slate-700">{c.puntaje_obtenido}</td>
                <td className="px-6 py-4 text-center text-slate-700">{c.puntaje_esperado}</td>
                <td className="px-6 py-4 text-center">
                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${colorGap(c.gap)}`}>
                    {c.gap === 0 ? "OK" : `-${c.gap}`}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-slate-600">{c.accion_recomendada}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
