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
// Frontend del cliente SOLO usa clientToken, nunca adminToken
api.interceptors.request.use((config) => {
  // Solo usar token de cliente
  const token = localStorage.getItem('clientToken');
  
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
      // Opcional: Redirigir al usuario a la página de inicio de sesión
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication
export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    // Si el registro devuelve token, guardarlo como cliente
    if (response.data.token) {
      localStorage.setItem('clientToken', response.data.token);
      localStorage.setItem('clientUser', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  login: async (credentials, isAdmin = false) => {
    const response = await api.post('/auth/login', credentials);
    if (response.data.token) {
      // Guardar token según el tipo de usuario
      if (isAdmin) {
        localStorage.setItem('adminToken', response.data.token);
        localStorage.setItem('adminUser', JSON.stringify(response.data.user));
      } else {
        localStorage.setItem('clientToken', response.data.token);
        localStorage.setItem('clientUser', JSON.stringify(response.data.user));
      }
      // Mantener compatibilidad con 'token' para requests que no especifican contexto
      localStorage.setItem('token', response.data.token);
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

// Orders
export const ordersAPI = {
  getAll: async () => {
    const response = await api.get('/orders');
    return response.data;
  },

  create: async (orderData) => {
    const response = await api.post('/orders', orderData);
    return response.data;
  },

  getStatus: async (orderId) => {
    const response = await api.get(`/orders/${orderId}/status`);
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

// Addresses
export const addressesAPI = {
  getAll: async () => {
    const response = await api.get('/addresses');
    return response.data;
  },

  create: async (addressData) => {
    const response = await api.post('/addresses', addressData);
    return response.data;
  },

  setDefault: async (addressId) => {
    const response = await api.put(`/addresses/${addressId}/default`);
    return response.data;
  },
};

export default api;
