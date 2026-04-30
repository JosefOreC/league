import { useState, useEffect } from "react";
import { Plus, Search, Trophy, Calendar, Users, Rocket, AlertCircle, Loader2 } from "lucide-react";
import { Link } from "react-router";
import { getTournaments, startTournament } from "../../services/tournamentService";
import { EstadoTorneo, Tournament } from "../../types/tournament";
import axios from "axios";

export function TournamentsList() {
  const [torneos, setTorneos] = useState<Tournament[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<{ id: string; msg: string } | null>(null);
  const [startingId, setStartingId] = useState<string | null>(null);

  useEffect(() => {
    fetchTorneos();
  }, []);

  const fetchTorneos = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getTournaments();
      setTorneos(data);
    } catch (err) {
      setError("Error al cargar la lista de torneos.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartTournament = async (id: string) => {
    setActionError(null);
    setStartingId(id);
    try {
      await startTournament(id);
      // Volvemos a solicitar la lista de torneos para actualizar la vista después de iniciar el torneo
      await fetchTorneos();
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const msg = err.response?.data?.error || "Error al iniciar el torneo.";
        setActionError({ id, msg });
      } else {
        setActionError({ id, msg: "Error de conexión." });
      }
    } finally {
      setStartingId(null);
    }
  };

  const getStatusColor = (estado: EstadoTorneo) => {
    switch (estado) {
      case EstadoTorneo.IN_PROGRESS:
        return "bg-green-50 text-green-700 border-green-200";
      case EstadoTorneo.REGISTRATION_OPEN:
        return "bg-blue-50 text-blue-700 border-blue-200";
      case EstadoTorneo.REGISTRATION_CLOSED:
        return "bg-purple-50 text-purple-700 border-purple-200";
      case EstadoTorneo.DRAFT:
        return "bg-slate-100 text-slate-700 border-slate-200";
      case EstadoTorneo.FINISHED:
        return "bg-gray-50 text-gray-700 border-gray-200";
      default:
        return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Torneos</h1>
          <p className="text-sm text-slate-500 mt-1">Gestiona todos los torneos de robótica.</p>
        </div>
        <Link
          to="/dashboard/torneos/nuevo"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm"
        >
          <Plus className="mr-2 h-4 w-4" />
          Crear torneo
        </Link>
      </div>

      {error && (
        <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      <div className="flex flex-col sm:flex-row items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative w-full sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar torneos..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <select className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option>Todos los estados</option>
          </select>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-8 text-center text-slate-500">Cargando torneos...</div>
          ) : torneos.length === 0 ? (
            <div className="p-8 text-center text-slate-500">No hay torneos creados aún.</div>
          ) : (
            <table className="w-full text-sm text-left text-slate-500">
              <thead className="text-xs text-slate-700 uppercase bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4 font-semibold">Torneo</th>
                  <th className="px-6 py-4 font-semibold">Estado</th>
                  <th className="px-6 py-4 font-semibold">Fechas</th>
                  <th className="px-6 py-4 font-semibold">Categorías</th>
                  <th className="px-6 py-4 font-semibold text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {torneos.map((torneo) => (
                  <tr key={torneo.id} className="bg-white border-b border-slate-100 hover:bg-slate-50 last:border-0">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                          <Trophy className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="font-semibold text-slate-900">{torneo.nombre}</div>
                          <div className="text-xs text-slate-500 mt-0.5">{torneo.tipo_torneo}</div>
                        </div>
                      </div>
                      {actionError?.id === torneo.id && (
                        <p className="mt-2 text-xs text-red-600">{actionError.msg}</p>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(torneo.estado)}`}>
                        {torneo.estado}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center text-slate-600">
                        <Calendar className="mr-2 h-4 w-4 text-slate-400" />
                        {torneo.fecha_inicio} al {torneo.fecha_fin}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center font-medium text-slate-900">
                        <Users className="mr-2 h-4 w-4 text-slate-400" />
                        {torneo.categorias_habilitadas?.join(", ")}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {torneo.estado === EstadoTorneo.REGISTRATION_CLOSED && (
                        <button
                          onClick={() => handleStartTournament(torneo.id)}
                          disabled={startingId === torneo.id}
                          className="inline-flex items-center justify-center rounded-md text-xs font-medium bg-green-100 text-green-700 hover:bg-green-200 px-3 py-1.5 transition-colors disabled:opacity-50"
                          title="Generar Fixtures e Iniciar Torneo"
                        >
                          {startingId === torneo.id ? (
                            <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                          ) : (
                            <Rocket className="h-4 w-4 mr-1" />
                          )}
                          Iniciar Torneo
                        </button>
                      )}
                      {torneo.estado === EstadoTorneo.DRAFT && (
                        <Link
                          to={`/dashboard/torneos/${torneo.id}/reglas`}
                          className="inline-flex items-center justify-center rounded-md text-xs font-medium bg-blue-50 text-blue-700 hover:bg-blue-100 px-3 py-1.5 transition-colors"
                        >
                          Configurar Reglas
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
