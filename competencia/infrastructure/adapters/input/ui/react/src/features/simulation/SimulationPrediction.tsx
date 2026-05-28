import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  Trophy,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Loader2,
  FileText,
  ArrowLeft,
} from "lucide-react";
// @ts-expect-error — canvas-confetti no incluye tipos
import confetti from "canvas-confetti";
import { PrediccionSimulacion } from "../../types/simulation";
import { obtenerPrediccion } from "../../services/simulationService";

function badgeConfianza(c: number) {
  if (c >= 0.8) return { bg: "bg-green-100", text: "text-green-700", label: "Alta" };
  if (c >= 0.6) return { bg: "bg-yellow-100", text: "text-yellow-700", label: "Media" };
  return { bg: "bg-red-100", text: "text-red-700", label: "Baja" };
}

export function SimulationPrediction() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [prediccion, setPrediccion] = useState<PrediccionSimulacion | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    obtenerPrediccion(id)
      .then((data) => {
        setPrediccion(data);
        if (data.posicion_estimada <= 3 && data.nivel_confianza >= 0.7) {
          confetti({
            particleCount: 120,
            spread: 70,
            origin: { y: 0.6 },
          });
        }
      })
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex justify-center py-24">
        <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!prediccion) {
    return <p className="text-center text-slate-500 py-12">No se pudo cargar la predicción.</p>;
  }

  const conf = badgeConfianza(prediccion.nivel_confianza);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Predicción de Desempeño
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Resultados generados por el modelo de machine learning.
          </p>
        </div>
        <button
          onClick={() => navigate("/dashboard/simulacion")}
          className="px-3 py-2 text-sm text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 inline-flex items-center"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Nueva simulación
        </button>
      </div>

      {prediccion.advertencia && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 shrink-0" />
          <p className="text-sm text-yellow-800">{prediccion.advertencia}</p>
        </div>
      )}

      {/* Resumen principal */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <div className="flex items-center space-x-3 mb-2">
            <Trophy className="h-5 w-5 text-blue-600" />
            <p className="text-sm font-medium text-slate-500">Posición estimada</p>
          </div>
          <p className="text-4xl font-bold text-slate-900">
            #{prediccion.posicion_estimada}
            <span className="text-base text-slate-500 font-normal ml-2">
              ± {prediccion.margen_error}
            </span>
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <p className="text-sm font-medium text-slate-500 mb-2">Puntaje total estimado</p>
          <p className="text-4xl font-bold text-slate-900">
            {prediccion.puntaje_total_estimado}
            <span className="text-base text-slate-500 font-normal ml-2">pts</span>
          </p>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <p className="text-sm font-medium text-slate-500 mb-2">Nivel de confianza</p>
          <div className="flex items-baseline gap-3">
            <p className="text-4xl font-bold text-slate-900">
              {Math.round(prediccion.nivel_confianza * 100)}%
            </p>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${conf.bg} ${conf.text}`}>
              {conf.label}
            </span>
          </div>
        </div>
      </div>

      {/* Fortalezas y debilidades */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
            <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
            Fortalezas
          </h2>
          {prediccion.fortalezas.length === 0 ? (
            <p className="text-sm text-slate-500">
              Aún no se detectan fortalezas claras (criterios con puntaje ≥ 75%).
            </p>
          ) : (
            <ul className="space-y-4">
              {prediccion.fortalezas.map((f) => (
                <li key={f.criterio_id} className="border-l-4 border-green-500 pl-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-slate-900">{f.criterio_nombre}</span>
                    <span className="text-sm font-bold text-green-700">
                      {f.puntaje_porcentaje}%
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">{f.recomendacion_mejora}</p>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
            <TrendingDown className="h-5 w-5 mr-2 text-red-600" />
            Áreas de mejora
          </h2>
          {prediccion.debilidades.length === 0 ? (
            <p className="text-sm text-slate-500">
              ¡Excelente! No se detectan debilidades (criterios con puntaje &lt; 50%).
            </p>
          ) : (
            <ul className="space-y-4">
              {prediccion.debilidades.map((d) => (
                <li key={d.criterio_id} className="border-l-4 border-red-500 pl-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-slate-900">{d.criterio_nombre}</span>
                    <span className="text-sm font-bold text-red-700">{d.puntaje_porcentaje}%</span>
                  </div>
                  <p className="text-sm text-slate-600">{d.recomendacion_mejora}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => navigate(`/dashboard/simulacion/${id}/retroalimentacion`)}
          className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 inline-flex items-center"
        >
          <FileText className="h-4 w-4 mr-2" />
          Ver retroalimentación detallada
        </button>
      </div>
    </div>
  );
}
