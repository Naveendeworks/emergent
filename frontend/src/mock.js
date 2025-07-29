// Mock data for order management system

export const mockOrders = [
  {
    id: 1,
    customerName: "Sarah Johnson",
    orderTime: "2025-01-08T10:30:00Z",
    items: [
      { name: "Margherita Pizza", quantity: 2 },
      { name: "Caesar Salad", quantity: 1 },
      { name: "Coca Cola", quantity: 3 }
    ],
    status: "pending",
    totalItems: 6
  },
  {
    id: 2,
    customerName: "Mike Rodriguez",
    orderTime: "2025-01-08T10:45:00Z",
    items: [
      { name: "Chicken Burger", quantity: 1 },
      { name: "French Fries", quantity: 2 },
      { name: "Milkshake", quantity: 1 }
    ],
    status: "pending",
    totalItems: 4
  },
  {
    id: 3,
    customerName: "Emma Thompson",
    orderTime: "2025-01-08T11:15:00Z",
    items: [
      { name: "Beef Tacos", quantity: 3 },
      { name: "Guacamole", quantity: 1 },
      { name: "Lime Water", quantity: 2 }
    ],
    status: "pending",
    totalItems: 6
  },
  {
    id: 4,
    customerName: "David Chen",
    orderTime: "2025-01-08T09:20:00Z",
    items: [
      { name: "Sushi Roll", quantity: 2 },
      { name: "Miso Soup", quantity: 1 }
    ],
    status: "completed",
    totalItems: 3
  },
  {
    id: 5,
    customerName: "Lisa Park",
    orderTime: "2025-01-08T11:30:00Z",
    items: [
      { name: "Pasta Carbonara", quantity: 1 },
      { name: "Garlic Bread", quantity: 2 },
      { name: "Red Wine", quantity: 1 }
    ],
    status: "pending",
    totalItems: 4
  }
];

// Helper functions for mock data manipulation
export const getPendingOrders = () => {
  return mockOrders.filter(order => order.status === 'pending');
};

export const getCompletedOrders = () => {
  return mockOrders.filter(order => order.status === 'completed');
};

export const completeOrder = (orderId) => {
  const order = mockOrders.find(order => order.id === orderId);
  if (order) {
    order.status = 'completed';
  }
  return order;
};

export const formatOrderTime = (timeString) => {
  const time = new Date(timeString);
  return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export const getTotalItemsInOrder = (items) => {
  return items.reduce((total, item) => total + item.quantity, 0);
};