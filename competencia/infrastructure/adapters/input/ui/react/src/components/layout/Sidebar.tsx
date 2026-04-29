import { Link, useLocation } from "react-router";
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

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Torneos", href: "/dashboard/torneos", icon: Trophy },
  { name: "Equipos", href: "/dashboard/equipos", icon: Users },
  { name: "Competencias", href: "/dashboard/competencias", icon: Swords },
  { name: "Resultados", href: "/dashboard/resultados", icon: ListOrdered },
  { name: "IA Recomendaciones", href: "/dashboard/ia", icon: BrainCircuit },
  { name: "Reportes", href: "/dashboard/reportes", icon: FileBarChart },
  { name: "Instituciones", href: "/dashboard/instituciones", icon: Building2 },
  { name: "Calendario", href: "/dashboard/calendario", icon: CalendarDays },
  { name: "Soporte", href: "/dashboard/soporte", icon: LifeBuoy },
];

export function Sidebar() {
  const location = useLocation();

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
          {navItems.map((item) => {
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
      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <BrainCircuit className="h-4 w-4 text-purple-400" />
            <p className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Motor IA</p>
          </div>
          <div className="flex justify-between items-end mb-1">
            <p className="text-sm text-white font-medium">Estado Óptimo</p>
            <span className="text-[10px] text-green-400 font-bold bg-green-400/10 px-1.5 py-0.5 rounded">98%</span>
          </div>
          <div className="mt-2 w-full bg-slate-700 rounded-full h-1.5">
            <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: '98%' }}></div>
          </div>
          <p className="text-xs text-slate-400 mt-2">Analizando 45 equipos</p>
        </div>
      </div>
    </div>
  );
}
