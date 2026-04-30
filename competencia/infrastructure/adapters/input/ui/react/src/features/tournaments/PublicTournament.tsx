import { useEffect, useState } from "react";
import { useParams, Link } from "react-router";
import { Trophy, Users, Swords, Calendar, Info, Loader2, ArrowLeft } from "lucide-react";
import axios from "axios";
import { useAuth } from "../../context/AuthContext";

interface PublicData {
  tournament: any;
  teams: any[];
  matches: any[];
  standings: any[];
}

export function PublicTournament() {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated } = useAuth();
  const backLink = isAuthenticated ? "/dashboard/torneos" : "/";

  const [data, setData] = useState<PublicData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"info" | "teams" | "standings" | "matches">("info");

  useEffect(() => {
    const fetchPublicData = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/";
        const response = await axios.get(`${apiUrl}competencia/torneo/${id}/public/`);
        setData(response.data);
      } catch (err) {
        setError("No se pudo cargar la información del torneo. Es posible que no exista o no sea público.");
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchPublicData();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4 text-slate-500">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
          <p>Cargando información del torneo...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 p-6">
        <Trophy className="h-16 w-16 text-slate-300 mb-4" />
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Torneo no disponible</h1>
        <p className="text-slate-500 mb-6 text-center max-w-md">{error}</p>
        <Link to={backLink} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Volver al inicio
        </Link>
      </div>
    );
  }

  const { tournament, teams, matches, standings } = data;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-blue-100">
      {/* Header Público */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Link to={backLink} className="text-slate-400 hover:text-slate-600 transition-colors mr-2">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-sm">
                <Trophy className="h-5 w-5 text-white" />
              </div>
              <h1 className="font-bold text-xl text-slate-900 truncate max-w-[200px] sm:max-w-md">
                {tournament.name}
              </h1>
            </div>
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide border ${
                tournament.state === "published" || tournament.state === "in_progress" 
                  ? "bg-green-50 text-green-700 border-green-200" 
                  : "bg-slate-100 text-slate-600 border-slate-200"
              }`}>
                {tournament.state.replace("_", " ")}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="bg-gradient-to-br from-blue-900 to-indigo-900 text-white py-12 px-4 sm:px-6 lg:px-8 border-b border-indigo-950">
        <div className="max-w-6xl mx-auto flex flex-col items-center text-center">
          <div className="p-4 bg-white/10 rounded-2xl backdrop-blur-md mb-6 shadow-xl ring-1 ring-white/20">
             <Trophy className="h-12 w-12 text-blue-200" />
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-r from-white to-blue-200">
            {tournament.name}
          </h2>
          <p className="text-lg text-blue-100 max-w-2xl mx-auto leading-relaxed opacity-90 mb-8">
            {tournament.description || "Un emocionante torneo de robótica competitivo."}
          </p>
          <div className="flex flex-wrap justify-center gap-4 text-sm font-medium">
             <div className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/10 shadow-inner">
               <Calendar className="h-4 w-4 text-blue-300" />
               {new Date(tournament.date_start).toLocaleDateString()} - {new Date(tournament.date_end).toLocaleDateString()}
             </div>
             <div className="flex items-center gap-2 bg-white/10 px-4 py-2 rounded-full backdrop-blur-sm border border-white/10 shadow-inner">
               <Users className="h-4 w-4 text-blue-300" />
               Categoría: <span className="capitalize">{tournament.category}</span>
             </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Navigation Tabs */}
        <div className="flex space-x-1 bg-white p-1 rounded-xl shadow-sm border border-slate-200 mb-8 overflow-x-auto overflow-y-hidden">
          {[
            { id: "info", label: "Información", icon: Info },
            { id: "teams", label: "Equipos Registrados", icon: Users },
            { id: "matches", label: "Partidos / Competencias", icon: Swords },
            { id: "standings", label: "Tabla de Posiciones", icon: Trophy },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ease-in-out whitespace-nowrap ${
                activeTab === tab.id
                  ? "bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-100"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              <tab.icon className={`h-4 w-4 ${activeTab === tab.id ? 'text-blue-600' : 'text-slate-400'}`} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-8 min-h-[400px]">
          
          {/* TAB: INFO */}
          {activeTab === "info" && (
            <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-xl font-bold text-slate-900 border-b border-slate-100 pb-4 flex items-center gap-2">
                 <Info className="h-5 w-5 text-blue-500"/>
                 Detalles Generales
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-slate-50 rounded-xl p-5 border border-slate-100">
                  <h4 className="font-semibold text-slate-800 mb-4 uppercase text-xs tracking-wider">Reglas del Torneo</h4>
                  <ul className="space-y-3 text-sm text-slate-600">
                    <li className="flex justify-between items-center bg-white p-2 rounded-md shadow-sm border border-slate-100">
                        <span className="text-slate-500">Máximo de Equipos:</span> 
                        <span className="font-semibold text-slate-800">{tournament.max_teams}</span>
                    </li>
                    {tournament.tournament_rule && (
                      <>
                        <li className="flex justify-between items-center bg-white p-2 rounded-md shadow-sm border border-slate-100">
                            <span className="text-slate-500">Tipo de Acceso:</span> 
                            <span className="font-semibold text-slate-800 capitalize">{tournament.tournament_rule.access_type}</span>
                        </li>
                        <li className="flex justify-between items-center bg-white p-2 rounded-md shadow-sm border border-slate-100">
                            <span className="text-slate-500">Miembros por equipo:</span> 
                            <span className="font-semibold text-slate-800">{tournament.tournament_rule.min_members} - {tournament.tournament_rule.max_members}</span>
                        </li>
                      </>
                    )}
                  </ul>
                </div>
                <div className="bg-slate-50 rounded-xl p-5 border border-slate-100">
                  <h4 className="font-semibold text-slate-800 mb-4 uppercase text-xs tracking-wider">Formato</h4>
                  {tournament.config_tournament ? (
                    <ul className="space-y-3 text-sm text-slate-600">
                        <li className="flex justify-between items-center bg-white p-2 rounded-md shadow-sm border border-slate-100">
                            <span className="text-slate-500">Tipo de Formato:</span> 
                            <span className="font-semibold text-slate-800 uppercase tracking-wide text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">{tournament.config_tournament.type.replace("_", " ")}</span>
                        </li>
                    </ul>
                  ) : (
                    <p className="text-sm text-slate-500 italic bg-white p-4 rounded-lg border border-slate-200 text-center">Formato aún no configurado.</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB: TEAMS */}
          {activeTab === "teams" && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-xl font-bold text-slate-900 border-b border-slate-100 pb-4 mb-6 flex items-center justify-between">
                 <div className="flex items-center gap-2">
                    <Users className="h-5 w-5 text-blue-500"/>
                    Equipos Registrados
                 </div>
                 <span className="text-sm font-normal bg-blue-50 text-blue-700 px-3 py-1 rounded-full border border-blue-100 shadow-inner">
                    Total: <strong className="font-bold">{teams.length}</strong>
                 </span>
              </h3>
              {teams.length === 0 ? (
                <div className="text-center py-12 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                  <Users className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-500">No hay equipos registrados aún en este torneo.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                  {teams.map((team) => (
                    <div key={team.id} className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-all duration-200 group">
                      <div className="flex items-center gap-4 mb-3">
                        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 border border-slate-200 flex items-center justify-center group-hover:scale-105 transition-transform">
                          <Users className="h-6 w-6 text-slate-500 group-hover:text-blue-600 transition-colors" />
                        </div>
                        <div>
                           <h4 className="font-bold text-slate-900 text-lg leading-tight">{team.name}</h4>
                           <span className="text-xs font-medium text-slate-500 px-2 py-0.5 bg-slate-100 rounded mt-1 inline-block">ID: {team.id.substring(0,6)}...</span>
                        </div>
                      </div>
                      <div className="space-y-2 mt-4 pt-4 border-t border-slate-100">
                          <div className="flex justify-between items-center text-sm">
                             <span className="text-slate-500">Integrantes:</span>
                             <span className="font-medium text-slate-800">{team.participants?.length || 0}</span>
                          </div>
                          <div className="flex justify-between items-center text-sm">
                             <span className="text-slate-500">Nivel Declarado:</span>
                             <span className="font-medium text-slate-800 capitalize">{team.nivel_tecnico_declarado}</span>
                          </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB: MATCHES */}
          {activeTab === "matches" && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-xl font-bold text-slate-900 border-b border-slate-100 pb-4 mb-6 flex items-center gap-2">
                 <Swords className="h-5 w-5 text-blue-500"/>
                 Competencias Programadas
              </h3>
              {matches.length === 0 ? (
                <div className="text-center py-12 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                  <Swords className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-500">Aún no se han generado enfrentamientos o el torneo no ha iniciado.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {matches.map((match) => (
                    <div key={match.id} className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm hover:border-blue-300 transition-colors">
                      <div className="bg-slate-50 px-4 py-2 border-b border-slate-200 flex justify-between items-center text-xs font-semibold text-slate-500 uppercase tracking-wide">
                        <span>Fase: {match.fase}</span>
                        <span className={`px-2 py-1 rounded-full ${match.estado === "FINISHED" ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                          {match.estado}
                        </span>
                      </div>
                      <div className="p-5 flex justify-between items-center relative">
                         {/* Local */}
                         <div className="flex flex-col items-center flex-1">
                             <span className="font-bold text-slate-900 text-center mb-1">{match.equipo_local_id ? teams.find(t=>t.id===match.equipo_local_id)?.name || 'Local' : 'Por definir'}</span>
                             {match.estado === "FINISHED" && match.ganador_id === match.equipo_local_id && <Trophy className="h-4 w-4 text-yellow-500 mt-1"/>}
                         </div>
                         {/* VS */}
                         <div className="px-4 flex flex-col items-center z-10">
                            <div className="h-8 w-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-xs font-bold text-slate-400">
                                VS
                            </div>
                         </div>
                         {/* Visitante */}
                         <div className="flex flex-col items-center flex-1">
                             <span className="font-bold text-slate-900 text-center mb-1">{match.equipo_visitante_id ? teams.find(t=>t.id===match.equipo_visitante_id)?.name || 'Visitante' : 'Por definir'}</span>
                             {match.estado === "FINISHED" && match.ganador_id === match.equipo_visitante_id && <Trophy className="h-4 w-4 text-yellow-500 mt-1"/>}
                         </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB: STANDINGS */}
          {activeTab === "standings" && (
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="text-xl font-bold text-slate-900 border-b border-slate-100 pb-4 mb-6 flex items-center gap-2">
                 <Trophy className="h-5 w-5 text-blue-500"/>
                 Tabla de Posiciones
              </h3>
              {standings.length === 0 ? (
                <div className="text-center py-12 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                  <Trophy className="h-12 w-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-500">La tabla de posiciones se actualizará cuando haya resultados.</p>
                </div>
              ) : (
                <div className="overflow-hidden rounded-xl border border-slate-200 shadow-sm">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm whitespace-nowrap">
                      <thead className="bg-slate-50 text-slate-600 font-semibold uppercase text-xs tracking-wider">
                        <tr>
                          <th className="px-6 py-4 border-b border-slate-200">#</th>
                          <th className="px-6 py-4 border-b border-slate-200">Equipo</th>
                          <th className="px-6 py-4 border-b border-slate-200 text-center">PTS</th>
                          <th className="px-6 py-4 border-b border-slate-200 text-center">PJ</th>
                          <th className="px-6 py-4 border-b border-slate-200 text-center">PG</th>
                          <th className="px-6 py-4 border-b border-slate-200 text-center">PE</th>
                          <th className="px-6 py-4 border-b border-slate-200 text-center">PP</th>
                          <th className="px-6 py-4 border-b border-slate-200 text-center">DIF</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 bg-white">
                        {standings.map((teamStats, index) => (
                          <tr key={teamStats.equipo_id} className={`hover:bg-slate-50 transition-colors ${index < 3 ? 'bg-blue-50/30' : ''}`}>
                            <td className="px-6 py-4 font-medium text-slate-900">
                               <div className="flex items-center gap-2">
                                  {index === 0 && <Trophy className="h-4 w-4 text-yellow-500" />}
                                  {index === 1 && <Trophy className="h-4 w-4 text-slate-400" />}
                                  {index === 2 && <Trophy className="h-4 w-4 text-amber-600" />}
                                  {index > 2 && <span className="w-4 text-center">{index + 1}</span>}
                               </div>
                            </td>
                            <td className="px-6 py-4 font-bold text-slate-800">
                                {teams.find(t => t.id === teamStats.equipo_id)?.name || "Equipo Desconocido"}
                            </td>
                            <td className="px-6 py-4 font-bold text-blue-600 text-center">{teamStats.puntos}</td>
                            <td className="px-6 py-4 text-slate-600 text-center">{teamStats.partidos_jugados}</td>
                            <td className="px-6 py-4 text-slate-600 text-center">{teamStats.partidos_ganados}</td>
                            <td className="px-6 py-4 text-slate-600 text-center">{teamStats.partidos_empatados}</td>
                            <td className="px-6 py-4 text-slate-600 text-center">{teamStats.partidos_perdidos}</td>
                            <td className="px-6 py-4 font-medium text-slate-600 text-center">{teamStats.diferencia_puntaje}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
