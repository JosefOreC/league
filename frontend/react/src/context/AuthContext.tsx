import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { User, AuthState } from "../types/auth";
import {
  getAccessToken,
  decodeJwt,
  saveTokens,
  logoutUser,
  getUserProfile,
} from "../services/authService";
import type { LoginRequest } from "../types/auth";
import { loginUser } from "../services/authService";

// ─── Context ──────────────────────────────────────────────────────────────────

interface AuthContextValue extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// ─── Provider ─────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Al montar, verificar si ya hay un token guardado y si sigue vigente
  useEffect(() => {
    const initAuth = async () => {
      const token = getAccessToken();
      if (token) {
        const decoded = decodeJwt(token);
        // Verificar que el token no haya expirado
        if (decoded && decoded.exp * 1000 > Date.now()) {
          // Primero seteamos lo que hay en el token para rapidez
          setUser(decoded);
          try {
            // Luego pedimos los datos completos (nombre real) al backend
            const fullProfile = await getUserProfile();
            setUser(fullProfile);
          } catch (error) {
            console.error("Error cargando perfil completo:", error);
          }
        } else {
          logoutUser();
        }
      }
      setIsLoading(false);
    };
    
    initAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    const data = await loginUser(credentials);
    saveTokens(data.token.access_token, data.token.refresh_token);
    
    // Primero seteamos los datos del token para asegurar que el usuario entre
    const decoded = decodeJwt(data.token.access_token);
    setUser(decoded as User);

    try {
      // Intentamos obtener el perfil completo (nombre real), pero si falla, no bloqueamos el login
      const fullProfile = await getUserProfile();
      setUser(fullProfile);
    } catch (error) {
      console.warn("No se pudo cargar el perfil completo en el login:", error);
    }
  };

  const logout = () => {
    logoutUser();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, isLoading, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  }
  return context;
}
