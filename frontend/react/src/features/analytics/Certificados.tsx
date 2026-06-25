import { useState } from "react";
import { Search, Download, Bot } from "lucide-react";
import { PageHeader, viewColor } from "./shared/AnalyticsUI";

/* HU-AN-06 — Certificados y Reconocimientos · /torneos/:id/certificados */

interface Participante {
  id: number;
  nombre: string;
  equipo: string;
  autorizado: boolean;
  estado: "Pendiente" | "Excluido" | "Generado";
  ie: string;
  categoria: string;
  codigo: string;
}

const PARTICIPANTES: Participante[] = [
  { id: 1, nombre: "Quispe Ramos, Andrea", equipo: "RoboChampions", autorizado: true, estado: "Pendiente", ie: "I.E. San Ramón", categoria: "SECONDARY", codigo: "TRR2024-RC-001" },
  { id: 2, nombre: "Mamani Torres, Luis", equipo: "RoboChampions", autorizado: true, estado: "Pendiente", ie: "I.E. San Ramón", categoria: "SECONDARY", codigo: "TRR2024-RC-002" },
  { id: 3, nombre: "Flores Inca, Diana", equipo: "RoboChampions", autorizado: true, estado: "Pendiente", ie: "I.E. San Ramón", categoria: "SECONDARY", codigo: "TRR2024-RC-003" },
  { id: 4, nombre: "Huamán Soto, Pedro", equipo: "Innova Robots", autorizado: false, estado: "Excluido", ie: "I.E. Santa Isabel", categoria: "SECONDARY", codigo: "TRR2024-IR-001" },
  { id: 5, nombre: "Rojas Vega, Camila", equipo: "CircuitMasters", autorizado: true, estado: "Pendiente", ie: "I.E. Mariscal Castilla", categoria: "PRIMARY", codigo: "TRR2024-CM-001" },
];

const TABS = ["Participación", "Ganadores", "Menciones especiales"] as const;

export function Certificados() {
  const [tab, setTab] = useState<(typeof TABS)[number]>("Participación");
  const [sel, setSel] = useState<Participante>(PARTICIPANTES[0]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <PageHeader title="Certificados y reconocimientos — Torneo Regional 2024" />

      {/* Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200">
        <div className="flex gap-6">
          {TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`-mb-px border-b-2 pb-3 text-sm font-medium transition-colors ${
                tab === t ? "border-indigo-600 text-indigo-600" : "border-transparent text-slate-400 hover:text-slate-600"
              }`}
            >
              {t} {tab === t && "✓"}
            </button>
          ))}
        </div>
        <button className="mb-2 inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-semibold text-white" style={{ backgroundColor: viewColor.indigo }}>
          <Download className="h-4 w-4" /> Descargar todo (ZIP)
        </button>
      </div>

      {/* EstadoGeneracionBar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap gap-2">
          <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">Aptos para certificado: 48 participantes</span>
          <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-700">Sin autorización: 2 excluidos</span>
          <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">Generados: 0 / 48</span>
        </div>
        <button className="rounded-md px-4 py-2 text-sm font-semibold text-white" style={{ backgroundColor: viewColor.indigo }}>
          Generar todos los certificados →
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ParticipantesTable */}
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-xs uppercase text-slate-400 bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">#</th>
                  <th className="px-4 py-3 text-left font-semibold">Participante</th>
                  <th className="px-4 py-3 text-left font-semibold">Equipo</th>
                  <th className="px-4 py-3 text-center font-semibold">Autor.</th>
                  <th className="px-4 py-3 text-left font-semibold">Estado</th>
                </tr>
              </thead>
              <tbody>
                {PARTICIPANTES.map((p) => (
                  <tr
                    key={p.id}
                    onClick={() => setSel(p)}
                    className={`cursor-pointer border-b border-slate-50 transition-colors hover:bg-slate-50 ${sel.id === p.id ? "bg-indigo-50" : ""}`}
                    style={!p.autorizado ? { backgroundColor: "#fef2f2" } : undefined}
                  >
                    <td className="px-4 py-3 text-slate-400">{p.id}</td>
                    <td className={`px-4 py-3 font-medium ${!p.autorizado ? "text-slate-400 line-through" : "text-slate-800"}`}>{p.nombre}</td>
                    <td className="px-4 py-3 text-slate-500">{p.equipo}</td>
                    <td className="px-4 py-3 text-center">
                      {p.autorizado ? <span className="font-semibold text-green-600">✓ SÍ</span> : <span className="font-semibold text-red-600">✗ NO</span>}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                          p.estado === "Generado" ? "bg-green-100 text-green-700" : p.estado === "Excluido" ? "bg-red-100 text-red-700" : "bg-slate-100 text-slate-500"
                        }`}
                      >
                        {p.estado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="border-t border-slate-100 p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                placeholder="Buscar participante..."
                className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <p className="mt-3 text-center text-xs text-slate-400">· · · 43 participantes más · · ·</p>
          </div>
        </div>

        {/* CertificadoPreview */}
        <div className="flex items-start justify-center">
          <div
            className="w-full rounded-lg p-8 text-center"
            style={{ backgroundColor: "#fefce8", border: `2px solid #d97706` }}
          >
            <p className="text-lg font-bold tracking-wide" style={{ color: "#ea580c" }}>
              CERTIFICADO DE {tab === "Participación" ? "PARTICIPACIÓN" : tab.toUpperCase()}
            </p>
            <p className="text-xs text-slate-500">Torneo Regional de Robótica Educativa 2024</p>

            <div className="my-5 flex justify-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full" style={{ backgroundColor: viewColor.indigo }}>
                <Bot className="h-8 w-8 text-white" />
              </div>
            </div>

            <p className="text-sm text-slate-500">Se certifica que</p>
            <p className="text-lg font-bold text-slate-900">{sel.nombre}</p>
            <p className="text-sm text-slate-500">participó como integrante del equipo</p>
            <p className="text-base font-semibold" style={{ color: viewColor.indigo }}>
              {sel.equipo}
            </p>

            <p className="mt-3 text-sm text-slate-600">
              {sel.ie} · Categoría {sel.categoria}
            </p>
            <p className="mt-1 text-xs text-slate-400">Código: {sel.codigo} · 18 dic 2024</p>

            <div className="mt-6 flex justify-around">
              <div className="text-center">
                <div className="mx-auto mb-1 w-32 border-t border-slate-400" />
                <p className="text-xs text-slate-500">Organizador</p>
              </div>
              <div className="text-center">
                <div className="mx-auto mb-1 w-32 border-t border-slate-400" />
                <p className="text-xs text-slate-500">Dirección I.E.</p>
              </div>
            </div>

            <p className="mt-5 text-[10px] text-slate-400">
              Verificar en: plataforma.robotica.edu.pe/cert/{sel.codigo}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
