import { CalendarDays, ChevronLeft, ChevronRight, Clock, MapPin, Users } from "lucide-react";

export function CalendarView() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Calendario de competencias
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Visualiza los torneos y eventos próximos en la región.
          </p>
        </div>
        <div className="flex items-center space-x-2 bg-white border border-slate-200 rounded-lg p-1 shadow-sm">
          <button className="p-1 hover:bg-slate-100 rounded-md transition-colors text-slate-500">
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span className="text-sm font-semibold text-slate-900 min-w-[100px] text-center">Abril 2026</span>
          <button className="p-1 hover:bg-slate-100 rounded-md transition-colors text-slate-500">
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Calendar Grid (Mocked Visual) */}
        <div className="lg:col-span-3 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="grid grid-cols-7 border-b border-slate-200 bg-slate-50">
            {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'].map(day => (
              <div key={day} className="py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {day}
              </div>
            ))}
          </div>
          <div className="grid grid-cols-7 grid-rows-5 h-[600px] bg-slate-200 gap-[1px]">
            {Array.from({ length: 35 }).map((_, i) => {
              const date = i - 2; // Offset for starting day
              const isCurrentMonth = date > 0 && date <= 30;
              const hasEvent1 = date >= 15 && date <= 17;
              const hasEvent2 = date === 24;

              return (
                <div key={i} className={`bg-white p-2 flex flex-col ${!isCurrentMonth ? 'text-slate-400 bg-slate-50/50' : 'text-slate-900'}`}>
                  <span className={`text-sm font-medium w-7 h-7 flex items-center justify-center rounded-full mb-1 ${date === 16 ? 'bg-blue-600 text-white' : ''}`}>
                    {date > 0 && date <= 30 ? date : date <= 0 ? 31 + date : date - 30}
                  </span>
                  
                  <div className="flex-1 overflow-y-auto space-y-1">
                    {hasEvent1 && (
                      <div className="text-xs px-1.5 py-1 bg-blue-100 text-blue-700 rounded truncate border border-blue-200 font-medium">
                        Torneo Regional
                      </div>
                    )}
                    {date === 15 && (
                      <div className="text-[10px] px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded truncate flex items-center">
                        <Clock className="w-3 h-3 mr-1" /> 08:00 - Registro
                      </div>
                    )}
                    {hasEvent2 && (
                      <div className="text-xs px-1.5 py-1 bg-purple-100 text-purple-700 rounded truncate border border-purple-200 font-medium">
                        Taller Robótica
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Event List Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5">
            <h3 className="font-bold text-slate-900 mb-4 flex items-center">
              <CalendarDays className="h-5 w-5 mr-2 text-blue-600" />
              Próximos Eventos
            </h3>
            
            <div className="space-y-4">
              <div className="relative pl-4 border-l-2 border-blue-500 pb-4">
                <div className="absolute w-2 h-2 bg-blue-500 rounded-full -left-[5px] top-1.5"></div>
                <p className="text-xs font-bold text-blue-600 mb-1 uppercase tracking-wider">15 - 17 Abril</p>
                <h4 className="text-sm font-bold text-slate-900">Torneo Regional Huancayo</h4>
                <div className="mt-2 space-y-1">
                  <div className="flex items-center text-xs text-slate-500">
                    <MapPin className="w-3 h-3 mr-1.5 shrink-0 text-slate-400" />
                    Coliseo Wanka
                  </div>
                  <div className="flex items-center text-xs text-slate-500">
                    <Users className="w-3 h-3 mr-1.5 shrink-0 text-slate-400" />
                    45 equipos
                  </div>
                </div>
              </div>

              <div className="relative pl-4 border-l-2 border-purple-500 pb-4">
                <div className="absolute w-2 h-2 bg-purple-500 rounded-full -left-[5px] top-1.5"></div>
                <p className="text-xs font-bold text-purple-600 mb-1 uppercase tracking-wider">24 Abril</p>
                <h4 className="text-sm font-bold text-slate-900">Taller de Robótica Avanzada</h4>
                <div className="mt-2 space-y-1">
                  <div className="flex items-center text-xs text-slate-500">
                    <MapPin className="w-3 h-3 mr-1.5 shrink-0 text-slate-400" />
                    Auditorio UCCI
                  </div>
                  <div className="flex items-center text-xs text-slate-500">
                    <Clock className="w-3 h-3 mr-1.5 shrink-0 text-slate-400" />
                    10:00 AM - 13:00 PM
                  </div>
                </div>
              </div>
              
              <div className="relative pl-4 border-l-2 border-slate-300">
                <div className="absolute w-2 h-2 bg-slate-300 rounded-full -left-[5px] top-1.5"></div>
                <p className="text-xs font-bold text-slate-500 mb-1 uppercase tracking-wider">01 - 10 Mayo</p>
                <h4 className="text-sm font-bold text-slate-900">Liga Escolar Fase 1</h4>
                <div className="mt-2 space-y-1">
                  <div className="flex items-center text-xs text-slate-500">
                    <MapPin className="w-3 h-3 mr-1.5 shrink-0 text-slate-400" />
                    Multiples Sedes
                  </div>
                </div>
              </div>
            </div>
            
            <button className="w-full mt-6 bg-slate-50 text-slate-700 border border-slate-200 hover:bg-slate-100 font-medium py-2 rounded-lg text-sm transition-colors">
              Añadir evento
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
