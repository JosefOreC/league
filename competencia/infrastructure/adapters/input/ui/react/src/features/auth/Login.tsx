import { Link, useNavigate } from "react-router";
import { Bot, LogIn } from "lucide-react";
import { useState } from "react";
import { ImageWithFallback } from "../../components/ui/ImageWithFallback";

export function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState("organizer");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left Column - Form */}
      <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24">
        <div className="mx-auto w-full max-w-sm lg:w-96">
          <div className="flex items-center text-blue-600 gap-2 mb-8">
            <Bot size={40} className="text-purple-600" />
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
              Zoids League
            </h2>
          </div>
          
          <h3 className="text-xl font-bold text-slate-900 mb-2">Bienvenido de nuevo</h3>
          <p className="text-sm text-slate-500 mb-8">
            Plataforma inteligente de gestión de torneos de robótica
          </p>

          <form className="space-y-6" onSubmit={handleLogin}>
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-slate-700"
              >
                Correo electrónico
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="admin@zoidsleague.com"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-slate-700"
              >
                Contraseña
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium text-slate-700">
                Seleccionar rol
              </label>
              <select
                id="role"
                name="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-slate-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="organizer">Organizador</option>
                <option value="judge">Juez</option>
                <option value="team">Representante de Equipo</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                />
                <label
                  htmlFor="remember-me"
                  className="ml-2 block text-sm text-slate-900"
                >
                  Recordarme
                </label>
              </div>

              <div className="text-sm">
                <a
                  href="#"
                  className="font-medium text-blue-600 hover:text-blue-500"
                >
                  ¿Olvidó su contraseña?
                </a>
              </div>
            </div>

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                <LogIn className="mr-2 h-5 w-5" />
                Iniciar sesión
              </button>
            </div>
          </form>

          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-slate-500">
                  ¿No tienes una cuenta?
                </span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                to="/registro"
                className="w-full flex justify-center py-2.5 px-4 border border-slate-300 rounded-md shadow-sm text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                Registrarse
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Right Column - Image */}
      <div className="hidden lg:block relative w-0 flex-1">
        <div className="absolute inset-0 bg-blue-900 mix-blend-multiply z-10 opacity-60"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-blue-900 via-transparent to-transparent z-10 opacity-80"></div>
        <ImageWithFallback
          className="absolute inset-0 h-full w-full object-cover"
          src="https://images.unsplash.com/photo-1562758778-e5638b5b6607?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb2JvdGljcyUyMGNvbXBldGl0aW9uJTIwc3R1ZGVudHxlbnwxfHx8fDE3NzU3NDI3Njl8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Estudiantes en competencia de robótica"
        />
        <div className="absolute bottom-0 left-0 right-0 z-20 p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Empodera a la próxima generación</h2>
          <p className="text-lg text-blue-100 max-w-lg">
            Gestiona torneos, equipos y resultados en tiempo real con la ayuda de nuestra Inteligencia Artificial para recomendaciones óptimas.
          </p>
        </div>
      </div>
    </div>
  );
}
