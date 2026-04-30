import { Link, useNavigate } from "react-router";
import { Bot, UserPlus, AlertCircle, Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { ImageWithFallback } from "../../components/ui/ImageWithFallback";
import { registerUser } from "../../services/authService";

export function Register() {
  const navigate = useNavigate();
  const [role, setRole] = useState("participant");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Enviamos los datos al backend (rol se ignora o se maneja internamente en el backend)
      const response = await registerUser({
        email,
        password,
        name,
        birth_date: birthDate
      });
      
      console.log("Registro exitoso:", response);
      // Si el registro es exitoso, redirigimos al login con estado exitoso
      navigate("/", { state: { registered: true } });
    } catch (err: any) {
      console.error("Error completo de registro:", err);
      // Intentamos extraer el mensaje de error específico del backend
      const backendError = err.response?.data?.error;
      const detailError = err.response?.data?.detail;
      
      setError(backendError || detailError || "Error de conexión con el servidor.");
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
          
          <h3 className="text-xl font-bold text-slate-900 mb-2">Crear nueva cuenta</h3>
          <p className="text-sm text-slate-500 mb-8">
            Únete a la plataforma líder en gestión de torneos de robótica
          </p>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 flex items-center gap-3 text-red-700 text-sm animate-in fade-in slide-in-from-top-1">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleRegister}>
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-slate-700"
              >
                Nombre completo
              </label>
              <div className="mt-1">
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Juan Pérez"
                />
              </div>

              <label
                htmlFor="email"
                className="block text-sm font-medium text-slate-700 mt-4"
              >
                Correo electrónico
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="juan@ejemplo.com"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-medium text-slate-700"
                  >
                    Contraseña
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="appearance-none block w-full px-3 py-2 pr-10 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>
                <div>
                  <label
                    htmlFor="birth_date"
                    className="block text-sm font-medium text-slate-700"
                  >
                    Fecha Nac.
                  </label>
                  <div className="mt-1">
                    <input
                      id="birth_date"
                      name="birth_date"
                      type="date"
                      required
                      value={birthDate}
                      onChange={(e) => setBirthDate(e.target.value)}
                      className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
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
                <option value="participant">Participante / Estudiante</option>
                <option value="coach">Representante / Docente</option>
                <option value="manager">Organizador de Torneo</option>
              </select>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <UserPlus className="mr-2 h-5 w-5" />
                    Crear cuenta
                  </>
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
                <span className="px-2 bg-white text-slate-500">
                  ¿Ya tienes una cuenta?
                </span>
              </div>
            </div>

            <div className="mt-6">
              <Link
                to="/"
                className="w-full flex justify-center py-2.5 px-4 border border-slate-300 rounded-md shadow-sm text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
              >
                Iniciar sesión
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Right Column - Image */}
      <div className="hidden lg:block relative w-0 flex-1">
        <div className="absolute inset-0 bg-purple-900 mix-blend-multiply z-10 opacity-50"></div>
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent z-10 opacity-90"></div>
        <ImageWithFallback
          className="absolute inset-0 h-full w-full object-cover"
          src="https://images.unsplash.com/photo-1578918748648-7d30d67436c2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjByb2JvdCUyMGFybSUyMGNvZGluZyUyMGRhc2hib2FyZHxlbnwxfHx8fDE3NzU3NDI3Njl8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Panel de control robótico moderno"
        />
        <div className="absolute bottom-0 left-0 right-0 z-20 p-12 text-white">
          <h2 className="text-3xl font-bold mb-4">Tecnología en tus manos</h2>
          <p className="text-lg text-slate-200 max-w-lg">
            Regístrate y comienza a configurar y administrar las futuras estrellas de la innovación tecnológica.
          </p>
        </div>
      </div>
    </div>
  );
}
