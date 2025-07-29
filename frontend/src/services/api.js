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
  },

  // Get order by order number (no authentication required)
  getOrderByNumber: async (orderNumber) => {
    try {
      const response = await axios.get(`${API}/orders/myorder/${orderNumber}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching order by number:', error);
      throw error;
    }
  },

  // Get orders grouped by items (requires authentication)
  getOrdersByItem: async () => {
    try {
      const response = await axios.get(`${API}/orders/view-orders`);
      return response.data;
    } catch (error) {
      console.error('Error fetching orders by item:', error);
      throw error;
    }
  },

  // Update cooking status of an item (requires authentication)
  updateCookingStatus: async (orderId, itemName, cookingStatus) => {
    try {
      const response = await axios.patch(`${API}/orders/cooking-status`, {
        order_id: orderId,
        item_name: itemName,
        cooking_status: cookingStatus
      });
      return response.data;
    } catch (error) {
      console.error('Error updating cooking status:', error);
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

// Reports API calls
export const reportsAPI = {
  // Get payment method reports
  getPaymentReports: async () => {
    try {
      const response = await axios.get(`${API}/reports/payment`);
      return response.data;
    } catch (error) {
      console.error('Error fetching payment reports:', error);
      throw error;
    }
  },

  // Get item reports
  getItemReports: async () => {
    try {
      const response = await axios.get(`${API}/reports/items`);
      return response.data;
    } catch (error) {
      console.error('Error fetching item reports:', error);
      throw error;
    }
  },

  // Download payment reports as Excel
  downloadPaymentReports: async () => {
    try {
      const response = await axios.get(`${API}/reports/payment/export`, {
        responseType: 'blob',
      });
      
      // Create blob and download
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      
      // Get filename from response headers
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'payment_reports.xlsx';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]*)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return { success: true, filename };
    } catch (error) {
      console.error('Error downloading payment reports:', error);
      throw error;
    }
  },

  // Download item reports as Excel
  downloadItemReports: async () => {
    try {
      const response = await axios.get(`${API}/reports/items/export`, {
        responseType: 'blob',
      });
      
      // Create blob and download
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      
      // Get filename from response headers
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'menu_items_reports.xlsx';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]*)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return { success: true, filename };
    } catch (error) {
      console.error('Error downloading item reports:', error);
      throw error;
    }
  }
};

// Utility functions
export const formatOrderTime = (timeString) => {
  const time = new Date(timeString);
  return time.toLocaleString('en-US', {
    timeZone: 'America/New_York',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatDeliveryTime = (minutes) => {
  if (!minutes) return 'N/A';
  if (minutes < 60) {
    return `${Math.round(minutes)}m`;
  } else {
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
  }
};