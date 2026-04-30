import { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { ArrowLeft, Save, AlertCircle, Plus, Trash2, Users } from "lucide-react";
import { registerTeam } from "../../services/teamService";
import { getTournamentById } from "../../services/tournamentService";
import {
  NivelTecnico,
  TipoInstitucion,
  Participante,
  Institucion,
  DocenteAsesor,
} from "../../types/team";
import { Tournament, CategoriaTorneo } from "../../types/tournament";
import axios from "axios";

export function RegisterTeam() {
  const navigate = useNavigate();
  const { id: tournamentId } = useParams<{ id: string }>();

  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [isLoadingTournament, setIsLoadingTournament] = useState(true);

  const [nombre, setNombre] = useState("");
  const [categoria, setCategoria] = useState<CategoriaTorneo | "">("");
  const [nivelTecnico, setNivelTecnico] = useState<NivelTecnico>(NivelTecnico.BASICO);

  const [institucion, setInstitucion] = useState<Institucion>({
    nombre: "",
    tipo: TipoInstitucion.PUBLICA,
    ciudad: "",
    pais: "PE",
  });

  const [docente, setDocente] = useState<DocenteAsesor>({
    nombre_completo: "",
    email: "",
    telefono: "",
  });

  const [participantes, setParticipantes] = useState<Participante[]>([
    {
      nombres: "",
      apellidos: "",
      edad: 0,
      grado_academico: "",
      documento_identidad: "",
      autorizacion_datos: false,
      rol_en_equipo: "",
    },
  ]);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!tournamentId) return;
    getTournamentById(tournamentId)
      .then((t) => setTournament(t))
      .catch((err) => console.error("Error al cargar torneo", err))
      .finally(() => setIsLoadingTournament(false));
  }, [tournamentId]);

  const handleAddParticipante = () => {
    setParticipantes((prev) => [
      ...prev,
      {
        nombres: "",
        apellidos: "",
        edad: 0,
        grado_academico: "",
        documento_identidad: "",
        autorizacion_datos: false,
        rol_en_equipo: "",
      },
    ]);
  };

  const handleRemoveParticipante = (index: number) => {
    setParticipantes((prev) => prev.filter((_, i) => i !== index));
  };

  const handleChangeParticipante = (index: number, field: keyof Participante, value: any) => {
    setParticipantes((prev) =>
      prev.map((p, i) => (i === index ? { ...p, [field]: value } : p))
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    setErrors({});

    // Validación básica en el cliente antes de enviar al servidor
    const newErrors: Record<string, string> = {};
    if (!nombre.trim()) newErrors.nombre = "El nombre del equipo es requerido";
    if (!categoria) newErrors.categoria = "La categoría es requerida";
    
    // Verificamos que todos los participantes hayan aceptado el tratamiento de datos
    const missingConsent = participantes.some((p) => !p.autorizacion_datos);
    if (missingConsent) {
      setGeneralError("Todos los participantes deben contar con autorización de datos.");
      return;
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSaving(true);
    try {
      await registerTeam(tournamentId!, {
        nombre,
        categoria,
        nivel_tecnico_declarado: nivelTecnico,
        institucion,
        docente_asesor: docente,
        participantes,
      });

      alert("Equipo inscrito exitosamente y pendiente de aprobación.");
      navigate("/dashboard/equipos");
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        const data = err.response?.data;

        if (status === 409) {
          // Error de conflicto: Posiblemente el participante ya se encuentra registrado en este torneo
          setGeneralError(data?.error || "Conflicto al inscribir equipo.");
        } else if (status === 422 || status === 400) {
          // Error de validación: Categoría inválida, edad incorrecta o falta de autorizaciones
          if (data?.campo) {
            setErrors({ [data.campo]: data.error });
            setGeneralError(`Error en el campo ${data.campo}: ${data.error}`);
          } else if (data?.error) {
            setGeneralError(data.error);
          } else {
            setGeneralError("Datos inválidos. Revisa los campos.");
          }
        } else {
          setGeneralError("Ocurrió un error inesperado al inscribir el equipo.");
        }
      } else {
        setGeneralError("Error de conexión. Verifique su red.");
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoadingTournament) {
    return <div className="p-8 text-center text-slate-500">Cargando datos del torneo...</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-10">
      <div className="flex items-center space-x-4 mb-6">
        <Link
          to="/dashboard/torneos"
          className="inline-flex items-center justify-center rounded-md text-slate-500 hover:text-slate-900 transition-colors p-2 hover:bg-slate-100"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Inscribir Equipo</h1>
          <p className="text-sm text-slate-500">
            Torneo: {tournament?.nombre}
          </p>
        </div>
      </div>

      {generalError && (
        <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm">
          <AlertCircle size={16} className="shrink-0" />
          <span>{generalError}</span>
        </div>
      )}

      <div className="bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
        <form onSubmit={handleSubmit}>
          <div className="p-6 md:p-8 space-y-8">
            
            {/* Sección con los detalles principales del equipo */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Detalles del Equipo
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Nombre del Equipo <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={nombre}
                    onChange={(e) => setNombre(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                  {errors.nombre && <p className="text-xs text-red-600">{errors.nombre}</p>}
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Categoría <span className="text-red-500">*</span>
                  </label>
                  <select
                    required
                    value={categoria}
                    onChange={(e) => setCategoria(e.target.value as CategoriaTorneo)}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="" disabled>Seleccione una categoría</option>
                    {tournament?.categorias_habilitadas.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                  {errors.categoria && <p className="text-xs text-red-600">{errors.categoria}</p>}
                </div>

                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Nivel Técnico Declarado <span className="text-red-500">*</span>
                  </label>
                  <select
                    required
                    value={nivelTecnico}
                    onChange={(e) => setNivelTecnico(e.target.value as NivelTecnico)}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={NivelTecnico.BASICO}>Básico</option>
                    <option value={NivelTecnico.INTERMEDIO}>Intermedio</option>
                    <option value={NivelTecnico.AVANZADO}>Avanzado</option>
                  </select>
                </div>
              </div>
            </section>

            {/* Sección para los datos de la institución educativa */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Institución Educativa
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Nombre <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={institucion.nombre}
                    onChange={(e) => setInstitucion({ ...institucion, nombre: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Tipo <span className="text-red-500">*</span>
                  </label>
                  <select
                    required
                    value={institucion.tipo}
                    onChange={(e) => setInstitucion({ ...institucion, tipo: e.target.value as TipoInstitucion })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={TipoInstitucion.PUBLICA}>Pública</option>
                    <option value={TipoInstitucion.PRIVADA}>Privada</option>
                    <option value={TipoInstitucion.CONCERTADA}>Concertada</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Ciudad <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={institucion.ciudad}
                    onChange={(e) => setInstitucion({ ...institucion, ciudad: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    País <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={institucion.pais}
                    onChange={(e) => setInstitucion({ ...institucion, pais: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </section>

            {/* Sección para registrar al docente asesor */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Docente Asesor
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Nombre Completo <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={docente.nombre_completo}
                    onChange={(e) => setDocente({ ...docente, nombre_completo: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">
                    Email <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={docente.email}
                    onChange={(e) => setDocente({ ...docente, email: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div className="space-y-1 md:col-span-2">
                  <label className="text-sm font-medium text-slate-700">
                    Teléfono <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={docente.telefono}
                    onChange={(e) => setDocente({ ...docente, telefono: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            </section>

            {/* Sección dinámica para agregar o quitar participantes */}
            <section className="space-y-4">
              <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                <h3 className="text-lg font-semibold text-slate-900">Participantes</h3>
              </div>
              <div className="space-y-6">
                {participantes.map((p, index) => (
                  <div key={index} className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <div className="flex justify-between items-center mb-4">
                      <h4 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        Participante {index + 1}
                      </h4>
                      {participantes.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveParticipante(index)}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-700">Nombres *</label>
                        <input
                          type="text"
                          required
                          value={p.nombres}
                          onChange={(e) => handleChangeParticipante(index, "nombres", e.target.value)}
                          className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-700">Apellidos *</label>
                        <input
                          type="text"
                          required
                          value={p.apellidos}
                          onChange={(e) => handleChangeParticipante(index, "apellidos", e.target.value)}
                          className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-700">Edad *</label>
                        <input
                          type="number"
                          required
                          value={p.edad || ""}
                          onChange={(e) => handleChangeParticipante(index, "edad", parseInt(e.target.value))}
                          className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                        {errors.edad && <p className="text-xs text-red-600">{errors.edad}</p>}
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-700">Grado Académico *</label>
                        <input
                          type="text"
                          required
                          value={p.grado_academico}
                          onChange={(e) => handleChangeParticipante(index, "grado_academico", e.target.value)}
                          className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-700">Documento Identidad (DNI) *</label>
                        <input
                          type="text"
                          required
                          value={p.documento_identidad}
                          onChange={(e) => handleChangeParticipante(index, "documento_identidad", e.target.value)}
                          className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-xs font-medium text-slate-700">Rol en el equipo</label>
                        <input
                          type="text"
                          value={p.rol_en_equipo || ""}
                          onChange={(e) => handleChangeParticipante(index, "rol_en_equipo", e.target.value)}
                          className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="col-span-1 md:col-span-2 mt-2">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={p.autorizacion_datos}
                            onChange={(e) => handleChangeParticipante(index, "autorizacion_datos", e.target.checked)}
                            className="h-4 w-4 text-blue-600 border-slate-300 rounded focus:ring-blue-500"
                          />
                          <span className="text-sm text-slate-700">
                            Confirmo autorización de tratamiento de datos personales *
                          </span>
                        </label>
                        {errors.autorizacion_datos && <p className="text-xs text-red-600 mt-1">{errors.autorizacion_datos}</p>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <button
                type="button"
                onClick={handleAddParticipante}
                className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700 mt-4"
              >
                <Plus className="h-4 w-4 mr-1" /> Agregar Participante
              </button>
            </section>
          </div>

          <div className="flex items-center justify-end border-t border-slate-200 bg-slate-50 p-6">
            <button
              type="submit"
              disabled={isSaving}
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-blue-600 text-white hover:bg-blue-700 h-10 px-6 py-2 shadow-sm disabled:opacity-50"
            >
              {isSaving ? "Enviando..." : <><Save className="mr-2 h-4 w-4" /> Inscribir Equipo</>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
