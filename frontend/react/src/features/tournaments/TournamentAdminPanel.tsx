import { useState, useEffect } from "react";
import { useParams, Link, Navigate } from "react-router";
import {
  ArrowLeft, Settings, Users, Trophy, BarChart3,
  CheckCircle, XCircle, Clock, Rocket, AlertCircle,
  Loader2, ChevronRight, Lock, Eye
} from "lucide-react";
import { useRoleGuard } from "../../hooks/useRoleGuard";
import { getTournamentById, startTournament, openRegistrations, closeRegistrations } from "../../services/tournamentService";
import { getTeamsByTournament, approveTeam, rejectTeam } from "../../services/teamService";
import { Tournament, EstadoTorneo } from "../../types/tournament";
import { Equipo, EstadoInscripcion } from "../../types/team";
import axios from "axios";

// ─── Types ─────────────────────────────────────────────────────────────────────
type TabId = "overview" | "teams" | "fixtures" | "standings";

const TABS: { id: TabId; label: string; icon: React.FC<any> }[] = [
  { id: "overview",  label: "Visión General", icon: BarChart3 },
  { id: "teams",     label: "Inscripciones",  icon: Users },
  { id: "fixtures",  label: "Fixtures",       icon: Trophy },
  { id: "standings", label: "Posiciones",     icon: BarChart3 },
];

const STATUS_CONFIG: Record<EstadoTorneo, { label: string; dot: string; bar: string }> = {
  [EstadoTorneo.DRAFT]:               { label: "Borrador",             dot: "bg-slate-400", bar: "bg-slate-300" },
  [EstadoTorneo.IN_REVIEW]:           { label: "En Revisión",          dot: "bg-amber-500", bar: "bg-amber-400" },
  [EstadoTorneo.REGISTRATION_OPEN]:   { label: "Inscripciones Abiertas", dot: "bg-emerald-500", bar: "bg-emerald-400" },
  [EstadoTorneo.REGISTRATION_CLOSED]: { label: "Inscripciones Cerradas", dot: "bg-purple-500", bar: "bg-purple-400" },
  [EstadoTorneo.IN_PROGRESS]:         { label: "En Progreso",          dot: "bg-blue-500", bar: "bg-blue-400" },
  [EstadoTorneo.FINISHED]:            { label: "Finalizado",           dot: "bg-gray-400", bar: "bg-gray-300" },
  [EstadoTorneo.CANCELLED]:           { label: "Cancelado",            dot: "bg-red-500", bar: "bg-red-400" },
};

// ─── Sub-components ────────────────────────────────────────────────────────────

function OverviewTab({ tournament, onAction, processing }: {
  tournament: Tournament;
  onAction: (action: "open" | "close" | "start") => void;
  processing: boolean;
}) {
  const cfg = STATUS_CONFIG[tournament.state] ?? STATUS_CONFIG[EstadoTorneo.DRAFT];

  return (
    <div className="space-y-6">
      {/* State card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">Estado del Torneo</h2>
        <div className="flex items-center gap-3 mb-6">
          <span className={`inline-block w-3 h-3 rounded-full ${cfg.dot} animate-pulse`} />
          <span className="text-xl font-bold text-slate-900">{cfg.label}</span>
        </div>

        {/* Workflow steps */}
        <div className="flex items-center gap-1 text-xs text-slate-400 flex-wrap">
          {[
            { s: EstadoTorneo.DRAFT, label: "Borrador" },
            { s: EstadoTorneo.IN_REVIEW, label: "Revisión" },
            { s: EstadoTorneo.REGISTRATION_OPEN, label: "Inscripciones" },
            { s: EstadoTorneo.REGISTRATION_CLOSED, label: "Cerrado" },
            { s: EstadoTorneo.IN_PROGRESS, label: "En Curso" },
            { s: EstadoTorneo.FINISHED, label: "Finalizado" },
          ].map((step, idx, arr) => {
            const states = Object.values(EstadoTorneo);
            const currentIdx = states.indexOf(tournament.state);
            const stepIdx = states.indexOf(step.s);
            const done = stepIdx <= currentIdx;
            return (
              <div key={step.s} className="flex items-center gap-1">
                <span className={`px-2 py-1 rounded font-semibold ${done ? "bg-blue-100 text-blue-700" : "bg-slate-100 text-slate-400"}`}>
                  {step.label}
                </span>
                {idx < arr.length - 1 && <ChevronRight size={12} className="text-slate-300" />}
              </div>
            );
          })}
        </div>
      </div>

      {/* Metadata grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <InfoCard label="Inicio Torneo" value={new Date(tournament.date_start).toLocaleDateString("es-PE", { dateStyle: "long" })} />
        <InfoCard label="Fin Torneo" value={new Date(tournament.date_end).toLocaleDateString("es-PE", { dateStyle: "long" })} />
        <InfoCard 
          label="Inicio Inscripciones" 
          value={tournament.tournament_rule?.date_start_inscription 
            ? new Date(tournament.tournament_rule.date_start_inscription).toLocaleDateString("es-PE", { dateStyle: "medium" }) 
            : "Indefinido"} 
          className={!tournament.tournament_rule?.date_start_inscription ? "text-slate-400 font-normal italic" : ""}
        />
        <InfoCard 
          label="Cierre Inscripciones" 
          value={tournament.tournament_rule?.date_end_inscription 
            ? new Date(tournament.tournament_rule.date_end_inscription).toLocaleDateString("es-PE", { dateStyle: "medium" }) 
            : "Indefinido"} 
          className={!tournament.tournament_rule?.date_end_inscription ? "text-slate-400 font-normal italic" : ""}
        />
        <InfoCard label="Categoría" value={tournament.category} className="capitalize" />
        <InfoCard label="Formato" value={tournament.config_tournament?.type ?? "No configurado"} />
        <InfoCard label="Mín/Máx Equipos" value={`${tournament.tournament_rule?.min_teams ?? 0} / ${tournament.tournament_rule?.max_teams ?? 0}`} />
        <InfoCard label="Mín/Máx Miembros" value={`${tournament.tournament_rule?.min_members ?? 0} / ${tournament.tournament_rule?.max_members ?? 0}`} />
        <InfoCard label="Descripción" value={tournament.description || "Sin descripción"} colSpan />
      </div>

      {/* Quick actions */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">Acciones Rápidas</h2>
        <div className="flex flex-wrap gap-3">
          <Link
            to={`/dashboard/torneos/${tournament.id}/reglas`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-50 text-blue-700 text-sm font-semibold hover:bg-blue-100 transition-colors"
          >
            <Settings size={16} /> Configurar Reglas
          </Link>
          {tournament.state === EstadoTorneo.REGISTRATION_OPEN && (
            <button
              onClick={() => onAction("close")}
              disabled={processing}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-50 text-amber-700 text-sm font-semibold hover:bg-amber-100 transition-colors disabled:opacity-50"
            >
              <Lock size={16} /> Cerrar Inscripciones
            </button>
          )}
          {tournament.state === EstadoTorneo.REGISTRATION_CLOSED && (
            <button
              onClick={() => onAction("start")}
              disabled={processing}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 transition-colors disabled:opacity-50"
            >
              {processing ? <Loader2 size={16} className="animate-spin" /> : <Rocket size={16} />}
              Iniciar Torneo
            </button>
          )}
          <Link
            to={`/t/${tournament.id}`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-100 text-slate-600 text-sm font-semibold hover:bg-slate-200 transition-colors"
          >
            <Eye size={16} /> Vista Pública
          </Link>
        </div>
      </div>
    </div>
  );
}

function InfoCard({ label, value, className = "", colSpan = false }: {
  label: string; value: string; className?: string; colSpan?: boolean;
}) {
  return (
    <div className={`bg-white rounded-xl border border-slate-200 p-5 shadow-sm ${colSpan ? "md:col-span-2 lg:col-span-4" : ""}`}>
      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">{label}</p>
      <p className={`text-sm font-semibold text-slate-800 ${className}`}>{value}</p>
    </div>
  );
}

// ─── Teams Tab ─────────────────────────────────────────────────────────────────
function TeamsTab({ tournamentId }: { tournamentId: string }) {
  const [teams, setTeams] = useState<Equipo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [filter, setFilter] = useState<EstadoInscripcion | "ALL">("ALL");

  useEffect(() => { loadTeams(); }, []);

  const loadTeams = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTeamsByTournament(tournamentId);
      setTeams(data);
    } catch {
      setError("No se pudo cargar los equipos.");
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (teamId: string) => {
    setProcessingId(teamId);
    try {
      await approveTeam(teamId);
      setTeams(prev => prev.map(t => t.id === teamId ? { ...t, estado_inscripcion: EstadoInscripcion.APROBADO } : t));
    } catch { 
      // Handled by global interceptor
    }
    finally { setProcessingId(null); }
  };

  const handleReject = async (teamId: string) => {
    if (!confirm("¿Rechazar esta inscripción?")) return;
    setProcessingId(teamId);
    try {
      await rejectTeam(teamId);
      setTeams(prev => prev.map(t => t.id === teamId ? { ...t, estado_inscripcion: EstadoInscripcion.RECHAZADO } : t));
    } catch { 
      // Handled by global interceptor
    }
    finally { setProcessingId(null); }
  };

  const filtered = filter === "ALL" ? teams : teams.filter(t => t.estado_inscripcion === filter);
  const approved = teams.filter(t => t.estado_inscripcion === EstadoInscripcion.APROBADO).length;
  const pending  = teams.filter(t => t.estado_inscripcion === EstadoInscripcion.PENDIENTE).length;
  const rejected = teams.filter(t => t.estado_inscripcion === EstadoInscripcion.RECHAZADO).length;

  const ESTADO_CONFIG = {
    [EstadoInscripcion.PENDIENTE]: { label: "Pendiente", classes: "bg-amber-50 text-amber-700 border-amber-200" },
    [EstadoInscripcion.APROBADO]:  { label: "Aprobado",  classes: "bg-emerald-50 text-emerald-700 border-emerald-200" },
    [EstadoInscripcion.RECHAZADO]: { label: "Rechazado", classes: "bg-red-50 text-red-700 border-red-200" },
  };

  return (
    <div className="space-y-5">
      {/* Summary counters */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-emerald-700">{approved}</p>
          <p className="text-xs font-semibold text-emerald-600 uppercase tracking-wider mt-1">Aprobados</p>
        </div>
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-amber-700">{pending}</p>
          <p className="text-xs font-semibold text-amber-600 uppercase tracking-wider mt-1">Pendientes</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-bold text-red-700">{rejected}</p>
          <p className="text-xs font-semibold text-red-600 uppercase tracking-wider mt-1">Rechazados</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 flex-wrap">
        {(["ALL", EstadoInscripcion.PENDIENTE, EstadoInscripcion.APROBADO, EstadoInscripcion.RECHAZADO] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-colors ${
              filter === f ? "bg-slate-900 text-white border-slate-900" : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
            }`}
          >
            {f === "ALL" ? "Todos" : f}
          </button>
        ))}
      </div>

      {/* Error / Loading */}
      {error && <div className="bg-red-50 text-red-700 border border-red-200 rounded-lg p-4 text-sm">{error}</div>}
      {loading && <div className="flex items-center justify-center py-16 gap-3 text-slate-400"><Loader2 className="animate-spin" /> Cargando…</div>}

      {/* Teams list */}
      {!loading && filtered.length === 0 && (
        <div className="text-center py-16 text-slate-400 font-medium">No hay equipos en este filtro.</div>
      )}
      <div className="space-y-3">
        {filtered.map(team => {
          const cfg = ESTADO_CONFIG[team.estado_inscripcion];
          const isProc = processingId === team.id;
          return (
            <div key={team.id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-5">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-base font-bold text-slate-900">{team.name}</h3>
                      <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${cfg.classes}`}>
                        {cfg.label}
                      </span>
                      <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded font-medium capitalize">
                        {team.category}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">
                      Inscrito el: {new Date(team.fecha_inscripcion).toLocaleDateString("es-PE")} ·{" "}
                      {team.participants?.length ?? 0} participante(s)
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {team.estado_inscripcion === EstadoInscripcion.PENDIENTE && (
                      <>
                        <button
                          disabled={isProc}
                          onClick={() => handleApprove(team.id)}
                          className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-emerald-600 text-white text-sm font-bold hover:bg-emerald-700 transition-colors disabled:opacity-50"
                        >
                          <CheckCircle size={15} /> Aprobar
                        </button>
                        <button
                          disabled={isProc}
                          onClick={() => handleReject(team.id)}
                          className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-red-200 text-red-600 bg-white text-sm font-bold hover:bg-red-50 transition-colors disabled:opacity-50"
                        >
                          <XCircle size={15} /> Rechazar
                        </button>
                      </>
                    )}
                    {team.estado_inscripcion === EstadoInscripcion.APROBADO && (
                      <button
                        disabled={isProc}
                        onClick={() => handleReject(team.id)}
                        className="text-xs text-slate-400 hover:text-red-500 font-semibold uppercase tracking-tight transition-colors"
                      >
                        Revocar
                      </button>
                    )}
                    {team.estado_inscripcion === EstadoInscripcion.RECHAZADO && (
                      <button
                        disabled={isProc}
                        onClick={() => handleApprove(team.id)}
                        className="text-xs text-slate-400 hover:text-emerald-600 font-semibold uppercase tracking-tight transition-colors"
                      >
                        Re-aprobar
                      </button>
                    )}
                  </div>
                </div>

                {/* Participants */}
                {team.participants && team.participants.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-2 md:grid-cols-4 gap-3">
                    {team.participants.map((p, i) => (
                      <div key={i} className="bg-slate-50 rounded-lg p-3 text-xs">
                        <p className="font-semibold text-slate-800">{p.nombres} {p.apellidos}</p>
                        <p className="text-slate-400 mt-0.5">{p.rol_en_equipo || "Participante"} · {p.edad} años</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Fixtures Tab (placeholder) ────────────────────────────────────────────────
function FixturesTab({ tournamentId, state }: { tournamentId: string; state: EstadoTorneo }) {
  if (state === EstadoTorneo.DRAFT || state === EstadoTorneo.IN_REVIEW || state === EstadoTorneo.REGISTRATION_OPEN || state === EstadoTorneo.REGISTRATION_CLOSED) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-16 text-center shadow-sm">
        <Clock className="mx-auto h-12 w-12 text-slate-300 mb-4" />
        <p className="text-slate-500 font-semibold text-lg">Los fixtures se generan al iniciar el torneo.</p>
        <p className="text-slate-400 text-sm mt-2">Cierra las inscripciones e inicia el torneo para ver los partidos.</p>
      </div>
    );
  }
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm">
      <p className="text-slate-500 text-sm">Gestión de fixtures — <Link to={`/dashboard/torneos/${tournamentId}/competencias`} className="text-blue-600 font-semibold hover:underline">Ver vista completa →</Link></p>
    </div>
  );
}

// ─── Standings Tab (placeholder) ───────────────────────────────────────────────
function StandingsTab({ tournamentId }: { tournamentId: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm">
      <p className="text-slate-500 text-sm">
        Tabla de posiciones — <Link to={`/dashboard/torneos/${tournamentId}/posiciones`} className="text-blue-600 font-semibold hover:underline">Ver tabla completa →</Link>
      </p>
    </div>
  );
}

// ─── Main Panel ────────────────────────────────────────────────────────────────
export function TournamentAdminPanel() {
  const { id: tournamentId } = useParams<{ id: string }>();
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [processing, setProcessing] = useState(false);

  const { isManagerOrAdmin, userId, user } = useRoleGuard(tournament ?? undefined);

  // Determine if this user is the owner (can edit)
  const isOwner = !!tournament && !!userId && tournament.creator_user_id === userId;
  const canEdit = isManagerOrAdmin && isOwner;

  useEffect(() => {
    if (tournamentId) loadTournament();
  }, [tournamentId]);

  const loadTournament = async () => {
    try {
      setLoading(true);
      const data = await getTournamentById(tournamentId!);
      setTournament(data);
    } catch {
      setError("No se pudo cargar el torneo.");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: "open" | "close" | "start") => {
    setProcessing(true);
    try {
      if (action === "open")  await openRegistrations(tournamentId!);
      if (action === "close") await closeRegistrations(tournamentId!);
      if (action === "start") await (await import("../../services/tournamentService")).startTournament(tournamentId!);
      await loadTournament();
    } catch (err) {
      // Handled by global interceptor
    } finally {
      setProcessing(false);
    }
  };

  // ── Guard ────────────────────────────────────────────────────────────────────
  if (!loading && !isManagerOrAdmin) return <Navigate to="/dashboard" replace />;
  if (!loading && tournament && !canEdit) {
    // Admin without ownership → read-only notice
    // (Still render but with read-only banner)
  }

  // ── Render ───────────────────────────────────────────────────────────────────
  if (loading) return (
    <div className="flex items-center justify-center min-h-[400px]">
      <Loader2 className="animate-spin h-10 w-10 text-blue-600" />
    </div>
  );

  if (error || !tournament) return (
    <div className="max-w-2xl mx-auto mt-20 text-center">
      <AlertCircle className="mx-auto h-12 w-12 text-red-400 mb-4" />
      <p className="text-slate-600 font-medium">{error || "Torneo no encontrado."}</p>
      <Link to="/dashboard/torneos" className="mt-4 inline-block text-blue-600 font-semibold hover:underline">← Volver a torneos</Link>
    </div>
  );

  const stateCfg = STATUS_CONFIG[tournament.state] ?? STATUS_CONFIG[EstadoTorneo.DRAFT];

  return (
    <div className="max-w-7xl mx-auto pb-12 space-y-6">
      {/* ── Breadcrumb + Header ── */}
      <div className="flex items-start gap-4">
        <Link to="/dashboard/torneos" className="mt-1 p-2 rounded-lg hover:bg-slate-100 transition-colors shrink-0">
          <ArrowLeft size={20} className="text-slate-500" />
        </Link>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-2xl font-bold text-slate-900 truncate">{tournament.name}</h1>
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
              tournament.state === EstadoTorneo.IN_PROGRESS  ? "bg-blue-50 text-blue-700 border-blue-200" :
              tournament.state === EstadoTorneo.REGISTRATION_OPEN ? "bg-emerald-50 text-emerald-700 border-emerald-200" :
              tournament.state === EstadoTorneo.DRAFT ? "bg-slate-100 text-slate-600 border-slate-200" :
              "bg-amber-50 text-amber-700 border-amber-200"
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${stateCfg.dot}`} />
              {stateCfg.label}
            </span>
            {!canEdit && (
              <span className="inline-flex items-center gap-1 text-xs bg-amber-50 text-amber-700 border border-amber-200 px-2 py-1 rounded-full font-semibold">
                <Eye size={12} /> Solo lectura
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Panel de administración · {tournament.category}
          </p>
        </div>
      </div>

      {/* ── Read-only warning for ADMIN without ownership ── */}
      {!canEdit && isManagerOrAdmin && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle size={18} className="text-amber-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-800">Modo solo lectura</p>
            <p className="text-xs text-amber-700 mt-0.5">
              No eres el manager de este torneo, por lo que no puedes editar ni realizar acciones. Solo puedes ver la información.
            </p>
          </div>
        </div>
      )}

      {/* ── Tabs ── */}
      <div className="border-b border-slate-200">
        <nav className="flex gap-1 -mb-px">
          {TABS.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-semibold border-b-2 transition-colors ${
                  isActive
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300"
                }`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* ── Tab content ── */}
      <div className="min-h-[400px]">
        {activeTab === "overview" && (
          <OverviewTab
            tournament={tournament}
            onAction={canEdit ? handleAction : () => {}}
            processing={processing}
          />
        )}
        {activeTab === "teams" && (
          canEdit
            ? <TeamsTab tournamentId={tournamentId!} />
            : <div className="bg-slate-50 rounded-xl p-16 text-center text-slate-400 font-medium">No tienes permisos para gestionar inscripciones de este torneo.</div>
        )}
        {activeTab === "fixtures" && <FixturesTab tournamentId={tournamentId!} state={tournament.state} />}
        {activeTab === "standings" && <StandingsTab tournamentId={tournamentId!} />}
      </div>
    </div>
  );
}
