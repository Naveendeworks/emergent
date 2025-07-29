import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth service
export const authService = {
  // Login
  login: async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password
      });
      
      // Store token in localStorage
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('username', response.data.username);
      
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Logout
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
  },

  // Get token
  getToken: () => {
    return localStorage.getItem('token');
  },

  // Get username
  getUsername: () => {
    return localStorage.getItem('username');
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    return token !== null;
  },

  // Verify token
  verifyToken: async () => {
    try {
      const token = authService.getToken();
      if (!token) return false;

      const response = await axios.get(`${API}/auth/verify`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.data.valid;
    } catch (error) {
      console.error('Token verification error:', error);
      authService.logout(); // Clear invalid token
      return false;
    }
  }
};

// Axios interceptor to add token to requests
axios.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Axios interceptor to handle 401 responses
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      window.location.reload();
    }
    return Promise.reject(error);
  }
);