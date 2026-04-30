import { useState, useEffect } from "react";
import { Plus, Trophy, Rocket, AlertCircle, Loader2 } from "lucide-react";
import { Link } from "react-router";
import { 
  getTournaments, 
  startTournament, 
  openRegistrations, 
  closeRegistrations, 
  reviewTournament,
  backToDraft
} from "../../services/tournamentService";
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
      await fetchTorneos();
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setActionError({ id, msg: err.response?.data?.error || "Error al iniciar el torneo." });
      } else {
        setActionError({ id, msg: "Error de conexión." });
      }
    } finally {
      setStartingId(null);
    }
  };

  const handleAction = async (id: string, action: "open" | "close" | "review" | "draft") => {
    setActionError(null);
    try {
      if (action === "open") await openRegistrations(id);
      else if (action === "close") await closeRegistrations(id);
      else if (action === "review") await reviewTournament(id);
      else if (action === "draft") await backToDraft(id);
      await fetchTorneos();
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setActionError({ id, msg: err.response?.data?.error || "Error al realizar acción." });
      }
    }
  };

  const getStatusColor = (estado: EstadoTorneo) => {
    switch (estado) {
      case EstadoTorneo.IN_PROGRESS: return "bg-green-50 text-green-700 border-green-200";
      case EstadoTorneo.REGISTRATION_OPEN: return "bg-blue-50 text-blue-700 border-blue-200";
      case EstadoTorneo.REGISTRATION_CLOSED: return "bg-purple-50 text-purple-700 border-purple-200";
      case EstadoTorneo.DRAFT: return "bg-slate-100 text-slate-700 border-slate-200";
      case EstadoTorneo.IN_REVIEW: return "bg-amber-50 text-amber-700 border-amber-200";
      case EstadoTorneo.FINISHED: return "bg-gray-50 text-gray-700 border-gray-200";
      default: return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Torneos</h1>
          <p className="text-sm text-slate-500 mt-1">Gestiona todos los torneos de robótica.</p>
        </div>
        <Link to="/dashboard/torneos/nuevo" className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm">
          <Plus className="mr-2 h-4 w-4" /> Crear torneo
        </Link>
      </div>

      {(error) && (
        <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
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
            {isLoading ? (
              <tr><td colSpan={5} className="p-8 text-center">Cargando...</td></tr>
            ) : torneos.length === 0 ? (
              <tr><td colSpan={5} className="p-8 text-center">No hay torneos.</td></tr>
            ) : (
              torneos.map((torneo) => (
                <tr key={torneo.id} className="bg-white border-b border-slate-100 hover:bg-slate-50 last:border-0">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                        <Trophy className="h-5 w-5" />
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900">{torneo.name}</div>
                        <div className="text-xs text-slate-500 mt-0.5">{torneo.config_tournament?.type || "Standard"}</div>
                      </div>
                    </div>
                    {actionError?.id === torneo.id && (
                      <p className="mt-2 text-xs text-red-600 font-medium">{actionError.msg}</p>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(torneo.state)}`}>
                      {torneo.state}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-slate-600">
                    {new Date(torneo.date_start).toLocaleDateString()} al {new Date(torneo.date_end).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-slate-900 font-medium capitalize">
                    {torneo.category}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex flex-wrap justify-end gap-2">
                      {torneo.state === EstadoTorneo.DRAFT && (
                        <>
                          <Link to={`/dashboard/torneos/${torneo.id}/reglas`} className="px-3 py-1.5 rounded-md text-xs font-medium bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors">Configurar</Link>
                          <button onClick={() => handleAction(torneo.id, "review")} className="px-3 py-1.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors">Revisión</button>
                        </>
                      )}
                      {torneo.state === EstadoTorneo.IN_REVIEW && (
                        <>
                          <button onClick={() => handleAction(torneo.id, "open")} className="px-3 py-1.5 rounded-md text-xs font-medium bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition-colors">Abrir Inscripciones</button>
                          <button onClick={() => handleAction(torneo.id, "draft")} className="px-3 py-1.5 rounded-md text-xs font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors">Volver a Borrador</button>
                        </>
                      )}
                      {torneo.state === EstadoTorneo.REGISTRATION_OPEN && (
                        <button onClick={() => handleAction(torneo.id, "close")} className="px-3 py-1.5 rounded-md text-xs font-medium bg-amber-50 text-amber-700 hover:bg-amber-100 transition-colors">Cerrar Inscripciones</button>
                      )}
                      {torneo.state === EstadoTorneo.REGISTRATION_CLOSED && (
                        <button onClick={() => handleStartTournament(torneo.id)} disabled={startingId === torneo.id} className="px-3 py-1.5 rounded-md text-xs font-medium bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-50 transition-colors flex items-center gap-1.5">
                          {startingId === torneo.id ? <Loader2 size={12} className="animate-spin" /> : <Rocket size={12} />} Iniciar
                        </button>
                      )}
                      {(torneo.state === EstadoTorneo.REGISTRATION_OPEN || torneo.state === EstadoTorneo.IN_PROGRESS) && (
                        <Link to={`/dashboard/torneos/${torneo.id}/posiciones`} className="px-3 py-1.5 rounded-md text-xs font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors">Ver Tabla</Link>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
