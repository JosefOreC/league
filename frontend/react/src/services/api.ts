import axios from "axios";
import { getAccessToken, refreshAccessToken, clearTokens } from "./authService";
import { toast } from "sonner";

// Configuración base de Axios para comunicarse con el servidor (backend)

export const api = axios.create({
  //PRUEBA LOCAL
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/",
  //DESPLIEGUE EN PRODUCCIÓN
  // baseURL: import.meta.env.VITE_API_URL || "http://backend:8000/api/",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// ─── Interceptor de Peticiones ────────────────────────────────────────────────
// Agrega el token de autorización automáticamente antes de enviar cada petición

api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Interceptor de Respuestas ────────────────────────────────────────────────
// Verifica si el token expiró (error 401). Si expiró, trata de pedir uno nuevo.
// Si falla al pedir uno nuevo, cierra la sesión del usuario.

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null) {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve(token!);
    }
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => {
    // Show success toasts for mutations only if there's an explicit message
    const method = response.config.method?.toUpperCase();
    if (["POST", "PUT", "DELETE", "PATCH"].includes(method || "")) {
      const isAuthRoute =
        response.config.url?.includes("/auth/login") ||
        response.config.url?.includes("/auth/refresh");

      if (!isAuthRoute) {
        // Only show toast if backend returned an explicit message or detail
        const message = response.data?.message || response.data?.detail;
        if (message && typeof message === "string") {
          toast.success(message);
        }
      }
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle generic error messages
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      const method = originalRequest.method?.toUpperCase();

      // Show error toast for everything except specific auth flows handled elsewhere
      if (status !== 401 || originalRequest.url?.includes("/auth/login")) {
        const errorMsg = data?.detail || data?.error || data?.message || `Error ${status}: El servidor no pudo procesar la solicitud.`;
        toast.error(errorMsg);
      }
    } else if (error.request) {
      toast.error("No se pudo conectar con el servidor. Verifica tu conexión.");
    }

    // Auth refresh logic
    const isAuthRoute =
      originalRequest.url?.includes("/auth/login") ||
      originalRequest.url?.includes("/auth/refresh");

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthRoute) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await refreshAccessToken();
        processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();
        window.location.href = "/";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
