import { useEffect, useState } from "react";
import { LineChart as LineChartIcon, Loader2, Inbox, Users } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { PanelDocenteResponse } from "../../types/simulation";
import { obtenerPanelDocente } from "../../services/simulationService";

const EQUIPOS_DEL_DOCENTE = [
  { id: "equipo-propio", nombre: "Robotix Junior" },
  { id: "equipo-002", nombre: "Steam Pioneers" },
  { id: "equipo-003", nombre: "Mecanix Lab" },
];

function colorConfianza(c: number) {
  if (c >= 0.8) return "text-green-700";
  if (c >= 0.6) return "text-yellow-700";
  return "text-red-700";
}

export function CoachPanel() {
  const [equipoId, setEquipoId] = useState(EQUIPOS_DEL_DOCENTE[0].id);
  const [panel, setPanel] = useState<PanelDocenteResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    obtenerPanelDocente(equipoId)
      .then(setPanel)
      .finally(() => setIsLoading(false));
  }, [equipoId]);

  const dataChart =
    panel?.evolucion.map((p) => ({
      fecha: new Date(p.fecha).toLocaleDateString("es-PE", { day: "2-digit", month: "short" }),
      puntaje: p.puntaje,
    })) ?? [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
            <LineChartIcon className="mr-3 h-7 w-7 text-blue-600" />
            Panel de Simulaciones del Equipo
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Historial completo y evolución de desempeño de tus equipos.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Users className="h-5 w-5 text-slate-500" />
          <select
            value={equipoId}
            onChange={(e) => setEquipoId(e.target.value)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {EQUIPOS_DEL_DOCENTE.map((eq) => (
              <option key={eq.id} value={eq.id}>
                {eq.nombre}
              </option>
            ))}
          </select>
        </div>
      </div>

      {isLoading && (
        <div className="flex justify-center py-24">
          <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
        </div>
      )}

      {!isLoading && panel && panel.simulaciones.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-12 text-center">
          <Inbox className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">
            {panel.mensaje ?? "Este equipo aún no ha realizado simulaciones."}
          </p>
        </div>
      )}

      {!isLoading && panel && panel.simulaciones.length > 0 && (
        <>
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">
              Evolución de puntaje — {panel.equipo_nombre}
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dataChart} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="fecha" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "white",
                      border: "1px solid #e2e8f0",
                      borderRadius: "8px",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="puntaje"
                    stroke="#2563eb"
                    strokeWidth={2.5}
                    dot={{ fill: "#2563eb", r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
              <h2 className="text-lg font-semibold text-slate-900">Historial de simulaciones</h2>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wider text-slate-500 border-b border-slate-200">
                  <th className="px-6 py-3">Fecha</th>
                  <th className="px-6 py-3 text-center">Posición estimada</th>
                  <th className="px-6 py-3 text-center">Puntaje</th>
                  <th className="px-6 py-3 text-center">Confianza</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {panel.simulaciones.map((s) => (
                  <tr key={s.simulacion_id} className="hover:bg-slate-50">
                    <td className="px-6 py-3 text-slate-700">
                      {new Date(s.fecha).toLocaleString("es-PE")}
                    </td>
                    <td className="px-6 py-3 text-center font-semibold text-slate-900">
                      #{s.posicion_estimada}
                    </td>
                    <td className="px-6 py-3 text-center text-slate-700">{s.puntaje_total}</td>
                    <td className={`px-6 py-3 text-center font-semibold ${colorConfianza(s.nivel_confianza)}`}>
                      {Math.round(s.nivel_confianza * 100)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
