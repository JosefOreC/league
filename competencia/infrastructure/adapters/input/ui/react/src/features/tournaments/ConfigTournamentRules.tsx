import { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { ArrowLeft, Save, Send, Plus, Trash2, AlertCircle, Loader2, CheckCircle } from "lucide-react";
import { getTournamentById, configTournamentRules, reviewTournament } from "../../services/tournamentService";
import {
  ConfigKnockout as KOConfig,
  ConfigRoundRobin as RRConfig,
  ConfigHybrid as HYConfig,
  UpdateConfigRequest
} from "../../types/tournament";

type TournamentType = "knockout" | "round_robin" | "hybrid";

interface CriteriaForm {
  id?: string;
  name: string;
  description: string;
  min_value: number;
  max_value: number;
  value: number; // 0.0 – 1.0 (peso)
}

interface RuleForm {
  id?: string;
  min_members: number;
  max_members: number;
  min_teams: number;
  max_teams: number;
  access_type: "public" | "private";
  validation_list: string[];
  date_start_inscription: string;
  date_end_inscription: string;
}

import axios from "axios";

// ── Componente ───────────────────────────────────────────────────────────────

export function ConfigTournamentRules() {
  const { id: tournamentId } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isReadOnly, setIsReadOnly] = useState(false);

  // Datos generales (solo lectura)
  const [meta, setMeta] = useState({ name: "", category: "", state: "", date_start: "", date_end: "" });

  // Reglas operativas
  const [rule, setRule] = useState<RuleForm>({
    min_members: 2, max_members: 5, min_teams: 4, max_teams: 16,
    access_type: "private", validation_list: [],
    date_start_inscription: "", date_end_inscription: "",
  });

  // Formato del torneo
  const [tournamentType, setTournamentType] = useState<TournamentType>("knockout");
  const [koConfig, setKoConfig] = useState<KOConfig>({ seed_enabled: true, third_place: true, best_of: 3 });
  const [rrConfig, setRrConfig] = useState<RRConfig>({ num_rounds: 1, point_to_victory: 3, point_to_draw: 1, point_to_defeat: 0, tie_breaking_criteria: ["DIFF_POINTS", "POINTS_FOR"] });
  const [hyConfig, setHyConfig] = useState<HYConfig>({ teams_for_group: 4, classified_by_group: 2, num_rounds: 1, third_place: false, final_format: "KNOCKOUT" });

  // Criterios de evaluación
  const [criterias, setCriterias] = useState<CriteriaForm[]>([]);
  const [newInstitution, setNewInstitution] = useState("");

  // ── Carga inicial ─────────────────────────────────────────────────────────

  useEffect(() => {
    if (!tournamentId) return;
    (async () => {
      try {
        const t: any = await getTournamentById(tournamentId);
        setIsReadOnly(t.state !== "draft");
        setMeta({ name: t.name, category: t.category, state: t.state, date_start: t.date_start, date_end: t.date_end });

        const r = t.tournament_rule || {};
        setRule({
          id: r.id,
          min_members: r.min_members ?? 2,
          max_members: r.max_members ?? 5,
          min_teams: r.min_teams ?? 4,
          max_teams: r.max_teams ?? 16,
          access_type: r.access_type ?? "private",
          validation_list: r.validation_list ?? [],
          date_start_inscription: r.date_start_inscription ? r.date_start_inscription.substring(0, 10) : "",
          date_end_inscription: r.date_end_inscription ? r.date_end_inscription.substring(0, 10) : "",
        });

        const cfg = t.config_tournament;
        if (cfg) {
          const tp = cfg.type as TournamentType;
          setTournamentType(tp);
          if (tp === "knockout") setKoConfig({ seed_enabled: cfg.config.seed_enabled ?? true, third_place: cfg.config.third_place ?? true, best_of: cfg.config.best_of ?? 3 });
          if (tp === "round_robin") setRrConfig({ num_rounds: cfg.config.num_rounds ?? 1, point_to_victory: cfg.config.point_to_victory ?? 3, point_to_draw: cfg.config.point_to_draw ?? 1, point_to_defeat: cfg.config.point_to_defeat ?? 0, tie_breaking_criteria: cfg.config.tie_breaking_criteria ?? [] });
          if (tp === "hybrid") setHyConfig({ teams_for_group: cfg.config.teams_for_group ?? 4, classified_by_group: cfg.config.classified_by_group ?? 2, num_rounds: cfg.config.num_rounds ?? 1, third_place: cfg.config.third_place ?? false, final_format: cfg.config.final_format ?? "KNOCKOUT" });
        }

        const ev = t.tournament_evaluation;
        if (ev?.criterias?.length) {
          setCriterias(ev.criterias.map((c: any) => ({ id: c.id, name: c.name, description: c.description, min_value: c.min_value, max_value: c.max_value, value: c.value })));
        }
      } catch {
        setError("No se pudo cargar el torneo.");
      } finally {
        setIsLoading(false);
      }
    })();
  }, [tournamentId]);

  // ── Helpers ───────────────────────────────────────────────────────────────

  const totalPeso = criterias.reduce((s, c) => s + c.value, 0);
  const pesoValido = Math.abs(totalPeso - 1.0) < 0.001;

  const buildPayload = (): UpdateConfigRequest => ({
    tournament_rule: {
      ...rule,
      date_start_inscription: rule.date_start_inscription ? `${rule.date_start_inscription}T00:00:00` : null,
      date_end_inscription: rule.date_end_inscription ? `${rule.date_end_inscription}T23:59:59` : null,
    },
    tournament_config: {
      type: tournamentType,
      config: tournamentType === "knockout" ? koConfig : tournamentType === "round_robin" ? rrConfig : hyConfig,
    },
    tournament_evaluation: {
      criterias: criterias.map(c => ({
        id: c.id,
        name: c.name,
        description: c.description,
        min_value: c.min_value,
        max_value: c.max_value,
        value: c.value
      }))
    },
  });

  // ── Acciones ──────────────────────────────────────────────────────────────

  const handleSave = async () => {
    setError(null); setSuccess(null); setIsSaving(true);
    try {
      await configTournamentRules(tournamentId!, buildPayload());
      setSuccess("Configuración guardada correctamente.");
    } catch (err) {
      setError(axios.isAxiosError(err) ? err.response?.data?.error ?? "Error al guardar." : "Error de conexión.");
    } finally { setIsSaving(false); }
  };

  const handleReview = async () => {
    if (!pesoValido) { setError("La suma de los pesos de criterios debe ser exactamente 1.0 (100%)."); return; }
    setError(null); setSuccess(null); setIsReviewing(true);
    try {
      await handleSave();
      await reviewTournament(tournamentId!);
      navigate("/dashboard/torneos");
    } catch (err) {
      setError(axios.isAxiosError(err) ? err.response?.data?.error ?? "Error al enviar a revisión." : "Error de conexión.");
    } finally { setIsReviewing(false); }
  };

  const addCriteria = () => setCriterias([...criterias, { name: "", description: "", min_value: 0, max_value: 10, value: 0 }]);
  const removeCriteria = (i: number) => setCriterias(criterias.filter((_, idx) => idx !== i));
  const updateCriteria = (i: number, field: keyof CriteriaForm, val: any) => {
    const arr = [...criterias]; arr[i] = { ...arr[i], [field]: val }; setCriterias(arr);
  };

  const addInstitution = () => { if (newInstitution.trim()) { setRule(r => ({ ...r, validation_list: [...r.validation_list, newInstitution.trim()] })); setNewInstitution(""); } };
  const removeInstitution = (i: number) => setRule(r => ({ ...r, validation_list: r.validation_list.filter((_, idx) => idx !== i) }));

  // ── UI ────────────────────────────────────────────────────────────────────

  if (isLoading) return <div className="flex items-center justify-center h-64 text-slate-500"><Loader2 className="animate-spin mr-2" />Cargando torneo...</div>;

  const fieldCls = "flex h-10 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-slate-50 disabled:text-slate-400";
  const sectionCls = "bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden";
  const headerCls = "px-6 py-4 bg-slate-50 border-b border-slate-200 font-semibold text-slate-800 text-sm uppercase tracking-wide";

  return (
    <div className="max-w-4xl mx-auto pb-16 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/dashboard/torneos" className="p-2 rounded-md hover:bg-slate-100 text-slate-500">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-900">{meta.name || "Configurar Torneo"}</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            <span className="capitalize">{meta.category}</span> · Estado: <span className="font-medium capitalize">{meta.state}</span>
          </p>
        </div>
        {isReadOnly && (
          <span className="text-xs bg-amber-100 text-amber-700 border border-amber-200 px-3 py-1.5 rounded-full font-medium">Solo lectura</span>
        )}
      </div>

      {/* Alertas */}
      {error && <div className="flex items-center gap-3 p-3 rounded-md bg-red-50 border border-red-300 text-red-700 text-sm"><AlertCircle size={16} />{error}</div>}
      {success && <div className="flex items-center gap-3 p-3 rounded-md bg-green-50 border border-green-300 text-green-700 text-sm"><CheckCircle size={16} />{success}</div>}

      {/* ── SECCIÓN 1: Reglas Operativas ── */}
      <div className={sectionCls}>
        <div className={headerCls}>Reglas Operativas</div>
        <div className="p-6 grid grid-cols-2 gap-4">
          {[
            { label: "Mín. miembros/equipo", field: "min_members" },
            { label: "Máx. miembros/equipo", field: "max_members" },
            { label: "Mín. equipos", field: "min_teams" },
            { label: "Máx. equipos", field: "max_teams" },
          ].map(({ label, field }) => (
            <div key={field} className="space-y-1">
              <label className="text-sm font-medium text-slate-700">{label}</label>
              <input type="number" disabled={isReadOnly} className={fieldCls}
                value={(rule as any)[field]}
                onChange={e => setRule(r => ({ ...r, [field]: Number(e.target.value) }))}
              />
            </div>
          ))}

          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-700">Tipo de acceso</label>
            <select disabled={isReadOnly} className={fieldCls} value={rule.access_type}
              onChange={e => setRule(r => ({ ...r, access_type: e.target.value as any }))}>
              <option value="private">Privado (por institución)</option>
              <option value="public">Público (abierto)</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-700">Inicio inscripciones</label>
            <input type="date" disabled={isReadOnly} className={fieldCls} value={rule.date_start_inscription}
              onChange={e => setRule(r => ({ ...r, date_start_inscription: e.target.value }))} />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-700">Cierre inscripciones</label>
            <input type="date" disabled={isReadOnly} className={fieldCls} value={rule.date_end_inscription}
              onChange={e => setRule(r => ({ ...r, date_end_inscription: e.target.value }))} />
          </div>

          {rule.access_type === "private" && (
            <div className="col-span-2 space-y-2">
              <label className="text-sm font-medium text-slate-700">Instituciones habilitadas</label>
              {rule.validation_list.map((inst, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="flex-1 px-3 py-1.5 rounded bg-slate-100 text-sm">{inst}</span>
                  {!isReadOnly && <button onClick={() => removeInstitution(i)} className="text-red-500 hover:text-red-700"><Trash2 size={14} /></button>}
                </div>
              ))}
              {!isReadOnly && (
                <div className="flex gap-2">
                  <input type="text" placeholder="ID de institución…" className={fieldCls} value={newInstitution}
                    onChange={e => setNewInstitution(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && (e.preventDefault(), addInstitution())} />
                  <button onClick={addInstitution} className="px-3 py-2 rounded-md bg-slate-900 text-white text-sm hover:bg-slate-700 whitespace-nowrap">
                    <Plus size={14} />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* ── SECCIÓN 2: Formato del torneo ── */}
      <div className={sectionCls}>
        <div className={headerCls}>Formato del Torneo</div>
        <div className="p-6 space-y-5">
          <div className="space-y-1">
            <label className="text-sm font-medium text-slate-700">Tipo de torneo</label>
            <select disabled={isReadOnly} className={fieldCls} value={tournamentType}
              onChange={e => setTournamentType(e.target.value as TournamentType)}>
              <option value="knockout">Eliminación Directa (Knockout)</option>
              <option value="round_robin">Todos contra todos (Round Robin)</option>
              <option value="hybrid">Híbrido (Grupos + Eliminación)</option>
            </select>
          </div>

          {tournamentType === "knockout" && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-sm font-medium text-slate-700">Best of (rondas por duelo)</label>
                <input type="number" min={1} disabled={isReadOnly} className={fieldCls} value={koConfig.best_of}
                  onChange={e => setKoConfig(c => ({ ...c, best_of: Number(e.target.value) }))} />
              </div>
              <div className="flex items-center gap-6 pt-6">
                <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                  <input type="checkbox" disabled={isReadOnly} checked={koConfig.seed_enabled}
                    onChange={e => setKoConfig(c => ({ ...c, seed_enabled: e.target.checked }))} />
                  Semillas habilitadas
                </label>
                <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                  <input type="checkbox" disabled={isReadOnly} checked={koConfig.third_place}
                    onChange={e => setKoConfig(c => ({ ...c, third_place: e.target.checked }))} />
                  3er puesto
                </label>
              </div>
            </div>
          )}

          {tournamentType === "round_robin" && (
            <div className="grid grid-cols-2 gap-4">
              {([
                { label: "Número de vueltas", field: "num_rounds" },
                { label: "Puntos victoria", field: "point_to_victory" },
                { label: "Puntos empate", field: "point_to_draw" },
                { label: "Puntos derrota", field: "point_to_defeat" },
              ] as { label: string; field: keyof RRConfig }[]).map(({ label, field }) => (
                <div key={field} className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">{label}</label>
                  <input type="number" disabled={isReadOnly} className={fieldCls}
                    value={rrConfig[field] as number}
                    onChange={e => setRrConfig(c => ({ ...c, [field]: Number(e.target.value) }))} />
                </div>
              ))}
              <div className="col-span-2 space-y-1">
                <label className="text-sm font-medium text-slate-700">Criterios desempate (separados por coma)</label>
                <input type="text" disabled={isReadOnly} className={fieldCls}
                  value={rrConfig.tie_breaking_criteria.join(", ")}
                  onChange={e => setRrConfig(c => ({ ...c, tie_breaking_criteria: e.target.value.split(",").map(s => s.trim()).filter(Boolean) }))} />
                <p className="text-xs text-slate-400">Ej: DIFF_POINTS, POINTS_FOR, HEAD_TO_HEAD</p>
              </div>
            </div>
          )}

          {tournamentType === "hybrid" && (
            <div className="grid grid-cols-2 gap-4">
              {([
                { label: "Equipos por grupo", field: "teams_for_group" },
                { label: "Clasificados por grupo", field: "classified_by_group" },
                { label: "Vueltas en fase grupos", field: "num_rounds" },
              ] as { label: string; field: keyof HYConfig }[]).map(({ label, field }) => (
                <div key={field} className="space-y-1">
                  <label className="text-sm font-medium text-slate-700">{label}</label>
                  <input type="number" disabled={isReadOnly} className={fieldCls}
                    value={hyConfig[field] as number}
                    onChange={e => setHyConfig(c => ({ ...c, [field]: Number(e.target.value) }))} />
                </div>
              ))}
              <div className="flex items-center gap-6 pt-6">
                <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                  <input type="checkbox" disabled={isReadOnly} checked={hyConfig.third_place}
                    onChange={e => setHyConfig(c => ({ ...c, third_place: e.target.checked }))} />
                  3er puesto en final
                </label>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── SECCIÓN 3: Criterios de Evaluación ── */}
      <div className={sectionCls}>
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <span className="font-semibold text-slate-800 text-sm uppercase tracking-wide">Criterios de Evaluación</span>
          <span className={`text-xs font-semibold px-2 py-1 rounded-full ${pesoValido ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            Suma pesos: {(totalPeso * 100).toFixed(1)}% {pesoValido ? "✓" : "(debe ser 100%)"}
          </span>
        </div>
        <div className="p-6 space-y-4">
          {criterias.length === 0 && (
            <p className="text-sm text-slate-400 text-center py-4">Sin criterios. Agrega al menos uno para poder enviar a revisión.</p>
          )}
          {criterias.map((c, i) => (
            <div key={i} className="border border-slate-200 rounded-lg p-4 space-y-3 bg-slate-50/50">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase">Criterio {i + 1}</span>
                {!isReadOnly && (
                  <button onClick={() => removeCriteria(i)} className="text-red-400 hover:text-red-600"><Trash2 size={14} /></button>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600">Nombre</label>
                  <input type="text" disabled={isReadOnly} className={fieldCls} value={c.name}
                    onChange={e => updateCriteria(i, "name", e.target.value)} />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600">Peso (0.0 – 1.0)</label>
                  <input type="number" step="0.01" min="0" max="1" disabled={isReadOnly} className={fieldCls}
                    value={c.value}
                    onChange={e => updateCriteria(i, "value", parseFloat(e.target.value) || 0)} />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600">Valor mínimo calificación</label>
                  <input type="number" disabled={isReadOnly} className={fieldCls} value={c.min_value}
                    onChange={e => updateCriteria(i, "min_value", Number(e.target.value))} />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600">Valor máximo calificación</label>
                  <input type="number" disabled={isReadOnly} className={fieldCls} value={c.max_value}
                    onChange={e => updateCriteria(i, "max_value", Number(e.target.value))} />
                </div>
                <div className="col-span-2 space-y-1">
                  <label className="text-xs font-medium text-slate-600">Descripción</label>
                  <input type="text" disabled={isReadOnly} className={fieldCls} value={c.description}
                    onChange={e => updateCriteria(i, "description", e.target.value)} />
                </div>
              </div>
            </div>
          ))}
          {!isReadOnly && (
            <button onClick={addCriteria}
              className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 font-medium py-1 px-2 rounded hover:bg-blue-50 transition-colors">
              <Plus size={16} /> Agregar criterio
            </button>
          )}
        </div>
      </div>

      {/* ── Barra de Acciones ── */}
      {!isReadOnly && (
        <div className="flex items-center justify-end gap-3 pt-2">
          <Link to="/dashboard/torneos" className="px-4 py-2 text-sm rounded-md border border-slate-300 text-slate-700 hover:bg-slate-50">
            Cancelar
          </Link>
          <button onClick={handleSave} disabled={isSaving}
            className="inline-flex items-center gap-2 px-4 py-2 text-sm rounded-md bg-white border border-blue-300 text-blue-700 hover:bg-blue-50 disabled:opacity-50 transition-colors">
            {isSaving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
            Guardar borrador
          </button>
          <button onClick={handleReview} disabled={isReviewing || !pesoValido}
            className="inline-flex items-center gap-2 px-5 py-2 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm">
            {isReviewing ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
            Enviar a Revisión
          </button>
        </div>
      )}
    </div>
  );
}
