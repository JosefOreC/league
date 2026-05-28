import { useState, useEffect } from "react";
import { useParams } from "react-router";
import { 
  Trophy, Medal, Star, AlertCircle, RefreshCw, 
  ChevronRight, Info, BarChart3, Table, Users
} from "lucide-react";
import { getPublicTournamentData } from "../../services/tournamentService";

export function Results() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { id: torneoId } = useParams<{ id: string }>();
  
  const [matches, setMatches] = useState<any[]>([]);
  const [teams, setTeams] = useState<any[]>([]);
  const [standings, setStandings] = useState<any[]>([]);
  const [tournament, setTournament] = useState<any>(null);

  const fetchData = async () => {
    if (!torneoId) return;
    setIsLoading(true);
    try {
      const data = await getPublicTournamentData(torneoId);
      setMatches(data.matches || []);
      setTeams(data.teams || []);
      setStandings(data.standings || []);
      setTournament(data.tournament);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || "Error al cargar los datos de resultados.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [torneoId]);

  const getTeamName = (teamId: string) => {
    const team = teams.find(t => String(t.id) === String(teamId) || String(t.team?.id) === String(teamId));
    return team ? (team.name || team.team?.name || "Desconocido") : `Equipo ${teamId.substring(0, 5)}`;
  };

  const getTeamTotalByCriterion = (teamId: string, criterionId: string) => {
    const results = matches.flatMap(m => m.results || []).filter(r => 
      String(r.equipo_id) === String(teamId) && 
      String(r.criterio_id) === String(criterionId)
    );
    if (results.length === 0) return 0;
    return results.reduce((acc, curr) => acc + Number(curr.valor_registrado || 0), 0);
  };

  const getTeamTotalAccumulated = (teamId: string) => {
    const results = matches.flatMap(m => m.results || []).filter(r => 
      String(r.equipo_id) === String(teamId)
    );
    return results.reduce((acc, curr) => acc + Number(curr.valor_normalizado || 0), 0);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <RefreshCw className="h-10 w-10 text-indigo-600 animate-spin" />
        <p className="text-slate-500 font-bold animate-pulse">Cargando tablero de posiciones...</p>
      </div>
    );
  }

  const criterias = tournament?.tournament_evaluation?.criterias || [];

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-20">
      {error && (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-r-xl flex items-center shadow-md">
          <AlertCircle className="h-5 w-5 mr-3" />
          <p className="font-bold">{error}</p>
        </div>
      )}

      {/* Header Premium */}
      <div className="bg-white rounded-3xl p-10 border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 h-64 w-64 bg-indigo-50 rounded-full blur-[100px] opacity-40"></div>
        <div className="relative z-10">
          <div className="inline-flex items-center px-4 py-1.5 bg-slate-900 text-white rounded-full text-[10px] font-black uppercase tracking-[0.2em] mb-4">
             <Trophy className="h-3 w-3 mr-2 text-yellow-400" /> Resultados y Posiciones
          </div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight leading-none mb-2">
            Desempeño del Torneo
          </h1>
          <p className="text-slate-500 font-medium">Resumen estadístico acumulado por criterios y rondas.</p>
        </div>
        <button 
          onClick={fetchData}
          className="h-14 px-8 bg-indigo-600 text-white rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-indigo-700 transition-all shadow-xl shadow-indigo-100 flex items-center gap-3 active:scale-95"
        >
          <RefreshCw className="h-4 w-4" /> Actualizar Datos
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Tabla de Posiciones Reforzada */}
        <div className="lg:col-span-3 space-y-8">
          <div className="bg-white border border-slate-200 rounded-[2.5rem] shadow-sm overflow-hidden">
            <div className="p-8 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <h2 className="text-xl font-black text-slate-900 flex items-center">
                <Table className="h-6 w-6 mr-3 text-indigo-600" />
                Tabla General de Desempeño
              </h2>
              <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Filtrado por puntaje acumulado</span>
            </div>
            
            <div className="overflow-x-auto">
              {standings.length === 0 ? (
                <div className="p-20 text-center text-slate-400 font-bold uppercase tracking-widest text-sm">
                  No hay datos de competencia registrados aún.
                </div>
              ) : (
                <table className="w-full text-sm text-left">
                  <thead>
                    <tr className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] bg-slate-50 border-b border-slate-100">
                      <th className="px-8 py-5 text-center w-20">POS</th>
                      <th className="px-8 py-5">EQUIPO DE COMPETENCIA</th>
                      <th className="px-6 py-5 text-center bg-indigo-50/30 text-indigo-600">PTS</th>
                      {criterias.map((c: any) => (
                        <th key={c.id} className="px-6 py-5 text-center font-bold text-[9px]">{c.name}</th>
                      ))}
                      <th className="px-8 py-5 text-center">PG</th>
                      <th className="px-8 py-5 text-center">PJ</th>
                      <th className="px-8 py-5 text-right font-black text-slate-900">ACUMULADO</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {standings.map((row: any, i: number) => {
                      const accumulated = getTeamTotalAccumulated(row.equipo_id);
                      return (
                        <tr key={row.equipo_id} className="hover:bg-slate-50/80 transition-colors group">
                          <td className="px-8 py-6 text-center">
                            {i === 0 ? <div className="h-10 w-10 bg-yellow-400 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-yellow-100"><Trophy className="h-5 w-5 text-white" /></div> : 
                             i === 1 ? <div className="h-8 w-8 bg-slate-200 rounded-xl flex items-center justify-center mx-auto"><Medal className="h-4 w-4 text-slate-500" /></div> :
                             i === 2 ? <div className="h-8 w-8 bg-orange-100 rounded-xl flex items-center justify-center mx-auto"><Medal className="h-4 w-4 text-orange-500" /></div> :
                             <span className="font-black text-slate-300">{i + 1}</span>}
                          </td>
                          <td className="px-8 py-6">
                             <div className="flex items-center gap-4">
                                <div className="h-10 w-10 bg-slate-100 rounded-xl flex items-center justify-center font-black text-slate-400 text-xs">
                                   {getTeamName(row.equipo_id).substring(0, 2).toUpperCase()}
                                </div>
                                <span className="font-black text-slate-900 text-lg tracking-tight">{getTeamName(row.equipo_id)}</span>
                             </div>
                          </td>
                          <td className="px-6 py-6 text-center bg-indigo-50/20">
                             <span className="text-xl font-black text-indigo-600">{row.puntos}</span>
                          </td>
                          {criterias.map((c: any) => (
                            <td key={c.id} className="px-6 py-6 text-center text-slate-500 font-bold">
                               {getTeamTotalByCriterion(row.equipo_id, c.id)}
                            </td>
                          ))}
                          <td className="px-8 py-6 text-center font-bold text-slate-500">{row.victorias}</td>
                          <td className="px-8 py-6 text-center font-bold text-slate-500">{row.partidos_jugados}</td>
                          <td className="px-8 py-6 text-right">
                             <span className="inline-flex items-center px-4 py-2 bg-slate-900 text-white rounded-xl font-black text-sm shadow-xl shadow-slate-100">
                                {accumulated.toFixed(2)}
                             </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Sección de Rondas Recientes */}
          <div className="bg-white border border-slate-200 rounded-[2.5rem] p-8 shadow-sm">
             <div className="flex items-center justify-between mb-8">
                <h3 className="text-xl font-black text-slate-900 flex items-center uppercase tracking-tight">
                   <BarChart3 className="h-6 w-6 mr-3 text-indigo-600" />
                   Historial de Rondas Ganadas
                </h3>
             </div>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {matches.filter(m => m.estado === 'FINISHED').slice(0, 6).map(m => (
                   <div key={m.id} className="p-6 border-2 border-slate-50 rounded-3xl flex items-center justify-between hover:border-indigo-100 transition-all">
                      <div className="flex items-center gap-4">
                         <div className="h-12 w-12 bg-slate-900 text-white rounded-2xl flex items-center justify-center font-black text-xs">
                            R{m.ronda}
                         </div>
                         <div>
                            <p className="text-xs font-black text-slate-400 uppercase tracking-widest">Ganador</p>
                            <p className="font-black text-slate-800">{getTeamName(m.ganador_id)}</p>
                         </div>
                      </div>
                      <ChevronRight className="h-5 w-5 text-slate-200" />
                   </div>
                ))}
             </div>
          </div>
        </div>

        {/* Sidebar Informativo */}
        <div className="space-y-8">
           <div className="bg-indigo-600 rounded-[2.5rem] p-8 text-white relative overflow-hidden shadow-2xl shadow-indigo-100">
              <div className="absolute -right-8 -top-8 h-40 w-40 bg-white/10 rounded-full blur-2xl"></div>
              <Trophy className="h-12 w-12 text-yellow-300 mb-6" />
              <h3 className="text-xs font-black uppercase tracking-[0.2em] text-indigo-200 mb-2">Líder Absoluto</h3>
              <div className="text-3xl font-black tracking-tight mb-4 leading-none">
                 {standings.length > 0 ? getTeamName(standings[0].equipo_id) : "N/A"}
              </div>
              <div className="flex items-center justify-between pt-6 border-t border-white/10">
                 <div className="text-center">
                    <p className="text-[10px] font-black uppercase text-indigo-200">Puntos</p>
                    <p className="text-xl font-black">{standings.length > 0 ? standings[0].puntos : 0}</p>
                 </div>
                 <div className="text-center">
                    <p className="text-[10px] font-black uppercase text-indigo-200">Victorias</p>
                    <p className="text-xl font-black">{standings.length > 0 ? standings[0].victorias : 0}</p>
                 </div>
              </div>
           </div>

           <div className="bg-slate-50 rounded-[2.5rem] p-8 border border-slate-200">
              <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-6 flex items-center">
                 <Info className="h-4 w-4 mr-2" /> Estadísticas
              </h3>
              <div className="space-y-6">
                 <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-slate-600">Equipos Activos</span>
                    <span className="font-black text-slate-900">{teams.length}</span>
                 </div>
                 <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-slate-600">Partidos Jugados</span>
                    <span className="font-black text-slate-900">{matches.filter(m => m.estado === 'FINISHED').length}</span>
                 </div>
                 <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-slate-600">Criterios Evaluados</span>
                    <span className="font-black text-slate-900">{criterias.length}</span>
                 </div>
              </div>
           </div>

           <div className="p-6 text-center">
              <p className="text-[10px] font-black text-slate-300 uppercase tracking-[0.3em]">Powered by Antigravity</p>
           </div>
        </div>
      </div>
    </div>
  );
}
