import { useState, useEffect } from "react";
import { Plus, Trophy, Rocket, AlertCircle, Loader2, Settings, Eye, Lock, Users } from "lucide-react";
import { Link } from "react-router";
import { useRoleGuard } from "../../hooks/useRoleGuard";
import {
  getTournaments,
  startTournament,
  openRegistrations,
  closeRegistrations,
  reviewTournament,
  backToDraft,
} from "../../services/tournamentService";
import { EstadoTorneo, Tournament } from "../../types/tournament";
import axios from "axios";

// ─── Status Badge ──────────────────────────────────────────────────────────────
const STATUS_CONFIG: Record<EstadoTorneo, { label: string; classes: string }> = {
  [EstadoTorneo.DRAFT]:               { label: "Borrador",           classes: "bg-slate-100 text-slate-600 border-slate-200" },
  [EstadoTorneo.IN_REVIEW]:           { label: "En Revisión",        classes: "bg-amber-50 text-amber-700 border-amber-200" },
  [EstadoTorneo.REGISTRATION_OPEN]:   { label: "Inscripciones Abiertas", classes: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  [EstadoTorneo.REGISTRATION_CLOSED]: { label: "Inscripciones Cerradas", classes: "bg-purple-50 text-purple-700 border-purple-200" },
  [EstadoTorneo.IN_PROGRESS]:         { label: "En Progreso",        classes: "bg-blue-50 text-blue-700 border-blue-200" },
  [EstadoTorneo.FINISHED]:            { label: "Finalizado",         classes: "bg-gray-50 text-gray-600 border-gray-200" },
  [EstadoTorneo.CANCELLED]:           { label: "Cancelado",          classes: "bg-red-50 text-red-700 border-red-200" },
};

function StatusBadge({ state }: { state: EstadoTorneo }) {
  const cfg = STATUS_CONFIG[state] ?? STATUS_CONFIG[EstadoTorneo.DRAFT];
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${cfg.classes}`}>
      {cfg.label}
    </span>
  );
}

// ─── Component ─────────────────────────────────────────────────────────────────
export function TournamentsList() {
  const { isParticipant, isManagerOrAdmin, canCreateTournament, canViewTournament, userId } = useRoleGuard();

  const [torneos, setTorneos] = useState<Tournament[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<{ id: string; msg: string } | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => { fetchTorneos(); }, []);

  const fetchTorneos = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const all = await getTournaments();

      // Filter by role
      let filtered: Tournament[];
      if (isParticipant) {
        // Participants see only open tournaments
        filtered = all.filter(t => t.state === EstadoTorneo.REGISTRATION_OPEN);
      } else {
        // Admin/Manager use canViewTournament (admin: all; manager: only theirs)
        filtered = all.filter(t => canViewTournament(t));
      }
      setTorneos(filtered);
    } catch (err) {
      setError("Error al cargar la lista de torneos.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAction = async (
    id: string,
    action: "open" | "close" | "review" | "draft" | "start"
  ) => {
    setActionError(null);
    setProcessingId(id);
    try {
      if (action === "open")   await openRegistrations(id);
      if (action === "close")  await closeRegistrations(id);
      if (action === "review") await reviewTournament(id);
      if (action === "draft")  await backToDraft(id);
      if (action === "start")  await startTournament(id);
      await fetchTorneos();
    } catch (err) {
      const msg = axios.isAxiosError(err)
        ? err.response?.data?.error || "Error al realizar acción."
        : "Error de conexión.";
      setActionError({ id, msg });
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            {isParticipant ? "Torneos Disponibles" : "Mis Torneos"}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            {isParticipant
              ? "Torneos abiertos a inscripción."
              : "Gestiona y administra tus torneos de robótica."}
          </p>
        </div>
        {canCreateTournament && (
          <Link
            to="/dashboard/torneos/nuevo"
            className="inline-flex items-center justify-center rounded-lg text-sm font-semibold transition-all bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm gap-2"
          >
            <Plus className="h-4 w-4" /> Crear torneo
          </Link>
        )}
      </div>

      {/* Global error */}
      {error && (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          <AlertCircle size={16} /> <span>{error}</span>
        </div>
      )}

      {/* Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-20 gap-3 text-slate-400">
            <Loader2 className="animate-spin" size={24} />
            <span className="text-sm font-medium">Cargando torneos…</span>
          </div>
        ) : torneos.length === 0 ? (
          <div className="text-center py-20">
            <Trophy className="mx-auto h-10 w-10 text-slate-300 mb-3" />
            <p className="text-slate-500 font-medium">
              {isParticipant ? "No hay torneos con inscripciones abiertas." : "Aún no tienes torneos creados."}
            </p>
            {canCreateTournament && (
              <Link to="/dashboard/torneos/nuevo" className="inline-flex items-center mt-4 text-sm text-blue-600 font-semibold hover:underline gap-1">
                <Plus size={16} /> Crear tu primer torneo
              </Link>
            )}
          </div>
        ) : (
          <table className="w-full text-sm text-left text-slate-500">
            <thead className="text-xs text-slate-700 uppercase bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 font-semibold">Torneo</th>
                <th className="px-6 py-4 font-semibold">Estado</th>
                <th className="px-6 py-4 font-semibold">Fechas</th>
                <th className="px-6 py-4 font-semibold">Categoría</th>
                <th className="px-6 py-4 font-semibold text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {torneos.map((torneo) => {
                const isOwner = torneo.creator_user_id === userId;
                const canEdit = isManagerOrAdmin && isOwner;
                const isProcessing = processingId === torneo.id;

                return (
                  <tr key={torneo.id} className="bg-white border-b border-slate-100 hover:bg-slate-50 last:border-0 transition-colors">
                    {/* Name cell */}
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600 shrink-0">
                          <Trophy className="h-5 w-5" />
                        </div>
                        <div>
                          <div className="font-semibold text-slate-900 flex items-center gap-2">
                            {torneo.name}
                            {/* Ownership indicator for ADMINs viewing others' tournaments */}
                            {!isOwner && isManagerOrAdmin && (
                              <span className="text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded font-bold uppercase flex items-center gap-1">
                                <Eye size={10} /> Solo lectura
                              </span>
                            )}
                            {isOwner && (
                              <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded font-bold uppercase">
                                Manager
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-slate-400 mt-0.5">
                            {torneo.config_tournament?.type || "Formato no configurado"}
                          </div>
                          {actionError?.id === torneo.id && (
                            <p className="mt-1 text-xs text-red-600 font-medium">{actionError.msg}</p>
                          )}
                        </div>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="px-6 py-4">
                      <StatusBadge state={torneo.state} />
                    </td>

                    {/* Dates */}
                    <td className="px-6 py-4 whitespace-nowrap text-slate-600">
                      {new Date(torneo.date_start).toLocaleDateString("es-PE")}
                      {" "}&rarr;{" "}
                      {new Date(torneo.date_end).toLocaleDateString("es-PE")}
                    </td>

                    {/* Category */}
                    <td className="px-6 py-4 text-slate-700 font-medium capitalize">
                      {torneo.category}
                    </td>

                    {/* Actions */}
                    <td className="px-6 py-4 text-right">
                      <div className="flex flex-wrap justify-end gap-2 items-center">

                        {/* ── PARTICIPANT actions ───────────────────────── */}
                        {isParticipant && (
                          <>
                            <Link
                              to={`/t/${torneo.id}`}
                              className="btn-ghost-sm flex items-center gap-1"
                            >
                              <Eye size={12} /> Ver
                            </Link>
                            {torneo.state === EstadoTorneo.REGISTRATION_OPEN && (
                              <Link
                                to={`/dashboard/torneos/${torneo.id}/inscribir-equipo`}
                                className="btn-primary-sm"
                              >
                                Inscribirse
                              </Link>
                            )}
                          </>
                        )}

                        {/* ── MANAGER / ADMIN actions ───────────────────── */}
                        {isManagerOrAdmin && (
                          <>
                            {/* Read-only view for non-owners */}
                            {!isOwner && (
                              <Link to={`/t/${torneo.id}`} className="btn-ghost-sm flex items-center gap-1">
                                <Lock size={12} /> Solo Lectura
                              </Link>
                            )}

                            {/* Full management for owners */}
                            {isOwner && (
                              <>
                                {/* Workflow state transitions */}
                                {torneo.state === EstadoTorneo.DRAFT && (
                                  <>
                                    <Link to={`/dashboard/torneos/${torneo.id}/reglas`} className="btn-secondary-sm flex items-center gap-1">
                                      <Settings size={12} /> Configurar
                                    </Link>
                                    <button
                                      onClick={() => handleAction(torneo.id, "review")}
                                      disabled={isProcessing}
                                      className="btn-ghost-sm"
                                    >
                                      Enviar a Revisión
                                    </button>
                                  </>
                                )}

                                {torneo.state === EstadoTorneo.IN_REVIEW && (
                                  <>
                                    <button
                                      onClick={() => handleAction(torneo.id, "open")}
                                      disabled={isProcessing}
                                      className="btn-emerald-sm"
                                    >
                                      Abrir Inscripciones
                                    </button>
                                    <button
                                      onClick={() => handleAction(torneo.id, "draft")}
                                      disabled={isProcessing}
                                      className="btn-ghost-sm"
                                    >
                                      ← Borrador
                                    </button>
                                  </>
                                )}

                                {torneo.state === EstadoTorneo.REGISTRATION_OPEN && (
                                  <button
                                    onClick={() => handleAction(torneo.id, "close")}
                                    disabled={isProcessing}
                                    className="btn-amber-sm"
                                  >
                                    Cerrar Inscripciones
                                  </button>
                                )}

                                {torneo.state === EstadoTorneo.REGISTRATION_CLOSED && (
                                  <button
                                    onClick={() => handleAction(torneo.id, "start")}
                                    disabled={isProcessing}
                                    className="btn-dark-sm flex items-center gap-1"
                                  >
                                    {isProcessing
                                      ? <Loader2 size={12} className="animate-spin" />
                                      : <Rocket size={12} />}
                                    Iniciar
                                  </button>
                                )}

                                {/* Admin panel */}
                                <Link
                                  to={`/dashboard/torneos/${torneo.id}/admin`}
                                  className="btn-primary-sm flex items-center gap-1"
                                >
                                  <Settings size={12} /> Panel Admin
                                </Link>

                                {/* Teams management */}
                                <Link
                                  to={`/dashboard/torneos/${torneo.id}/equipos`}
                                  className="btn-ghost-sm flex items-center gap-1"
                                >
                                  <Users size={12} /> Equipos
                                </Link>
                              </>
                            )}

                            {/* Public page always visible */}
                            <Link to={`/t/${torneo.id}`} className="btn-ghost-sm flex items-center gap-1">
                              <Eye size={12} /> Pública
                            </Link>

                            {/* Standings only when relevant */}
                            {[EstadoTorneo.REGISTRATION_OPEN, EstadoTorneo.IN_PROGRESS, EstadoTorneo.FINISHED].includes(torneo.state) && (
                              <Link
                                to={`/dashboard/torneos/${torneo.id}/posiciones`}
                                className="btn-primary-sm"
                              >
                                Tabla
                              </Link>
                            )}
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Button style utilities — injected inline via a style tag */}
      <style>{`
        .btn-primary-sm { @apply px-3 py-1.5 rounded-md text-xs font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors; }
        .btn-secondary-sm { @apply px-3 py-1.5 rounded-md text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors; }
        .btn-ghost-sm { @apply px-3 py-1.5 rounded-md text-xs font-semibold bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 transition-colors; }
        .btn-emerald-sm { @apply px-3 py-1.5 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition-colors; }
        .btn-amber-sm { @apply px-3 py-1.5 rounded-md text-xs font-semibold bg-amber-50 text-amber-700 hover:bg-amber-100 transition-colors; }
        .btn-dark-sm { @apply px-3 py-1.5 rounded-md text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-50 transition-colors; }
      `}</style>
    </div>
  );
}
