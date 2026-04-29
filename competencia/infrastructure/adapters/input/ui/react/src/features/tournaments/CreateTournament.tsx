import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { ArrowLeft, Save, Sparkles } from "lucide-react";

export function CreateTournament() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nombre: "",
    fechaInicio: "",
    fechaFin: "",
    categoria: "explorador",
    limiteEquipos: "",
    descripcion: "",
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({}); // Limpiar errores

    // Validaciones
    const newErrors: Record<string, string> = {};
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    const inicio = new Date(`${formData.fechaInicio}T00:00:00`);
    const fin = new Date(`${formData.fechaFin}T00:00:00`);

    if (inicio < hoy) {
      newErrors.fechaInicio = "La fecha de inicio no puede ser anterior a hoy.";
    }
    if (fin < inicio) {
      newErrors.fechaFin = "La fecha de fin debe ser igual o posterior a la fecha de inicio.";
    }

    const equipos = parseInt(formData.limiteEquipos);
    if (isNaN(equipos) || equipos < 4 || equipos > 64) {
      newErrors.limiteEquipos = "El máximo de equipos debe estar entre 4 y 64.";
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      const payload = {
        name: formData.nombre,
        description: formData.descripcion,
        date_start: formData.fechaInicio ? `${formData.fechaInicio}T00:00:00` : new Date().toISOString(),
        date_end: formData.fechaFin ? `${formData.fechaFin}T23:59:59` : new Date().toISOString(),
        category: formData.categoria,
        max_teams: parseInt(formData.limiteEquipos) || 16,
      };

      const res = await fetch("http://localhost:8000/api/competencia/create/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const tournament = await res.json();
        alert("Torneo creado exitosamente en estado borrador.");
        // Redirigir a configuración de reglas
        navigate(`/dashboard/torneos/${tournament.id}/reglas`);
      } else {
        const errorData = await res.json();
        alert("Error: " + JSON.stringify(errorData));
      }
    } catch (error) {
      alert("Error de red: " + error);
    }
  };

  const generateDescriptionAI = () => {
    const nombreTorneo = formData.nombre || "este gran torneo";
    setFormData((prev) => ({
      ...prev,
      descripcion: `¡Bienvenidos a ${nombreTorneo}! Un evento diseñado para fomentar la innovación, el trabajo en equipo y las habilidades tecnológicas en la robótica. Únete a nosotros en esta emocionante competencia donde la creatividad y la ingeniería se encuentran.`,
    }));
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center space-x-4 mb-6">
        <Link
          to="/dashboard/torneos"
          className="inline-flex items-center justify-center rounded-md text-slate-500 hover:text-slate-900 transition-colors p-2 hover:bg-slate-100"
        >
          <ArrowLeft className="h-5 w-5" />
          <span className="sr-only">Volver</span>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Crear torneo</h1>
          <p className="text-sm text-slate-500">Configura los detalles principales y reglas del evento.</p>
        </div>
      </div>

      <div className="bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
        <form onSubmit={handleSubmit}>
          <div className="p-6 md:p-8 space-y-8">
            {/* Sección: Detalles Generales */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Detalles Generales
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="col-span-1 md:col-span-2 space-y-2">
                  <label htmlFor="nombre" className="text-sm font-medium text-slate-700 leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Nombre del torneo <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="nombre"
                    type="text"
                    required
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50"
                    placeholder="Ej. Torneo de Robótica Wanka 2026"
                  />
                </div>

                <div className="col-span-1 md:col-span-2 space-y-2">
                  <div className="flex items-center justify-between">
                    <label htmlFor="descripcion" className="text-sm font-medium text-slate-700 leading-none">
                      Descripción
                    </label>
                    <button
                      type="button"
                      onClick={generateDescriptionAI}
                      className="inline-flex items-center text-xs font-medium text-purple-700 bg-purple-100 hover:bg-purple-200 px-3 py-1.5 rounded-full transition-colors"
                    >
                      <Sparkles className="h-3 w-3 mr-1.5" />
                      Generar con IA
                    </button>
                  </div>
                  <textarea
                    id="descripcion"
                    rows={3}
                    value={formData.descripcion}
                    onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                    className="flex w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
                    placeholder="Describe brevemente de qué trata el torneo..."
                  ></textarea>
                </div>

                <div className="space-y-2">
                  <label htmlFor="fechaInicio" className="text-sm font-medium text-slate-700 leading-none">
                    Fecha de inicio <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="fechaInicio"
                    type="date"
                    required
                    value={formData.fechaInicio}
                    onChange={(e) => setFormData({ ...formData, fechaInicio: e.target.value })}
                    className={`flex h-10 w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.fechaInicio ? 'border-red-500' : 'border-slate-300'}`}
                  />
                  {errors.fechaInicio && <p className="text-xs text-red-500 mt-1">{errors.fechaInicio}</p>}
                </div>

                <div className="space-y-2">
                  <label htmlFor="fechaFin" className="text-sm font-medium text-slate-700 leading-none">
                    Fecha de fin <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="fechaFin"
                    type="date"
                    required
                    value={formData.fechaFin}
                    onChange={(e) => setFormData({ ...formData, fechaFin: e.target.value })}
                    className={`flex h-10 w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.fechaFin ? 'border-red-500' : 'border-slate-300'}`}
                  />
                  {errors.fechaFin && <p className="text-xs text-red-500 mt-1">{errors.fechaFin}</p>}
                </div>

                <div className="space-y-2">
                  <label htmlFor="categoria" className="text-sm font-medium text-slate-700 leading-none">
                    Categoría
                  </label>
                  <select
                    id="categoria"
                    value={formData.categoria}
                    onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="explorador">Explorador</option>
                    <option value="constructor">Constructor</option>
                    <option value="innovador">Innovador</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label htmlFor="limiteEquipos" className="text-sm font-medium text-slate-700 leading-none">
                    Límite de equipos
                  </label>
                  <input
                    id="limiteEquipos"
                    type="number"
                    value={formData.limiteEquipos}
                    onChange={(e) => setFormData({ ...formData, limiteEquipos: e.target.value })}
                    className={`flex h-10 w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${errors.limiteEquipos ? 'border-red-500' : 'border-slate-300'}`}
                    placeholder="Ej. 16, 32..."
                  />
                  {errors.limiteEquipos && <p className="text-xs text-red-500 mt-1">{errors.limiteEquipos}</p>}
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-end gap-4 border-t border-slate-200 bg-slate-50 p-6">
            <Link
              to="/dashboard/torneos"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 hover:bg-slate-100 text-slate-700 h-10 px-4 py-2 border border-slate-300"
            >
              Cancelar
            </Link>
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm"
            >
              <Save className="mr-2 h-4 w-4" />
              Guardar Torneo
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
