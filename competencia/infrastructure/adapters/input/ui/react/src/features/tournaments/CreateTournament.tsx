import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { ArrowLeft, Save, Sparkles, AlertCircle, Bot } from "lucide-react";
import { TipoTorneo, CategoriaTorneo } from "../../types/tournament";
import { createTournament } from "../../services/tournamentService";
import { analizarTexto } from "../../services/aiService";
import axios from "axios";

interface FormData {
  nombre: string;
  descripcion: string;
  fecha_inicio: string;
  fecha_fin: string;
  fecha_inicio_inscripcion: string;
  fecha_fin_inscripcion: string;
  max_equipos: string;
  min_equipos: string;
  tipo_torneo: TipoTorneo;
  categorias_habilitadas: CategoriaTorneo[];
}

export function CreateTournament() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState<FormData>({
    nombre: "",
    descripcion: "",
    fecha_inicio: "",
    fecha_fin: "",
    fecha_inicio_inscripcion: "",
    fecha_fin_inscripcion: "",
    max_equipos: "16",
    min_equipos: "4",
    tipo_torneo: TipoTorneo.KNOCKOUT,
    categorias_habilitadas: [],
  });

  const [generalError, setGeneralError] = useState<string | null>(null);
  const [descLibre, setDescLibre] = useState("");
  const [isAnalizando, setIsAnalizando] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleAnalizarIA = async () => {
    if (!descLibre.trim()) return;
    setIsAnalizando(true);
    setGeneralError(null);
    try {
      const analysis = await analizarTexto(descLibre);

      // Mapeo de categorías de IA a categorías de Torneo
      let categoriaSugerida = formData.categorias_habilitadas;
      if (analysis.categoria) {
        categoriaSugerida = [analysis.categoria];
      }

      setFormData(prev => ({
        ...prev,
        nombre: prev.nombre || (analysis.intencion_usuario === "CREAR_TORNEO" ? "Nuevo Torneo" : prev.nombre),
        descripcion: descLibre,
        max_equipos: analysis.numero_equipos?.toString() || prev.max_equipos,
        categorias_habilitadas: categoriaSugerida,
        tipo_torneo: analysis.tipo_torneo_sugerido || prev.tipo_torneo
      }));
    } catch (err) {
      console.error("Error en análisis IA:", err);
      setGeneralError("No se pudo analizar el texto. Por favor complete manualmente.");
    } finally {
      setIsAnalizando(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    setIsSaving(true);

    try {
      const tournament = await createTournament({
        nombre: formData.nombre,
        descripcion: formData.descripcion || undefined,
        fecha_inicio: formData.fecha_inicio,
        fecha_fin: formData.fecha_fin,
        fecha_inicio_inscripcion: formData.fecha_inicio_inscripcion,
        fecha_fin_inscripcion: formData.fecha_fin_inscripcion,
        max_equipos: Number(formData.max_equipos),
        min_equipos: Number(formData.min_equipos),
        tipo_torneo: formData.tipo_torneo,
        categorias_habilitadas: formData.categorias_habilitadas,
      });

      navigate(`/dashboard/torneos/${tournament.id}/reglas`);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setGeneralError(err.response?.data?.error || "Error al crear el torneo.");
      } else {
        setGeneralError("Error de conexión.");
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-10">
      <div className="flex items-center space-x-4 mb-6">
        <Link to="/dashboard/torneos" className="inline-flex items-center justify-center rounded-md text-slate-500 hover:text-slate-900 p-2 hover:bg-slate-100 transition-colors">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Nuevo Torneo</h1>
          <p className="text-sm text-slate-500">Configuración básica inicial</p>
        </div>
      </div>

      <div className="bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-100 rounded-xl p-6 shadow-sm mb-8">
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 bg-indigo-600 rounded-lg text-white">
            <Sparkles size={18} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-indigo-900">Asistente de Creación IA</h3>
            <p className="text-xs text-indigo-700">Describe tu torneo en lenguaje natural y yo extraeré los datos por ti.</p>
          </div>
        </div>

        <div className="space-y-3">
          <textarea
            placeholder="Ej: Quiero un torneo de robótica para secundaria con 16 equipos que inicie el próximo mes..."
            className="w-full h-24 p-3 text-sm rounded-lg border border-indigo-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
            value={descLibre}
            onChange={(e) => setDescLibre(e.target.value)}
          />
          <button
            type="button"
            onClick={handleAnalizarIA}
            disabled={isAnalizando || !descLibre.trim()}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 h-9 px-4 shadow-sm disabled:opacity-50 transition-colors"
          >
            {isAnalizando ? (
              <><div className="animate-spin mr-2 border-2 border-white border-t-transparent rounded-full w-4 h-4" /> Analizando...</>
            ) : (
              <><Bot className="mr-2 h-4 w-4" /> Autocompletar con IA</>
            )}
          </button>
        </div>
      </div>

      {generalError && (
        <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm">
          <AlertCircle size={16} />
          <span>{generalError}</span>
        </div>
      )}

      <div className="bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
        <form onSubmit={handleSubmit}>
          <div className="p-6 md:p-8 space-y-8">
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">Datos Principales</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1 md:col-span-2">
                  <label className="text-sm font-medium text-slate-700">Nombre del Torneo</label>
                  <input
                    type="text"
                    required
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">Categoría</label>
                  <select
                    required
                    value={formData.categorias_habilitadas[0] || ""}
                    onChange={(e) => setFormData({ ...formData, categorias_habilitadas: [e.target.value as CategoriaTorneo] })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Seleccione...</option>
                    <option value={CategoriaTorneo.EXPLORADOR}>Explorador (Primary)</option>
                    <option value={CategoriaTorneo.INNOVADOR}>Innovador (Secondary)</option>
                    <option value={CategoriaTorneo.CONSTRUCTOR}>Constructor (Avanzado)</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">Máx. Equipos</label>
                  <input
                    type="number"
                    required
                    value={formData.max_equipos}
                    onChange={(e) => setFormData({ ...formData, max_equipos: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </section>

            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">Cronograma del Torneo</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">Fecha Inicio</label>
                  <input
                    type="date"
                    required
                    value={formData.fecha_inicio}
                    onChange={(e) => setFormData({ ...formData, fecha_inicio: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">Fecha Fin</label>
                  <input
                    type="date"
                    required
                    value={formData.fecha_fin}
                    onChange={(e) => setFormData({ ...formData, fecha_fin: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">Inicio Inscripciones</label>
                  <input
                    type="date"
                    required
                    value={formData.fecha_inicio_inscripcion}
                    onChange={(e) => setFormData({ ...formData, fecha_inicio_inscripcion: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">Cierre Inscripciones</label>
                  <input
                    type="date"
                    required
                    value={formData.fecha_fin_inscripcion}
                    onChange={(e) => setFormData({ ...formData, fecha_fin_inscripcion: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </section>

            <section className="space-y-4">
              <label className="text-sm font-medium text-slate-700">Descripción / Objetivo</label>
              <textarea
                rows={4}
                value={formData.descripcion}
                onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                className="block w-full rounded-md border-slate-300 border px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe el propósito del torneo..."
              />
            </section>
          </div>

          <div className="flex items-center justify-end border-t border-slate-200 bg-slate-50 p-6 gap-3">
            <Link
              to="/dashboard/torneos"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 h-10 px-4 py-2"
            >
              Cancelar
            </Link>
            <button
              type="submit"
              disabled={isSaving}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 h-10 px-6 shadow-sm disabled:opacity-50 transition-colors"
            >
              {isSaving ? "Creando..." : <><Save className="mr-2 h-4 w-4" /> Crear Torneo (Borrador)</>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
