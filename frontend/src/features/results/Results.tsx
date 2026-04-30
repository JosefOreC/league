import { useState, useEffect } from "react";
import { Activity, PlusCircle, Trophy, Medal, Star, Timer, AlertCircle, Save, CheckCircle, RefreshCw } from "lucide-react";
import { registerMatchResults, finalizeMatch, getTournamentStandings } from "../../services/tournamentService";
import { EstadoResultado, PosicionTabla } from "../../types/tournament";
import axios from "axios";

const mockCriterios = [
  { id: "c1", nombre: "Precisión", tipo_dato: "NUMERICO", valor_minimo: 0, valor_maximo: 100 },
  { id: "c2", nombre: "Tiempo", tipo_dato: "NUMERICO", valor_minimo: 0, valor_maximo: 300 },
];

export function Results() {
  const [showModal, setShowModal] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [generalError, setGeneralError] = useState<string | null>(null);

  // Datos de prueba, en una implementación real provienen de la URL o del contexto de la aplicación
  const [torneoId] = useState("t1"); 
  const [partidoId] = useState("p1"); 
  const [equipo1Id] = useState("1"); 
  const [equipo2Id] = useState("2"); 

  const [standings, setStandings] = useState<PosicionTabla[]>([]);
  
  const [valoresEq1, setValoresEq1] = useState<Record<string, number>>({});
  const [valoresEq2, setValoresEq2] = useState<Record<string, number>>({});

  const fetchStandings = async () => {
    setIsLoading(true);
    try {
      const data = await getTournamentStandings(torneoId);
      // El backend se encarga de ordenar los equipos; nosotros solo actualizamos el estado
      setStandings(data);
    } catch (err) {
      console.error("Error fetching standings:", err);
      // Opcionalmente se puede mostrar un mensaje de error en la interfaz
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStandings();
  }, [torneoId]);

  const handleValorChange = (equipoId: string, criterioId: string, value: string) => {
    const numValue = parseFloat(value);
    if (equipoId === equipo1Id) {
      setValoresEq1(prev => ({ ...prev, [criterioId]: isNaN(numValue) ? 0 : numValue }));
    } else {
      setValoresEq2(prev => ({ ...prev, [criterioId]: isNaN(numValue) ? 0 : numValue }));
    }
  };

  const handleSaveParcial = async () => {
    setGeneralError(null);
    setIsSaving(true);
    try {
      const resultados = [
        ...mockCriterios.map(c => ({
          criterio_id: c.id,
          equipo_id: equipo1Id,
          valor_registrado: valoresEq1[c.id] || 0,
          estado_resultado: EstadoResultado.PARTIAL
        })),
        ...mockCriterios.map(c => ({
          criterio_id: c.id,
          equipo_id: equipo2Id,
          valor_registrado: valoresEq2[c.id] || 0,
          estado_resultado: EstadoResultado.PARTIAL
        }))
      ];
      
      await registerMatchResults(torneoId, partidoId, resultados);
      alert("Resultados parciales guardados correctamente");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        const data = err.response?.data;
        if (status === 422) {
          setGeneralError(data?.error || "Error de validación de rangos");
        } else if (status === 409) {
          setGeneralError(data?.error || "El partido no está en estado válido para registrar resultados");
        } else {
          setGeneralError("Error inesperado al guardar resultados");
        }
      } else {
        setGeneralError("Error de red");
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleFinalizar = async () => {
    setGeneralError(null);
    setIsSaving(true);
    try {
      await finalizeMatch(torneoId, partidoId);
      alert("Partido finalizado y ganador calculado");
      setShowModal(false);
      // Obtenemos la tabla de posiciones inmediatamente después de finalizar un partido para mantener los datos en tiempo real
      fetchStandings();
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setGeneralError(err.response?.data?.error || "Error al finalizar partido");
      } else {
        setGeneralError("Error de red");
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
            Resultados y Posiciones
            <span className="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">
              <Activity className="w-3 h-3 mr-1 animate-pulse" /> En vivo
            </span>
          </h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchStandings}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 h-10 px-4 py-2 shadow-sm transition-colors"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 h-10 px-4 py-2 shadow-sm transition-colors"
          >
            <PlusCircle className="mr-2 h-4 w-4" />
            Evaluar Partido Activo
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-slate-900 flex items-center">
              <Trophy className="h-5 w-5 mr-2 text-yellow-500" />
              Tabla de posiciones
            </h2>
          </div>
          
          <div className="overflow-x-auto">
            {isLoading ? (
              <div className="p-8 text-center text-slate-500 flex items-center justify-center">
                <RefreshCw className="mr-2 h-5 w-5 animate-spin" /> Cargando posiciones...
              </div>
            ) : standings.length === 0 ? (
              <div className="p-8 text-center text-slate-500">No hay datos de posiciones disponibles.</div>
            ) : (
              <table className="w-full text-sm text-left text-slate-600">
                <thead className="text-xs text-slate-500 uppercase bg-slate-50/50 border-b border-slate-100">
                  <tr>
                    <th scope="col" className="px-6 py-4 font-semibold w-16">Pos</th>
                    <th scope="col" className="px-6 py-4 font-semibold">Equipo</th>
                    <th scope="col" className="px-6 py-4 font-semibold text-center">PJ</th>
                    <th scope="col" className="px-6 py-4 font-semibold text-center">PG</th>
                    <th scope="col" className="px-6 py-4 font-semibold text-center">PE</th>
                    <th scope="col" className="px-6 py-4 font-semibold text-center">PP</th>
                    <th scope="col" className="px-6 py-4 font-semibold text-center">DIF</th>
                    <th scope="col" className="px-6 py-4 font-semibold text-center">Pts</th>
                  </tr>
                </thead>
                <tbody>
                  {standings.map((row, i) => (
                    <tr key={row.equipo_id} className="bg-white border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 text-center font-semibold">
                        {i === 0 ? <Medal className="h-6 w-6 text-yellow-500 mx-auto" /> : 
                         i === 1 ? <Medal className="h-6 w-6 text-slate-400 mx-auto" /> :
                         i === 2 ? <Medal className="h-6 w-6 text-orange-400 mx-auto" /> :
                         <span className="text-slate-400">{row.posicion || i + 1}</span>}
                      </td>
                      <td className="px-6 py-4 font-medium text-slate-900">{row.equipo_nombre || `Equipo ${row.equipo_id}`}</td>
                      <td className="px-6 py-4 text-center text-slate-500">{row.partidos_jugados}</td>
                      <td className="px-6 py-4 text-center text-slate-500">{row.victorias}</td>
                      <td className="px-6 py-4 text-center text-slate-500">{row.empates}</td>
                      <td className="px-6 py-4 text-center text-slate-500">{row.derrotas}</td>
                      <td className="px-6 py-4 text-center text-slate-500">{row.diferencia_puntaje}</td>
                      <td className="px-6 py-4 text-center font-bold text-blue-600">{row.puntos}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div className="lg:col-span-1 space-y-6">
          <div className="bg-slate-900 rounded-xl p-6 shadow-sm text-white relative overflow-hidden">
            <div className="absolute -right-4 -top-4 opacity-10"><Trophy className="w-32 h-32" /></div>
            <h3 className="font-semibold text-slate-200 mb-2 flex items-center relative z-10">
              <Star className="h-4 w-4 mr-2 text-yellow-400" /> Líder Actual
            </h3>
            <div className="text-xl font-bold mb-1 relative z-10 truncate">
              {standings.length > 0 ? (standings[0].equipo_nombre || `Equipo ${standings[0].equipo_id}`) : "N/A"}
            </div>
            <div className="text-sm text-slate-400 relative z-10">
              {standings.length > 0 ? `${standings[0].puntos} pts` : "N/A"}
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
              <h2 className="text-lg font-bold text-slate-900 flex items-center">
                <PlusCircle className="mr-2 h-5 w-5 text-blue-600" /> Evaluar Enfrentamiento
              </h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">&times;</button>
            </div>
            
            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              {generalError && (
                <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm">
                  <AlertCircle size={16} />
                  <span>{generalError}</span>
                </div>
              )}

              <div className="grid grid-cols-2 gap-8 text-center mb-6">
                <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                  <h3 className="text-sm text-blue-600 font-semibold uppercase mb-1">Local</h3>
                  <p className="text-xl font-bold text-slate-900">RoboKids Alpha</p>
                </div>
                <div className="p-4 bg-red-50 rounded-xl border border-red-100">
                  <h3 className="text-sm text-red-600 font-semibold uppercase mb-1">Visitante</h3>
                  <p className="text-xl font-bold text-slate-900">AndesBot</p>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-slate-700 border-b pb-2">Criterios de Evaluación</h3>
                <div className="space-y-6">
                  {mockCriterios.map(criterio => (
                    <div key={criterio.id} className="grid grid-cols-12 gap-4 items-center">
                      <div className="col-span-4">
                        <label className="text-sm font-medium text-slate-900">{criterio.nombre}</label>
                        <p className="text-xs text-slate-500">[{criterio.valor_minimo} - {criterio.valor_maximo}]</p>
                      </div>
                      <div className="col-span-4">
                        <input
                          type="number"
                          placeholder="Valor Local"
                          value={valoresEq1[criterio.id] ?? ""}
                          onChange={(e) => handleValorChange(equipo1Id, criterio.id, e.target.value)}
                          className="w-full text-center rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div className="col-span-4">
                        <input
                          type="number"
                          placeholder="Valor Visitante"
                          value={valoresEq2[criterio.id] ?? ""}
                          onChange={(e) => handleValorChange(equipo2Id, criterio.id, e.target.value)}
                          className="w-full text-center rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-between gap-3">
              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="justify-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleSaveParcial}
                  disabled={isSaving}
                  className="inline-flex items-center justify-center rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 disabled:opacity-50"
                >
                  <Save className="mr-2 h-4 w-4" /> Guardar Parcial
                </button>
                <button
                  type="button"
                  onClick={handleFinalizar}
                  disabled={isSaving}
                  className="inline-flex items-center justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50 shadow-sm"
                >
                  <CheckCircle className="mr-2 h-4 w-4" /> Finalizar y Calcular
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
