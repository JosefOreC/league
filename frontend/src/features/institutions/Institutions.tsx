import { Building2, Plus, Search, MapPin, Phone, Mail, MoreVertical, User } from "lucide-react";
import { useState } from "react";

const institucionesData = [
  { id: 1, nombre: "I.E. Santa Isabel", tipo: "Pública", equipos: 12, ciudad: "Huancayo", contacto: "director@santaisabel.edu.pe" },
  { id: 2, nombre: "Colegio Andino", tipo: "Privada", equipos: 8, ciudad: "Huancayo", contacto: "info@colegioandino.edu.pe" },
  { id: 3, nombre: "I.E. Politécnico Regional", tipo: "Pública", equipos: 15, ciudad: "El Tambo", contacto: "contacto@politecnico.edu.pe" },
  { id: 4, nombre: "Colegio Claretiano", tipo: "Privada", equipos: 5, ciudad: "Huancayo", contacto: "sec@claretiano.edu.pe" },
  { id: 5, nombre: "I.E. Nuestra Señora del Rosario", tipo: "Pública", equipos: 4, ciudad: "Huancayo", contacto: "rosario@minedu.gob.pe" },
];

export function Institutions() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
            <Building2 className="mr-3 h-7 w-7 text-indigo-600" />
            Instituciones educativas
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Directorio de colegios y universidades que participan en los torneos.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 bg-indigo-600 text-white hover:bg-indigo-700 h-10 px-4 py-2 shadow-sm"
        >
          <Plus className="mr-2 h-4 w-4" />
          Registrar institución
        </button>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative w-full sm:max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar por nombre, ciudad o tipo..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
        <div className="flex gap-2 w-full sm:w-auto">
          <select className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex-1 sm:flex-none">
            <option>Todos los tipos</option>
            <option>Pública</option>
            <option>Privada</option>
          </select>
          <select className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex-1 sm:flex-none">
            <option>Todas las ciudades</option>
            <option>Huancayo</option>
            <option>El Tambo</option>
            <option>Chilca</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {institucionesData.map((inst) => (
          <div key={inst.id} className="bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden flex flex-col">
            <div className="p-5 flex-1 relative">
              <button className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 transition-colors p-1">
                <MoreVertical className="h-5 w-5" />
              </button>
              
              <div className="h-12 w-12 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600 mb-4 border border-indigo-100">
                <Building2 className="h-6 w-6" />
              </div>
              
              <h3 className="font-bold text-lg text-slate-900 leading-tight mb-2 pr-6">{inst.nombre}</h3>
              
              <div className="flex items-center gap-2 mb-4">
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                  inst.tipo === 'Pública' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-amber-100 text-amber-800 border border-amber-200'
                }`}>
                  {inst.tipo}
                </span>
                <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200 flex items-center">
                  {inst.equipos} equipos históricos
                </span>
              </div>

              <div className="space-y-2 mt-4 pt-4 border-t border-slate-100">
                <div className="flex items-center text-sm text-slate-600">
                  <MapPin className="h-4 w-4 mr-2 shrink-0 text-slate-400" />
                  <span className="truncate">{inst.ciudad}</span>
                </div>
                <div className="flex items-center text-sm text-slate-600">
                  <Mail className="h-4 w-4 mr-2 shrink-0 text-slate-400" />
                  <a href={`mailto:${inst.contacto}`} className="truncate hover:text-indigo-600 hover:underline">{inst.contacto}</a>
                </div>
              </div>
            </div>
            <div className="bg-slate-50 border-t border-slate-100 px-5 py-3 flex justify-between items-center">
              <span className="text-xs font-medium text-slate-500">Registrada: 2024</span>
              <button className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors">
                Ver detalles &rarr;
              </button>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-indigo-50/50">
              <h2 className="text-lg font-bold text-slate-900 flex items-center">
                <Building2 className="mr-2 h-5 w-5 text-indigo-600" /> Registrar institución
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
                <label className="text-sm font-medium text-slate-700">Nombre de la institución <span className="text-red-500">*</span></label>
                <input
                  type="text"
                  required
                  className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Ej. I.E. Santa Isabel"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Tipo <span className="text-red-500">*</span></label>
                  <select required className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="">Seleccionar...</option>
                    <option value="publica">Pública</option>
                    <option value="privada">Privada</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Ciudad / Distrito <span className="text-red-500">*</span></label>
                  <select required className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="huancayo">Huancayo</option>
                    <option value="tambo">El Tambo</option>
                    <option value="chilca">Chilca</option>
                    <option value="otro">Otro</option>
                  </select>
                </div>
              </div>

              <div className="space-y-4 pt-2">
                <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">Datos de Contacto</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-slate-700 flex items-center">
                      <User className="h-3 w-3 mr-1" /> Representante
                    </label>
                    <input
                      type="text"
                      className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="Nombre completo"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-slate-700 flex items-center">
                      <Phone className="h-3 w-3 mr-1" /> Teléfono
                    </label>
                    <input
                      type="tel"
                      className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="999 999 999"
                    />
                  </div>
                  <div className="space-y-2 col-span-2">
                    <label className="text-xs font-medium text-slate-700 flex items-center">
                      <Mail className="h-3 w-3 mr-1" /> Correo electrónico
                    </label>
                    <input
                      type="email"
                      className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="contacto@institucion.edu.pe"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4 flex gap-3 border-t border-slate-100 mt-6">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 justify-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  onClick={(e) => { e.preventDefault(); setShowModal(false); }}
                  className="flex-1 justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm transition-colors"
                >
                  Guardar Institución
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
