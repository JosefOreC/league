import { Link, useLocation, useNavigate } from "react-router";
import { useAuth } from "../../context/AuthContext";
import { 
  LayoutDashboard, 
  Trophy, 
  Users, 
  Swords, 
  ListOrdered, 
  BrainCircuit, 
  FileBarChart, 
  Building2, 
  CalendarDays, 
  LifeBuoy,
  Bot
} from "lucide-react";
import { SystemRol } from "../../types/auth";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.JUEZ, SystemRol.REPRESENTANTE] },
  { name: "Torneos", href: "/dashboard/torneos", icon: Trophy, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.JUEZ, SystemRol.REPRESENTANTE, SystemRol.PUBLICO] },
  { name: "Equipos", href: "/dashboard/equipos", icon: Users, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.REPRESENTANTE] },
  { name: "Competencias", href: "/dashboard/competencias", icon: Swords, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.JUEZ] },
  { name: "Resultados", href: "/dashboard/resultados", icon: ListOrdered, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.JUEZ, SystemRol.REPRESENTANTE, SystemRol.PUBLICO] },
  { name: "IA Recomendaciones", href: "/dashboard/ia", icon: BrainCircuit, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR] },
  { name: "Reportes", href: "/dashboard/reportes", icon: FileBarChart, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR] },
  { name: "Instituciones", href: "/dashboard/instituciones", icon: Building2, roles: [SystemRol.ADMIN] },
  { name: "Calendario", href: "/dashboard/calendario", icon: CalendarDays, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.JUEZ, SystemRol.REPRESENTANTE, SystemRol.PUBLICO] },
  { name: "Soporte", href: "/dashboard/soporte", icon: LifeBuoy, roles: [SystemRol.ADMIN, SystemRol.ORGANIZADOR, SystemRol.JUEZ, SystemRol.REPRESENTANTE, SystemRol.PUBLICO] },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const filteredNavItems = navItems.filter(
    (item) => user && item.roles.includes(user.rol)
  );

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className="flex flex-col w-64 bg-slate-900 border-r border-slate-800 h-full">
      <div className="flex items-center justify-center h-16 bg-slate-900 border-b border-slate-800">
        <Link to="/dashboard" className="flex items-center space-x-2 text-white font-bold text-xl">
          <Bot className="text-blue-500 h-8 w-8" />
          <span>Zoids League</span>
        </Link>
      </div>
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="space-y-1 px-2">
          {filteredNavItems.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  group flex items-center px-3 py-2 text-sm font-medium rounded-md
                  ${
                    isActive
                      ? "bg-slate-800 text-white"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }
                `}
              >
                <item.icon
                  className={`
                    flex-shrink-0 -ml-1 mr-3 h-5 w-5
                    ${
                      isActive
                        ? "text-blue-500"
                        : "text-slate-400 group-hover:text-blue-400"
                    }
                  `}
                />
                <span className="truncate">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="p-4 border-t border-slate-800 space-y-3">
        {/* Info de usuario autenticado */}
        {user && (
          <div className="flex items-center gap-3 px-1">
            <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
              {user.email.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-xs text-white font-medium truncate">{user.email}</p>
              <p className="text-[10px] text-slate-400 capitalize">{user.rol}</p>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="w-full text-left px-3 py-2 text-xs text-slate-400 hover:text-white hover:bg-slate-800 rounded-md transition-colors"
        >
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}
