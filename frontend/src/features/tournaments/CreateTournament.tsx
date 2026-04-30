import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { ArrowLeft, Save, Sparkles, AlertCircle } from "lucide-react";
import { TipoTorneo, CategoriaTorneo } from "../../types/tournament";
import type { TournamentFieldError } from "../../types/tournament";
import { createTournament } from "../../services/tournamentService";
import { analizarTexto } from "../../services/aiService";
import { EstadoAnalisisIA } from "../../types/ai";
import axios from "axios";

// ─── Tipos internos del formulario ────────────────────────────────────────────
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

// Función para validar los datos en el cliente antes de enviar al servidor
function validateForm(data: FormData): Record<string, string> {
  const errors: Record<string, string> = {};
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);

  const inicio = data.fecha_inicio ? new Date(data.fecha_inicio) : null;
  const fin = data.fecha_fin ? new Date(data.fecha_fin) : null;
  const inicioInscripcion = data.fecha_inicio_inscripcion
    ? new Date(data.fecha_inicio_inscripcion)
    : null;
  const finInscripcion = data.fecha_fin_inscripcion
    ? new Date(data.fecha_fin_inscripcion)
    : null;

  if (!data.nombre.trim()) errors.nombre = "requerido";

  // Validación: la fecha de inicio no puede ser en el pasado
  if (!data.fecha_inicio) {
    errors.fecha_inicio = "requerido";
  } else if (inicio && inicio < hoy) {
    errors.fecha_inicio = "debe ser posterior a la fecha actual";
  }

  // Validación: la fecha de fin no puede ser anterior a la fecha de inicio
  if (!data.fecha_fin) {
    errors.fecha_fin = "requerido";
  } else if (inicio && fin && fin < inicio) {
    errors.fecha_fin = "debe ser posterior o igual a fecha_inicio";
  }

  // fecha_inicio_inscripcion ≤ fecha_inicio
  if (!data.fecha_inicio_inscripcion) {
    errors.fecha_inicio_inscripcion = "requerido";
  } else if (inicio && inicioInscripcion && inicioInscripcion > inicio) {
    errors.fecha_inicio_inscripcion = "debe ser menor o igual a fecha_inicio";
  }

  // fecha_fin_inscripcion ≤ fecha_inicio
  if (!data.fecha_fin_inscripcion) {
    errors.fecha_fin_inscripcion = "requerido";
  } else if (inicio && finInscripcion && finInscripcion > inicio) {
    errors.fecha_fin_inscripcion = "debe ser menor o igual a fecha_inicio";
  }

  const max = parseInt(data.max_equipos);
  const min = parseInt(data.min_equipos);

  if (!data.max_equipos) {
    errors.max_equipos = "requerido";
  } else if (isNaN(max) || max < 2 || max > 128) {
    errors.max_equipos = "debe estar entre 2 y 128";
  } else if (data.tipo_torneo === TipoTorneo.KNOCKOUT && max % 2 !== 0) {
    // Validación: en formato Knockout, la cantidad de equipos debe ser par
    errors.max_equipos = "debe ser par para formato Knockout";
  }

  if (!data.min_equipos) {
    errors.min_equipos = "requerido";
  } else if (!isNaN(max) && !isNaN(min) && min > max) {
    errors.min_equipos = "no puede ser mayor que max_equipos";
  } else {
    // Validación: cantidades mínimas requeridas según el tipo de torneo
    const minimosPorTipo: Record<TipoTorneo, number> = {
      [TipoTorneo.KNOCKOUT]: 2,
      [TipoTorneo.ROUND_ROBIN]: 3,
      [TipoTorneo.HYBRID]: 6,
    };
    const minRequerido = minimosPorTipo[data.tipo_torneo];
    if (!isNaN(min) && min < minRequerido) {
      errors.min_equipos = `mínimo ${minRequerido} equipos para ${data.tipo_torneo}`;
    }
  }

  if (!data.tipo_torneo) errors.tipo_torneo = "requerido";

  if (data.categorias_habilitadas.length === 0) {
    errors.categorias_habilitadas = "selecciona al menos una categoría";
  }

  return errors;
}

// ─── Helpers de UI ────────────────────────────────────────────────────────────
function FieldError({ msg }: { msg?: string }) {
  if (!msg) return null;
  return <p className="mt-1 text-xs text-red-600">{msg}</p>;
}

function inputClass(error?: string) {
  return `flex h-10 w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
    error ? "border-red-400" : "border-slate-300"
  }`;
}

// Componente principal para la creación de un nuevo torneo
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

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const set = (field: keyof FormData, value: unknown) =>
    setFormData((prev) => ({ ...prev, [field]: value }));

  // Estados para IA
  const [aiText, setAiText] = useState("");
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiMissingFields, setAiMissingFields] = useState<string[]>([]);
  const [aiSuccess, setAiSuccess] = useState(false);

  const handleAnalizarIA = async () => {
    if (!aiText.trim()) return;
    setAiError(null);
    setAiMissingFields([]);
    setAiSuccess(false);
    setIsAiLoading(true);
    
    try {
      const result = await analizarTexto(aiText);
      if (result.estado_analisis === EstadoAnalisisIA.COMPLETO) {
        setFormData(prev => ({
          ...prev,
          max_equipos: result.numero_equipos?.toString() || prev.max_equipos,
          categorias_habilitadas: result.categoria ? [result.categoria] : prev.categorias_habilitadas,
          tipo_torneo: result.tipo_torneo_sugerido || prev.tipo_torneo,
        }));
        setAiSuccess(true);
      } else {
        setAiMissingFields(result.campos_faltantes || []);
        setAiError("La descripción es ambigua o le faltan datos.");
      }
    } catch (err: unknown) {
      setAiError("No se pudo analizar el texto con la IA. Verifique su red.");
    } finally {
      setIsAiLoading(false);
    }
  };

  // Maneja la selección múltiple de categorías
  const toggleCategoria = (cat: CategoriaTorneo) => {
    setFormData((prev) => {
      const current = prev.categorias_habilitadas;
      return {
        ...prev,
        categorias_habilitadas: current.includes(cat)
          ? current.filter((c) => c !== cat)
          : [...current, cat],
      };
    });
  };

  const generateDescriptionAI = () => {
    const nombre = formData.nombre || "este gran torneo";
    set(
      "descripcion",
      `¡Bienvenidos a ${nombre}! Un evento diseñado para fomentar la innovación, el trabajo en equipo y las habilidades tecnológicas en la robótica. Únete a nosotros en esta emocionante competencia donde la creatividad y la ingeniería se encuentran.`
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);

    // Paso 1: Ejecutar la validación local
    const localErrors = validateForm(formData);
    if (Object.keys(localErrors).length > 0) {
      setErrors(localErrors);
      return;
    }
    setErrors({});

    // Paso 2: Enviar los datos al backend
    setIsLoading(true);
    try {
      const tournament = await createTournament({
        nombre: formData.nombre,
        descripcion: formData.descripcion || undefined,
        fecha_inicio: formData.fecha_inicio,
        fecha_fin: formData.fecha_fin,
        fecha_inicio_inscripcion: formData.fecha_inicio_inscripcion,
        fecha_fin_inscripcion: formData.fecha_fin_inscripcion,
        max_equipos: parseInt(formData.max_equipos),
        min_equipos: parseInt(formData.min_equipos),
        tipo_torneo: formData.tipo_torneo,
        categorias_habilitadas: formData.categorias_habilitadas,
      });

      // En caso de éxito, redirigir al usuario para que configure las reglas del torneo
      navigate(`/dashboard/torneos/${tournament.id}/reglas`);
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const data = error.response?.data;

        if (status === 400 || status === 422) {
          // Manejo de errores específicos enviados por el servidor
          if (Array.isArray(data)) {
            const backendErrors: Record<string, string> = {};
            (data as TournamentFieldError[]).forEach(({ campo, error: msg }) => {
              backendErrors[campo] = msg;
            });
            setErrors(backendErrors);
          } else if (data?.campo) {
            setErrors({ [data.campo]: data.error });
          } else {
            setGeneralError("Datos inválidos. Revisa los campos.");
          }
        } else {
          setGeneralError("Ocurrió un error inesperado. Intente nuevamente.");
        }
      } else {
        setGeneralError("Error de conexión. Verifique su red.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Encabezado */}
      <div className="flex items-center space-x-4 mb-6">
        <Link
          to="/dashboard/torneos"
          className="inline-flex items-center justify-center rounded-md text-slate-500 hover:text-slate-900 transition-colors p-2 hover:bg-slate-100"
        >
          <ArrowLeft className="h-5 w-5" />
          <span className="sr-only">Volver</span>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Crear torneo
          </h1>
          <p className="text-sm text-slate-500">
            Configura los detalles principales del evento. Se creará en estado{" "}
            <span className="font-medium text-blue-600">Borrador</span>.
          </p>
        </div>
      </div>

      {/* Error general */}
      {generalError && (
        <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm">
          <AlertCircle size={16} className="shrink-0" />
          <span>{generalError}</span>
        </div>
      )}

      <div className="bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
        <form onSubmit={handleSubmit}>
          <div className="p-6 md:p-8 space-y-8">

            {/* ── Asistente IA (HU-IA-01) ── */}
            <section className="space-y-4 bg-purple-50 p-6 rounded-xl border border-purple-100">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="h-5 w-5 text-purple-600" />
                <h3 className="text-lg font-semibold text-purple-900">Asistente IA para Torneos</h3>
              </div>
              <p className="text-sm text-purple-700">
                Escribe una descripción de tu torneo (ej. "Quiero organizar un torneo para 12 equipos de secundaria con nivel intermedio, usando eliminación directa") y la IA configurará los campos automáticamente.
              </p>
              <div className="flex flex-col gap-3 sm:flex-row">
                <input
                  type="text"
                  value={aiText}
                  onChange={(e) => setAiText(e.target.value)}
                  placeholder="Describe el torneo libremente..."
                  className="flex-1 rounded-md border border-purple-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                  disabled={isAiLoading}
                />
                <button
                  type="button"
                  onClick={handleAnalizarIA}
                  disabled={isAiLoading || !aiText.trim()}
                  className="inline-flex shrink-0 items-center justify-center rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700 disabled:opacity-50"
                >
                  {isAiLoading ? "Analizando..." : "Analizar con IA"}
                </button>
              </div>
              {aiSuccess && (
                <div className="text-sm text-green-700 bg-green-50 border border-green-200 p-2 rounded-md">
                  ¡Entidades extraídas correctamente! Formulario actualizado. Por favor, revisa y confirma los datos antes de continuar.
                </div>
              )}
              {aiError && (
                <div className="text-sm text-red-600 bg-red-50 border border-red-200 p-2 rounded-md">
                  {aiError}
                  {aiMissingFields.length > 0 && (
                    <ul className="list-disc ml-5 mt-1">
                      {aiMissingFields.map(f => <li key={f}>Falta: {f}</li>)}
                    </ul>
                  )}
                </div>
              )}
            </section>

            {/* ── Sección 1: Detalles generales ── */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Detalles Generales
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Nombre */}
                <div className="col-span-2 space-y-1">
                  <label htmlFor="nombre" className="text-sm font-medium text-slate-700">
                    Nombre del torneo <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="nombre"
                    type="text"
                    required
                    value={formData.nombre}
                    onChange={(e) => set("nombre", e.target.value)}
                    className={inputClass(errors.nombre)}
                    placeholder="Ej. Torneo de Robótica Wanka 2026"
                  />
                  <FieldError msg={errors.nombre} />
                </div>

                {/* Descripción */}
                <div className="col-span-2 space-y-1">
                  <div className="flex items-center justify-between">
                    <label htmlFor="descripcion" className="text-sm font-medium text-slate-700">
                      Descripción <span className="text-slate-400 font-normal">(opcional)</span>
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
                    maxLength={2000}
                    value={formData.descripcion}
                    onChange={(e) => set("descripcion", e.target.value)}
                    className="flex w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-y"
                    placeholder="Describe brevemente de qué trata el torneo... (máx. 2000 caracteres)"
                  />
                </div>
              </div>
            </section>

            {/* ── Sección 2: Tipo y formato ── */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Formato de Competencia
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Tipo de torneo */}
                <div className="space-y-1">
                  <label htmlFor="tipo_torneo" className="text-sm font-medium text-slate-700">
                    Tipo de torneo <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="tipo_torneo"
                    value={formData.tipo_torneo}
                    onChange={(e) => set("tipo_torneo", e.target.value as TipoTorneo)}
                    className={inputClass(errors.tipo_torneo)}
                  >
                    <option value={TipoTorneo.KNOCKOUT}>Eliminación directa (Knockout)</option>
                    <option value={TipoTorneo.ROUND_ROBIN}>Todos contra todos (Round Robin)</option>
                    <option value={TipoTorneo.HYBRID}>Híbrido</option>
                  </select>
                  <FieldError msg={errors.tipo_torneo} />
                </div>

                {/* Máx equipos */}
                <div className="space-y-1">
                  <label htmlFor="max_equipos" className="text-sm font-medium text-slate-700">
                    Máx. equipos <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="max_equipos"
                    type="number"
                    min={2}
                    max={128}
                    value={formData.max_equipos}
                    onChange={(e) => set("max_equipos", e.target.value)}
                    className={inputClass(errors.max_equipos)}
                    placeholder="2 – 128"
                  />
                  <FieldError msg={errors.max_equipos} />
                </div>

                {/* Mín equipos */}
                <div className="space-y-1">
                  <label htmlFor="min_equipos" className="text-sm font-medium text-slate-700">
                    Mín. equipos <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="min_equipos"
                    type="number"
                    min={2}
                    value={formData.min_equipos}
                    onChange={(e) => set("min_equipos", e.target.value)}
                    className={inputClass(errors.min_equipos)}
                    placeholder="Mínimo para iniciar"
                  />
                  <FieldError msg={errors.min_equipos} />
                </div>
              </div>

              {/* Categorías habilitadas */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">
                  Categorías habilitadas <span className="text-red-500">*</span>
                </label>
                <div className="flex gap-4">
                  {Object.values(CategoriaTorneo).map((cat) => (
                    <label key={cat} className="flex items-center gap-2 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={formData.categorias_habilitadas.includes(cat)}
                        onChange={() => toggleCategoria(cat)}
                        className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-700">
                        {cat === CategoriaTorneo.PRIMARY ? "Primaria" : "Secundaria"}
                      </span>
                    </label>
                  ))}
                </div>
                <FieldError msg={errors.categorias_habilitadas} />
              </div>
            </section>

            {/* ── Sección 3: Fechas ── */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Fechas
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Fecha inicio competencia */}
                <div className="space-y-1">
                  <label htmlFor="fecha_inicio" className="text-sm font-medium text-slate-700">
                    Inicio de competencia <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="fecha_inicio"
                    type="date"
                    value={formData.fecha_inicio}
                    onChange={(e) => set("fecha_inicio", e.target.value)}
                    className={inputClass(errors.fecha_inicio)}
                  />
                  <FieldError msg={errors.fecha_inicio} />
                </div>

                {/* Fecha fin competencia */}
                <div className="space-y-1">
                  <label htmlFor="fecha_fin" className="text-sm font-medium text-slate-700">
                    Fin de competencia <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="fecha_fin"
                    type="date"
                    value={formData.fecha_fin}
                    onChange={(e) => set("fecha_fin", e.target.value)}
                    className={inputClass(errors.fecha_fin)}
                  />
                  <FieldError msg={errors.fecha_fin} />
                </div>

                {/* Inicio inscripciones */}
                <div className="space-y-1">
                  <label htmlFor="fecha_inicio_inscripcion" className="text-sm font-medium text-slate-700">
                    Inicio de inscripciones <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="fecha_inicio_inscripcion"
                    type="date"
                    value={formData.fecha_inicio_inscripcion}
                    onChange={(e) => set("fecha_inicio_inscripcion", e.target.value)}
                    className={inputClass(errors.fecha_inicio_inscripcion)}
                  />
                  <FieldError msg={errors.fecha_inicio_inscripcion} />
                </div>

                {/* Fin inscripciones */}
                <div className="space-y-1">
                  <label htmlFor="fecha_fin_inscripcion" className="text-sm font-medium text-slate-700">
                    Cierre de inscripciones <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="fecha_fin_inscripcion"
                    type="date"
                    value={formData.fecha_fin_inscripcion}
                    onChange={(e) => set("fecha_fin_inscripcion", e.target.value)}
                    className={inputClass(errors.fecha_fin_inscripcion)}
                  />
                  <FieldError msg={errors.fecha_fin_inscripcion} />
                </div>
              </div>
            </section>
          </div>

          {/* ── Footer ── */}
          <div className="flex items-center justify-end gap-4 border-t border-slate-200 bg-slate-50 p-6">
            <Link
              to="/dashboard/torneos"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-slate-100 text-slate-700 h-10 px-4 py-2 border border-slate-300"
            >
              Cancelar
            </Link>
            <button
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Guardar Torneo
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
