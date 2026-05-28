import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { Sparkles, AlertCircle, Loader2, Users, FlaskConical } from "lucide-react";
import { getMyTournaments, type MyTournamentEntry } from "../../services/teamService";
import { EstadoInscripcion } from "../../types/team";

const TEAM_STATE_CONFIG: Record<string, { label: string; color: string }> = {
  APROBADO: { label: "Aprobado", color: "bg-green-100 text-green-800 border-green-200" },
  PENDIENTE: { label: "Pendiente", color: "bg-amber-100 text-amber-800 border-amber-200" },
  RECHAZADO: { label: "Rechazado", color: "bg-red-100 text-red-800 border-red-200" },
};

export function MySimulations() {
  const navigate = useNavigate();
  const [entries, setEntries] = useState<MyTournamentEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getMyTournaments();
      // Solo equipos aprobados pueden simular
      setEntries(data.filter((e) => e.team.estado_inscripcion === EstadoInscripcion.APROBADO));
    } catch {
      setError("No se pudieron cargar tus torneos. Intenta nuevamente.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="h-12 w-12 text-blue-500 animate-spin" />
        <p className="text-slate-500 font-medium">Cargando tus simulaciones...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
          <div className="p-2 bg-purple-50 rounded-xl text-purple-600">
            <Sparkles size={22} />
          </div>
          Mis Simulaciones
        </h1>
        <p className="text-sm text-slate-500 mt-1 ml-1">
          Practica tu desempeño antes de competir.
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center gap-3 shadow-sm">
          <AlertCircle size={20} className="shrink-0" />
          <span>{error}</span>
          <button
            onClick={loadData}
            className="ml-auto text-sm font-semibold underline hover:no-underline"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Empty state */}
      {!error && entries.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-16 text-center shadow-sm">
          <div className="bg-slate-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-5">
            <Sparkles size={36} className="text-slate-300" />
          </div>
          <p className="text-slate-700 font-semibold text-lg">Aún no tienes equipos aprobados</p>
          <p className="text-slate-400 text-sm mt-2">
            Tu equipo debe estar aprobado en un torneo para poder simular.
          </p>
          <Link
            to="/dashboard/torneos"
            className="mt-6 inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors shadow-sm"
          >
            Ver torneos disponibles
          </Link>
        </div>
      )}

      {/* Cards */}
      <div className="grid grid-cols-1 gap-5">
        {entries.map(({ tournament, team }) => {
          const teamConf =
            TEAM_STATE_CONFIG[team.estado_inscripcion] ?? {
              label: team.estado_inscripcion,
              color: "bg-slate-100 text-slate-700 border-slate-200",
            };

          return (
            <div
              key={tournament.id}
              className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:border-purple-300 transition-colors p-6 space-y-4"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <h2 className="text-lg font-bold text-slate-900">{tournament.name}</h2>
                  <p className="text-sm text-slate-500 flex items-center gap-1.5">
                    <Users size={14} className="text-slate-400" />
                    Equipo: <span className="font-medium text-slate-700">{team.name}</span> ·{" "}
                    {team.participants?.length ?? 0} part. ·{" "}
                    <span className="capitalize">
                      {(team.nivel_tecnico_declarado ?? "").toLowerCase()}
                    </span>
                  </p>
                </div>
                <span
                  className={`shrink-0 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${teamConf.color}`}
                >
                  {teamConf.label}
                </span>
              </div>

              <div className="flex flex-wrap gap-3 pt-2 border-t border-slate-100">
                <button
                  onClick={() =>
                    navigate(`/dashboard/simulaciones/torneo/${tournament.id}/retos`)
                  }
                  className="px-4 py-2 text-sm text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 inline-flex items-center"
                >
                  <FlaskConical className="h-4 w-4 mr-2" />
                  Analizar retos
                </button>
                <button
                  onClick={() => navigate(`/dashboard/simulaciones/torneo/${tournament.id}`)}
                  className="px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 inline-flex items-center"
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Simular entregable →
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
