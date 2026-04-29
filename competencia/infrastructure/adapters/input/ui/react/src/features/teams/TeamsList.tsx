import { useState } from "react";
import { Plus, Search, Users, Building, Bot, MoreHorizontal, User } from "lucide-react";

const initialEquipos = [
  { id: 1, nombre: "RoboKids Alpha", institucion: "I.E. Santa Isabel", integrantes: 4, categoria: "Secundaria" },
  { id: 2, nombre: "CyberMentes", institucion: "Colegio Andino", integrantes: 3, categoria: "Primaria" },
  { id: 3, nombre: "InnovaBots", institucion: "I.E. Politécnico Regional", integrantes: 5, categoria: "Secundaria" },
  { id: 4, nombre: "TechSchool Huancayo", institucion: "Colegio Claretiano", integrantes: 4, categoria: "Primaria" },
];

export function TeamsList() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Equipos
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Administra los equipos participantes y sus integrantes.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm"
        >
          <Plus className="mr-2 h-4 w-4" />
          Registrar equipo
        </button>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative w-full sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar por equipo o institución..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {initialEquipos.map((equipo) => (
          <div key={equipo.id} className="bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden flex flex-col">
            <div className="p-5 flex-1">
              <div className="flex justify-between items-start mb-4">
                <div className="h-12 w-12 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
                  <Bot className="h-6 w-6" />
                </div>
                <button className="text-slate-400 hover:text-slate-600 transition-colors p-1">
                  <MoreHorizontal className="h-5 w-5" />
                </button>
              </div>
              
              <h3 className="font-bold text-lg text-slate-900 leading-tight mb-1">{equipo.nombre}</h3>
              <div className="flex items-center text-sm text-slate-500 mb-4">
                <Building className="h-3.5 w-3.5 mr-1.5 shrink-0" />
                <span className="truncate">{equipo.institucion}</span>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex items-center text-sm font-medium text-slate-700 bg-slate-100 px-2.5 py-1 rounded-md">
                  <Users className="h-4 w-4 mr-1.5 text-slate-500" />
                  {equipo.integrantes}
                </div>
                <span className="text-xs font-medium px-2 py-1 bg-purple-50 text-purple-700 border border-purple-100 rounded-md">
                  {equipo.categoria}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-900">Registrar equipo</h2>
              <button 
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                &times;
              </button>
            </div>
            
            <form className="p-6 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Nombre del equipo</label>
                <input
                  type="text"
                  required
                  className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej. RoboMinds Alpha"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Institución</label>
                <select className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>I.E. Santa Isabel</option>
                  <option>Colegio Andino</option>
                  <option>Colegio Claretiano</option>
                  <option>Otra institución...</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700 flex justify-between">
                  <span>Integrantes</span>
                  <button type="button" className="text-xs text-blue-600 hover:text-blue-700 font-medium">+ Añadir integrante</button>
                </label>
                
                <div className="space-y-3">
                  {[1, 2].map((i) => (
                    <div key={i} className="flex gap-2">
                      <div className="relative flex-1">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                        <input
                          type="text"
                          className="flex h-10 w-full rounded-md border border-slate-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={`Nombre del integrante ${i}`}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 flex gap-3">
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
                  Guardar Equipo
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
