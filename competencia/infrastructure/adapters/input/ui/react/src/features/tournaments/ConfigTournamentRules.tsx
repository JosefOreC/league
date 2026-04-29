import { useState } from "react";
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

  const [puntajeMaximo, setPuntajeMaximo] = useState("100");
  const [penalizaciones, setPenalizaciones] = useState("");
  const [desempate, setDesempate] = useState("");

  const [errorPeso, setErrorPeso] = useState("");
  const [reglasGuardadas, setReglasGuardadas] = useState(false);

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

  const handleSaveRules = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorPeso("");

    // Validación 1: Pesos
    if (sumaPesos !== 100) {
      setErrorPeso(`La suma de los pesos debe ser 100%. Actualmente suma ${sumaPesos}%`);
      return;
    }

    // Simulando guardado en Backend
    alert("¡Reglas asociadas al torneo correctamente! Ahora puedes publicarlo.");
    setReglasGuardadas(true);
  };

  const handlePublish = () => {
    if (!reglasGuardadas) {
      alert("Error: Faltan configurar las reglas u otros datos obligatorios.");
      return;
    }
    alert("¡Torneo publicado! El estado cambió a 'Inscripciones abiertas'. Se ha notificado a los docentes.");
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
            
            {/* Sección de Criterios */}
            <div className="space-y-4">
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
