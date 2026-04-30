import { Link, useNavigate, useLocation } from "react-router";
import { Bot, LogIn, AlertCircle, CheckCircle2, Lock, Eye, EyeOff } from "lucide-react";
import { useState, useEffect } from "react";
import { ImageWithFallback } from "../../components/ui/ImageWithFallback";
import { useAuth } from "../../context/AuthContext";
import { loginUser } from "../../services/authService";
import type { FieldError } from "../../types/auth";
import axios from "axios";

export function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  // Estados de error según los escenarios de la HU-GT-01
  const [generalError, setGeneralError] = useState<string | null>(null);    // 401, 423
  const [fieldErrors, setFieldErrors] = useState<FieldError[]>([]);          // 400
  const [blockedMinutes, setBlockedMinutes] = useState<number | null>(null); // 423

  // Verificar si venimos del registro exitoso
  useEffect(() => {
    if (location.state?.registered) {
      setSuccess("¡Cuenta creada con éxito! Ahora puedes iniciar sesión.");
    }
  }, [location]);

  const getFieldError = (campo: string) =>
    fieldErrors.find((e) => e.campo === campo)?.error ?? null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setGeneralError(null);
    setFieldErrors([]);
    setBlockedMinutes(null);
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate("/dashboard");
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const data = error.response?.data;

        if (status === 400) {
          // Escenario: campo obligatorio ausente → { campo, error }
          if (Array.isArray(data)) {
            setFieldErrors(data as FieldError[]);
          } else if (data?.campo) {
            setFieldErrors([data as FieldError]);
          } else {
            setGeneralError("Datos inválidos. Revisa los campos.");
          }
        } else if (status === 401) {
          // Escenario: credenciales incorrectas
          setGeneralError(data?.error ?? "Credenciales inválidas");
        } else if (status === 423) {
          // Escenario: cuenta bloqueada → extraer los minutos restantes del mensaje
          const message: string = data?.error ?? "Cuenta bloqueada. Intente más tarde.";
          const match = message.match(/(\d+)\s*minuto/i);
          if (match) setBlockedMinutes(parseInt(match[1]));
          setGeneralError(message);
        } else {
          setGeneralError("Ocurrió un error inesperado. Intente nuevamente.");
        }
      } else {
        setGeneralError("Error de conexión. Verifique su red.");
      }
    } finally {
      setIsLoading(false);
    }
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

          {/* ── Mensaje de éxito (Registro exitoso) ── */}
          {success && (
            <div className="flex items-start gap-3 p-3 rounded-md mb-6 text-sm bg-green-50 border border-green-300 text-green-700 animate-in fade-in slide-in-from-top-1">
              <CheckCircle2 className="mt-0.5 shrink-0" size={16} />
              <span>{success}</span>
            </div>
          )}

          {/* ── Error general (401 / 423) ── */}
          {generalError && (
            <div
              className={`flex items-start gap-3 p-3 rounded-md mb-6 text-sm ${
                blockedMinutes !== null
                  ? "bg-orange-50 border border-orange-300 text-orange-700"
                  : "bg-red-50 border border-red-300 text-red-700"
              }`}
            >
              {blockedMinutes !== null ? (
                <Lock className="mt-0.5 shrink-0" size={16} />
              ) : (
                <AlertCircle className="mt-0.5 shrink-0" size={16} />
              )}
              <span>{generalError}</span>
            </div>
          )}

          <form className="space-y-6" onSubmit={handleLogin}>
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700">
                Correo electrónico
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`appearance-none block w-full px-3 py-2 border rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    getFieldError("email") ? "border-red-400" : "border-slate-300"
                  }`}
                  placeholder="admin@zoidsleague.com"
                />
                {getFieldError("email") && (
                  <p className="mt-1 text-xs text-red-600">
                    El campo email es requerido
                  </p>
                )}
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700">
                Contraseña
              </label>
              <div className="mt-1 relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`appearance-none block w-full px-3 py-2 pr-10 border rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    getFieldError("password") ? "border-red-400" : "border-slate-300"
                  }`}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
                {getFieldError("password") && (
                  <p className="mt-1 text-xs text-red-600">
                    El campo contraseña es requerido
                  </p>
                )}
              </div>
            </div>

            {/* Remember me */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-900">
                  Recordarme
                </label>
              </div>
              <div className="text-sm">
                <a href="#" className="font-medium text-blue-600 hover:text-blue-500">
                  ¿Olvidó su contraseña?
                </a>
              </div>
            </div>

            {/* Submit */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Iniciando sesión...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <LogIn className="h-5 w-5" />
                    Iniciar sesión
                  </span>
                )}
              </button>
            </div>
          </form>

          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-slate-500">¿No tienes una cuenta?</span>
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
          src="https://images.unsplash.com/photo-1562758778-e5638b5b6607?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb2JvdGljcyUyMGNvbXBldGl0aW9uJTIwc3R1ZGVudHxlbnwxfHx8fDE3NzU3NDI3Njl8MA&ixlib=rb-4.1.0&q=80&w=1080"
          alt="Estudiantes en competencia de robótica"
        />
        <div className="absolute bottom-0 left-0 right-0 z-20 p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Empodera a la próxima generación</h2>
          <p className="text-lg text-blue-100 max-w-lg">
            Gestiona torneos, equipos y resultados en tiempo real con la ayuda de nuestra
            Inteligencia Artificial para recomendaciones óptimas.
          </p>
        </div>
      </div>
    </div>
  );
}
