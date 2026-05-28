import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { Play, Loader2, AlertCircle, Plus } from "lucide-react";
import { toast } from "sonner";
import { ejecutarSimulacion } from "../../services/simulationService";

export function RunSimulation() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [yaEjecutada, setYaEjecutada] = useState(false);

  const ejecutar = async () => {
    if (!id) return;
    setIsRunning(true);
    setError(null);
    const inicio = Date.now();

    try {
      await ejecutarSimulacion(id);
      const duracion = Date.now() - inicio;
      toast.success(`Simulación completada en ${(duracion / 1000).toFixed(1)}s`);
      navigate(`/dashboard/simulacion/${id}/prediccion`);
    } catch (err: any) {
      if (err?.response?.status === 409) {
        setYaEjecutada(true);
        setError(err.response.data?.error ?? "Esta simulación ya fue ejecutada.");
      } else {
        setError("Ocurrió un error al ejecutar la simulación.");
      }
    } finally {
      setIsRunning(false);
    }
  };

  // Ejecución automática al cargar
  useEffect(() => {
    ejecutar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Ejecutando simulación
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          El sistema está generando los enfrentamientos simulados con el modelo de machine learning.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-12 text-center">
        {isRunning && (
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
            <p className="text-lg font-medium text-slate-900">Procesando enfrentamientos…</p>
            <p className="text-sm text-slate-500">
              Esto debería tomar menos de 5 segundos.
            </p>
          </div>
        )}

        {!isRunning && error && (
          <div className="space-y-4">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto" />
            <p className="text-base text-red-700">{error}</p>
            <div className="flex justify-center gap-3 pt-2">
              {yaEjecutada ? (
                <>
                  <button
                    onClick={() => navigate(`/dashboard/simulacion/${id}/prediccion`)}
                    className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                  >
                    Ver predicción anterior
                  </button>
                  <button
                    onClick={() => navigate("/dashboard/simulacion")}
                    className="px-4 py-2 text-sm text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 inline-flex items-center"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Configurar nueva
                  </button>
                </>
              ) : (
                <button
                  onClick={ejecutar}
                  className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 inline-flex items-center"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Reintentar
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
