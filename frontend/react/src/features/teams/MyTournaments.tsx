import { useState, useEffect } from "react";
import { Link } from "react-router";
import {
  Trophy,
  Users,
  CalendarDays,
  ChevronRight,
  AlertCircle,
  Swords,
  ShieldCheck,
  Clock,
  Ban,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import { getMyTournaments, type MyTournamentEntry } from "../../services/teamService";

// ─── Estado del torneo → badge ────────────────────────────────────────────────
const STATE_CONFIG: Record<string, { label: string; color: string; Icon: React.ElementType }> = {
  draft:                { label: "Borrador",              color: "bg-slate-100 text-slate-600 border-slate-200",  Icon: Clock },
  in_review:            { label: "En revisión",           color: "bg-amber-50  text-amber-700  border-amber-200", Icon: Clock },
  registration_open:    { label: "Inscripciones abiertas",color: "bg-green-50  text-green-700  border-green-200", Icon: CheckCircle2 },
  registration_closed:  { label: "Inscripciones cerradas",color: "bg-orange-50 text-orange-700 border-orange-200",Icon: Ban },
  in_progress:          { label: "En progreso",           color: "bg-blue-50   text-blue-700   border-blue-200",  Icon: Swords },
  finalized:            { label: "Finalizado",            color: "bg-purple-50 text-purple-700 border-purple-200",Icon: ShieldCheck },
  cancelled:            { label: "Cancelado",             color: "bg-red-50    text-red-700    border-red-200",   Icon: Ban },
};

const TEAM_STATE_CONFIG: Record<string, { label: string; color: string }> = {
  APROBADO:  { label: "Aprobado",  color: "bg-green-100 text-green-800" },
  PENDIENTE: { label: "Pendiente", color: "bg-amber-100 text-amber-800" },
  RECHAZADO: { label: "Rechazado", color: "bg-red-100   text-red-800"   },
};

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("es-PE", {
    day: "2-digit", month: "short", year: "numeric",
  });
}

// ─── Component ────────────────────────────────────────────────────────────────
export function MyTournaments() {
  const [entries, setEntries]     = useState<MyTournamentEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError]         = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getMyTournaments();
      setEntries(data);
    } catch {
      setError("No se pudieron cargar tus torneos. Intenta nuevamente.");
    } finally {
      setIsLoading(false);
    }
  };

  // ── Loading ──────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <Loader2 className="h-12 w-12 text-blue-500 animate-spin" />
        <p className="text-slate-500 font-medium">Cargando tus torneos...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-3">
          <div className="p-2 bg-blue-50 rounded-xl text-blue-600">
            <Trophy size={22} />
          </div>
          Mis Torneos
        </h1>
        <p className="text-sm text-slate-500 mt-1 ml-1">
          Torneos en los que tu equipo está participando.
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
            <Trophy size={36} className="text-slate-300" />
          </div>
          <p className="text-slate-700 font-semibold text-lg">
            Aún no estás en ningún torneo
          </p>
          <p className="text-slate-400 text-sm mt-2">
            Busca un torneo disponible e inscribe a tu equipo para aparecer aquí.
          </p>
          <Link
            to="/dashboard/torneos"
            className="mt-6 inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors shadow-sm"
          >
            <Trophy size={16} /> Ver torneos disponibles
          </Link>
        </div>
      )}

      {/* Cards */}
      <div className="grid grid-cols-1 gap-5">
        {entries.map(({ tournament, team }) => {
          const stateConf = STATE_CONFIG[tournament.state] ?? {
            label: tournament.state,
            color: "bg-slate-100 text-slate-600 border-slate-200",
            Icon: Clock,
          };
          const teamConf = TEAM_STATE_CONFIG[team.estado_inscripcion] ?? {
            label: team.estado_inscripcion,
            color: "bg-slate-100 text-slate-700",
          };
          const StateIcon = stateConf.Icon;

          return (
            <div
              key={tournament.id}
              className="bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-blue-200 transition-all duration-200 overflow-hidden"
            >
              {/* Accent bar */}
              <div className={`h-1.5 w-full ${stateConf.color.split(" ")[0]}`} />

              <div className="p-6 flex flex-col lg:flex-row lg:items-center gap-6">
                {/* Tournament info */}
                <div className="flex-1 space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-lg font-bold text-slate-900">{tournament.name}</h2>
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${stateConf.color}`}>
                      <StateIcon size={11} />
                      {stateConf.label}
                    </span>
                  </div>

                  <p className="text-sm text-slate-500 line-clamp-2">{tournament.description}</p>

                  <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-500">
                    <span className="flex items-center gap-1.5">
                      <CalendarDays size={14} className="text-slate-400" />
                      <span className="font-medium text-slate-700">Inicio:</span>
                      {formatDate(tournament.date_start)}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <CalendarDays size={14} className="text-slate-400" />
                      <span className="font-medium text-slate-700">Fin:</span>
                      {formatDate(tournament.date_end)}
                    </span>
                    <span className="flex items-center gap-1.5 capitalize">
                      <Trophy size={14} className="text-slate-400" />
                      <span className="font-medium text-slate-700">Categoría:</span>
                      {tournament.category}
                    </span>
                  </div>
                </div>

                {/* Team info */}
                <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 min-w-[220px] space-y-3 shrink-0">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-blue-100 text-blue-600 rounded-lg">
                      <Users size={14} />
                    </div>
                    <span className="font-bold text-slate-900 text-sm truncate">{team.name}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500">Inscripción</span>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${teamConf.color}`}>
                      {teamConf.label}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500">Participantes</span>
                    <span className="text-xs font-semibold text-slate-700">
                      {team.participants?.length ?? 0}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-500">Nivel técnico</span>
                    <span className="text-xs font-semibold text-slate-700 capitalize">
                      {(team.nivel_tecnico_declarado ?? "").toLowerCase()}
                    </span>
                  </div>
                </div>

                {/* Ver torneo */}
                <Link
                  to={`/t/${tournament.id}`}
                  className="flex items-center gap-1 text-blue-600 hover:text-blue-700 font-semibold text-sm shrink-0 hover:underline transition-colors"
                >
                  Ver torneo <ChevronRight size={16} />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
