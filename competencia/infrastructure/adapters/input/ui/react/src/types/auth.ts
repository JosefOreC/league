// Roles según HU-GT-01
export enum SystemRol {
  ADMIN = "admin",
  ORGANIZADOR = "manager",
  COACH = "coach",
  PARTICIPANTE = "participant",
  PUBLICO = "invited",
}

// Usuario autenticado (extraído del JWT payload)
export interface User {
  user_id: string;
  email: string;
  name: string;
  rol: string;
  exp: number;
}

// Body que se envía al backend en POST /api/auth/login
export interface LoginRequest {
  email: string;
  password: string;
}

// Respuesta exitosa del backend en POST /api/auth/login
export interface LoginResponse {
  user: any;
  token: {
    access_token: string;
    refresh_token: string;
  };
}

// Respuesta exitosa del backend en POST /api/auth/refresh
export interface RefreshResponse {
  access_token: string;
}

// Error HTTP 400 — campo faltante
export interface FieldError {
  campo: string;
  error: string;
}

// Estado global de autenticación
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
