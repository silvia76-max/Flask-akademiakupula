/**
 * Configuración para el frontend React de Akademia Kupula
 * 
 * Este archivo contiene la configuración necesaria para conectar
 * el frontend React con el backend Flask.
 * 
 * Instrucciones:
 * 1. Copia este archivo en tu proyecto React
 * 2. Importa la configuración en tus archivos de API
 * 3. Usa la URL base para tus solicitudes
 */

// Configuración de la API
const API_CONFIG = {
  // URL base de la API
  BASE_URL: 'http://localhost:5000',
  
  // Endpoints principales
  ENDPOINTS: {
    // Autenticación
    AUTH: {
      LOGIN: '/api/auth/login',
      REGISTER: '/api/auth/register',
      LOGOUT: '/api/auth/logout',
      PROFILE: '/api/auth/profile',
      REFRESH: '/api/auth/refresh',
    },
    
    // Cursos
    CURSOS: {
      LIST: '/api/cursos/',
      DETAIL: (id) => `/api/cursos/${id}`,
      SEARCH: '/api/cursos/search',
    },
    
    // Carrito
    CART: {
      LIST: '/api/user/cart',
      ADD: '/api/user/cart/add',
      REMOVE: '/api/user/cart/remove',
      CLEAR: '/api/user/cart/clear',
    },
    
    // Lista de deseos
    WISHLIST: {
      LIST: '/api/user/wishlist',
      ADD: '/api/user/wishlist/add',
      REMOVE: '/api/user/wishlist/remove',
      CLEAR: '/api/user/wishlist/clear',
    },
    
    // Pagos
    PAYMENT: {
      CREATE_SESSION: '/api/payment/create-checkout-session',
      CHECK_STATUS: (sessionId) => `/api/payment/check-payment-status/${sessionId}`,
      HISTORY: '/api/payment/history',
    },
    
    // Pruebas
    TEST: {
      PING: '/api/test/ping',
      CORS: '/api/test/cors-test',
    },
  },
  
  // Configuración de las solicitudes
  REQUEST_CONFIG: {
    // Encabezados por defecto
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    
    // Tiempo de espera en milisegundos
    timeout: 10000,
    
    // Usar credenciales (cookies)
    withCredentials: false,
  },
};

/**
 * Función para crear una instancia de axios configurada
 * @param {Object} axios - Instancia de axios
 * @returns {Object} Instancia de axios configurada
 */
function createApiClient(axios) {
  // Crear instancia de axios con la configuración base
  const apiClient = axios.create({
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.REQUEST_CONFIG.timeout,
    headers: API_CONFIG.REQUEST_CONFIG.headers,
    withCredentials: API_CONFIG.REQUEST_CONFIG.withCredentials,
  });
  
  // Interceptor para añadir el token de autenticación
  apiClient.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
  
  // Interceptor para manejar errores
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      // Manejar errores de autenticación
      if (error.response && error.response.status === 401) {
        // Redirigir a la página de login
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
  
  return apiClient;
}

// Exportar la configuración
export { API_CONFIG, createApiClient };
