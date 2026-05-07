import { 
  PlayCircle, Shuffle, Swords, Trophy, GitFork, Calendar, 
  Users, AlertCircle, Loader2, Star, CheckCircle2, 
  XCircle, ChevronRight, BarChart3, Info, Table
} from "lucide-react";
import { useState, useEffect } from "react";
import { generateFixtures, getPublicTournamentData, registerMatchResults } from "../../services/tournamentService";
import { useParams } from "react-router";

export function Competitions() {
  const [activeFase, setActiveFase] = useState("Llaves");

  const { id } = useParams<{ id: string }>();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [matches, setMatches] = useState<any[]>([]);
  const [teams, setTeams] = useState<any[]>([]);
  const [standings, setStandings] = useState<any[]>([]);
  const [tournament, setTournament] = useState<any>(null);

  // Estado para el modal de calificación
  const [qualifyingMatch, setQualifyingMatch] = useState<any>(null);
  const [qualifications, setQualifications] = useState<any[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const loadData = async () => {
    if (!id) return;
    setIsLoading(true);
    try {
      const data = await getPublicTournamentData(id);
      setMatches(data.matches || []);
      setTeams(data.teams || []);
      setStandings(data.standings || []);
      setTournament(data.tournament);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || "No se pudo cargar la información del torneo.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleGenerateFixtures = async () => {
    if (!id) return;
    setIsGenerating(true);
    setError(null);
    try {
      await generateFixtures(id);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.error || "Error al generar emparejamientos");
    } finally {
      setIsGenerating(false);
    }
  };

  const openQualifyModal = (match: any) => {
    const criterias = tournament?.tournament_evaluation?.criterias || [];
    const initialQuals: any[] = [];
    
    [match.equipo_local_id, match.equipo_visitante_id].forEach(teamId => {
      if (!teamId) return;
      criterias.forEach((c: any) => {
        // Buscar si ya tiene un resultado previo (opcional, por ahora lo dejamos vacío)
        initialQuals.push({
          team_id: teamId,
          criterio_id: c.id,
          name: c.name,
          value: c.min_value_qualification || 0
        });
      });
    });
    
    setQualifications(initialQuals);
    setQualifyingMatch(match);
  };

  const handleQualChange = (teamId: string, critId: string, val: string) => {
    setQualifications(prev => prev.map(q => 
      (q.team_id === teamId && q.criterio_id === critId) 
        ? { ...q, value: val } 
        : q
    ));
  };

  const submitQualifications = async () => {
    if (!qualifyingMatch || !id) return;
    setIsSubmitting(true);
    try {
      const payload = {
        qualifications: qualifications.map(q => ({
          team_id: q.team_id,
          criterio_id: q.criterio_id,
          value: Number(q.value)
        }))
      };
      
      await registerMatchResults(id, qualifyingMatch.id, payload.qualifications);
      
      setQualifyingMatch(null);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.error || "Error al calificar el partido");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getTeamName = (teamId: string | null) => {
    if (!teamId) return "TBD";
    const team = teams.find(t => t.id === teamId || t.team?.id === teamId);
    if (!team) return "Desconocido";
    return team.name || team.team?.name || "Desconocido";
  };

  const getMatchScoreForCriterion = (match: any, teamId: string, criterionId: string) => {
    if (!match.results) return "-";
    const result = match.results.find((r: any) => 
      String(r.equipo_id) === String(teamId) && 
      String(r.criterio_id) === String(criterionId)
    );
    return result ? result.valor_registrado : "-";
  };

  // Agrupar matches por ronda
  const matchesByRound: { [key: number]: any[] } = {};
  matches.forEach(m => {
    const r = m.ronda || 1;
    if (!matchesByRound[r]) matchesByRound[r] = [];
    matchesByRound[r].push(m);
  });
  
  const rounds = Object.keys(matchesByRound).map(Number).sort((a, b) => a - b);
  const totalRounds = rounds.length;

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-6">
        <div className="relative">
          <div className="h-16 w-16 border-4 border-slate-100 border-t-indigo-600 rounded-full animate-spin"></div>
          <Trophy className="h-6 w-6 text-indigo-600 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
        </div>
        <p className="text-slate-500 font-bold animate-pulse tracking-wide">Cargando competencias...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-full mx-auto pb-20 px-4 sm:px-6">
      {error && (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-r-xl flex items-start shadow-md animate-in fade-in slide-in-from-top-4 duration-300">
          <AlertCircle className="h-5 w-5 mr-3 mt-0.5 flex-shrink-0" />
          <div>
             <p className="font-bold">Hubo un problema</p>
             <p className="text-sm opacity-90">{error}</p>
          </div>
        </div>
      )}

      {/* Header Premium */}
      <div className="bg-white rounded-[2.5rem] p-10 border border-slate-200 shadow-sm flex flex-col lg:flex-row items-center justify-between gap-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 h-64 w-64 bg-indigo-50 rounded-full blur-[100px] opacity-40"></div>
        <div className="absolute bottom-0 left-0 -mb-10 -ml-10 h-64 w-64 bg-blue-50 rounded-full blur-[100px] opacity-40"></div>
        
        <div className="relative z-10 text-center lg:text-left flex-1">
          <div className="inline-flex items-center px-4 py-1.5 bg-indigo-600 text-white rounded-full text-[10px] font-black uppercase tracking-[0.2em] mb-4 shadow-lg shadow-indigo-100">
             <Trophy className="h-3 w-3 mr-2" /> Central de Competencias
          </div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight leading-[1.1] mb-4">
            {tournament?.name || "Torneo de Robótica"}
          </h1>
          <div className="flex flex-wrap justify-center lg:justify-start gap-4 text-slate-500 font-medium text-sm">
             <span className="flex items-center"><Users className="h-4 w-4 mr-2 text-indigo-500" /> {teams.length} Equipos</span>
             <span className="flex items-center"><Calendar className="h-4 w-4 mr-2 text-indigo-500" /> {matches.length} Enfrentamientos</span>
             <span className="flex items-center"><Info className="h-4 w-4 mr-2 text-indigo-500" /> {tournament?.category}</span>
          </div>
        </div>

        <div className="flex flex-wrap justify-center gap-4 relative z-10">
           <button 
            onClick={handleGenerateFixtures}
            disabled={isGenerating || matches.length > 0}
            className={`inline-flex items-center justify-center rounded-[1.25rem] text-sm font-black transition-all h-14 px-10 shadow-xl ${
              matches.length > 0 
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed shadow-none' 
              : 'bg-slate-900 text-white hover:bg-indigo-600 hover:-translate-y-1 active:translate-y-0 shadow-slate-200'
            }`}
          >
            {isGenerating ? <Loader2 className="mr-3 h-5 w-5 animate-spin" /> : <Shuffle className="mr-3 h-5 w-5" />}
            {matches.length > 0 ? "FIXTURES ACTIVOS" : (isGenerating ? "GENERANDO..." : "GENERAR FIXTURES")}
          </button>
          
          <button 
            onClick={() => loadData()}
            className="h-14 w-14 bg-white border border-slate-200 rounded-[1.25rem] text-slate-600 hover:bg-slate-50 shadow-sm transition-all flex items-center justify-center hover:scale-105 active:scale-95"
          >
            <BarChart3 className="h-6 w-6" />
          </button>
        </div>
      </div>

      {/* Tabs Estilo Apple */}
      <div className="flex bg-slate-200/50 p-1.5 rounded-[1.5rem] w-full md:w-max mx-auto md:mx-0 shadow-inner backdrop-blur-sm">
        {[
          { id: "Llaves", icon: Trophy, label: "Árbol", color: "text-yellow-500" },
          { id: "Rondas", icon: PlayCircle, label: "Cronograma", color: "text-blue-500" },
          { id: "Resultados", icon: Table, label: "Tabla de Enfrentamientos", color: "text-indigo-500" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveFase(tab.id)}
            className={`flex items-center px-8 py-3.5 text-xs font-black uppercase tracking-widest rounded-[1.15rem] transition-all duration-300 ${
              activeFase === tab.id
                ? "bg-white text-slate-900 shadow-xl ring-1 ring-black/5"
                : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
            }`}
          >
            <tab.icon className={`mr-3 h-4 w-4 ${tab.color}`} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Contenido Principal con Animación */}
      <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
        {activeFase === "Llaves" && (
          <div className="bg-white border border-slate-200 rounded-[3rem] shadow-sm p-12 overflow-x-auto min-h-[600px] relative">
            <div className="flex items-center justify-between mb-16">
              <div>
                <h2 className="text-3xl font-black text-slate-900 flex items-center tracking-tight">
                  <GitFork className="mr-4 h-10 w-10 text-indigo-600 transform -rotate-90" />
                  Cuadro de Clasificación
                </h2>
                <p className="text-slate-400 font-bold text-sm mt-2 ml-14 uppercase tracking-widest">Eliminación Directa</p>
              </div>
            </div>
            
            {matches.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-32 text-center">
                <div className="h-32 w-32 bg-slate-50 rounded-full flex items-center justify-center mb-8 ring-[16px] ring-slate-50/50">
                  <Shuffle className="h-12 w-12 text-slate-200" />
                </div>
                <h3 className="text-slate-900 font-black text-2xl mb-4">Tablero Vacío</h3>
                <p className="text-slate-400 max-w-sm mx-auto font-medium leading-relaxed">
                  Utiliza el botón de arriba para generar los emparejamientos y activar el tablero de competencia.
                </p>
              </div>
            ) : (
              <div className="flex gap-24 min-w-max pb-12 px-4">
                {rounds.map((roundIndex, i) => {
                   const roundMatches = matchesByRound[roundIndex].sort((a,b) => a.posicion_en_ronda - b.posicion_en_ronda);
                   let roundTitle = `RONDA ${roundIndex}`;
                   let titleClass = "bg-slate-100 text-slate-500";
                   
                   if (i === totalRounds - 1) {
                      roundTitle = "GRAN FINAL";
                      titleClass = "bg-yellow-400 text-yellow-950 ring-8 ring-yellow-400/20";
                   } else if (i === totalRounds - 2) {
                      roundTitle = "SEMIFINALES";
                      titleClass = "bg-indigo-600 text-white shadow-lg shadow-indigo-100";
                   }

                   return (
                     <div key={roundIndex} className="flex flex-col justify-around gap-20 w-80 relative">
                       <div className={`text-[10px] font-black px-6 py-2 rounded-full mb-10 uppercase tracking-[0.3em] text-center w-max mx-auto shadow-sm ${titleClass}`}>
                          {roundTitle}
                       </div>
                       
                       {roundMatches.map((match, mIdx) => (
                         <div 
                           key={match.id} 
                           className={`group relative bg-white border-[3px] rounded-[2rem] transition-all z-10 shadow-sm ${
                             match.estado === "FINISHED" 
                             ? 'border-slate-50 bg-slate-50/20 shadow-none grayscale-[0.5]' 
                             : 'border-slate-200 hover:border-indigo-500 hover:shadow-2xl hover:shadow-indigo-200/50 hover:-translate-y-2'
                           }`}
                         >
                           {/* Badge de Estado Pro */}
                           <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                              {match.estado === "FINISHED" ? (
                                <div className="flex items-center px-4 py-1.5 bg-green-500 text-white rounded-full text-[9px] font-black uppercase tracking-widest shadow-lg shadow-green-200">
                                  <CheckCircle2 className="h-3 w-3 mr-2" /> FINALIZADO
                                </div>
                              ) : (match.equipo_local_id && match.equipo_visitante_id ? (
                                <div className="flex items-center px-4 py-1.5 bg-indigo-600 text-white rounded-full text-[9px] font-black uppercase tracking-widest shadow-lg shadow-indigo-200">
                                  LISTO
                                </div>
                              ) : null)}
                           </div>

                           <div className="p-1.5">
                             {/* Equipo Local */}
                             <div className={`p-5 rounded-t-[1.6rem] flex justify-between items-center transition-colors ${match.ganador_id === match.equipo_local_id ? 'bg-green-50/50' : ''}`}>
                               <div className="flex items-center min-w-0">
                                 <div className={`h-3 w-3 rounded-full mr-4 shrink-0 shadow-sm ${match.ganador_id === match.equipo_local_id ? 'bg-green-500 scale-125' : 'bg-slate-300 opacity-30'}`}></div>
                                 <span className={`text-sm font-black truncate tracking-tight ${match.ganador_id && match.ganador_id !== match.equipo_local_id ? 'text-slate-300 line-through decoration-[1.5px]' : 'text-slate-800'}`}>
                                   {getTeamName(match.equipo_local_id)}
                                 </span>
                               </div>
                               {match.estado === "FINISHED" && (
                                  <span className="text-[10px] font-black bg-white border border-slate-100 px-3 py-1 rounded-full shadow-sm text-slate-400">Puntaje</span>
                               )}
                             </div>

                             <div className="h-px bg-slate-100/60 mx-6"></div>

                             {/* Equipo Visitante */}
                             <div className={`p-5 rounded-b-[1.6rem] flex justify-between items-center transition-colors ${match.ganador_id === match.equipo_visitante_id ? 'bg-green-50/50' : ''}`}>
                               <div className="flex items-center min-w-0">
                                 <div className={`h-3 w-3 rounded-full mr-4 shrink-0 shadow-sm ${match.ganador_id === match.equipo_visitante_id ? 'bg-green-500 scale-125' : 'bg-slate-300 opacity-30'}`}></div>
                                 <span className={`text-sm font-black truncate tracking-tight ${match.ganador_id && match.ganador_id !== match.equipo_visitante_id ? 'text-slate-300 line-through decoration-[1.5px]' : 'text-slate-800'}`}>
                                   {getTeamName(match.equipo_visitante_id)}
                                 </span>
                               </div>
                               {match.estado === "FINISHED" && (
                                  <span className="text-[10px] font-black bg-white border border-slate-100 px-3 py-1 rounded-full shadow-sm text-slate-400">Puntaje</span>
                               )}
                             </div>
                           </div>

                           {/* Botón de Arbitraje Flotante */}
                           {match.estado !== "FINISHED" && match.equipo_local_id && match.equipo_visitante_id && (
                             <button 
                               onClick={() => openQualifyModal(match)}
                               className="absolute -right-4 top-1/2 transform -translate-y-1/2 bg-slate-900 text-white p-4 rounded-2xl shadow-2xl opacity-0 group-hover:opacity-100 transition-all hover:bg-indigo-600 hover:scale-110 active:scale-95 z-30 ring-4 ring-white"
                             >
                               <Swords className="h-5 w-5" />
                             </button>
                           )}
                           
                           {/* Conectores Curvados Premium */}
                           {i < totalRounds - 1 && (
                             <>
                               <div className="absolute top-1/2 -right-12 w-12 h-1 bg-slate-200 group-hover:bg-indigo-300 transition-colors"></div>
                               {mIdx % 2 !== 0 && (
                                 <div className="absolute -top-[calc(50%+2.5rem)] -right-12 w-1 h-[calc(100%+5rem)] bg-slate-200 group-hover:bg-indigo-300 transition-colors rounded-full"></div>
                               )}
                             </>
                           )}
                         </div>
                       ))}
                     </div>
                   );
                })}
              </div>
            )}
          </div>
        )}

        {activeFase === "Rondas" && (
          <div className="bg-white border border-slate-200 rounded-[3rem] shadow-sm p-12">
             <div className="flex items-center justify-between mb-12">
              <h2 className="text-3xl font-black text-slate-900 flex items-center tracking-tight">
                <Calendar className="mr-4 h-10 w-10 text-blue-500" />
                Planificación Estratégica
              </h2>
            </div>

            {rounds.length === 0 ? (
               <div className="text-center py-32 text-slate-400 font-bold">Sin rondas programadas.</div>
            ) : (
              <div className="space-y-16">
                {rounds.map(round => (
                  <div key={round} className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="flex items-center gap-6 mb-8">
                      <div className="h-14 w-14 bg-slate-900 text-white rounded-[1.25rem] flex items-center justify-center font-black text-xl shadow-2xl shadow-slate-200">
                        {round}
                      </div>
                      <h3 className="text-2xl font-black text-slate-800 uppercase tracking-tight">
                        Ronda de Clasificación {round}
                      </h3>
                      <div className="h-[2px] bg-slate-100 flex-grow"></div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                      {matchesByRound[round].map(match => (
                        <div key={match.id} className="group bg-white border-2 border-slate-100 rounded-[2rem] p-8 hover:border-indigo-500 hover:shadow-2xl transition-all relative overflow-hidden">
                          <div className="absolute top-0 right-0 h-24 w-24 bg-slate-50 rounded-full -mr-12 -mt-12 transition-colors group-hover:bg-indigo-50"></div>
                          
                          <div className="flex justify-between items-center mb-8 relative z-10">
                             <span className="text-[10px] font-black text-slate-400 bg-white border border-slate-100 px-4 py-1.5 rounded-full uppercase tracking-[0.2em]">
                               Partida #{match.posicion_en_ronda}
                             </span>
                             <span className={`text-[10px] font-black px-4 py-1.5 rounded-full uppercase tracking-[0.2em] shadow-sm ${
                               match.estado === "FINISHED" ? "bg-green-500 text-white" : "bg-blue-600 text-white"
                             }`}>
                               {match.estado}
                             </span>
                          </div>
                          <div className="space-y-5 relative z-10">
                             <div className="flex items-center justify-between group-hover:translate-x-2 transition-transform duration-300">
                                <span className={`font-black text-lg truncate max-w-[180px] ${match.ganador_id === match.equipo_local_id ? 'text-indigo-600' : 'text-slate-800'}`}>
                                  {getTeamName(match.equipo_local_id)}
                                </span>
                                {match.ganador_id === match.equipo_local_id && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                             </div>
                             <div className="flex items-center justify-center py-2">
                               <div className="h-px bg-slate-100 flex-grow"></div>
                               <span className="mx-4 text-xs font-black text-slate-300 italic uppercase">vs</span>
                               <div className="h-px bg-slate-100 flex-grow"></div>
                             </div>
                             <div className="flex items-center justify-between group-hover:translate-x-2 transition-transform duration-300">
                                <span className={`font-black text-lg truncate max-w-[180px] ${match.ganador_id === match.equipo_visitante_id ? 'text-indigo-600' : 'text-slate-800'}`}>
                                  {getTeamName(match.equipo_visitante_id)}
                                </span>
                                {match.ganador_id === match.equipo_visitante_id && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                             </div>
                          </div>
                          
                          {match.estado !== "FINISHED" && match.equipo_local_id && match.equipo_visitante_id && (
                             <button 
                               onClick={() => openQualifyModal(match)}
                               className="w-full mt-10 py-4 bg-slate-900 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] hover:bg-indigo-600 transition-all shadow-xl shadow-slate-100 hover:shadow-indigo-100"
                             >
                               Arbitrar Resultado
                             </button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeFase === "Resultados" && (
          <div className="bg-white border border-slate-200 rounded-[3rem] shadow-sm p-12">
            <div className="flex items-center justify-between mb-12">
              <div>
                <h2 className="text-3xl font-black text-slate-900 flex items-center tracking-tight">
                  <Table className="mr-4 h-10 w-10 text-indigo-600" />
                  Tabla de Enfrentamientos
                </h2>
                <p className="text-slate-400 font-bold text-sm mt-2 uppercase tracking-[0.2em]">Desglose de calificaciones por criterio</p>
              </div>
            </div>
            
            <div className="space-y-12">
               {matches.filter(m => m.estado === "FINISHED").length === 0 ? (
                 <div className="text-center py-32 bg-slate-50/50 rounded-[2rem] border-2 border-dashed border-slate-200">
                    <Info className="h-12 w-12 text-slate-200 mx-auto mb-4" />
                    <p className="text-slate-400 font-bold uppercase tracking-widest text-sm">No hay enfrentamientos calificados para mostrar</p>
                 </div>
               ) : (
                 matches.filter(m => m.estado === "FINISHED").map(match => (
                   <div key={match.id} className="bg-white border border-slate-100 rounded-[2.5rem] shadow-xl shadow-slate-100/50 overflow-hidden">
                      <div className="bg-slate-900 p-8 flex flex-col md:flex-row justify-between items-center gap-6">
                         <div className="flex items-center gap-6">
                            <div className="h-12 w-12 bg-white/10 rounded-2xl flex items-center justify-center font-black text-white">
                               {match.ronda}
                            </div>
                            <div>
                               <h4 className="text-white font-black text-lg uppercase tracking-tight">Ronda {match.ronda} - Partida {match.posicion_en_ronda}</h4>
                               <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mt-1">Cálculo de puntaje pesado finalizado</p>
                            </div>
                         </div>
                         <div className="flex items-center gap-4 bg-white/5 p-3 rounded-2xl border border-white/10 backdrop-blur-sm">
                            <span className="text-indigo-400 font-black text-sm px-3">{getTeamName(match.equipo_local_id)}</span>
                            <span className="text-white/20 text-xs font-black">VS</span>
                            <span className="text-indigo-400 font-black text-sm px-3">{getTeamName(match.equipo_visitante_id)}</span>
                         </div>
                      </div>
                      
                      <div className="p-8 overflow-x-auto">
                         <table className="w-full border-collapse">
                            <thead>
                               <tr className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] border-b border-slate-100">
                                  <th className="px-6 py-4 text-left">Equipo de Competencia</th>
                                  {tournament?.tournament_evaluation?.criterias?.map((c: any) => (
                                    <th key={c.id} className="px-6 py-4 text-center">{c.name}</th>
                                  ))}
                                  <th className="px-6 py-4 text-right bg-slate-50 rounded-t-xl">Total Pesado</th>
                               </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-50">
                               {[match.equipo_local_id, match.equipo_visitante_id].map((teamId, idx) => {
                                  const results = match.results?.filter((r: any) => String(r.equipo_id) === String(teamId)) || [];
                                  const totalScore = results.reduce((acc: number, curr: any) => acc + Number(curr.valor_normalizado || 0), 0);
                                  
                                  return (
                                    <tr key={teamId} className={`hover:bg-slate-50/50 transition-colors ${match.ganador_id === teamId ? 'bg-green-50/20' : ''}`}>
                                       <td className="px-6 py-6 font-black text-slate-800 flex items-center gap-4">
                                          <div className={`h-8 w-8 rounded-xl flex items-center justify-center font-black text-[10px] ${idx === 0 ? 'bg-blue-100 text-blue-600' : 'bg-purple-100 text-purple-600'}`}>
                                             {idx === 0 ? 'L' : 'V'}
                                          </div>
                                          {getTeamName(teamId)}
                                          {match.ganador_id === teamId && <Trophy className="h-4 w-4 text-yellow-500 ml-2" />}
                                       </td>
                                       {tournament?.tournament_evaluation?.criterias?.map((c: any) => (
                                         <td key={c.id} className="px-6 py-6 text-center font-bold text-slate-500">
                                            {getMatchScoreForCriterion(match, teamId, c.id)}
                                         </td>
                                       ))}
                                       <td className={`px-6 py-6 text-right font-black text-lg ${match.ganador_id === teamId ? 'text-green-600 bg-green-50/50' : 'text-slate-400 bg-slate-50'}`}>
                                          {totalScore.toFixed(2)}
                                       </td>
                                    </tr>
                                  );
                               })}
                            </tbody>
                         </table>
                      </div>
                   </div>
                 ))
               )}
            </div>
          </div>
        )}
      </div>

      {/* Modal de Calificación Premium - Rediseñado */}
      {qualifyingMatch && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-xl animate-in fade-in duration-300">
          <div className="bg-white rounded-[3rem] shadow-[0_0_100px_rgba(0,0,0,0.3)] w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col animate-in zoom-in-95 duration-500">
            {/* Header del Modal */}
            <div className="p-12 border-b border-slate-100 relative bg-slate-50">
               <button 
                 onClick={() => setQualifyingMatch(null)}
                 className="absolute top-10 right-10 p-3 hover:bg-white hover:shadow-lg rounded-full transition-all active:scale-90"
               >
                 <XCircle className="h-8 w-8 text-slate-400" />
               </button>
               <div className="inline-flex items-center px-5 py-2 bg-indigo-600 text-white rounded-full text-[10px] font-black uppercase tracking-[0.25em] mb-6 shadow-xl shadow-indigo-100">
                  <Swords className="h-4 w-4 mr-3" /> Arbitraje Pro
               </div>
               <h3 className="text-4xl font-black text-slate-900 tracking-tight">Calificación de Enfrentamiento</h3>
               
               <div className="flex flex-col md:flex-row items-center justify-between gap-10 mt-10 p-8 bg-white rounded-3xl shadow-sm border border-slate-100">
                  <div className="flex-1 text-center md:text-right">
                     <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Equipo Local</p>
                     <h4 className="text-2xl font-black text-indigo-600 truncate">{getTeamName(qualifyingMatch.equipo_local_id)}</h4>
                  </div>
                  <div className="h-16 w-16 bg-slate-900 text-white rounded-2xl flex items-center justify-center font-black text-xs ring-8 ring-slate-100">VS</div>
                  <div className="flex-1 text-center md:text-left">
                     <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Equipo Visitante</p>
                     <h4 className="text-2xl font-black text-indigo-600 truncate">{getTeamName(qualifyingMatch.equipo_visitante_id)}</h4>
                  </div>
               </div>
            </div>

            {/* Contenido Calificaciones */}
            <div className="p-12 overflow-y-auto flex-grow custom-scrollbar space-y-16">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
                 {/* Lado Local */}
                 <div className="space-y-10">
                   <div className="flex items-center justify-between pb-4 border-b-4 border-indigo-600">
                      <div className="flex items-center gap-4">
                         <div className="h-10 w-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center font-black">L</div>
                         <h4 className="font-black text-slate-900 uppercase text-lg tracking-tight">Registro Local</h4>
                      </div>
                   </div>
                   <div className="space-y-8">
                     {tournament?.tournament_evaluation?.criterias?.map((c: any) => (
                       <div key={c.id} className="group p-6 bg-slate-50 rounded-3xl border-2 border-transparent focus-within:border-indigo-600 focus-within:bg-white transition-all shadow-sm">
                         <div className="flex justify-between items-center mb-4">
                            <label className="text-xs font-black text-slate-800 uppercase tracking-widest">{c.name}</label>
                            <span className="text-[10px] font-black bg-indigo-100 text-indigo-600 px-3 py-1 rounded-full">{(c.value * 100).toFixed(0)}% PESO</span>
                         </div>
                         <div className="relative">
                           <input 
                             type="number"
                             step="0.1"
                             min={c.min_value_qualification}
                             max={c.max_value_qualification}
                             value={qualifications.find(q => q.team_id === qualifyingMatch.equipo_local_id && q.criterio_id === c.id)?.value || 0}
                             onChange={(e) => handleQualChange(qualifyingMatch.equipo_local_id, c.id, e.target.value)}
                             className="w-full pl-0 pr-12 py-2 bg-transparent border-b-2 border-slate-200 focus:border-indigo-600 font-black text-3xl text-slate-900 transition-all outline-none"
                           />
                           <span className="absolute right-0 bottom-3 text-xs font-black text-slate-300 uppercase">Pts</span>
                         </div>
                         <div className="flex justify-between text-[9px] font-black text-slate-400 mt-4 uppercase tracking-tighter opacity-60">
                            <span>Mínimo: {c.min_value_qualification}</span>
                            <span>Máximo: {c.max_value_qualification}</span>
                         </div>
                       </div>
                     ))}
                   </div>
                 </div>

                 {/* Lado Visitante */}
                 <div className="space-y-10">
                   <div className="flex items-center justify-between pb-4 border-b-4 border-indigo-600">
                      <div className="flex items-center gap-4">
                         <div className="h-10 w-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center font-black">V</div>
                         <h4 className="font-black text-slate-900 uppercase text-lg tracking-tight">Registro Visitante</h4>
                      </div>
                   </div>
                   <div className="space-y-8">
                     {tournament?.tournament_evaluation?.criterias?.map((c: any) => (
                       <div key={c.id} className="group p-6 bg-slate-50 rounded-3xl border-2 border-transparent focus-within:border-indigo-600 focus-within:bg-white transition-all shadow-sm">
                         <div className="flex justify-between items-center mb-4">
                            <label className="text-xs font-black text-slate-800 uppercase tracking-widest">{c.name}</label>
                            <span className="text-[10px] font-black bg-indigo-100 text-indigo-600 px-3 py-1 rounded-full">{(c.value * 100).toFixed(0)}% PESO</span>
                         </div>
                         <div className="relative">
                           <input 
                             type="number"
                             step="0.1"
                             min={c.min_value_qualification}
                             max={c.max_value_qualification}
                             value={qualifications.find(q => q.team_id === qualifyingMatch.equipo_visitante_id && q.criterio_id === c.id)?.value || 0}
                             onChange={(e) => handleQualChange(qualifyingMatch.equipo_visitante_id, c.id, e.target.value)}
                             className="w-full pl-0 pr-12 py-2 bg-transparent border-b-2 border-slate-200 focus:border-indigo-600 font-black text-3xl text-slate-900 transition-all outline-none"
                           />
                           <span className="absolute right-0 bottom-3 text-xs font-black text-slate-300 uppercase">Pts</span>
                         </div>
                         <div className="flex justify-between text-[9px] font-black text-slate-400 mt-4 uppercase tracking-tighter opacity-60">
                            <span>Mínimo: {c.min_value_qualification}</span>
                            <span>Máximo: {c.max_value_qualification}</span>
                         </div>
                       </div>
                     ))}
                   </div>
                 </div>
              </div>
            </div>

            {/* Footer Modal Pro */}
            <div className="p-12 bg-slate-50 border-t border-slate-100 flex gap-6">
               <button 
                 onClick={() => setQualifyingMatch(null)}
                 className="flex-1 py-5 bg-white border-2 border-slate-200 text-slate-500 rounded-[1.5rem] font-black text-xs uppercase tracking-widest hover:bg-slate-100 transition-all shadow-sm"
               >
                 ABORTAR CALIFICACIÓN
               </button>
               <button 
                 onClick={submitQualifications}
                 disabled={isSubmitting}
                 className="flex-[2] py-5 bg-slate-900 text-white rounded-[1.5rem] font-black text-xs uppercase tracking-[0.25em] hover:bg-indigo-600 shadow-2xl shadow-slate-300 hover:shadow-indigo-100 transition-all flex items-center justify-center gap-4"
               >
                 {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin" /> : (
                   <>
                     <CheckCircle2 className="h-5 w-5" /> VALIDAR Y FINALIZAR PARTIDA
                   </>
                 )}
               </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
