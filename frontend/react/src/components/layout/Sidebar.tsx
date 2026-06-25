import { useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { useAuth } from "../../context/AuthContext";
import {
  LayoutDashboard,
  Trophy,
  ListOrdered,
  BrainCircuit,
  FileBarChart,
  Building2,
  CalendarDays,
  LifeBuoy,
  Bot,
  Medal,
  Sparkles,
  PieChart,
  Activity,
  Lightbulb,
  Award,
  FileSignature,
} from "lucide-react";
import { SystemRol } from "../../types/auth";

const navItems = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.COACH, SystemRol.PARTICIPANTE],
  },
  {
    name: "Torneos",
    href: "/dashboard/torneos",
    icon: Trophy,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.COACH, SystemRol.PARTICIPANTE, SystemRol.PUBLICO],
  },
  {
    name: "Mis Torneos",
    href: "/dashboard/mis-torneos",
    icon: Medal,
    roles: [SystemRol.PARTICIPANTE],
  },
  {
    name: "Mis Simulaciones",
    href: "/dashboard/simulaciones",
    icon: Sparkles,
    roles: [SystemRol.PARTICIPANTE],
  },
  {
    name: "Resultados",
    href: "/dashboard/resultados",
    icon: ListOrdered,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.COACH, SystemRol.PARTICIPANTE, SystemRol.PUBLICO],
  },
  {
    name: "IA Recomendaciones",
    href: "/dashboard/ia",
    icon: BrainCircuit,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR],
  },
  {
    name: "Reportes",
    href: "/dashboard/reportes",
    icon: FileBarChart,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR],
  },
  {
    name: "Instituciones",
    href: "/dashboard/instituciones",
    icon: Building2,
    roles: [SystemRol.ADMIN],
  },
  // ── MVP3 · Analítica, Reportes e Inteligencia (demo torneo :id = 1) ──────
  {
    name: "Análisis Integral",
    href: "/dashboard/torneos/1/analisis-integral",
    icon: PieChart,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR],
  },
  {
    name: "Tablero Inteligencia",
    href: "/dashboard/torneos/1/tablero-inteligencia",
    icon: Activity,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR],
  },
  {
    name: "Apoyo a Decisiones",
    href: "/dashboard/torneos/1/apoyo-decisiones",
    icon: Lightbulb,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR],
  },
  {
    name: "Certificados",
    href: "/dashboard/torneos/1/certificados",
    icon: Award,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR],
  },
  {
    name: "Resumen Ejecutivo",
    href: "/dashboard/torneos/1/resumen-ejecutivo",
    icon: FileSignature,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR],
  },
  {
    name: "Reporte Institucional",
    href: "/dashboard/instituciones/ie-1/reporte?torneo=1",
    icon: Building2,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR],
  },
  {
    name: "Calendario",
    href: "/dashboard/calendario",
    icon: CalendarDays,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.COACH, SystemRol.PARTICIPANTE, SystemRol.PUBLICO],
  },
  {
    name: "Soporte",
    href: "/dashboard/soporte",
    icon: LifeBuoy,
    roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.COACH, SystemRol.PARTICIPANTE, SystemRol.PUBLICO],
  },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  // Extract tournament ID if present in current URL path, e.g. /dashboard/torneos/:id/...
  const match = location.pathname.match(/\/dashboard\/torneos\/([^/]+)/);
  const currentTournamentId = match ? match[1] : null;

  // Track the last active tournament ID to persist user context
  useEffect(() => {
    if (currentTournamentId && currentTournamentId !== "nuevo") {
      localStorage.setItem("lastTournamentId", currentTournamentId);
    }
  }, [currentTournamentId]);

  const activeTournamentId = currentTournamentId || localStorage.getItem("lastTournamentId") || "1";

  const getHref = (item: typeof navItems[number]) => {
    if (item.href.includes("/dashboard/torneos/1/")) {
      return item.href.replace("/dashboard/torneos/1/", `/dashboard/torneos/${activeTournamentId}/`);
    }
    if (item.href.includes("?torneo=1")) {
      return item.href.replace("?torneo=1", `?torneo=${activeTournamentId}`);
    }
    return item.href;
  };

  const filteredNavItems = navItems.filter(
    (item) => user && item.roles.includes(user.rol)
  );

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // Role display labels
  const rolLabel: Record<string, string> = {
    admin: "Administrador",
    manager: "Manager",
    participant: "Participante",
    coach: "Coach",
    invited: "Invitado",
  };

  return (
    <div className="flex flex-col w-64 bg-slate-900 border-r border-slate-800 h-full print:hidden">
      {/* Logo */}
      <div className="flex items-center justify-center h-16 bg-slate-900 border-b border-slate-800">
        <Link to="/dashboard" className="flex items-center space-x-2 text-white font-bold text-xl">
          <Bot className="text-blue-500 h-8 w-8" />
          <span>Zoids League</span>
        </Link>
      </div>

      {/* Nav items */}
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="space-y-0.5 px-2">
          {filteredNavItems.map((item) => {
            const itemHref = getHref(item);
            const isActive =
              item.href === "/dashboard"
                ? location.pathname === "/dashboard"
                : location.pathname.startsWith(itemHref);
            return (
              <Link
                key={item.name}
                to={itemHref}
                className={`group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                  isActive
                    ? "bg-slate-800 text-white"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`}
              >
                <item.icon
                  className={`flex-shrink-0 mr-3 h-5 w-5 transition-colors ${
                    isActive ? "text-blue-400" : "text-slate-400 group-hover:text-blue-400"
                  }`}
                />
                <span className="truncate">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* User info + logout */}
      <div className="p-4 border-t border-slate-800 space-y-3">
        {user && (
          <div className="flex items-center gap-3 px-1">
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center text-white text-sm font-bold shrink-0">
              {(user.name || user.email).charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-sm text-white font-semibold truncate leading-none mb-0.5">
                {user.name || user.email.split("@")[0]}
              </p>
              <p className="text-[10px] text-blue-400 font-bold uppercase tracking-wider">
                {rolLabel[user.rol] ?? user.rol}
              </p>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="w-full text-left px-3 py-2 text-xs text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
        >
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}
