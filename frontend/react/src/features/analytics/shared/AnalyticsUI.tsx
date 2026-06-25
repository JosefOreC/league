import { useState, useEffect, useCallback } from "react";
import type { ReactNode, CSSProperties } from "react";
import { useNavigate, useParams, useLocation } from "react-router";
import { ArrowLeft, Download, FileText, Loader2, Check, AlertTriangle, Inbox, Lock, RefreshCw } from "lucide-react";
import { getTournaments } from "../../../services/tournamentService";
import { useRoleGuard } from "../../../hooks/useRoleGuard";

/* ──────────────────────────────────────────────────────────────────────────
 * Tokens de diseño compartidos — MVP3 Analítica (solo presentación)
 * ────────────────────────────────────────────────────────────────────────── */
export const sev = {
  success: "#16a34a",
  warning: "#d97706",
  error: "#dc2626",
  info: "#2563eb",
  gold: "#f59e0b",
  silver: "#9ca3af",
  bronze: "#b45309",
} as const;

export const viewColor = {
  indigo: "#4f46e5",
  navy: "#1e3a5f",
  teal: "#134e4a",
} as const;

/* ── PageHeader ──────────────────────────────────────────────────────────── */
interface PageHeaderProps {
  title: string;
  subtitle?: string;
  meta?: string;
  statusBadge?: { label: string; tone?: "success" | "live" | "warning" };
  accent?: string;
  right?: ReactNode;
}

export function PageHeader({ title, subtitle, meta, statusBadge, accent = viewColor.indigo, right }: PageHeaderProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { id: urlTorneoId } = useParams<{ id: string }>();
  const { isParticipant, isAdmin, isManager, userId } = useRoleGuard();

  const [tournaments, setTournaments] = useState<any[]>([]);
  const [loadingList, setLoadingList] = useState(false);

  useEffect(() => {
    if (!urlTorneoId) return;

    let active = true;
    setLoadingList(true);
    getTournaments()
      .then((all) => {
        if (!active) return;
        let filtered: any[];
        if (isParticipant) {
          filtered = all.filter(t => t.state !== "draft" && t.state !== "in_review");
        } else {
          filtered = all.filter(t => {
            if (isAdmin) return true;
            if (isManager) return t.creator_user_id === userId;
            return false;
          });
        }
        setTournaments(filtered);
      })
      .catch((err) => console.error("Error loading tournament list in PageHeader:", err))
      .finally(() => {
        if (active) setLoadingList(false);
      });

    return () => {
      active = false;
    };
  }, [urlTorneoId, isParticipant, isAdmin, isManager, userId]);

  const handleTournamentSelect = (newId: string) => {
    if (!newId || newId === urlTorneoId) return;
    const newPath = location.pathname.replace(
      /\/dashboard\/torneos\/[^/]+/,
      `/dashboard/torneos/${newId}`
    );
    navigate(newPath);
  };

  return (
    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
      <div className="flex items-start gap-3 flex-1">
        <button
          onClick={() => navigate(-1)}
          className="mt-1 inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors print:hidden"
          aria-label="Volver"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-bold tracking-tight" style={{ color: accent }}>
              {title}
            </h1>
            {statusBadge && <StatusBadge {...statusBadge} />}
          </div>
          {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}
          {meta && <p className="text-xs text-slate-400 mt-0.5">{meta}</p>}

          {/* Selector de torneos dinámico */}
          {urlTorneoId && (
            <div className="mt-2.5 flex items-center gap-2 print:hidden">
              <span className="text-[10px] font-black uppercase tracking-wider text-slate-400">Torneo activo:</span>
              {loadingList ? (
                <span className="text-[10px] font-semibold text-slate-400 animate-pulse">Cargando...</span>
              ) : tournaments.length === 0 ? (
                <span className="text-[10px] font-bold text-red-500 bg-red-50 px-2 py-0.5 rounded border border-red-100">Sin torneos</span>
              ) : (
                <select
                  value={urlTorneoId}
                  onChange={(e) => handleTournamentSelect(e.target.value)}
                  className="bg-slate-100 border border-slate-200 text-slate-700 font-bold text-[10px] uppercase tracking-wider rounded-lg px-2 py-1 outline-none transition-all cursor-pointer focus:border-indigo-500"
                >
                  {tournaments.map((t) => (
                    <option key={t.id} value={t.id} className="font-bold text-slate-800 bg-white">
                      {t.name}
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}
        </div>
      </div>
      {right && <div className="flex items-center gap-3 flex-wrap">{right}</div>}
    </div>
  );
}

export function StatusBadge({ label, tone = "success" }: { label: string; tone?: "success" | "live" | "warning" }) {
  if (tone === "live") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-green-100 px-3 py-1 text-xs font-bold text-green-700">
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
        </span>
        {label}
      </span>
    );
  }
  const cls =
    tone === "warning"
      ? "bg-amber-100 text-amber-700"
      : "bg-green-100 text-green-700";
  return <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-bold ${cls}`}>{label}</span>;
}

/* ── Botón Exportar PDF — con sus 4 estados (token compartido) ────────────── */
type PdfState = "idle" | "loading" | "done" | "error";

export function ExportPdfButton({
  label = "PDF",
  variant = "solid",
  accent = viewColor.indigo,
}: {
  label?: string;
  variant?: "solid" | "outline";
  accent?: string;
}) {
  const [state, setState] = useState<PdfState>("idle");

  const run = () => {
    setState("loading");
    // Exportación real: abre el diálogo de impresión del navegador → "Guardar como PDF".
    // El CSS print: oculta el menú/header para una salida limpia.
    setTimeout(() => {
      window.print();
      setState("done");
      setTimeout(() => setState("idle"), 3000);
    }, 200);
  };

  const base =
    "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium h-10 px-4 transition-colors disabled:opacity-70";
  const styles =
    variant === "solid"
      ? "text-white shadow-sm hover:opacity-90"
      : "border bg-white hover:bg-slate-50";

  const content: Record<PdfState, ReactNode> = {
    idle: (
      <>
        <Download className="h-4 w-4" /> {label}
      </>
    ),
    loading: (
      <>
        <Loader2 className="h-4 w-4 animate-spin" /> Generando PDF...
      </>
    ),
    done: (
      <>
        <Check className="h-4 w-4" /> PDF listo
      </>
    ),
    error: (
      <>
        <AlertTriangle className="h-4 w-4" /> Error al generar
      </>
    ),
  };

  const style: CSSProperties =
    variant === "solid"
      ? { backgroundColor: state === "done" ? sev.success : state === "error" ? sev.error : accent }
      : { color: accent, borderColor: accent };

  return (
    <button onClick={run} disabled={state === "loading"} className={`${base} ${styles}`} style={style}>
      {content[state]}
    </button>
  );
}

export function ExportPdfOutline({ accent = viewColor.indigo }: { accent?: string }) {
  return (
    <button
      onClick={() => window.print()}
      className="inline-flex items-center gap-2 rounded-md border bg-white px-4 h-10 text-sm font-medium hover:bg-slate-50 transition-colors print:hidden"
      style={{ color: accent, borderColor: accent }}
    >
      <FileText className="h-4 w-4" /> Exportar PDF
    </button>
  );
}

/* ── KpiCardRow ──────────────────────────────────────────────────────────── */
export interface KpiCard {
  label: string;
  value: string | number;
  accentColor: string;
  wide?: boolean;
}

export function KpiCardRow({ cards }: { cards: KpiCard[] }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((c, i) => (
        <div
          key={i}
          className={`rounded-xl border border-slate-200 bg-white p-4 shadow-sm ${c.wide ? "col-span-2" : ""}`}
        >
          <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">{c.label}</p>
          <p className="mt-1 text-2xl font-bold leading-tight" style={{ color: c.accentColor }}>
            {c.value}
          </p>
        </div>
      ))}
    </div>
  );
}

/* ── Card contenedor ─────────────────────────────────────────────────────── */
export function Panel({
  title,
  subtitle,
  children,
  accentBar,
  right,
  className = "",
}: {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  accentBar?: string;
  right?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden ${className}`}
      style={accentBar ? { borderLeft: `4px solid ${accentBar}` } : undefined}
    >
      {(title || right) && (
        <div className="flex items-start justify-between gap-3 p-5 pb-3">
          <div>
            {title && <h2 className="text-base font-semibold text-slate-900">{title}</h2>}
            {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
          </div>
          {right}
        </div>
      )}
      <div className="p-5 pt-2">{children}</div>
    </div>
  );
}

/* ── AlertaBadge (chip) — AN-01, AN-04 ───────────────────────────────────── */
export function AlertaBadge({ type, text }: { type: "warning" | "success" | "info"; text: string }) {
  const map = {
    warning: { bg: "bg-amber-50", tx: "text-amber-700", icon: "⚠️" },
    success: { bg: "bg-green-50", tx: "text-green-700", icon: "✓" },
    info: { bg: "bg-blue-50", tx: "text-blue-700", icon: "ℹ️" },
  }[type];
  return (
    <div className={`flex items-start gap-2 rounded-lg ${map.bg} px-3 py-2 text-sm ${map.tx}`}>
      <span className="leading-5">{map.icon}</span>
      <span className="font-medium">{text}</span>
    </div>
  );
}

/* ── Barras horizontales simples ─────────────────────────────────────────── */
export function HBar({ label, value, max = 100, color }: { label: string; value: number; max?: number; color: string }) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="w-44 shrink-0 text-slate-600">{label}</span>
      <div className="h-3 flex-1 rounded-full bg-slate-100">
        <div className="h-3 rounded-full" style={{ width: `${(value / max) * 100}%`, backgroundColor: color }} />
      </div>
      <span className="w-12 shrink-0 text-right font-semibold text-slate-700">{value}</span>
    </div>
  );
}

/* ── PercentilGlobalBar — AN-02, AN-08 ───────────────────────────────────── */
export function PercentilGlobalBar({
  percentil,
  caption,
  accent = viewColor.indigo,
}: {
  percentil: number;
  caption: ReactNode;
  accent?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="relative h-4 w-full rounded-full bg-gradient-to-r from-slate-100 via-indigo-100 to-indigo-300">
        <div
          className="absolute -top-0.5 h-5 w-5 -translate-x-1/2 rounded-full border-2 border-white shadow"
          style={{ left: `${percentil}%`, backgroundColor: accent }}
        />
      </div>
      <p className="text-sm font-semibold text-slate-700">Percentil {percentil}°</p>
      <div className="text-sm text-slate-500">{caption}</div>
    </div>
  );
}

/* ── EvolucionRondaChart — AN-02, AN-08 (SVG line chart) ──────────────────── */
export function EvolucionRondaChart({
  values,
  promedio,
  color = viewColor.indigo,
}: {
  values: number[];
  promedio: number;
  color?: string;
}) {
  const w = 460;
  const h = 200;
  const pad = 28;
  // Auto-escala según los datos (incluye la línea de promedio si aplica)
  const all = [...values, promedio].filter((v) => Number.isFinite(v));
  const rawMin = Math.min(...all);
  const rawMax = Math.max(...all);
  const span = rawMax - rawMin || 1;
  const min = rawMin - span * 0.15;
  const max = rawMax + span * 0.15;
  const x = (i: number) => pad + (i * (w - pad * 2)) / Math.max(1, values.length - 1);
  const y = (v: number) => h - pad - ((v - min) / (max - min)) * (h - pad * 2);
  const path = values.map((v, i) => `${i === 0 ? "M" : "L"} ${x(i)} ${y(v)}`).join(" ");
  const yProm = y(promedio);

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full min-w-[420px]">
        {/* línea de promedio del torneo */}
        <line x1={pad} y1={yProm} x2={w - pad} y2={yProm} stroke="#cbd5e1" strokeDasharray="4 4" />
        <text x={w - pad} y={yProm - 6} textAnchor="end" className="fill-slate-400" fontSize="10">
          prom. {promedio}
        </text>
        {/* línea de datos */}
        <path d={path} fill="none" stroke={color} strokeWidth={2.5} />
        {values.map((v, i) => (
          <g key={i}>
            <circle cx={x(i)} cy={y(v)} r={4.5} fill="white" stroke={color} strokeWidth={2} />
            <text x={x(i)} y={y(v) - 10} textAnchor="middle" fontSize="10" className="fill-slate-600 font-semibold">
              {v}
            </text>
            <text x={x(i)} y={h - 10} textAnchor="middle" fontSize="10" className="fill-slate-400">
              R{i + 1}
            </text>
            <text x={x(i)} y={h - 22} textAnchor="middle" fontSize="9" className="fill-green-500">
              ✓
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

/* ── Medalla helper ──────────────────────────────────────────────────────── */
export function medalEmoji(pos: number) {
  return pos === 1 ? "🥇" : pos === 2 ? "🥈" : pos === 3 ? "🥉" : "";
}

export function medalFromText(m?: string | null) {
  if (!m) return "";
  const t = m.toUpperCase();
  if (t.includes("ORO") || t.includes("GOLD")) return "🥇";
  if (t.includes("PLATA") || t.includes("SILVER")) return "🥈";
  if (t.includes("BRONCE") || t.includes("BRONZE")) return "🥉";
  return "";
}

/* ── Hook de carga de datos con estados (loading / error / empty) ─────────── */
export type AsyncStatus = "loading" | "error" | "empty" | "ok";

export function useAsyncData<T>(fetcher: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [status, setStatus] = useState<AsyncStatus>("loading");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [errorCode, setErrorCode] = useState<number | undefined>(undefined);

  const load = useCallback(() => {
    let alive = true;
    setStatus("loading");
    fetcher()
      .then((d) => {
        if (!alive) return;
        const isEmpty =
          d == null || (Array.isArray(d) && d.length === 0);
        setData(d);
        setStatus(isEmpty ? "empty" : "ok");
      })
      .catch((err: unknown) => {
        if (!alive) return;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const e = err as any;
        const code: number | undefined = e?.response?.status;
        const msg =
          e?.response?.data?.error ||
          e?.response?.data?.detail ||
          e?.message ||
          "No se pudieron cargar los datos.";
        setErrorCode(code);
        setErrorMsg(msg);
        setStatus("error");
      });
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => load(), [load]);

  return { data, status, errorMsg, errorCode, reload: load };
}

/* ── Wrapper visual de estados globales (spec: loading/empty/error/restricted) ── */
export function AsyncBoundary({
  status,
  errorMsg,
  errorCode,
  onRetry,
  loadingLabel = "Cargando…",
  emptyLabel = "No hay datos disponibles para mostrar.",
  children,
}: {
  status: AsyncStatus;
  errorMsg?: string;
  errorCode?: number;
  onRetry?: () => void;
  loadingLabel?: string;
  emptyLabel?: string;
  children: ReactNode;
}) {
  if (status === "loading") {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-slate-400">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-500" />
        <p className="mt-3 text-sm font-medium">{loadingLabel}</p>
      </div>
    );
  }
  if (status === "error") {
    // 403 → acceso denegado (restricted)
    if (errorCode === 403) {
      return (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <Lock className="h-10 w-10 text-slate-300" />
          <p className="mt-3 text-lg font-semibold text-slate-700">Acceso denegado</p>
          <p className="mt-1 max-w-md text-sm text-slate-400">{errorMsg || "No tienes permiso para ver esta información."}</p>
        </div>
      );
    }
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <AlertTriangle className="h-10 w-10 text-red-400" />
        <p className="mt-3 text-lg font-semibold text-slate-700">No se pudo cargar</p>
        <p className="mt-1 max-w-md text-sm text-slate-400">{errorMsg}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-4 inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
          >
            <RefreshCw className="h-4 w-4" /> Reintentar
          </button>
        )}
      </div>
    );
  }
  if (status === "empty") {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <Inbox className="h-10 w-10 text-slate-300" />
        <p className="mt-3 text-lg font-semibold text-slate-700">Sin datos</p>
        <p className="mt-1 max-w-md text-sm text-slate-400">{emptyLabel}</p>
      </div>
    );
  }
  return <>{children}</>;
}
