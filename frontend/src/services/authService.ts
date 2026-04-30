import { api } from "./api";
import type { LoginRequest, LoginResponse, RefreshResponse, User } from "../types/auth";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

// ─── Funciones para manejar el almacenamiento local de tokens ────────────────────────────────────────────────────────────

export function saveTokens(access: string, refresh: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// ─── Decodificación del token JWT ───────────────────────────────────────────────────────────────

// Función para leer los datos del usuario directamente desde el token (sin backend)
export function decodeJwt(token: string): User | null {
  try {
    const payload = token.split(".")[1];
    const decoded = JSON.parse(atob(payload));
    return decoded as User;
  } catch {
    return null;
  }
}

// ─── Llamadas a la API ────────────────────────────────────────────────────────────────

// Función para iniciar sesión, devuelve los tokens de acceso y refresco
export async function loginUser(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>("/auth/login", credentials);
  return response.data;
}

// Función para renovar el token de acceso cuando caduca (usando el refresh token)
export async function refreshAccessToken(): Promise<string> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) throw new Error("No hay refresh token disponible");

  const response = await api.post<RefreshResponse>("/auth/refresh", {
    refresh_token: refreshToken,
  });

  const newToken = response.data.access_token;
  localStorage.setItem(ACCESS_TOKEN_KEY, newToken);
  return newToken;
}

// Función para limpiar la sesión actual del usuario
export function logoutUser() {
  clearTokens();
}
