import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { ArrowLeft, Save, Rocket, AlertCircle, Plus, Trash2 } from "lucide-react";
import {
  TipoTorneo,
  EstadoTorneo,
  CriterioByeKO,
  CriterioDesempate,
} from "../../types/tournament";
import type {
  Tournament,
  ConfigKnockout,
  ConfigRoundRobin,
  ConfigHybrid,
} from "../../types/tournament";
import {
  getTournamentById,
  configTournamentRules,
  openRegistrations,
} from "../../services/tournamentService";
import { 
  recomendarDificultad, 
  recomendarFormato, 
  generarReglasOperativas,
  generarCriteriosEvaluacion,
  responderRecomendacion
} from "../../services/aiService";
import { 
  RecomendacionDificultadResponse, 
  RecomendacionFormatoResponse, 
  ReglaOperativa 
} from "../../types/ai";
import { Sparkles, BrainCircuit, Wand2, CheckCircle, XCircle } from "lucide-react";
import axios from "axios";

// ─── Funciones de apoyo ──────────────────────────────────────────────────────────────────
function inputCls(err?: boolean) {
  return `flex h-10 w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${err ? "border-red-400" : "border-slate-300"}`;
}
function Err({ msg }: { msg?: string }) {
  return msg ? <p className="mt-1 text-xs text-red-600">{msg}</p> : null;
}

// ─── Componente para Criterios de Evaluación ──────────────────────────────────────────────────
interface Criterio { id: string; nombre: string; descripcion: string; peso: number; }

function CriteriosSection({
  criterios,
  setCriterios,
  onGenerar,
  isGenerando
}: {
  criterios: Criterio[];
  setCriterios: React.Dispatch<React.SetStateAction<Criterio[]>>;
  onGenerar: () => void;
  isGenerando: boolean;
}) {
  const suma = criterios.reduce((a, c) => a + (Number(c.peso) || 0), 0);
  const change = (id: string, f: keyof Criterio, v: string | number) =>
    setCriterios(prev => prev.map(c => c.id === id ? { ...c, [f]: v } : c));

  return (
    <section className="space-y-4 pt-4 border-t border-slate-100">
      <div className="flex justify-between items-center border-b border-slate-100 pb-2">
        <h3 className="text-lg font-semibold text-slate-900">Criterios de Evaluación</h3>
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={onGenerar}
            disabled={isGenerando}
            className="inline-flex shrink-0 items-center justify-center rounded-md bg-purple-100 px-3 py-1.5 text-xs font-medium text-purple-700 transition-colors hover:bg-purple-200 disabled:opacity-50"
          >
            <Wand2 className="h-3 w-3 mr-1.5" />
            {isGenerando ? "Generando..." : "Propuesta IA"}
          </button>
          <span className={`text-sm font-bold ${suma === 100 ? "text-green-600" : "text-orange-500"}`}>
            Total: {suma}%
          </span>
        </div>
      </div>
      {suma !== 100 && suma > 0 && (
        <p className="text-xs text-orange-600 bg-orange-50 border border-orange-200 rounded-md p-2">
          La suma debe ser exactamente 100%. Actualmente: {suma}%
        </p>
      )}
      <div className="space-y-3">
        {criterios.map(c => (
          <div key={c.id} className="flex gap-3 items-start bg-slate-50 p-4 rounded-lg border border-slate-200">
            <div className="flex-1 space-y-1">
              <label className="text-xs font-medium text-slate-600">Nombre</label>
              <input required value={c.nombre} onChange={e => change(c.id, "nombre", e.target.value)}
                className={inputCls()} placeholder="Ej. Diseño" />
            </div>
            <div className="flex-[2] space-y-1">
              <label className="text-xs font-medium text-slate-600">Descripción</label>
              <input value={c.descripcion} onChange={e => change(c.id, "descripcion", e.target.value)}
                className={inputCls()} placeholder="Detalle del criterio" />
            </div>
            <div className="w-24 space-y-1">
              <label className="text-xs font-medium text-slate-600">Peso (%)</label>
              <input type="number" min={1} max={100} required value={c.peso}
                onChange={e => change(c.id, "peso", Number(e.target.value))} className={inputCls()} />
            </div>
            {criterios.length > 1 && (
              <button type="button" onClick={() => setCriterios(prev => prev.filter(x => x.id !== c.id))}
                className="mt-6 p-1.5 text-red-500 hover:bg-red-50 rounded-md transition-colors">
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        ))}
      </div>
      {criterios.length < 10 && (
        <button type="button"
          onClick={() => setCriterios(prev => [...prev, { id: Date.now().toString(), nombre: "", descripcion: "", peso: 0 }])}
          className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700">
          <Plus className="h-4 w-4 mr-1" /> Agregar criterio
        </button>
      )}
    </section>
  );
}

// ─── Componente para Reglas Operativas (HU-IA-04) ──────────────────────────────────────────
function ReglasOperativasSection({
  reglas,
  setReglas,
  onGenerar,
  isGenerando
}: {
  reglas: ReglaOperativa[];
  setReglas: React.Dispatch<React.SetStateAction<ReglaOperativa[]>>;
  onGenerar: () => void;
  isGenerando: boolean;
}) {
  const change = (idx: number, f: keyof ReglaOperativa, v: string) => {
    setReglas(prev => {
      const copy = [...prev];
      copy[idx] = { ...copy[idx], [f]: v, valor_editado: f === "valor" ? v : copy[idx].valor_editado };
      return copy;
    });
  };

  return (
    <section className="space-y-4 pt-4 border-t border-slate-100">
      <div className="flex justify-between items-center border-b border-slate-100 pb-2">
        <h3 className="text-lg font-semibold text-slate-900">Reglas Operativas</h3>
        <button
          type="button"
          onClick={onGenerar}
          disabled={isGenerando}
          className="inline-flex shrink-0 items-center justify-center rounded-md bg-purple-100 px-3 py-1.5 text-xs font-medium text-purple-700 transition-colors hover:bg-purple-200 disabled:opacity-50"
        >
          <Wand2 className="h-3 w-3 mr-1.5" />
          {isGenerando ? "Generando..." : "Generar con IA"}
        </button>
      </div>
      <div className="space-y-3">
        {reglas.map((r, i) => (
          <div key={i} className="grid grid-cols-1 md:grid-cols-12 gap-3 items-start bg-slate-50 p-4 rounded-lg border border-slate-200">
            <div className="md:col-span-3 space-y-1">
              <label className="text-xs font-medium text-slate-600">Nombre</label>
              <input value={r.nombre} onChange={e => change(i, "nombre", e.target.value)} className={inputCls()} />
            </div>
            <div className="md:col-span-5 space-y-1">
              <label className="text-xs font-medium text-slate-600">Descripción</label>
              <input value={r.descripcion} onChange={e => change(i, "descripcion", e.target.value)} className={inputCls()} />
            </div>
            <div className="md:col-span-2 space-y-1">
              <label className="text-xs font-medium text-slate-600">Valor</label>
              <input value={r.valor_editado ?? r.valor} onChange={e => change(i, "valor", e.target.value)} className={inputCls()} />
            </div>
            <div className="md:col-span-1 space-y-1">
              <label className="text-xs font-medium text-slate-600">Unidad</label>
              <input value={r.unidad || ""} onChange={e => change(i, "unidad", e.target.value)} className={inputCls()} />
            </div>
            <div className="md:col-span-1 text-right mt-6">
              <button type="button" onClick={() => setReglas(prev => prev.filter((_, idx) => idx !== i))} className="p-1.5 text-red-500 hover:bg-red-50 rounded-md transition-colors">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
        {reglas.length === 0 && (
          <p className="text-sm text-slate-500 italic">No hay reglas definidas. Usa la IA para generar sugerencias según el nivel.</p>
        )}
      </div>
    </section>
  );
}

// ─── Panel de Configuración Knockout ───────────────────────────────────────────────────────────
function KnockoutPanel({ cfg, setCfg }: { cfg: ConfigKnockout; setCfg: (v: ConfigKnockout) => void }) {
  return (
    <section className="space-y-4 pt-4 border-t border-slate-100">
      <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
        Parámetros — Eliminación Directa (Knockout)
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <label className="flex items-center gap-3 cursor-pointer select-none">
          <input type="checkbox" checked={cfg.semilla_habilitada}
            onChange={e => setCfg({ ...cfg, semilla_habilitada: e.target.checked })}
            className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
          <span className="text-sm font-medium text-slate-700">Semilla habilitada</span>
        </label>
        <label className="flex items-center gap-3 cursor-pointer select-none">
          <input type="checkbox" checked={cfg.tercer_lugar}
            onChange={e => setCfg({ ...cfg, tercer_lugar: e.target.checked })}
            className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
          <span className="text-sm font-medium text-slate-700">Partido por 3er lugar</span>
        </label>
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Criterio para Byes</label>
          <select value={cfg.criterio_bye} onChange={e => setCfg({ ...cfg, criterio_bye: e.target.value as CriterioByeKO })}
            className={inputCls()}>
            <option value={CriterioByeKO.RANKING}>Por Ranking</option>
            <option value={CriterioByeKO.ALEATORIO}>Aleatorio</option>
          </select>
        </div>
      </div>
    </section>
  );
}

// ─── Panel de Configuración Round Robin ────────────────────────────────────────────────────────
const CRITERIOS_OPTS = [
  { value: CriterioDesempate.PUNTOS, label: "Puntos" },
  { value: CriterioDesempate.DIFF_PUNTAJE, label: "Diferencia de puntaje" },
  { value: CriterioDesempate.ENFRENTAMIENTO_DIRECTO, label: "Enfrentamiento directo" },
  { value: CriterioDesempate.PUNTAJE_FAVOR, label: "Puntaje a favor" },
  { value: CriterioDesempate.NOMBRE_ALFABETICO, label: "Nombre alfabético" },
];

function DesempateSelector({ value, onChange }: {
  value: CriterioDesempate[];
  onChange: (v: CriterioDesempate[]) => void;
}) {
  const toggle = (c: CriterioDesempate) =>
    onChange(value.includes(c) ? value.filter(x => x !== c) : [...value, c]);
  return (
    <div className="space-y-1">
      <label className="text-sm font-medium text-slate-700">Criterios de desempate (orden de prioridad)</label>
      <div className="flex flex-wrap gap-2 mt-1">
        {CRITERIOS_OPTS.map(opt => (
          <label key={opt.value} className="flex items-center gap-1.5 text-xs cursor-pointer select-none
            bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-full transition-colors">
            <input type="checkbox" checked={value.includes(opt.value)} onChange={() => toggle(opt.value)}
              className="h-3 w-3 text-blue-600" />
            {opt.label}
          </label>
        ))}
      </div>
    </div>
  );
}

function RoundRobinPanel({ cfg, setCfg, errors }: {
  cfg: ConfigRoundRobin;
  setCfg: (v: ConfigRoundRobin) => void;
  errors: Record<string, string>;
}) {
  return (
    <section className="space-y-4 pt-4 border-t border-slate-100">
      <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
        Parámetros — Round Robin (Todos contra todos)
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Número de vueltas</label>
          <select value={cfg.num_vueltas} onChange={e => setCfg({ ...cfg, num_vueltas: Number(e.target.value) as 1 | 2 })}
            className={inputCls()}>
            <option value={1}>1 — Solo ida</option>
            <option value={2}>2 — Ida y vuelta</option>
          </select>
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Puntos victoria</label>
          <input type="number" min={0} value={cfg.puntos_victoria}
            onChange={e => setCfg({ ...cfg, puntos_victoria: Number(e.target.value) })}
            className={inputCls(!!errors.puntos_victoria)} />
          <Err msg={errors.puntos_victoria} />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Puntos empate</label>
          <input type="number" min={0} value={cfg.puntos_empate}
            onChange={e => setCfg({ ...cfg, puntos_empate: Number(e.target.value) })}
            className={inputCls(!!errors.puntos_empate)} />
          <Err msg={errors.puntos_empate} />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Puntos derrota</label>
          <input type="number" min={0} value={cfg.puntos_derrota}
            onChange={e => setCfg({ ...cfg, puntos_derrota: Number(e.target.value) })}
            className={inputCls(!!errors.puntos_derrota)} />
          <Err msg={errors.puntos_derrota} />
        </div>
      </div>
      <DesempateSelector value={cfg.criterios_desempate}
        onChange={v => setCfg({ ...cfg, criterios_desempate: v })} />
    </section>
  );
}

// ─── Panel de Configuración Híbrido ────────────────────────────────────────────────────────────
function HybridPanel({ cfg, setCfg, errors }: {
  cfg: ConfigHybrid;
  setCfg: (v: ConfigHybrid) => void;
  errors: Record<string, string>;
}) {
  return (
    <section className="space-y-4 pt-4 border-t border-slate-100">
      <h3 className="text-lg font-semibold text-slate-900 border-b border-slate-100 pb-2">
        Parámetros — Híbrido (Grupos + Eliminación)
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Equipos por grupo (3–5)</label>
          <input type="number" min={3} max={5} value={cfg.equipos_por_grupo}
            onChange={e => setCfg({ ...cfg, equipos_por_grupo: Number(e.target.value) })}
            className={inputCls(!!errors.equipos_por_grupo)} />
          <Err msg={errors.equipos_por_grupo} />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Clasificados por grupo</label>
          <input type="number" min={1} value={cfg.clasificados_por_grupo}
            onChange={e => setCfg({ ...cfg, clasificados_por_grupo: Number(e.target.value) })}
            className={inputCls(!!errors.clasificados_por_grupo)} />
          <Err msg={errors.clasificados_por_grupo} />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Vueltas en fase de grupos</label>
          <select value={cfg.num_vueltas_grupos}
            onChange={e => setCfg({ ...cfg, num_vueltas_grupos: Number(e.target.value) as 1 | 2 })}
            className={inputCls()}>
            <option value={1}>1 — Solo ida</option>
            <option value={2}>2 — Ida y vuelta</option>
          </select>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="space-y-1">
          <label className="text-sm font-medium text-slate-700">Formato fase final</label>
          <input readOnly value="KNOCKOUT"
            className="flex h-10 w-40 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500" />
        </div>
        <label className="flex items-center gap-3 cursor-pointer select-none mt-5">
          <input type="checkbox" checked={cfg.tercer_lugar_final}
            onChange={e => setCfg({ ...cfg, tercer_lugar_final: e.target.checked })}
            className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
          <span className="text-sm font-medium text-slate-700">3er lugar en fase final</span>
        </label>
      </div>
      <DesempateSelector value={cfg.criterios_desempate}
        onChange={v => setCfg({ ...cfg, criterios_desempate: v })} />
    </section>
  );
}

// ─── Componente Principal de Reglas ─────────────────────────────────────────────────────
export function ConfigTournamentRules() {
  const navigate = useNavigate();
  const { id: tournamentId } = useParams<{ id: string }>();

  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [isLocked, setIsLocked] = useState(false); // torneo ya publicado

  const [criterios, setCriterios] = useState<Criterio[]>([
    { id: "1", nombre: "Diseño", descripcion: "Calidad de construcción", peso: 50 },
    { id: "2", nombre: "Desempeño", descripcion: "Funcionamiento en arena", peso: 50 },
  ]);

  // Estado para reglas operativas generadas por IA
  const [reglasOperativas, setReglasOperativas] = useState<ReglaOperativa[]>([]);

  // Estado para las configuraciones por cada tipo de torneo
  const [cfgKO, setCfgKO] = useState<ConfigKnockout>({
    semilla_habilitada: true,
    tercer_lugar: true,
    criterio_bye: CriterioByeKO.RANKING,
  });
  const [cfgRR, setCfgRR] = useState<ConfigRoundRobin>({
    num_vueltas: 1,
    puntos_victoria: 3,
    puntos_empate: 1,
    puntos_derrota: 0,
    criterios_desempate: [CriterioDesempate.PUNTOS, CriterioDesempate.DIFF_PUNTAJE],
  });
  const [cfgHY, setCfgHY] = useState<ConfigHybrid>({
    equipos_por_grupo: 4,
    clasificados_por_grupo: 2,
    num_vueltas_grupos: 1,
    formato_fase_final: "KNOCKOUT",
    tercer_lugar_final: true,
    criterios_desempate: [CriterioDesempate.PUNTOS, CriterioDesempate.DIFF_PUNTAJE],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [configGuardada, setConfigGuardada] = useState(false);

  // Estados de IA para la recomendación de dificultad
  const [recomendacionIA, setRecomendacionIA] = useState<RecomendacionDificultadResponse | null>(null);
  const [isRecomendando, setIsRecomendando] = useState(false);
  const [errorRecomendacion, setErrorRecomendacion] = useState<string | null>(null);

  // Estados de IA para formato
  const [recomendacionFormato, setRecomendacionFormato] = useState<RecomendacionFormatoResponse | null>(null);
  const [isRecomendandoFormato, setIsRecomendandoFormato] = useState(false);
  const [formatoObjetivo, setFormatoObjetivo] = useState("");
  const [formatoDias, setFormatoDias] = useState<number | "">("");

  // Estado de IA para reglas y criterios
  const [isGenerandoReglas, setIsGenerandoReglas] = useState(false);
  const [isGenerandoCriterios, setIsGenerandoCriterios] = useState(false);

  // Funciones Human-in-the-Loop (HU-IA-06)
  const [rechazoMotivo, setRechazoMotivo] = useState<Record<string, string>>({});
  const [procesandoHitl, setProcesandoHitl] = useState<Record<string, boolean>>({});

  const handleResponderHitl = async (sesionId: string, accion: "ACEPTAR" | "RECHAZAR", formType: "DIFICULTAD" | "FORMATO") => {
    setProcesandoHitl(prev => ({ ...prev, [sesionId]: true }));
    try {
      await responderRecomendacion(sesionId, { accion, motivo: rechazoMotivo[sesionId] });
      // Limpiamos de la vista si se rechaza
      if (accion === "RECHAZAR") {
        if (formType === "DIFICULTAD") setRecomendacionIA(null);
        if (formType === "FORMATO") setRecomendacionFormato(null);
      } else {
        // En un caso real, aquí el frontend también "aceptaría" configurando los datos correspondientes.
        if (formType === "FORMATO" && recomendacionFormato) {
          // Asignar el formato recomendado
          // Nota: El tipo de torneo no se puede cambiar localmente de forma tan directa sin afectar el objeto 'tournament', 
          // pero el backend ya tomaría nota.
          setGeneralError("Formato aceptado y registrado por la IA.");
        }
      }
    } catch (err) {
      setGeneralError("Error al registrar la acción de IA.");
    } finally {
      setProcesandoHitl(prev => ({ ...prev, [sesionId]: false }));
    }
  };

  const handleRecomendarDificultad = async () => {
    if (!tournamentId) return;
    setIsRecomendando(true);
    setErrorRecomendacion(null);
    setRecomendacionIA(null);
    try {
      const resp = await recomendarDificultad(tournamentId);
      setRecomendacionIA(resp);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 422) {
          setErrorRecomendacion(err.response.data.error || "Se requieren al menos 2 equipos aprobados.");
        } else {
          setErrorRecomendacion("Error al generar recomendación.");
        }
      } else {
        setErrorRecomendacion("Error de conexión.");
      }
    } finally {
      setIsRecomendando(false);
    }
  };

  const handleRecomendarFormato = async () => {
    if (!tournamentId) return;
    setIsRecomendandoFormato(true);
    setRecomendacionFormato(null);
    try {
      const dias = formatoDias ? Number(formatoDias) : undefined;
      const resp = await recomendarFormato(tournamentId, formatoObjetivo, dias);
      setRecomendacionFormato(resp);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        setGeneralError(err.response.data.error || "Faltan datos para la recomendación");
      } else {
        setGeneralError("Error al recomendar formato");
      }
    } finally {
      setIsRecomendandoFormato(false);
    }
  };

  const handleGenerarReglas = async () => {
    if (!tournamentId) return;
    setIsGenerandoReglas(true);
    try {
      const resp = await generarReglasOperativas(tournamentId);
      setReglasOperativas(resp);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        setGeneralError(err.response.data.error || "Se requiere definir el nivel de dificultad primero.");
      } else {
        setGeneralError("Error al generar reglas operativas.");
      }
    } finally {
      setIsGenerandoReglas(false);
    }
  };

  const handleGenerarCriterios = async () => {
    if (!tournamentId) return;
    setIsGenerandoCriterios(true);
    try {
      const resp = await generarCriteriosEvaluacion(tournamentId);
      const mapeados: Criterio[] = resp.map(r => ({
        id: r.id,
        nombre: r.nombre,
        descripcion: r.descripcion,
        peso: Number(r.peso_porcentual)
      }));
      setCriterios(mapeados);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 422) {
        setGeneralError(err.response.data.error || "Error al generar rúbricas.");
      } else {
        setGeneralError("Error de conexión al generar rúbricas.");
      }
    } finally {
      setIsGenerandoCriterios(false);
    }
  };

  // Obtener los datos del torneo al iniciar el componente
  useEffect(() => {
    if (!tournamentId) return;
    getTournamentById(tournamentId).then(t => {
      setTournament(t);
      setIsLocked(t.estado !== EstadoTorneo.DRAFT);
    }).catch(console.error);
  }, [tournamentId]);

  const tipoTorneo = tournament?.tipo_torneo ?? TipoTorneo.KNOCKOUT;
  const sumaPesos = criterios.reduce((a, c) => a + (Number(c.peso) || 0), 0);

  // Función para validar localmente los datos ingresados
  function validate(): Record<string, string> {
    const errs: Record<string, string> = {};
    if (sumaPesos !== 100) errs.criterios = `La suma de los pesos debe ser 100%. Actualmente: ${sumaPesos}%`;

    if (tipoTorneo === TipoTorneo.ROUND_ROBIN) {
      if (cfgRR.puntos_victoria <= cfgRR.puntos_empate)
        errs.puntos_victoria = "puntos_victoria debe ser mayor que puntos_empate";
      if (cfgRR.puntos_empate <= cfgRR.puntos_derrota)
        errs.puntos_empate = "puntos_empate debe ser mayor que puntos_derrota";
      if (cfgRR.puntos_derrota < 0)
        errs.puntos_derrota = "no puede ser negativo";
    }
    if (tipoTorneo === TipoTorneo.HYBRID) {
      if (cfgHY.clasificados_por_grupo >= cfgHY.equipos_por_grupo)
        errs.clasificados_por_grupo = "debe ser menor que equipos_por_grupo";
      if (cfgHY.equipos_por_grupo < 3 || cfgHY.equipos_por_grupo > 5)
        errs.equipos_por_grupo = "debe estar entre 3 y 5";
    }
    return errs;
  }

  const getConfigPayload = () => {
    if (tipoTorneo === TipoTorneo.KNOCKOUT) return cfgKO;
    if (tipoTorneo === TipoTorneo.ROUND_ROBIN) return cfgRR;
    return cfgHY;
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    const localErrs = validate();
    if (Object.keys(localErrs).length > 0) { setErrors(localErrs); return; }
    setErrors({});
    setIsSaving(true);
    try {
      const payloadBackend = {
        tournament_rule: reglasOperativas.map(r => ({
          name: r.nombre,
          description: r.descripcion,
          value: r.valor_editado ?? r.valor,
          unit: r.unidad || ""
        })),
        tournament_config: getConfigPayload(),
        tournament_evaluation: criterios.map((c, i) => ({
          name: c.nombre,
          description: c.descripcion,
          percentage_weight: c.peso,
          order: i + 1,
          higher_is_better: true, 
          data_type: "NUMERICO" 
        }))
      };

      await configTournamentRules(tournamentId!, payloadBackend);
      setConfigGuardada(true);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        const data = err.response?.data;
        if (status === 409) {
          setGeneralError(data?.detail ?? "El tipo de torneo es inmutable una vez publicado.");
        } else if (status === 422 || status === 400) {
          if (data?.error) setGeneralError(data.error);
          else if (data?.campo) setErrors({ [data.campo]: data.error });
          else setGeneralError("Datos inválidos. Revisa los campos.");
        } else {
          setGeneralError("Error inesperado. Intente nuevamente.");
        }
      } else {
        setGeneralError("Error de conexión.");
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!configGuardada) { setGeneralError("Guarda la configuración antes de abrir inscripciones."); return; }
    setIsPublishing(true);
    setGeneralError(null);
    try {
      await openRegistrations(tournamentId!);
      navigate("/dashboard/torneos");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setGeneralError(err.response?.data?.detail ?? err.response?.data?.error ?? "No se pudieron abrir las inscripciones.");
      } else {
        setGeneralError("Error de conexión.");
      }
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto pb-10">
      {/* Sección del encabezado del componente */}
      <div className="flex items-center space-x-4 mb-6">
        <Link to="/dashboard/torneos"
          className="inline-flex items-center justify-center rounded-md text-slate-500 hover:text-slate-900 p-2 hover:bg-slate-100 transition-colors">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Configurar Formato de Competencia
          </h1>
          <p className="text-sm text-slate-500">
            Torneo ID: {tournamentId}
            {tournament && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                {tournament.tipo_torneo}
              </span>
            )}
            {isLocked && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
                Solo lectura — ya publicado
              </span>
            )}
          </p>
        </div>
      </div>

      {/* Visualización de errores generales */}
      {generalError && (
        <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm">
          <AlertCircle size={16} className="shrink-0" />
          <span>{generalError}</span>
        </div>
      )}

      {/* ── Recomendación IA (HU-IA-02) ── */}
      <div className="bg-purple-50 shadow-sm border border-purple-100 rounded-xl overflow-hidden p-6 mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
          <div>
            <h3 className="text-lg font-semibold text-purple-900 flex items-center">
              <BrainCircuit className="h-5 w-5 text-purple-600 mr-2" />
              Asesor IA: Nivel de Dificultad
            </h3>
            <p className="text-sm text-purple-700 mt-1">
              Analiza el perfil de los equipos inscritos para obtener el nivel de dificultad ideal.
            </p>
          </div>
          <button
            type="button"
            onClick={handleRecomendarDificultad}
            disabled={isRecomendando}
            className="inline-flex shrink-0 items-center justify-center rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700 disabled:opacity-50"
          >
            {isRecomendando ? "Analizando..." : "Generar Recomendación"}
          </button>
        </div>

        {errorRecomendacion && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-200 p-3 rounded-md flex items-center">
            <AlertCircle className="h-4 w-4 mr-2" />
            {errorRecomendacion}
          </div>
        )}

        {recomendacionIA && (
          <div className="bg-white border border-purple-200 rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center">
              <div className="font-semibold text-slate-800">
                Nivel Recomendado: <span className="text-purple-600">Nivel {recomendacionIA.nivel_recomendado}</span>
              </div>
              <div className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                Confianza: {(recomendacionIA.nivel_confianza * 100).toFixed(0)}%
              </div>
            </div>
            <p className="text-sm text-slate-600">{recomendacionIA.justificacion}</p>
            {recomendacionIA.alertas && recomendacionIA.alertas.length > 0 && (
              <div className="mt-2 pt-2 border-t border-purple-100">
                <p className="text-xs font-semibold text-orange-600 mb-1">Alertas:</p>
                <ul className="list-disc ml-5 text-xs text-orange-700 space-y-1">
                  {recomendacionIA.alertas.map((alerta, idx) => (
                    <li key={idx}>{alerta}</li>
                  ))}
                </ul>
              </div>
            )}
            {/* Controles de Supervisión HITL */}
            <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-purple-100">
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => handleResponderHitl(recomendacionIA.sesion_ia_id, "ACEPTAR", "DIFICULTAD")}
                  disabled={procesandoHitl[recomendacionIA.sesion_ia_id]}
                  className="inline-flex flex-1 items-center justify-center rounded-md bg-green-100 px-3 py-2 text-sm font-medium text-green-700 transition-colors hover:bg-green-200"
                >
                  <CheckCircle className="h-4 w-4 mr-2" /> Aceptar Dificultad
                </button>
                <button
                  type="button"
                  onClick={() => handleResponderHitl(recomendacionIA.sesion_ia_id, "RECHAZAR", "DIFICULTAD")}
                  disabled={procesandoHitl[recomendacionIA.sesion_ia_id] || !rechazoMotivo[recomendacionIA.sesion_ia_id]}
                  className="inline-flex flex-1 items-center justify-center rounded-md bg-red-100 px-3 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-200 disabled:opacity-50"
                >
                  <XCircle className="h-4 w-4 mr-2" /> Rechazar
                </button>
              </div>
              <input
                type="text"
                placeholder="Motivo de rechazo (obligatorio si rechaza)"
                value={rechazoMotivo[recomendacionIA.sesion_ia_id] || ""}
                onChange={e => setRechazoMotivo(prev => ({ ...prev, [recomendacionIA.sesion_ia_id]: e.target.value }))}
                className="w-full text-xs rounded border border-purple-200 px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* ── Recomendación de Formato IA (HU-IA-03) ── */}
      <div className="bg-purple-50 shadow-sm border border-purple-100 rounded-xl overflow-hidden p-6 mb-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-purple-900 flex items-center">
            <Sparkles className="h-5 w-5 text-purple-600 mr-2" />
            Asesor IA: Formato de Competencia
          </h3>
          <p className="text-sm text-purple-700 mt-1">
            Indica tu objetivo y tiempo disponible para sugerirte el modelo ideal (Knockout, Round Robin o Híbrido).
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 mb-4">
          <input
            type="text"
            placeholder="Ej. Evaluar completamente el desempeño"
            value={formatoObjetivo}
            onChange={e => setFormatoObjetivo(e.target.value)}
            className="flex-1 rounded-md border border-purple-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <input
            type="number"
            placeholder="Días disp."
            value={formatoDias}
            onChange={e => setFormatoDias(e.target.value ? Number(e.target.value) : "")}
            className="w-28 rounded-md border border-purple-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            type="button"
            onClick={handleRecomendarFormato}
            disabled={isRecomendandoFormato}
            className="inline-flex shrink-0 items-center justify-center rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700 disabled:opacity-50"
          >
            {isRecomendandoFormato ? "Analizando..." : "Sugerir Formato"}
          </button>
        </div>

        {recomendacionFormato && (
          <div className="bg-white border border-purple-200 rounded-lg p-4 space-y-3">
            <div className="flex justify-between items-center">
              <div className="font-semibold text-slate-800">
                Sugerencia: <span className="text-purple-600">{recomendacionFormato.formato_recomendado}</span>
              </div>
              <div className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-full">
                Confianza: {(recomendacionFormato.nivel_confianza * 100).toFixed(0)}%
              </div>
            </div>
            <p className="text-sm text-slate-600">{recomendacionFormato.justificacion}</p>
            {/* Controles de Supervisión HITL */}
            <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-purple-100">
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => handleResponderHitl(recomendacionFormato.sesion_ia_id, "ACEPTAR", "FORMATO")}
                  disabled={procesandoHitl[recomendacionFormato.sesion_ia_id]}
                  className="inline-flex flex-1 items-center justify-center rounded-md bg-green-100 px-3 py-2 text-sm font-medium text-green-700 transition-colors hover:bg-green-200"
                >
                  <CheckCircle className="h-4 w-4 mr-2" /> Aceptar Formato
                </button>
                <button
                  type="button"
                  onClick={() => handleResponderHitl(recomendacionFormato.sesion_ia_id, "RECHAZAR", "FORMATO")}
                  disabled={procesandoHitl[recomendacionFormato.sesion_ia_id] || !rechazoMotivo[recomendacionFormato.sesion_ia_id]}
                  className="inline-flex flex-1 items-center justify-center rounded-md bg-red-100 px-3 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-200 disabled:opacity-50"
                >
                  <XCircle className="h-4 w-4 mr-2" /> Rechazar
                </button>
              </div>
              <input
                type="text"
                placeholder="Motivo de rechazo (obligatorio si rechaza)"
                value={rechazoMotivo[recomendacionFormato.sesion_ia_id] || ""}
                onChange={e => setRechazoMotivo(prev => ({ ...prev, [recomendacionFormato.sesion_ia_id]: e.target.value }))}
                className="w-full text-xs rounded border border-purple-200 px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
          </div>
        )}
      </div>

      <div className="bg-white shadow-sm border border-slate-200 rounded-xl overflow-hidden">
        <fieldset disabled={isLocked}>
          <form onSubmit={handleSave}>
            <div className="p-6 md:p-8 space-y-0">

              {/* Panel de criterios de evaluación (visible en todos los formatos) */}
              <CriteriosSection 
                criterios={criterios} 
                setCriterios={setCriterios} 
                onGenerar={handleGenerarCriterios}
                isGenerando={isGenerandoCriterios}
              />
              {errors.criterios && (
                <p className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded-md border border-red-200">
                  {errors.criterios}
                </p>
              )}

              {/* Panel dinámico según tipo_torneo */}
              {tipoTorneo === TipoTorneo.KNOCKOUT && (
                <KnockoutPanel cfg={cfgKO} setCfg={setCfgKO} />
              )}
              {tipoTorneo === TipoTorneo.ROUND_ROBIN && (
                <RoundRobinPanel cfg={cfgRR} setCfg={setCfgRR} errors={errors} />
              )}
              {tipoTorneo === TipoTorneo.HYBRID && (
                <HybridPanel cfg={cfgHY} setCfg={setCfgHY} errors={errors} />
              )}

              {/* Panel para reglas operativas generadas por IA */}
              <ReglasOperativasSection
                reglas={reglasOperativas}
                setReglas={setReglasOperativas}
                onGenerar={handleGenerarReglas}
                isGenerando={isGenerandoReglas}
              />
            </div>

            {/* Sección inferior con botones de acción */}
            <div className="flex items-center justify-between border-t border-slate-200 bg-slate-50 p-6">
              <button type="submit" disabled={isSaving || isLocked}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 h-10 px-4 py-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
                {isSaving ? (
                  <><svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>Guardando...</>
                ) : (
                  <><Save className="mr-2 h-4 w-4" />Guardar Configuración</>
                )}
              </button>

              <button type="button" onClick={handlePublish}
                disabled={!configGuardada || isPublishing || isLocked}
                className={`inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors h-10 px-6 py-2 shadow-sm ${
                  configGuardada && !isLocked
                    ? "bg-green-600 text-white hover:bg-green-700"
                    : "bg-slate-200 text-slate-400 cursor-not-allowed"
                }`}>
                {isPublishing ? (
                  <><svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>Abriendo inscripciones...</>
                ) : (
                  <><Rocket className="mr-2 h-4 w-4" />Abrir Inscripciones</>
                )}
              </button>
            </div>
          </form>
        </fieldset>
      </div>
    </div>
  );
}
