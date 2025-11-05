import axios from 'axios';

// Use environment variable for API base URL in prod; fall back to same origin
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.origin;
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.withCredentials = true;

// Add request interceptor
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // The error will be handled by the components using useToast
    return Promise.reject(error);
  }
);

export default axios; 