import axios from "axios";

/**
 * Configuración centralizada de Axios para la conexión de Frontend con Django REST Framework.
 */
export const api = axios.create({
  // Vite procesará esta variable de entorno de forma automática si la incluyes en un archivo .env
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
  // true es fundamental al comunicarse con Django para aceptar cookies de sesión y CSRF Tokens
  withCredentials: true, 
});

// Interceptor de Peticiones: 
// Muy útil para agregar el Token JWT a todas las llamadas que hagas al Backend (si usan JWT).
api.interceptors.request.use(
  (config) => {
    // Ejemplo:
    // const token = localStorage.getItem('access_token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de Respuestas:
// Excelente lugar para manejar expiración de tokens o redirigir al /login globalmente si da un 401.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Manejar cierre de sesión o token vencido aquí
      // window.location.href = "/";
    }
    return Promise.reject(error);
  }
);
