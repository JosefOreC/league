import { BrainCircuit, Check, ShieldAlert, Sparkles, TrendingUp, Cpu } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const performanceData = [
  { name: "Semana 1", victorias: 12, derrotas: 2 },
  { name: "Semana 2", victorias: 15, derrotas: 3 },
  { name: "Semana 3", victorias: 18, derrotas: 5 },
  { name: "Semana 4", victorias: 20, derrotas: 4 },
];

export function AIRecommendations() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
          <BrainCircuit className="h-6 w-6 text-purple-600 mr-2" />
          Inteligencia Artificial
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Asistente inteligente para optimizar torneos basado en el rendimiento histórico de los equipos.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Recomendación Principal */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-purple-200 rounded-2xl shadow-sm overflow-hidden relative">
            <div className="absolute top-0 left-0 w-2 h-full bg-purple-500"></div>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  <h2 className="text-lg font-semibold text-slate-900">Recomendación de dificultad</h2>
                </div>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                  <TrendingUp className="w-3 h-3 mr-1" /> Confianza: 85%
                </span>
              </div>
              
              <div className="mt-4 flex flex-col sm:flex-row gap-6 items-start">
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-purple-700 mb-2">
                    Nivel sugerido: Intermedio
                  </h3>
                  <p className="text-slate-600 text-sm mb-4 leading-relaxed">
                    Basado en los resultados de los últimos 3 meses, el 70% de los equipos inscritos de la región Junín han dominado los desafíos básicos. Sugerimos incrementar la dificultad incorporando obstáculos dinámicos en la pista de seguidores de línea para mantener el nivel competitivo.
                  </p>
                  
                  <div className="space-y-3 mb-6">
                    <h4 className="font-medium text-slate-900 text-sm">Ajustes propuestos:</h4>
                    <ul className="space-y-2">
                      <li className="flex items-start text-sm text-slate-600">
                        <Check className="h-4 w-4 text-green-500 mr-2 shrink-0 mt-0.5" />
                        Añadir 2 intersecciones en ángulo recto a la pista.
                      </li>
                      <li className="flex items-start text-sm text-slate-600">
                        <Check className="h-4 w-4 text-green-500 mr-2 shrink-0 mt-0.5" />
                        Reducir el tiempo de clasificación de 3 min a 2 min.
                      </li>
                      <li className="flex items-start text-sm text-slate-600">
                        <Check className="h-4 w-4 text-green-500 mr-2 shrink-0 mt-0.5" />
                        Peso máximo del robot reducido a 1.2 kg.
                      </li>
                    </ul>
                  </div>

                  <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium px-5 py-2.5 rounded-lg text-sm transition-colors shadow-sm w-full sm:w-auto">
                    Aplicar recomendación
                  </button>
                </div>
                
                <div className="w-full sm:w-64 bg-slate-50 p-4 rounded-xl border border-slate-100 shrink-0">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
                    Métricas de Análisis
                  </h4>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-600">Tasa de finalización</span>
                        <span className="font-bold text-slate-900">92%</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-1.5">
                        <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '92%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-600">Tiempo prom. resolución</span>
                        <span className="font-bold text-slate-900">1m 15s</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-1.5">
                        <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: '45%' }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-600">Precisión de sensores</span>
                        <span className="font-bold text-slate-900">Elevada</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-1.5">
                        <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: '88%' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
            <h3 className="font-semibold text-slate-900 mb-6 flex items-center">
              <Cpu className="h-5 w-5 mr-2 text-slate-500" />
              Rendimiento Histórico de Categoría "Secundaria"
            </h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={performanceData} id="ai-performance-chart">
                  <defs key="defs">
                    <linearGradient key="colorVic" id="colorVictorias" x1="0" y1="0" x2="0" y2="1">
                      <stop key="v1" offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop key="v2" offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient key="colorDer" id="colorDerrotas" x1="0" y1="0" x2="0" y2="1">
                      <stop key="d1" offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                      <stop key="d2" offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid key="grid" strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis key="xaxis" dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis key="yaxis" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip key="tooltip" />
                  <Area key="areaVic" type="monotone" dataKey="victorias" stroke="#10b981" fillOpacity={1} fill="url(#colorVictorias)" strokeWidth={2} name="Completaron el reto" />
                  <Area key="areaDer" type="monotone" dataKey="derrotas" stroke="#ef4444" fillOpacity={1} fill="url(#colorDerrotas)" strokeWidth={2} name="No completaron" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Alertas y Otras Sugerencias */}
        <div className="space-y-6">
          <div className="bg-white border border-orange-200 rounded-2xl shadow-sm p-6">
            <div className="flex items-center space-x-2 mb-4">
              <ShieldAlert className="h-5 w-5 text-orange-500" />
              <h3 className="font-semibold text-slate-900">Alerta de Seguridad IA</h3>
            </div>
            <p className="text-sm text-slate-600 mb-4">
              Hemos detectado un incremento en diseños de robots con materiales reflectantes que podrían interferir con sensores infrarrojos estándar en la categoría de Seguidores de Línea.
            </p>
            <div className="bg-orange-50 border border-orange-100 rounded-lg p-3">
              <h4 className="text-xs font-semibold text-orange-800 mb-1">Acción sugerida:</h4>
              <p className="text-xs text-orange-700">Actualizar el reglamento (Art. 4.2) para prohibir acabados espejados o cromados en el chasis inferior.</p>
            </div>
            <button className="mt-4 w-full bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 font-medium px-4 py-2 rounded-lg text-sm transition-colors shadow-sm">
              Revisar Reglamento
            </button>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Otras recomendaciones</h3>
            
            <div className="space-y-4">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <div className="flex justify-between items-start mb-1">
                  <h4 className="text-sm font-medium text-slate-900">Formato de llaves</h4>
                  <span className="text-[10px] font-bold bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Alta</span>
                </div>
                <p className="text-xs text-slate-500 mb-2">
                  Usar formato de doble eliminación debido al número atípico de 23 equipos.
                </p>
                <button className="text-xs font-medium text-blue-600 hover:text-blue-800">
                  Ver estructura sugerida &rarr;
                </button>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                <div className="flex justify-between items-start mb-1">
                  <h4 className="text-sm font-medium text-slate-900">Horarios</h4>
                  <span className="text-[10px] font-bold bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full">Media</span>
                </div>
                <p className="text-xs text-slate-500 mb-2">
                  Asignar bloques de 15 min de inspección técnica para evitar retrasos matutinos.
                </p>
                <button className="text-xs font-medium text-blue-600 hover:text-blue-800">
                  Ajustar calendario &rarr;
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
