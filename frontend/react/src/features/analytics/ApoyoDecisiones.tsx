import { useState } from "react";
import { useNavigate, useParams } from "react-router";
import { ArrowLeft } from "lucide-react";
import { AsyncBoundary, useAsyncData, viewColor, sev } from "./shared/AnalyticsUI";
import { analyticsService } from "../../services/analyticsService";
import type { SugerenciaDTO } from "../../types/analytics";

/* HU-AN-05 — Sistema de Apoyo a Decisiones · /torneos/:id/apoyo-decisiones
 * Conectado a GET /api/analitica/torneos/:id/sugerencias/
 */

type Severidad = "ERROR" | "WARNING" | "INFO";

const STYLES: Record<Severidad, { border: string; headerBg: string; btn: string; icon: string; text: string }> = {
  ERROR: { border: sev.error, headerBg: "#fef2f2", btn: "#991b1b", icon: "●", text: "text-red-600" },
  WARNING: { border: sev.warning, headerBg: "#fff7ed", btn: "#b45309", icon: "⚠️", text: "text-amber-600" },
  INFO: { border: sev.info, headerBg: "#eff6ff", btn: "#1e40af", icon: "ℹ️", text: "text-blue-600" },
};

function normSeveridad(s: string): Severidad {
  const t = (s || "").toUpperCase();
  if (t.includes("ERROR") || t.includes("CRIT")) return "ERROR";
  if (t.includes("INFO")) return "INFO";
  return "WARNING";
}

// Estado local de la UI por sugerencia (el backend no expone PATCH aún)
type EstadoLocal = "PENDIENTE" | "ATENDIDA" | "DESCARTADA";

function EstadoBadge({ estado, severidad }: { estado: EstadoLocal; severidad: Severidad }) {
  if (estado === "ATENDIDA")
    return <span className="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-bold text-green-700">ATENDIDA</span>;
  if (estado === "DESCARTADA")
    return <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-bold text-slate-500">DESCARTADA</span>;
  return (
    <span className="rounded-full border px-2.5 py-0.5 text-xs font-bold" style={{ borderColor: STYLES[severidad].border, color: STYLES[severidad].border }}>
      PENDIENTE
    </span>
  );
}

export function ApoyoDecisiones() {
  const navigate = useNavigate();
  const { id = "" } = useParams();
  const { data, status, errorMsg, errorCode, reload } = useAsyncData(
    () => analyticsService.getSugerencias(id),
    [id]
  );

  const [filtro, setFiltro] = useState<Severidad | "TODAS">("TODAS");
  const [estados, setEstados] = useState<Record<string, EstadoLocal>>({});

  const sugerencias: SugerenciaDTO[] = data?.sugerencias ?? [];
  const getEstado = (s: SugerenciaDTO): EstadoLocal => estados[s.id] ?? (s.estado as EstadoLocal) ?? "PENDIENTE";
  const setEstado = (sid: string, e: EstadoLocal) => setEstados((p) => ({ ...p, [sid]: e }));

  const counts = {
    ERROR: sugerencias.filter((s) => normSeveridad(s.severidad) === "ERROR").length,
    WARNING: sugerencias.filter((s) => normSeveridad(s.severidad) === "WARNING").length,
    INFO: sugerencias.filter((s) => normSeveridad(s.severidad) === "INFO").length,
  };
  const visibles = filtro === "TODAS" ? sugerencias : sugerencias.filter((s) => normSeveridad(s.severidad) === filtro);
  const activas = sugerencias.filter((s) => getEstado(s) === "PENDIENTE").length;
  const atendidas = sugerencias.filter((s) => getEstado(s) === "ATENDIDA").length;

  const FilterBtn = ({ value, label, color }: { value: Severidad | "TODAS"; label: string; color?: string }) => {
    const active = filtro === value;
    return (
      <button
        onClick={() => setFiltro(value)}
        className="rounded-md border px-3 py-1.5 text-xs font-semibold transition-colors"
        style={
          active && color
            ? { borderColor: color, color, backgroundColor: `${color}14` }
            : active
            ? { borderColor: "#cbd5e1", backgroundColor: "#f1f5f9", color: "#475569" }
            : { borderColor: "#e2e8f0", color: "#94a3b8" }
        }
      >
        {label}
      </button>
    );
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100" aria-label="Volver">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <h1 className="text-2xl font-bold tracking-tight" style={{ color: viewColor.navy }}>
            Sistema de apoyo a decisiones
          </h1>
        </div>
        <span className="text-sm text-slate-400">{activas} sugerencias activas</span>
      </div>

      <AsyncBoundary
        status={status}
        errorMsg={errorMsg}
        errorCode={errorCode}
        onRetry={reload}
        loadingLabel="Evaluando el torneo…"
        emptyLabel="No hay sugerencias de acción para este torneo."
      >
        <>
          {data?.mensaje && (
            <div className="rounded-lg bg-blue-50 px-4 py-2 text-sm text-blue-700">{data.mensaje}</div>
          )}

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-slate-500">Filtrar por:</span>
            <FilterBtn value="ERROR" label={`⚠️ ERROR (${counts.ERROR})`} color={sev.error} />
            <FilterBtn value="WARNING" label={`⚠️ WARNING (${counts.WARNING})`} color={sev.warning} />
            <FilterBtn value="INFO" label={`ℹ️ INFO (${counts.INFO})`} color={sev.info} />
            <FilterBtn value="TODAS" label="Todas" />
          </div>

          <div className="space-y-4">
            {visibles.map((s) => {
              const severidad = normSeveridad(s.severidad);
              const st = STYLES[severidad];
              const estado = getEstado(s);
              return (
                <div key={s.id} className="rounded-xl border bg-white shadow-sm overflow-hidden" style={{ borderLeft: `4px solid ${st.border}` }}>
                  <div className="flex items-center justify-between gap-3 px-5 py-3" style={{ backgroundColor: st.headerBg }}>
                    <p className="flex items-center gap-2 text-sm font-semibold text-slate-800">
                      <span className={st.text}>{st.icon}</span> {s.tipo.replace(/_/g, " ")}
                    </p>
                    <EstadoBadge estado={estado} severidad={severidad} />
                  </div>
                  <div className="px-5 py-4 text-sm text-slate-600">
                    <p>{s.descripcion}</p>
                    <p className="mt-2">
                      <span className="font-semibold text-slate-700">Acción sugerida: </span>
                      {s.accion_sugerida}
                    </p>
                    {s.entidad_ref_id && (
                      <p className="mt-1">
                        <span className="inline-block rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500">
                          Entidad: {s.entidad_ref_id}
                        </span>
                      </p>
                    )}
                  </div>
                  <div className="flex justify-end gap-2 border-t border-slate-100 px-5 py-3">
                    <button onClick={() => setEstado(s.id, "ATENDIDA")} className="rounded-md px-3 py-1.5 text-xs font-semibold text-white" style={{ backgroundColor: st.btn }}>
                      Atender →
                    </button>
                    <button onClick={() => setEstado(s.id, "DESCARTADA")} className="rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-500 hover:bg-slate-50">
                      Descartar
                    </button>
                  </div>
                </div>
              );
            })}
            {visibles.length === 0 && (
              <div className="rounded-xl border border-dashed border-slate-200 p-10 text-center text-sm text-slate-400">
                No hay sugerencias para este filtro.
              </div>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <span className="text-sm text-slate-400">{sugerencias.length} sugerencias generadas</span>
            <span className="text-sm text-slate-400">{atendidas} atendidas · {activas} pendientes</span>
          </div>
        </>
      </AsyncBoundary>
    </div>
  );
}
