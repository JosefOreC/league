import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft } from "lucide-react";
import { viewColor, sev } from "./shared/AnalyticsUI";

/* HU-AN-05 — Sistema de Apoyo a Decisiones · /torneos/:id/apoyo-decisiones */

type Severidad = "ERROR" | "WARNING" | "INFO";
type Estado = "PENDIENTE" | "ATENDIDA" | "DESCARTADA";

interface Sugerencia {
  id: number;
  severidad: Severidad;
  titulo: string;
  descripcion: string;
  accion: string;
  entidad: string;
  estado: Estado;
}

const SUGERENCIAS: Sugerencia[] = [
  {
    id: 1,
    severidad: "ERROR",
    titulo: "Partido con retraso crítico",
    descripcion: "El partido de la Mesa 3 acumula 35 minutos de retraso y bloquea el inicio de la Ronda 5.",
    accion: "Reprogramar el partido o reasignar mesa disponible.",
    entidad: "Partido Ronda 4 · Mesa 3 · ByteRunners vs. NanoBot Jr.",
    estado: "PENDIENTE",
  },
  {
    id: 2,
    severidad: "WARNING",
    titulo: "Alta varianza en criterio Robustez",
    descripcion: "El criterio Robustez del sistema presenta σ=18, muy por encima del promedio del torneo.",
    accion: "Revisar la calibración de la rúbrica con el jurado técnico.",
    entidad: "Criterio: Robustez del sistema",
    estado: "PENDIENTE",
  },
  {
    id: 3,
    severidad: "INFO",
    titulo: "Equipos en percentil bajo",
    descripcion: "2 equipos se encuentran en el percentil ≤ 10 y podrían requerir acompañamiento.",
    accion: "Notificar a los coaches para retroalimentación temprana.",
    entidad: "Equipos: NanoBot Jr., MicroChip Kids",
    estado: "PENDIENTE",
  },
];

const STYLES: Record<Severidad, { border: string; headerBg: string; btn: string; icon: string; text: string }> = {
  ERROR: { border: sev.error, headerBg: "#fef2f2", btn: "#991b1b", icon: "●", text: "text-red-600" },
  WARNING: { border: sev.warning, headerBg: "#fff7ed", btn: "#b45309", icon: "⚠️", text: "text-amber-600" },
  INFO: { border: sev.info, headerBg: "#eff6ff", btn: "#1e40af", icon: "ℹ️", text: "text-blue-600" },
};

function EstadoBadge({ estado, severidad }: { estado: Estado; severidad: Severidad }) {
  if (estado === "ATENDIDA")
    return <span className="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-bold text-green-700">ATENDIDA</span>;
  if (estado === "DESCARTADA")
    return <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-bold text-slate-500">DESCARTADA</span>;
  return (
    <span
      className="rounded-full border px-2.5 py-0.5 text-xs font-bold"
      style={{ borderColor: STYLES[severidad].border, color: STYLES[severidad].border }}
    >
      PENDIENTE
    </span>
  );
}

export function ApoyoDecisiones() {
  const navigate = useNavigate();
  const [items, setItems] = useState(SUGERENCIAS);
  const [filtro, setFiltro] = useState<Severidad | "TODAS">("TODAS");

  const setEstado = (id: number, estado: Estado) =>
    setItems((prev) => prev.map((s) => (s.id === id ? { ...s, estado } : s)));

  const counts = {
    ERROR: items.filter((s) => s.severidad === "ERROR").length,
    WARNING: items.filter((s) => s.severidad === "WARNING").length,
    INFO: items.filter((s) => s.severidad === "INFO").length,
  };
  const visibles = filtro === "TODAS" ? items : items.filter((s) => s.severidad === filtro);
  const activas = items.filter((s) => s.estado === "PENDIENTE").length;
  const atendidas = items.filter((s) => s.estado === "ATENDIDA").length;

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
            Sistema de apoyo a decisiones — Torneo Regional 2024
          </h1>
        </div>
        <span className="text-sm text-slate-400">{activas} sugerencias activas</span>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-slate-500">Filtrar por:</span>
        <FilterBtn value="ERROR" label={`⚠️ ERROR (${counts.ERROR})`} color={sev.error} />
        <FilterBtn value="WARNING" label={`⚠️ WARNING (${counts.WARNING})`} color={sev.warning} />
        <FilterBtn value="INFO" label={`ℹ️ INFO (${counts.INFO})`} color={sev.info} />
        <FilterBtn value="TODAS" label="Todas" />
      </div>

      {/* Cards */}
      <div className="space-y-4">
        {visibles.map((s) => {
          const st = STYLES[s.severidad];
          return (
            <div key={s.id} className="rounded-xl border bg-white shadow-sm overflow-hidden" style={{ borderLeft: `4px solid ${st.border}` }}>
              <div className="flex items-center justify-between gap-3 px-5 py-3" style={{ backgroundColor: st.headerBg }}>
                <p className="flex items-center gap-2 text-sm font-semibold text-slate-800">
                  <span className={st.text}>{st.icon}</span> {s.titulo}
                </p>
                <EstadoBadge estado={s.estado} severidad={s.severidad} />
              </div>
              <div className="px-5 py-4 text-sm text-slate-600">
                <p>{s.descripcion}</p>
                <p className="mt-2">
                  <span className="font-semibold text-slate-700">Acción sugerida: </span>
                  {s.accion}
                </p>
                <p className="mt-1">
                  <span className="inline-block rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500">
                    {s.entidad}
                  </span>
                </p>
              </div>
              <div className="flex justify-end gap-2 border-t border-slate-100 px-5 py-3">
                <button
                  onClick={() => setEstado(s.id, "ATENDIDA")}
                  className="rounded-md px-3 py-1.5 text-xs font-semibold text-white"
                  style={{ backgroundColor: st.btn }}
                >
                  Atender →
                </button>
                <button
                  onClick={() => setEstado(s.id, "DESCARTADA")}
                  className="rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-500 hover:bg-slate-50"
                >
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

      {/* Historial */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700">✓ Ronda 2 completada</span>
          <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700">✓ Criterio Tiempo ajustado</span>
        </div>
        <span className="text-sm text-slate-400">
          {atendidas} atendidas · {activas} pendientes
        </span>
      </div>
    </div>
  );
}
