import { Download, FileText, FileSpreadsheet, History, Filter, Search, BarChart3, Trophy } from "lucide-react";

const historialData = [
  { id: "TRH-25", nombre: "Torneo Regional Huancayo 2025", fecha: "Abril 2025", equipos: 40, ganador: "AndesBot", categoria: "Secundaria" },
  { id: "LRE-25", nombre: "Liga de Robótica Escolar 2025", fecha: "Junio 2025", equipos: 28, ganador: "CyberMentes", categoria: "Primaria" },
  { id: "DAI-24", nombre: "Desafío Andino de Innovación 2024", fecha: "Noviembre 2024", equipos: 55, ganador: "RoboKids Alpha", categoria: "Universitario" },
  { id: "TRH-24", nombre: "Torneo Regional Huancayo 2024", fecha: "Abril 2024", equipos: 35, ganador: "InnovaBots", categoria: "Secundaria" },
];

export function Reports() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
            <BarChart3 className="mr-2 h-6 w-6 text-blue-600" />
            Reportes e Historial
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Visualiza el historial de torneos y exporta los resultados oficiales.
          </p>
        </div>
        <div className="flex space-x-3">
          <button className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 h-10 px-4 py-2 shadow-sm">
            <FileText className="mr-2 h-4 w-4" />
            Exportar PDF
          </button>
          <button className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-500 bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 h-10 px-4 py-2 shadow-sm">
            <FileSpreadsheet className="mr-2 h-4 w-4" />
            Exportar Excel
          </button>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
          <Filter className="h-5 w-5 mr-2 text-slate-500" /> Filtros de generación
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-700 uppercase tracking-wide">Torneo</label>
            <select className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>Todos los torneos</option>
              <option>Torneo Regional Huancayo 2026</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-700 uppercase tracking-wide">Categoría</label>
            <select className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>Todas las categorías</option>
              <option>Primaria</option>
              <option>Secundaria</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-700 uppercase tracking-wide">Año</label>
            <select className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>2026</option>
              <option>2025</option>
              <option>2024</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-700 uppercase tracking-wide">Tipo de reporte</label>
            <select className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>Resultados Finales</option>
              <option>Estadísticas de Participación</option>
              <option>Rendimiento por Equipo</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50">
          <h2 className="text-lg font-semibold text-slate-900 flex items-center">
            <History className="h-5 w-5 mr-2 text-slate-600" />
            Historial de torneos
          </h2>
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar en el historial..."
              className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-slate-600">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50/50 border-b border-slate-100">
              <tr>
                <th scope="col" className="px-6 py-4 font-semibold w-24">ID</th>
                <th scope="col" className="px-6 py-4 font-semibold">Nombre del Torneo</th>
                <th scope="col" className="px-6 py-4 font-semibold">Fecha</th>
                <th scope="col" className="px-6 py-4 font-semibold">Categoría</th>
                <th scope="col" className="px-6 py-4 font-semibold text-center">Equipos</th>
                <th scope="col" className="px-6 py-4 font-semibold">Ganador</th>
                <th scope="col" className="px-6 py-4 font-semibold text-right">Acción</th>
              </tr>
            </thead>
            <tbody>
              {historialData.map((row) => (
                <tr key={row.id} className="bg-white border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-slate-500">{row.id}</td>
                  <td className="px-6 py-4 font-bold text-slate-900">{row.nombre}</td>
                  <td className="px-6 py-4 text-slate-600">{row.fecha}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs font-medium">
                      {row.categoria}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center font-medium">{row.equipos}</td>
                  <td className="px-6 py-4 text-blue-600 font-semibold flex items-center">
                    <Trophy className="w-3 h-3 mr-1 text-yellow-500" />
                    {row.ganador}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-blue-600 hover:text-blue-800 transition-colors p-2 rounded-md hover:bg-blue-50 inline-flex items-center text-xs font-semibold">
                      <Download className="w-4 h-4 mr-1" />
                      Datos
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
