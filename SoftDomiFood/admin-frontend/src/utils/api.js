import axios from 'axios';

// API Base URL from environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
// Para admin-frontend, siempre usar adminToken
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken');
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Add response interceptor to handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.error('Authentication failed:', error.response.data);
      // Redirigir al login si no está autenticado
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

// Authentication
export const authAPI = {
  login: async (credentials, isAdmin = true) => {
    const response = await api.post('/auth/login', credentials);
    if (response.data.token) {
      // Guardar token de admin
      localStorage.setItem('adminToken', response.data.token);
      localStorage.setItem('adminUser', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile');
    return response.data;
  },
};

// Products
export const productsAPI = {
  getAll: async () => {
    const response = await api.get('/products');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/products/${id}`);
    return response.data;
  },
};

// Admin
export const adminAPI = {
  getAllOrders: async () => {
    const response = await api.get('/admin/orders');
    return response.data;
  },

  updateOrderStatus: async (orderId, status) => {
    const response = await api.patch(`/admin/orders/${orderId}/status`, { status });
    return response.data;
  },

  createProduct: async (productData) => {
    const response = await api.post('/admin/products', productData);
    return response.data;
  },

  updateProduct: async (productId, productData) => {
    const response = await api.put(`/admin/products/${productId}`, productData);
    return response.data;
  },

  getAllCustomers: async () => {
    const response = await api.get('/admin/customers');
    return response.data;
  },
};

export default api;
