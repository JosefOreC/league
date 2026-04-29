import { Activity, PlusCircle, Trophy, Medal, Star, Timer } from "lucide-react";
import { useState } from "react";

const rankingData = [
  { id: 1, equipo: "RoboKids Alpha", pts: 450, pg: 4, pe: 1, pp: 0, time: "2m 10s", trend: "up" },
  { id: 2, equipo: "AndesBot", pts: 420, pg: 4, pe: 0, pp: 1, time: "2m 25s", trend: "same" },
  { id: 3, equipo: "Pioneros", pts: 380, pg: 3, pe: 1, pp: 1, time: "2m 40s", trend: "up" },
  { id: 4, equipo: "CyberMentes", pts: 350, pg: 3, pe: 0, pp: 2, time: "3m 05s", trend: "down" },
  { id: 5, equipo: "InnovaBots", pts: 310, pg: 2, pe: 2, pp: 1, time: "3m 15s", trend: "same" },
];

export function Results() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
            Resultados
            <span className="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
              <Activity className="w-3 h-3 mr-1 animate-pulse" /> En vivo
            </span>
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Ranking en tiempo real y registro de puntajes de la competencia actual.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm"
        >
          <PlusCircle className="mr-2 h-4 w-4" />
          Registrar puntaje
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-slate-900 flex items-center">
              <Trophy className="h-5 w-5 mr-2 text-yellow-500" />
              Tabla de posiciones
            </h2>
            <div className="flex gap-2">
              <select className="text-sm border-slate-200 rounded-md text-slate-600 focus:ring-blue-500 focus:border-blue-500 bg-slate-50">
                <option>Categoría Secundaria</option>
                <option>Categoría Primaria</option>
              </select>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-slate-600">
              <thead className="text-xs text-slate-500 uppercase bg-slate-50/50 border-b border-slate-100">
                <tr>
                  <th scope="col" className="px-6 py-4 font-semibold w-16">Pos</th>
                  <th scope="col" className="px-6 py-4 font-semibold">Equipo</th>
                  <th scope="col" className="px-6 py-4 font-semibold text-center" title="Puntos">Pts</th>
                  <th scope="col" className="px-6 py-4 font-semibold text-center" title="Partidos Ganados">PG</th>
                  <th scope="col" className="px-6 py-4 font-semibold text-center" title="Partidos Empatados">PE</th>
                  <th scope="col" className="px-6 py-4 font-semibold text-center" title="Partidos Perdidos">PP</th>
                  <th scope="col" className="px-6 py-4 font-semibold text-center" title="Mejor Tiempo">Mejor Tiempo</th>
                </tr>
              </thead>
              <tbody>
                {rankingData.map((row, i) => (
                  <tr key={row.id} className="bg-white border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4 text-center font-semibold">
                      {i === 0 ? <Medal className="h-6 w-6 text-yellow-500 mx-auto" /> : 
                       i === 1 ? <Medal className="h-6 w-6 text-slate-400 mx-auto" /> : 
                       i === 2 ? <Medal className="h-6 w-6 text-amber-600 mx-auto" /> : 
                       <span className="text-slate-400">{i + 1}</span>}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-900 flex items-center">
                      {row.equipo}
                      {row.trend === 'up' && <span className="ml-2 text-green-500 text-xs">▲</span>}
                      {row.trend === 'down' && <span className="ml-2 text-red-500 text-xs">▼</span>}
                    </td>
                    <td className="px-6 py-4 text-center font-bold text-blue-600">{row.pts}</td>
                    <td className="px-6 py-4 text-center text-slate-500">{row.pg}</td>
                    <td className="px-6 py-4 text-center text-slate-500">{row.pe}</td>
                    <td className="px-6 py-4 text-center text-slate-500">{row.pp}</td>
                    <td className="px-6 py-4 text-center font-mono text-xs text-slate-500 flex justify-center items-center">
                      <Timer className="h-3 w-3 mr-1 text-slate-400" />
                      {row.time}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-900 rounded-xl p-6 shadow-sm text-white relative overflow-hidden">
            <div className="absolute -right-4 -top-4 opacity-10">
              <Trophy className="w-32 h-32" />
            </div>
            <h3 className="font-semibold text-slate-200 mb-2 flex items-center relative z-10">
              <Star className="h-4 w-4 mr-2 text-yellow-400" /> MVP Actual
            </h3>
            <div className="text-2xl font-bold mb-1 relative z-10">RoboKids Alpha</div>
            <p className="text-xs text-slate-400 mb-4 relative z-10">I.E. Santa Isabel</p>
            <div className="flex gap-2 flex-wrap relative z-10">
              <span className="text-[10px] uppercase font-bold px-2 py-1 bg-slate-800 rounded-md text-green-400 border border-slate-700">Invicto</span>
              <span className="text-[10px] uppercase font-bold px-2 py-1 bg-slate-800 rounded-md text-blue-400 border border-slate-700">Récord Tiempo</span>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">
            <h3 className="font-semibold text-slate-900 mb-4 text-sm uppercase tracking-wider">Últimos registros</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center text-sm">
                <div>
                  <div className="font-medium text-slate-900">AndesBot</div>
                  <div className="text-xs text-slate-500">Ronda 4 - Pista B</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-green-600">+90 pts</div>
                  <div className="text-xs text-slate-400">Hace 2 min</div>
                </div>
              </div>
              <div className="border-t border-slate-100"></div>
              <div className="flex justify-between items-center text-sm">
                <div>
                  <div className="font-medium text-slate-900">CyberMentes</div>
                  <div className="text-xs text-slate-500">Ronda 4 - Pista A</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-green-600">+45 pts</div>
                  <div className="text-xs text-slate-400">Hace 5 min</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
              <h2 className="text-lg font-bold text-slate-900 flex items-center">
                <PlusCircle className="mr-2 h-5 w-5 text-blue-600" /> Registrar puntaje
              </h2>
              <button 
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                &times;
              </button>
            </div>
            
            <form className="p-6 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Equipo</label>
                <select className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Seleccionar equipo...</option>
                  <option>RoboKids Alpha</option>
                  <option>AndesBot</option>
                  <option>Pioneros</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Ronda / Fase</label>
                  <select className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option>Cuartos de Final</option>
                    <option>Semifinal</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Pista</label>
                  <select className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option>Pista A</option>
                    <option>Pista B</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Puntos Obtenidos</label>
                  <input
                    type="number"
                    className="flex h-12 text-lg font-bold text-center w-full rounded-md border border-blue-300 bg-blue-50 px-3 py-2 text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Tiempo (mm:ss)</label>
                  <input
                    type="text"
                    className="flex h-12 text-lg font-mono text-center w-full rounded-md border border-slate-300 px-3 py-2 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="00:00"
                  />
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <label className="text-sm font-medium text-slate-700">Observaciones del Juez (Opcional)</label>
                <textarea
                  className="flex w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none h-20"
                  placeholder="Penalizaciones, faltas, etc."
                ></textarea>
              </div>

              <div className="pt-4 flex gap-3 border-t border-slate-100 mt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 justify-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
                >
                  Guardar Resultado
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
