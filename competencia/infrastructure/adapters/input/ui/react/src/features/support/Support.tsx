import { LifeBuoy, MessageSquare, Mail, HelpCircle, FileText, Send, ChevronRight } from "lucide-react";

export function Support() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
          <LifeBuoy className="mr-3 h-7 w-7 text-blue-600" />
          Soporte y Ayuda
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Encuentra respuestas a preguntas frecuentes o contacta con el equipo técnico.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* FAQ Section */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-6 flex items-center">
              <HelpCircle className="h-5 w-5 mr-2 text-slate-500" />
              Preguntas Frecuentes
            </h2>
            
            <div className="space-y-4">
              {[
                { q: "¿Cómo generar emparejamientos automáticos?", a: "Dirígete a la sección de Competencias, selecciona el torneo activo y haz clic en el botón superior 'Generar emparejamientos'. El sistema utilizará la IA para distribuir a los equipos de manera equitativa." },
                { q: "¿Puedo modificar un resultado ya registrado?", a: "Sí, los organizadores principales y administradores pueden editar resultados en la pestaña 'Historial de Partidas' dentro de la vista de Resultados, hasta antes de cerrar la ronda." },
                { q: "¿Qué significan las alertas de IA?", a: "La Inteligencia Artificial analiza las reglas y el diseño de los robots registrados para alertar sobre posibles riesgos de seguridad o desequilibrios en la dificultad de la competencia." },
                { q: "¿Cómo exportar los reportes finales al MINEDU?", a: "En la sección 'Reportes', selecciona el torneo finalizado y usa el botón 'Exportar PDF'. El sistema generará el formato estándar requerido por las autoridades educativas locales." }
              ].map((faq, i) => (
                <details key={i} className="group bg-slate-50 rounded-lg p-4 cursor-pointer [&_summary::-webkit-details-marker]:hidden border border-slate-200 hover:border-blue-300 transition-colors">
                  <summary className="flex items-center justify-between font-medium text-slate-900 text-sm list-none">
                    <span>{faq.q}</span>
                    <span className="transition group-open:rotate-90">
                      <ChevronRight className="h-4 w-4 text-slate-400" />
                    </span>
                  </summary>
                  <p className="text-slate-600 mt-3 text-sm leading-relaxed border-t border-slate-200 pt-3">
                    {faq.a}
                  </p>
                </details>
              ))}
            </div>
            
            <button className="mt-6 text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors flex items-center">
              <FileText className="w-4 h-4 mr-1.5" />
              Ver manual completo de usuario
            </button>
          </div>
        </div>

        {/* Contact Form */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 relative overflow-hidden">
            <div className="absolute -right-6 -top-6 opacity-5">
              <MessageSquare className="w-32 h-32 text-blue-900" />
            </div>
            
            <h2 className="text-lg font-semibold text-slate-900 mb-1 relative z-10">Enviar consulta</h2>
            <p className="text-xs text-slate-500 mb-6 relative z-10">
              ¿No encuentras lo que buscas? Escríbenos.
            </p>
            
            <form className="space-y-4 relative z-10">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">Asunto</label>
                <select className="flex h-10 w-full rounded-md border border-slate-300 bg-slate-50 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Problema técnico</option>
                  <option>Duda sobre emparejamientos</option>
                  <option>Sugerencia de mejora</option>
                  <option>Otro</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-700 uppercase tracking-wide">Mensaje</label>
                <textarea
                  className="flex w-full rounded-md border border-slate-300 bg-slate-50 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none h-32"
                  placeholder="Describe tu consulta con el mayor detalle posible..."
                  required
                ></textarea>
              </div>

              <div className="space-y-2">
                <label className="flex items-center text-xs text-slate-600 cursor-pointer">
                  <input type="checkbox" className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 mr-2" />
                  Adjuntar captura de pantalla actual
                </label>
              </div>

              <button
                type="button"
                className="w-full inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm mt-2"
              >
                <Send className="mr-2 h-4 w-4" />
                Enviar mensaje
              </button>
            </form>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-xl shadow-sm p-5 text-center">
            <Mail className="h-6 w-6 text-slate-400 mx-auto mb-2" />
            <h3 className="font-semibold text-slate-900 text-sm mb-1">Soporte Directo</h3>
            <p className="text-xs text-slate-500 mb-3">Tiempo de respuesta: ~2 horas</p>
            <a href="mailto:soporte@zoidsleague.com" className="text-blue-600 hover:text-blue-800 text-sm font-medium hover:underline">
              soporte@zoidsleague.com
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
