import axios from 'axios';

// Create axios instance
// Ensure the backend URL is correctly set
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Log the API base URL for debugging
console.log('API Base URL:', API_BASE_URL);

const axiosConfig: any = {
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Expires': '0',
  },
  withCredentials: true, // Send cookies with requests
  timeout: 60000, // Increased to 60 seconds for audio processing
  maxContentLength: 100 * 1024 * 1024, // 100MB max content length
  maxBodyLength: 100 * 1024 * 1024, // 100MB max body length
};

const api = axios.create(axiosConfig);

// Add request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout - The server took too long to respond');
    } else if (!error.response) {
      console.error('Network Error - Please check your internet connection');
    } else if (error.response?.status === 401) {
      // Handle unauthorized errors
      localStorage.removeItem('token');
      // Redirect to login if not already on the login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;