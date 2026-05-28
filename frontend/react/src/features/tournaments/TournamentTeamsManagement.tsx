import { useState, useEffect } from "react";
import { useParams, Link } from "react-router";
import { 
  ArrowLeft, 
  Users, 
  CheckCircle, 
  XCircle, 
  Info,
  Clock,
  Building2,
  User,
  AlertCircle
} from "lucide-react";
import { getTeamsByTournament, approveTeam, rejectTeam } from "../../services/teamService";
import { getTournamentById } from "../../services/tournamentService";
import { Equipo, EstadoInscripcion } from "../../types/team";
import { Tournament } from "../../types/tournament";

export function TournamentTeamsManagement() {
  const { id: tournamentId } = useParams<{ id: string }>();
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [teams, setTeams] = useState<Equipo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    if (tournamentId) {
      loadData();
    }
  }, [tournamentId]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const [tData, teamsData] = await Promise.all([
        getTournamentById(tournamentId!),
        getTeamsByTournament(tournamentId!)
      ]);
      setTournament(tData);
      setTeams(teamsData);
    } catch (err) {
      setError("No se pudo cargar la información de los equipos.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (teamId: string) => {
    setProcessingId(teamId);
    try {
      await approveTeam(teamId);
      setTeams(prev => prev.map(t => t.id === teamId ? { ...t, estado_inscripcion: EstadoInscripcion.APROBADO } : t));
    } catch (err) {
      alert("Error al aprobar el equipo.");
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (teamId: string) => {
    if (!confirm("¿Estás seguro de rechazar esta inscripción?")) return;
    setProcessingId(teamId);
    try {
      await rejectTeam(teamId);
      setTeams(prev => prev.map(t => t.id === teamId ? { ...t, estado_inscripcion: EstadoInscripcion.RECHAZADO } : t));
    } catch (err) {
      alert("Error al rechazar el equipo.");
    } finally {
      setProcessingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="text-slate-500 font-medium">Cargando equipos...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      <div className="flex items-center space-x-4 mb-2">
        <Link to="/dashboard/torneos" className="p-2 hover:bg-slate-100 rounded-full transition-colors">
          <ArrowLeft size={20} className="text-slate-600" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Administrar Inscripciones</h1>
          <p className="text-sm text-slate-500">{tournament?.name}</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-3 shadow-sm">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4">
        {teams.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-16 text-center shadow-sm">
            <div className="bg-slate-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users size={32} className="text-slate-300" />
            </div>
            <p className="text-slate-500 font-medium text-lg">Aún no hay equipos inscritos.</p>
            <p className="text-slate-400 text-sm mt-1">Las inscripciones aparecerán aquí a medida que los equipos se registren.</p>
          </div>
        ) : (
          teams.map(team => (
            <div key={team.id} className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:border-blue-200 transition-all duration-200">
              <div className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center flex-wrap gap-2">
                      <h3 className="text-xl font-bold text-slate-900">{team.name}</h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border ${
                        team.estado_inscripcion === EstadoInscripcion.APROBADO ? 'bg-green-50 text-green-700 border-green-200' :
                        team.estado_inscripcion === EstadoInscripcion.RECHAZADO ? 'bg-red-50 text-red-700 border-red-200' :
                        'bg-amber-50 text-amber-700 border-amber-200'
                      }`}>
                        {team.estado_inscripcion}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-500">
                      <div className="flex items-center gap-2"><Building2 size={16} className="text-slate-400" /> <span className="font-medium text-slate-700">ID Inst:</span> {team.institution_id}</div>
                      <div className="flex items-center gap-2 capitalize"><Info size={16} className="text-slate-400" /> <span className="font-medium text-slate-700">Categoría:</span> {team.category}</div>
                      <div className="flex items-center gap-2"><Clock size={16} className="text-slate-400" /> <span className="font-medium text-slate-700">Inscrito el:</span> {new Date(team.fecha_inscripcion).toLocaleDateString()}</div>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 shrink-0">
                    {team.estado_inscripcion === EstadoInscripcion.PENDIENTE && (
                      <>
                        <button
                          onClick={() => handleApprove(team.id)}
                          disabled={processingId === team.id}
                          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-bold transition-all shadow-sm hover:shadow active:scale-95 disabled:opacity-50"
                        >
                          <CheckCircle size={18} /> Aprobar Inscripción
                        </button>
                        <button
                          onClick={() => handleReject(team.id)}
                          disabled={processingId === team.id}
                          className="flex items-center gap-2 bg-white border border-red-200 text-red-600 hover:bg-red-50 px-5 py-2.5 rounded-lg text-sm font-bold transition-all active:scale-95 disabled:opacity-50"
                        >
                          <XCircle size={18} /> Rechazar
                        </button>
                      </>
                    )}
                    {team.estado_inscripcion === EstadoInscripcion.APROBADO && (
                       <button
                       onClick={() => handleReject(team.id)}
                       disabled={processingId === team.id}
                       className="text-xs font-semibold text-slate-400 hover:text-red-500 transition-colors uppercase tracking-tight"
                     >
                       Mover a Rechazado
                     </button>
                    )}
                    {team.estado_inscripcion === EstadoInscripcion.RECHAZADO && (
                       <button
                       onClick={() => handleApprove(team.id)}
                       disabled={processingId === team.id}
                       className="text-xs font-semibold text-slate-400 hover:text-green-600 transition-colors uppercase tracking-tight"
                     >
                       Mover a Aprobado
                     </button>
                    )}
                  </div>
                </div>

                <div className="mt-8 pt-6 border-t border-slate-100">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                      <div className="p-1 bg-blue-50 text-blue-600 rounded">
                        <User size={16} />
                      </div>
                      Miembros del Equipo ({team.participants?.length || 0})
                    </h4>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {team.participants?.map((p, idx) => (
                      <div key={idx} className="bg-slate-50/50 p-4 rounded-xl border border-slate-100 flex flex-col justify-between hover:bg-slate-50 transition-colors">
                        <div>
                          <div className="font-bold text-slate-900 text-sm">{p.nombres} {p.apellidos}</div>
                          <div className="text-[11px] text-slate-400 mt-1 uppercase tracking-wider font-semibold">DNI: {p.documento_identidad}</div>
                        </div>
                        <div className="mt-3 flex items-center justify-between">
                          <span className="bg-blue-100 text-blue-700 text-[10px] px-2 py-0.5 rounded font-bold uppercase">{p.rol_en_equipo || 'Participante'}</span>
                          <span className="text-[10px] text-slate-400 font-medium">{p.edad} años</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
