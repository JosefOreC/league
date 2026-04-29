import { Plus, Search, Trophy, MoreHorizontal, Calendar, Users } from "lucide-react";
import { Link } from "react-router";

const torneos = [
  {
    id: 1,
    nombre: "Torneo Regional Huancayo 2026",
    estado: "En curso",
    fecha: "15 Abril - 20 Abril",
    equipos: 45,
    categoria: "Secundaria",
  },
  {
    id: 2,
    nombre: "Liga de Robótica Escolar",
    estado: "Próximo",
    fecha: "01 Mayo - 10 Mayo",
    equipos: 32,
    categoria: "Primaria",
  },
  {
    id: 3,
    nombre: "Desafío Andino de Innovación",
    estado: "Finalizado",
    fecha: "10 Enero - 15 Enero",
    equipos: 60,
    categoria: "Universitario",
  },
];

export function TournamentsList() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Torneos
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Gestiona todos los torneos de robótica de la institución.
          </p>
        </div>
        <Link
          to="/dashboard/torneos/nuevo"
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm"
        >
          <Plus className="mr-2 h-4 w-4" />
          Crear torneo
        </Link>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative w-full sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar torneos..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <select className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1 sm:flex-none">
            <option>Todos los estados</option>
            <option>En curso</option>
            <option>Próximo</option>
            <option>Finalizado</option>
          </select>
          <select className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1 sm:flex-none">
            <option>Todas las categorías</option>
            <option>Primaria</option>
            <option>Secundaria</option>
          </select>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-500">
            <thead className="text-xs text-slate-700 uppercase bg-slate-50 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-6 py-4 font-semibold">Torneo</th>
                <th scope="col" className="px-6 py-4 font-semibold">Estado</th>
                <th scope="col" className="px-6 py-4 font-semibold">Fecha</th>
                <th scope="col" className="px-6 py-4 font-semibold">Equipos</th>
                <th scope="col" className="px-6 py-4 font-semibold text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {torneos.map((torneo) => (
                <tr key={torneo.id} className="bg-white border-b border-slate-100 hover:bg-slate-50 last:border-0">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                        <Trophy className="h-5 w-5" />
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900">{torneo.nombre}</div>
                        <div className="text-xs text-slate-500 mt-0.5">{torneo.categoria}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border
                      ${torneo.estado === 'En curso' ? 'bg-green-50 text-green-700 border-green-200' : 
                        torneo.estado === 'Próximo' ? 'bg-blue-50 text-blue-700 border-blue-200' : 
                        'bg-slate-100 text-slate-700 border-slate-200'}`}
                    >
                      {torneo.estado}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center text-slate-600">
                      <Calendar className="mr-2 h-4 w-4 text-slate-400" />
                      {torneo.fecha}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center font-medium text-slate-900">
                      <Users className="mr-2 h-4 w-4 text-slate-400" />
                      {torneo.equipos}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-slate-400 hover:text-blue-600 transition-colors p-2 rounded-md hover:bg-blue-50">
                      <MoreHorizontal className="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
