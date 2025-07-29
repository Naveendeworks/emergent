import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Order API calls
export const ordersAPI = {
  // Get all orders
  getOrders: async () => {
    try {
      const response = await axios.get(`${API}/orders/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching orders:', error);
      throw error;
    }
  },

  // Create new order
  createOrder: async (orderData) => {
    try {
      const response = await axios.post(`${API}/orders/`, orderData);
      return response.data;
    } catch (error) {
      console.error('Error creating order:', error);
      throw error;
    }
  },

  // Update existing order
  updateOrder: async (orderId, orderData) => {
    try {
      const response = await axios.put(`${API}/orders/${orderId}`, orderData);
      return response.data;
    } catch (error) {
      console.error('Error updating order:', error);
      throw error;
    }
  },

  // Mark order as complete
  completeOrder: async (orderId) => {
    try {
      const response = await axios.put(`${API}/orders/${orderId}/complete`);
      return response.data;
    } catch (error) {
      console.error('Error completing order:', error);
      throw error;
    }
  },

  // Cancel order
  cancelOrder: async (orderId) => {
    try {
      const response = await axios.delete(`${API}/orders/${orderId}`);
      return response.data;
    } catch (error) {
      console.error('Error cancelling order:', error);
      throw error;
    }
  },

  // Get order statistics
  getOrderStats: async () => {
    try {
      const response = await axios.get(`${API}/orders/stats/summary`);
      return response.data;
    } catch (error) {
      console.error('Error fetching order stats:', error);
      throw error;
    }
  }
};

// Menu API calls
export const menuAPI = {
  // Get complete menu
  getMenu: async () => {
    try {
      const response = await axios.get(`${API}/menu/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching menu:', error);
      throw error;
    }
  },

  // Get menu item by ID
  getMenuItem: async (itemId) => {
    try {
      const response = await axios.get(`${API}/menu/item/${itemId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching menu item:', error);
      throw error;
    }
  },

  // Get items by category
  getItemsByCategory: async (category) => {
    try {
      const response = await axios.get(`${API}/menu/category/${category}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching items by category:', error);
      throw error;
    }
  },

  // Search menu items
  searchMenuItems: async (query) => {
    try {
      const response = await axios.get(`${API}/menu/search/${query}`);
      return response.data;
    } catch (error) {
      console.error('Error searching menu items:', error);
      throw error;
    }
  }
};

// Utility functions
export const formatOrderTime = (timeString) => {
  const time = new Date(timeString);
  return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};