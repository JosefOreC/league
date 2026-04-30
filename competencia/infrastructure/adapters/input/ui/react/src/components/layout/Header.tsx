import { Bell, Search, User, LogOut } from "lucide-react";
import { Link } from "react-router";
import { useAuth } from "../../context/AuthContext";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="flex-shrink-0 border-b border-slate-200 bg-white">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex flex-1">
          <div className="flex w-full md:ml-0">
            <div className="relative w-full text-slate-400 focus-within:text-slate-600 max-w-md">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                <Search className="h-5 w-5" aria-hidden="true" />
              </div>
              <input
                className="block h-full w-full border-transparent bg-slate-100 py-2 pl-10 pr-3 text-slate-900 placeholder-slate-500 focus:border-transparent focus:placeholder-slate-400 focus:outline-none focus:ring-0 sm:text-sm rounded-md"
                placeholder="Buscar equipos, torneos, resultados..."
                type="search"
                name="search"
              />
            </div>
          </div>
        </div>
        <div className="ml-4 flex items-center md:ml-6 space-x-4">
          <button
            type="button"
            className="relative rounded-full bg-white p-1 text-slate-400 hover:text-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <span className="sr-only">Ver notificaciones</span>
            <Bell className="h-6 w-6" aria-hidden="true" />
            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white" />
          </button>

          <div className="relative ml-3 border-l border-slate-200 pl-4 flex items-center space-x-3">
            <div className="flex flex-col text-right">
              <span className="text-sm font-bold text-slate-900 leading-none mb-1 block">
                {user?.name || user?.email?.split('@')[0] || "Invitado"}
              </span>
              <span className="text-[10px] text-blue-600 font-extrabold uppercase tracking-tight">
                {user?.rol || "Sin rol"}
              </span>
            </div>
            <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
              <User className="h-5 w-5" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
