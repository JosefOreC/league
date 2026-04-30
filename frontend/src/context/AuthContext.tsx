import { createContext, useContext, useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { User, AuthState } from "../types/auth";
import {
  getAccessToken,
  decodeJwt,
  saveTokens,
  logoutUser,
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
    const token = getAccessToken();
    if (token) {
      const decoded = decodeJwt(token);
      // Verificar que el token no haya expirado
      if (decoded && decoded.exp * 1000 > Date.now()) {
        setUser(decoded);
      } else {
        logoutUser();
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (credentials: LoginRequest) => {
    const data = await loginUser(credentials);
    saveTokens(data.access_token, data.refresh_token);
    const decoded = decodeJwt(data.access_token);
    setUser(decoded);
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
