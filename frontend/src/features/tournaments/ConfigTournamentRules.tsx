import { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { ArrowLeft, Save, Rocket, Plus, Trash2 } from "lucide-react";

interface Criteria {
  id: string;
  nombre: string;
  descripcion: string;
  peso: number;
}

export function ConfigTournamentRules() {
  const navigate = useNavigate();
  const { id: tournamentId } = useParams();

  const [criterias, setCriterias] = useState<Criteria[]>([
    { id: "1", nombre: "Diseño", descripcion: "Calidad de construcción", peso: 50 },
    { id: "2", nombre: "Desempeño", descripcion: "Funcionamiento en arena", peso: 50 },
  ]);

  const [rules, setRules] = useState({
    minMembers: 2,
    maxMembers: 5,
    minTeams: 4,
    maxTeams: 16,
    accessType: "private",
  });

  const [puntajeMaximo, setPuntajeMaximo] = useState("100");
  const [penalizaciones, setPenalizaciones] = useState("");
  const [desempate, setDesempate] = useState("");

  const [errorPeso, setErrorPeso] = useState("");
  const [reglasGuardadas, setReglasGuardadas] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Cargar datos iniciales
  useEffect(() => {
    const fetchTournament = async () => {
      try {
        const res = await fetch(`http://localhost:8000/competencia/torneo/${tournamentId}/`);
        if (res.ok) {
          const data = await res.json();
          if (data.rules) {
            setRules({
              minMembers: data.rules.min_members,
              maxMembers: data.rules.max_members,
              minTeams: data.rules.min_teams,
              maxTeams: data.rules.max_teams,
              accessType: data.rules.access_type,
            });
            if (data.rules.criterias && data.rules.criterias.length > 0) {
              setCriterias(data.rules.criterias.map((c: any, i: number) => ({
                id: i.toString(),
                nombre: c.name,
                descripcion: c.description,
                peso: c.value * 100
              })));
            }
          }
        }
      } catch (err) {
        console.error("Error al cargar torneo:", err);
      }
    };
    if (tournamentId) fetchTournament();
  }, [tournamentId]);

  // Calcula la suma actual
  const sumaPesos = criterias.reduce((acc, c) => acc + (Number(c.peso) || 0), 0);

  const handleAddCriteria = () => {
    if (criterias.length < 10) {
      setCriterias([...criterias, { id: Date.now().toString(), nombre: "", descripcion: "", peso: 0 }]);
    }
  };

  const handleRemoveCriteria = (id: string) => {
    if (criterias.length > 1) {
      setCriterias(criterias.filter((c) => c.id !== id));
    }
  };

  const handleChangeCriteria = (id: string, field: keyof Criteria, value: string | number) => {
    setCriterias(criterias.map((c) => (c.id === id ? { ...c, [field]: value } : c)));
  };

  const handleSaveRules = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorPeso("");

    if (sumaPesos !== 100) {
      setErrorPeso(`La suma de los pesos debe ser 100%. Actualmente suma ${sumaPesos}%`);
      return;
    }

    setIsLoading(true);
    try {
      const payload = {
        min_members: rules.minMembers,
        max_members: rules.maxMembers,
        min_teams: rules.minTeams,
        max_teams: rules.maxTeams,
        access_type: rules.accessType,
        validation_list: [], // TODO: Agregar selector de instituciones si es privado
        criterias: criterias.map(c => ({
          name: c.nombre,
          description: c.descripcion,
          value: c.peso / 100
        }))
      };

      const res = await fetch(`http://localhost:8000/competencia/torneo/${tournamentId}/rules/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        alert("¡Reglas asociadas al torneo correctamente!");
        setReglasGuardadas(true);
      } else {
        const error = await res.json();
        alert("Error al guardar reglas: " + (error.error || JSON.stringify(error)));
      }
    } catch (error) {
      alert("Error de red: " + error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!reglasGuardadas) {
      alert("Error: Faltan configurar las reglas u otros datos obligatorios.");
      return;
    }
    // En el futuro esto llamará a un endpoint de publicación (status transition)
    alert("¡Torneo publicado! El estado cambió a 'Inscripciones abiertas'.");
    navigate("/dashboard/torneos");
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-10">
      <div className="flex items-center space-x-4 mb-6">
        <Link
          to="/dashboard/torneos"
          className="inline-flex items-center justify-center rounded-md text-slate-500 hover:text-slate-900 transition-colors p-2 hover:bg-slate-100"
        >
          <ArrowLeft className="h-5 w-5" />
          <span className="sr-only">Volver</span>
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Configurar Reglas del Torneo</h1>
          <p className="text-sm text-slate-500">Torneo ID: {tournamentId}</p>
        </div>
      </div>

      <div className="bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
        <form onSubmit={handleSaveRules}>
          <div className="p-6 md:p-8 space-y-8">
            
            {/* Sección: Reglas de Participación */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Reglas de Participación
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Mínimo de equipos</label>
                  <input
                    type="number"
                    value={rules.minTeams}
                    onChange={(e) => setRules({ ...rules, minTeams: parseInt(e.target.value) })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Máximo de equipos</label>
                  <input
                    type="number"
                    value={rules.maxTeams}
                    onChange={(e) => setRules({ ...rules, maxTeams: parseInt(e.target.value) })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Tipo de Acceso</label>
                  <select
                    value={rules.accessType}
                    onChange={(e) => setRules({ ...rules, accessType: e.target.value })}
                    className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="private">Privado (Solo instituciones)</option>
                    <option value="public">Público (Abierto)</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Mín. miembros por equipo</label>
                  <input
                    type="number"
                    value={rules.minMembers}
                    onChange={(e) => setRules({ ...rules, minMembers: parseInt(e.target.value) })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Máx. miembros por equipo</label>
                  <input
                    type="number"
                    value={rules.maxMembers}
                    onChange={(e) => setRules({ ...rules, maxMembers: parseInt(e.target.value) })}
                    className="flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Sección de Criterios */}
            <div className="space-y-4 pt-4 border-t border-slate-100">
              <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                <h3 className="text-lg font-semibold text-slate-900">
                  Criterios de Evaluación
                </h3>
                <span className={`text-sm font-bold ${sumaPesos === 100 ? 'text-green-600' : 'text-orange-500'}`}>
                  Total: {sumaPesos}%
                </span>
              </div>
              
              {errorPeso && (
                <div className="bg-red-50 text-red-700 p-3 rounded-md text-sm font-medium border border-red-200">
                  {errorPeso}
                </div>
              )}

              <div className="space-y-4">
                {criterias.map((c, index) => (
                  <div key={c.id} className="flex gap-4 items-start bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <div className="w-1/3 space-y-2">
                      <label className="text-xs font-medium text-slate-700">Nombre del criterio</label>
                      <input
                        type="text"
                        required
                        value={c.nombre}
                        onChange={(e) => handleChangeCriteria(c.id, "nombre", e.target.value)}
                        className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500"
                        placeholder="Ej. Diseño"
                      />
                    </div>
                    <div className="w-1/2 space-y-2">
                      <label className="text-xs font-medium text-slate-700">Descripción</label>
                      <input
                        type="text"
                        value={c.descripcion}
                        onChange={(e) => handleChangeCriteria(c.id, "descripcion", e.target.value)}
                        className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500"
                        placeholder="Detalles del criterio"
                      />
                    </div>
                    <div className="w-24 space-y-2">
                      <label className="text-xs font-medium text-slate-700">Peso (%)</label>
                      <input
                        type="number"
                        required
                        min="1"
                        max="100"
                        value={c.peso}
                        onChange={(e) => handleChangeCriteria(c.id, "peso", Number(e.target.value))}
                        className="flex h-9 w-full rounded-md border border-slate-300 px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    {criterias.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveCriteria(c.id)}
                        className="mt-6 p-1.5 text-red-500 hover:bg-red-50 rounded-md transition-colors"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {criterias.length < 10 && (
                <button
                  type="button"
                  onClick={handleAddCriteria}
                  className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Agregar criterio
                </button>
              )}
            </div>

            {/* Otras Reglas */}
            <div className="space-y-4 pt-4 border-t border-slate-100">
              <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
                Otras Especificaciones
              </h3>
              <div className="grid grid-cols-1 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Puntaje Máximo</label>
                  <input
                    type="number"
                    value={puntajeMaximo}
                    onChange={(e) => setPuntajeMaximo(e.target.value)}
                    className="flex h-10 w-full md:w-1/3 rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Penalizaciones</label>
                  <textarea
                    rows={2}
                    value={penalizaciones}
                    onChange={(e) => setPenalizaciones(e.target.value)}
                    className="flex w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe las penalizaciones..."
                  ></textarea>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Condiciones de Desempate</label>
                  <textarea
                    rows={2}
                    value={desempate}
                    onChange={(e) => setDesempate(e.target.value)}
                    className="flex w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe cómo se resolverán los empates..."
                  ></textarea>
                </div>
              </div>
            </div>

          </div>

          <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 p-6">
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 h-10 px-4 py-2 shadow-sm"
            >
              <Save className="mr-2 h-4 w-4" />
              Guardar Reglas
            </button>

            <button
              type="button"
              onClick={handlePublish}
              disabled={!reglasGuardadas}
              className={`inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors h-10 px-6 py-2 shadow-sm ${
                reglasGuardadas 
                  ? "bg-green-600 text-white hover:bg-green-700" 
                  : "bg-slate-200 text-slate-400 cursor-not-allowed"
              }`}
            >
              <Rocket className="mr-2 h-4 w-4" />
              Publicar Torneo
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
