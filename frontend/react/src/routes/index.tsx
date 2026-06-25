import React from "react";
import { createBrowserRouter } from "react-router";
import { Login } from "../features/auth/Login";
import { Register } from "../features/auth/Register";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { DashboardHome } from "../features/dashboard/DashboardHome";
import { TournamentsList } from "../features/tournaments/TournamentsList";
import { CreateTournament } from "../features/tournaments/CreateTournament";
import { ConfigTournamentRules } from "../features/tournaments/ConfigTournamentRules";
import { TournamentAdminPanel } from "../features/tournaments/TournamentAdminPanel";
import { TournamentTeamsManagement } from "../features/tournaments/TournamentTeamsManagement";
import { RegisterTeam } from "../features/teams/RegisterTeam";
import { MyTournaments } from "../features/teams/MyTournaments";
import { Competitions } from "../features/competitions/Competitions";
import { Results } from "../features/results/Results";
import { AIRecommendations } from "../features/ai/AIRecommendations";
import { Reports } from "../features/reports/Reports";
import { Institutions } from "../features/institutions/Institutions";
import { CalendarView } from "../features/calendar/CalendarView";
import { Support } from "../features/support/Support";
import { PublicTournament } from "../features/tournaments/PublicTournament";
import { MySimulations } from "../features/simulation/MySimulations";
import { SimulationEditor } from "../features/simulation/SimulationEditor";
import { RetoAnalyzer } from "../features/simulation/RetoAnalyzer";
// ── MVP3 — Analítica, Reportes e Inteligencia de Torneo ───────────────────
import { AnalisisIntegral } from "../features/analytics/AnalisisIntegral";
import { ReporteIndividual } from "../features/analytics/ReporteIndividual";
import { ReporteInstitucional } from "../features/analytics/ReporteInstitucional";
import { TableroInteligencia } from "../features/analytics/TableroInteligencia";
import { ApoyoDecisiones } from "../features/analytics/ApoyoDecisiones";
import { Certificados } from "../features/analytics/Certificados";
import { ResumenEjecutivo } from "../features/analytics/ResumenEjecutivo";
import { PanelDocente } from "../features/analytics/PanelDocente";
import { RoleGuard } from "../components/auth/RoleGuard";
import { SystemRol } from "../types/auth";

// Convenience wrappers for common role sets
const ManagerOrAdmin = ({ children }: { children: React.ReactNode }) => (
  <RoleGuard allowedRoles={[SystemRol.ADMIN, SystemRol.ORGANIZADOR]}>{children}</RoleGuard>
);

const ParticipantOnly = ({ children }: { children: React.ReactNode }) => (
  <RoleGuard allowedRoles={[SystemRol.PARTICIPANTE]} redirectTo="/dashboard">{children}</RoleGuard>
);

const NotParticipant = ({ children }: { children: React.ReactNode }) => (
  <RoleGuard allowedRoles={[SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.COACH]} redirectTo="/dashboard">{children}</RoleGuard>
);

export const router = createBrowserRouter([
  // ── Public routes ─────────────────────────────────────────────────────────
  { path: "/",           Component: Login },
  { path: "/registro",   Component: Register },
  { path: "/t/:id",      Component: PublicTournament },

  // ── Dashboard (requires auth — DashboardLayout handles unauthenticated) ───
  {
    path: "/dashboard",
    Component: DashboardLayout,
    children: [
      // ── Visible to ALL authenticated roles ─────────────────────────────
      { index: true,              Component: DashboardHome },
      { path: "torneos",          Component: TournamentsList },
      { path: "torneos/:id/posiciones", Component: Results },
      { path: "torneos/:id/resultados", Component: Results },
      { path: "resultados",       Component: Results },
      { path: "calendario",       Component: CalendarView },
      { path: "soporte",          Component: Support },

      // ── Participant only ────────────────────────────────────
      {
        path: "mis-torneos",
        Component: () => <ParticipantOnly><MyTournaments /></ParticipantOnly>,
      },
      {
        path: "simulaciones",
        Component: () => <ParticipantOnly><MySimulations /></ParticipantOnly>,
      },
      {
        path: "simulaciones/torneo/:tournamentId",
        Component: () => <ParticipantOnly><SimulationEditor /></ParticipantOnly>,
      },
      {
        path: "simulaciones/torneo/:tournamentId/retos",
        Component: () => <ParticipantOnly><RetoAnalyzer /></ParticipantOnly>,
      },

      // ── Manager / Admin only ────────────────────────────────────────────
      {
        path: "torneos/nuevo",
        Component: () => <ManagerOrAdmin><CreateTournament /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/reglas",
        Component: () => <ManagerOrAdmin><ConfigTournamentRules /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/admin",
        Component: () => <ManagerOrAdmin><TournamentAdminPanel /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/equipos",
        Component: () => <ManagerOrAdmin><TournamentTeamsManagement /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/competencias",
        Component: () => <ManagerOrAdmin><Competitions /></ManagerOrAdmin>,
      },
      {
        path: "ia",
        Component: () => <ManagerOrAdmin><AIRecommendations /></ManagerOrAdmin>,
      },
      {
        path: "reportes",
        Component: () => <ManagerOrAdmin><Reports /></ManagerOrAdmin>,
      },
      {
        path: "instituciones",
        Component: () => (
          <RoleGuard allowedRoles={[SystemRol.ADMIN]}><Institutions /></RoleGuard>
        ),
      },

      // ── MVP3 · Analítica, Reportes e Inteligencia (Manager / Admin) ─────
      {
        path: "torneos/:id/analisis-integral",
        Component: () => <ManagerOrAdmin><AnalisisIntegral /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/equipos/:eid/reporte-individual",
        Component: () => <ManagerOrAdmin><ReporteIndividual /></ManagerOrAdmin>,
      },
      {
        path: "instituciones/:id/reporte",
        Component: () => <RoleGuard allowedRoles={[SystemRol.ADMIN]}><ReporteInstitucional /></RoleGuard>,
      },
      {
        path: "torneos/:id/tablero-inteligencia",
        Component: () => <ManagerOrAdmin><TableroInteligencia /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/apoyo-decisiones",
        Component: () => <ManagerOrAdmin><ApoyoDecisiones /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/certificados",
        Component: () => <ManagerOrAdmin><Certificados /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/resumen-ejecutivo",
        Component: () => <ManagerOrAdmin><ResumenEjecutivo /></ManagerOrAdmin>,
      },
      {
        path: "torneos/:id/equipos/:eid/panel-docente",
        Component: () => <NotParticipant><PanelDocente /></NotParticipant>,
      },

      // ── Participant only ────────────────────────────────────────────────
      {
        path: "torneos/:id/inscribir-equipo",
        Component: () => <ParticipantOnly><RegisterTeam /></ParticipantOnly>,
      },

      // ── Fallback ────────────────────────────────────────────────────────
      {
        path: "*",
        Component: () => (
          <div className="p-16 text-center">
            <p className="text-2xl font-bold text-slate-300">404</p>
            <p className="text-slate-400 mt-2">Ruta no encontrada.</p>
          </div>
        ),
      },
    ],
  },
]);
