import { createBrowserRouter } from "react-router";
import { Login } from "../features/auth/Login";
import { Register } from "../features/auth/Register";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { DashboardHome } from "../features/dashboard/DashboardHome";
import { TournamentsList } from "../features/tournaments/TournamentsList";
import { CreateTournament } from "../features/tournaments/CreateTournament";
import { ConfigTournamentRules } from "../features/tournaments/ConfigTournamentRules";
import { RegisterTeam } from "../features/teams/RegisterTeam";
import { TeamsList } from "../features/teams/TeamsList";
import { Competitions } from "../features/competitions/Competitions";
import { Results } from "../features/results/Results";
import { AIRecommendations } from "../features/ai/AIRecommendations";
import { Reports } from "../features/reports/Reports";
import { Institutions } from "../features/institutions/Institutions";
import { CalendarView } from "../features/calendar/CalendarView";
import { Support } from "../features/support/Support";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Login,
  },
  {
    path: "/registro",
    Component: Register,
  },
  {
    path: "/dashboard",
    Component: DashboardLayout,
    children: [
      { index: true, Component: DashboardHome },
      { path: "torneos", Component: TournamentsList },
      { path: "torneos/nuevo", Component: CreateTournament },
      { path: "torneos/:id/reglas", Component: ConfigTournamentRules },
      { path: "torneos/:id/inscribir-equipo", Component: RegisterTeam },
      { path: "torneos/:id/competencias", Component: Competitions },
      { path: "torneos/:id/posiciones", Component: Results },
      { path: "torneos/:id/resultados", Component: Results },
      { path: "equipos", Component: TeamsList },
      { path: "competencias", Component: Competitions },
      { path: "resultados", Component: Results },
      { path: "ia", Component: AIRecommendations },
      { path: "reportes", Component: Reports },
      { path: "instituciones", Component: Institutions },
      { path: "calendario", Component: CalendarView },
      { path: "soporte", Component: Support },
      { path: "*", Component: () => <div className="p-8 text-center">Ruta no encontrada</div> },
    ],
  },
]);
