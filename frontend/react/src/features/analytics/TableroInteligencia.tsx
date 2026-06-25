import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router";
import type { ReactNode } from "react";
import { ArrowLeft, RefreshCw } from "lucide-react";
import {
  KpiCardRow,
  StatusBadge,
  AsyncBoundary,
  useAsyncData,
  medalFromText,
  viewColor,
  sev,
} from "./shared/AnalyticsUI";
import { analyticsService } from "../../services/analyticsService";

/* HU-AN-04 — Tablero de Inteligencia · /torneos/:id/tablero-inteligencia (tiempo real)
 * Conectado a GET /api/analitica/torneos/:id/tablero-inteligencia/
 */

function AlertCard({ tone, title, children }: { tone: "error" | "info" | "success"; title: string; children: ReactNode }) {
  const map = {
    error: { border: sev.warning, bg: "#fff7ed", icon: "⚠️" },
    info: { border: sev.info, bg: "#eff6ff", icon: "ℹ️" },
    success: { border: sev.success, bg: "#f0fdf4", icon: "✓" },
  }[tone];
  return (
    <div className="rounded-lg p-3" style={{ borderLeft: `4px solid ${map.border}`, backgroundColor: map.bg }}>
      <p className="text-sm font-semibold text-slate-800">{map.icon} {title}</p>
      <div className="mt-1 text-xs text-slate-500">{children}</div>
    </div>
  );
}

function SectionCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-3 text-base font-semibold text-slate-900">{title}</h2>
      {children}
    </div>
  );
}

function toneFromSeveridad(s: string): "error" | "info" | "success" {
  const t = s.toUpperCase();
  if (t.includes("ERROR") || t.includes("CRIT")) return "error";
  if (t.includes("SUCCESS") || t.includes("OK")) return "success";
  return "info";
}

export function TableroInteligencia() {
  const navigate = useNavigate();
  const { id = "" } = useParams();
  const [secs, setSecs] = useState(0);

  const { data, status, errorMsg, errorCode, reload } = useAsyncData(
    () => analyticsService.getTableroInteligencia(id),
    [id]
  );

  // Contador "hace Xs" + refresco automático cada 15s (modo tiempo real)
  useEffect(() => {
    const tick = setInterval(() => setSecs((s) => s + 1), 1000);
    const poll = setInterval(() => {
      setSecs(0);
      reload();
    }, 15000);
    return () => {
      clearInterval(tick);
      clearInterval(poll);
    };
  }, [reload]);

  const enCurso = (data?.estado_torneo || "").toUpperCase().includes("PROGRESS");
  const met = data?.metricas;

  const kpis = met
    ? [
        { label: "En curso", value: met.partidos_en_progreso, accentColor: sev.success },
        { label: "Pendientes", value: met.partidos_pendientes, accentColor: sev.warning },
        { label: "Finalizados", value: met.partidos_finalizados, accentColor: sev.info },
        { label: "Total equipos", value: met.total_equipos, accentColor: viewColor.indigo },
        { label: "Total partidos", value: met.total_partidos, accentColor: sev.info },
        { label: "Alertas", value: `${data?.alertas_activas.length ?? 0} ⚠️`, accentColor: sev.error },
      ]
    : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* PageHeader con badge activo */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100" aria-label="Volver">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight" style={{ color: viewColor.navy }}>
              {data?.torneo_nombre ? `Tablero — ${data.torneo_nombre}` : "Tablero de inteligencia"}
            </h1>
            <div className="mt-1 flex items-center gap-3">
              {enCurso ? <StatusBadge label="EN CURSO" tone="live" /> : data && <StatusBadge label={data.estado_torneo} tone="success" />}
              <span className="text-xs text-slate-400">Última actualización: hace {secs}s</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => { setSecs(0); reload(); }}
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 hover:bg-slate-50"
          aria-label="Refrescar"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      <AsyncBoundary
        status={status}
        errorMsg={errorMsg}
        errorCode={errorCode}
        onRetry={reload}
        loadingLabel="Cargando tablero de inteligencia…"
        emptyLabel="No hay datos en tiempo real para este torneo."
      >
        {data && met && (
          <>
            {/* AvanceTorneoBar */}
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="mb-2 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-900">Avance del torneo</p>
                  <p className="text-xs text-slate-500">{met.partidos_finalizados} de {met.total_partidos} partidos finalizados</p>
                </div>
                <span className="text-xl font-bold" style={{ color: viewColor.indigo }}>
                  {met.porcentaje_avance.toFixed(1)}%
                </span>
              </div>
              <div className="h-3 w-full rounded-full bg-slate-100">
                <div className="h-3 rounded-full" style={{ width: `${met.porcentaje_avance}%`, backgroundColor: viewColor.indigo }} />
              </div>
            </div>

            <KpiCardRow cards={kpis} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <SectionCard title="Tabla de posiciones — Top">
                <table className="w-full text-sm">
                  <thead className="text-xs uppercase text-slate-400">
                    <tr className="border-b border-slate-100">
                      <th className="py-2 text-left font-semibold">Pos</th>
                      <th className="py-2 text-left font-semibold">Equipo</th>
                      <th className="py-2 text-center font-semibold">Vict.</th>
                      <th className="py-2 text-right font-semibold">Puntaje</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.top_3.map((t, i) => (
                      <tr key={t.equipo_id} className="border-b border-slate-50" style={i === 0 ? { backgroundColor: "#fef3c7" } : undefined}>
                        <td className="py-2 font-bold text-slate-700">{t.posicion_actual}</td>
                        <td className="py-2 font-medium text-slate-800">{t.equipo_nombre} {medalFromText(t.medalla)}</td>
                        <td className="py-2 text-center text-slate-600">{t.victorias}</td>
                        <td className="py-2 text-right font-semibold text-slate-700">{t.puntaje_acumulado.toFixed(1)}</td>
                      </tr>
                    ))}
                    {data.top_3.length === 0 && (
                      <tr><td colSpan={4} className="py-3 text-center text-xs text-slate-400">Sin posiciones aún.</td></tr>
                    )}
                  </tbody>
                </table>
              </SectionCard>

              <SectionCard title="Alertas activas">
                <div className="space-y-3">
                  {data.alertas_activas.map((a, i) => (
                    <AlertCard key={i} tone={toneFromSeveridad(a.severidad)} title={a.tipo}>
                      {a.mensaje}
                      {a.minutos_retraso != null && (
                        <><br /><span className="font-semibold text-amber-700">{a.minutos_retraso} min de retraso</span></>
                      )}
                    </AlertCard>
                  ))}
                  {data.alertas_activas.length === 0 && (
                    <p className="text-xs text-slate-400">Sin alertas activas. ✓</p>
                  )}
                </div>
              </SectionCard>

              <SectionCard title="Próximos partidos">
                <div className="flex flex-col gap-2">
                  {data.partidos_proximos.map((p) => {
                    const retraso = (p.minutos_retraso ?? 0) > 0;
                    return (
                      <span
                        key={p.partido_id}
                        className={`rounded-md px-3 py-1.5 text-xs font-medium ${retraso ? "bg-amber-50 text-amber-700" : "bg-green-50 text-green-700"}`}
                      >
                        R{p.ronda}: {p.equipo_local_nombre} vs. {p.equipo_visitante_nombre}
                        {retraso && ` ⚠️ ${p.minutos_retraso} min`}
                      </span>
                    );
                  })}
                  {data.partidos_proximos.length === 0 && (
                    <p className="text-xs text-slate-400">No hay partidos próximos.</p>
                  )}
                </div>
              </SectionCard>
            </div>
          </>
        )}
      </AsyncBoundary>
    </div>
  );
}
