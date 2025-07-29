import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ClipboardList, CheckCircle, Clock, Plus, RefreshCw, Package, Hash, ChefHat } from 'lucide-react';
import OrderCard from './OrderCard';
import CreateOrderModal from './CreateOrderModal';
import EditOrderModal from './EditOrderModal';
import NotificationSystem from './NotificationSystem';
import { ordersAPI, formatOrderTime, formatDeliveryTime } from '../services/api';
import { useToast } from '../hooks/use-toast';

const OrderManager = ({ onLogout }) => {
  const [orders, setOrders] = useState([]);
  const [activeTab, setActiveTab] = useState('pending');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ pending: 0, completed: 0, total: 0, averageDeliveryTime: null });
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [viewOrdersData, setViewOrdersData] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const { toast } = useToast();

  useEffect(() => {
    loadOrders();
    loadStats();
    if (activeTab === 'view-orders') {
      loadViewOrdersData();
    }
  }, [activeTab]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const ordersData = await ordersAPI.getOrders();
      setOrders(ordersData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load orders",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await ordersAPI.getOrderStats();
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadViewOrdersData = async () => {
    try {
      setLoading(true);
      const data = await ordersAPI.getOrdersByItem();
      setViewOrdersData(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load view orders data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCookingStatusUpdate = async (orderId, itemName, newStatus) => {
    try {
      await ordersAPI.updateCookingStatus(orderId, itemName, newStatus);
      // Reload view orders data to reflect changes
      loadViewOrdersData();
      toast({
        title: "Success",
        description: `${itemName} status updated to ${newStatus}`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update cooking status",
        variant: "destructive",
      });
    }
  };

  const handleCompleteOrder = async (orderId) => {
    try {
      const updatedOrder = await ordersAPI.completeOrder(orderId);
      
      // Update orders list
      setOrders(prevOrders => 
        prevOrders.map(order => 
          order.id === orderId 
            ? { ...order, status: 'completed', completedTime: updatedOrder.completedTime }
            : order
        )
      );

      // Update stats
      await loadStats();

      const completedOrder = orders.find(order => order.id === orderId);
      toast({
        title: "Order Completed",
        description: `Order for ${completedOrder?.customerName} has been marked as complete.`,
        duration: 3000,
      });

      // Auto-switch to pending tab if no more pending orders
      const remainingPending = orders.filter(order => order.status === 'pending' && order.id !== orderId);
      if (remainingPending.length === 0) {
        setTimeout(() => setActiveTab('completed'), 1500);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to complete order",
        variant: "destructive",
      });
    }
  };

  const handleOrderCreated = (newOrder) => {
    setOrders(prevOrders => [newOrder, ...prevOrders]);
    loadStats();
  };

  const handleEditOrder = (order) => {
    setSelectedOrder(order);
    setEditModalOpen(true);
  };

  const addNotification = (orderNumber, customerName, itemName, quantity) => {
    const newNotification = {
      id: Date.now() + Math.random(),
      orderNumber,
      customerName,
      itemName,
      quantity,
      timestamp: new Date().toISOString()
    };
    
    setNotifications(prev => [newNotification, ...prev]);
  };

  const dismissNotification = (notificationId) => {
    setNotifications(prev => prev.filter(n => n.id !== notificationId));
  };

  const handleOrderUpdated = (updatedOrder = null) => {
    if (updatedOrder) {
      // Update specific order if provided
      setOrders(prevOrders => 
        prevOrders.map(order => 
          order.id === updatedOrder.id ? updatedOrder : order
        )
      );
      
      // Check if this is an update (not creation) and add notifications for new items
      const existingOrder = orders.find(o => o.id === updatedOrder.id);
      if (existingOrder) {
        // Compare items to find new additions
        const existingItems = existingOrder.items || [];
        const newItems = updatedOrder.items || [];
        
        newItems.forEach(newItem => {
          const existingItem = existingItems.find(item => item.name === newItem.name);
          if (!existingItem || existingItem.quantity < newItem.quantity) {
            const addedQuantity = existingItem ? 
              newItem.quantity - existingItem.quantity : newItem.quantity;
            addNotification(
              updatedOrder.orderNumber,
              updatedOrder.customerName,
              newItem.name,
              addedQuantity
            );
          }
        });
      }
    } else {
      // Reload all orders if no specific order provided
      loadOrders();
    }
    
    loadStats();
    
    // Reload view orders data if on that tab
    if (activeTab === 'view-orders') {
      loadViewOrdersData();
    }
  };

  const handleCancelOrder = async (orderId) => {
    try {
      await ordersAPI.cancelOrder(orderId);
      
      // Remove order from list
      setOrders(prevOrders => prevOrders.filter(order => order.id !== orderId));
      
      // Update stats
      await loadStats();

      toast({
        title: "Order Cancelled",
        description: "Order has been successfully cancelled.",
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to cancel order",
        variant: "destructive",
      });
    }
  };

  const handleRefresh = () => {
    loadOrders();
    loadStats();
  };

  const pendingOrders = orders.filter(order => order.status === 'pending');
  const completedOrders = orders.filter(order => order.status === 'completed');

  return (
    <div className="p-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={handleRefresh}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button 
                onClick={() => setCreateModalOpen(true)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Order
              </Button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Orders</CardTitle>
              <Clock className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {stats.pending}
              </div>
              <p className="text-xs text-gray-600">Orders awaiting completion</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats.completed}
              </div>
              <p className="text-xs text-gray-600">Orders completed today</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Orders</CardTitle>
              <ClipboardList className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {stats.total}
              </div>
              <p className="text-xs text-gray-600">All orders today</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Delivery Time</CardTitle>
              <Clock className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {formatDeliveryTime(stats.averageDeliveryTime)}
              </div>
              <p className="text-xs text-gray-600">Order to completion</p>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="pending" className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Pending Orders
              {pendingOrders.length > 0 && (
                <Badge variant="secondary" className="ml-2">
                  {pendingOrders.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="completed" className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Completed Orders
              {completedOrders.length > 0 && (
                <Badge variant="secondary" className="ml-2">
                  {completedOrders.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="view-orders" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              View Orders
              {viewOrdersData.length > 0 && (
                <Badge variant="secondary" className="ml-2">
                  {viewOrdersData.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="pending" className="space-y-4">
            {pendingOrders.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <CheckCircle className="h-16 w-16 text-green-500 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">All caught up!</h3>
                  <p className="text-gray-600 text-center">
                    No pending orders at the moment. Great work!
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {pendingOrders.map((order) => (
                  <OrderCard 
                    key={order.id} 
                    order={order} 
                    onComplete={handleCompleteOrder}
                    onEdit={handleEditOrder}
                    onCancel={handleCancelOrder}
                    onOrderUpdated={handleOrderUpdated}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="completed" className="space-y-4">
            {completedOrders.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Clock className="h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No completed orders yet</h3>
                  <p className="text-gray-600 text-center">
                    Completed orders will appear here.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {completedOrders.map((order) => (
                  <OrderCard 
                    key={order.id} 
                    order={order} 
                    onComplete={handleCompleteOrder}
                    onEdit={handleEditOrder}
                    onCancel={handleCancelOrder}
                    onOrderUpdated={handleOrderUpdated}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="view-orders" className="space-y-4">
            {viewOrdersData.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <ChefHat className="h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">No pending orders</h3>
                  <p className="text-gray-600 text-center">
                    Orders grouped by food category will appear here.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                {viewOrdersData.map((categoryGroup) => (
                  <Card key={categoryGroup.category_name} className="border-l-4 border-l-blue-500">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-2">
                          <ChefHat className="h-5 w-5 text-blue-600" />
                          <span className="text-blue-800">{categoryGroup.category_name}</span>
                        </span>
                        <Badge variant="outline" className="bg-blue-50 text-blue-700">
                          {categoryGroup.total_items} items
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {categoryGroup.items.map((itemGroup) => (
                          <div key={itemGroup.item_name} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center gap-2">
                                <Package className="h-4 w-4 text-gray-600" />
                                <span className="font-semibold text-gray-800">{itemGroup.item_name}</span>
                              </div>
                              <Badge variant="outline" className="bg-white">
                                Total Qty: {itemGroup.total_quantity}
                              </Badge>
                            </div>
                            
                            <div className="space-y-2">
                              {itemGroup.orders.map((orderInfo, index) => (
                                <div key={index} className="flex items-center justify-between p-3 bg-white rounded border">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                      <Hash className="h-4 w-4 text-gray-500" />
                                      <span className="font-medium">#{orderInfo.orderNumber}</span>
                                      <span className="text-gray-600">• {orderInfo.customerName}</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                      <span>Qty: {orderInfo.quantity}</span>
                                      <span>•</span>
                                      <span>${orderInfo.subtotal?.toFixed(2) || '0.00'}</span>
                                      <span>•</span>
                                      <span>{formatOrderTime(orderInfo.orderTime)}</span>
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Badge 
                                      className={`${
                                        orderInfo.cooking_status === 'finished' ? 'bg-green-100 text-green-800 border-green-200' :
                                        orderInfo.cooking_status === 'cooking' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                                        'bg-gray-100 text-gray-800 border-gray-200'
                                      } border text-xs`}
                                    >
                                      {orderInfo.cooking_status}
                                    </Badge>
                                    <Select 
                                      value={orderInfo.cooking_status} 
                                      onValueChange={(value) => handleCookingStatusUpdate(orderInfo.order_id, itemGroup.item_name, value)}
                                    >
                                      <SelectTrigger className="w-32 h-8">
                                        <SelectValue />
                                      </SelectTrigger>
                                      <SelectContent>
                                        <SelectItem value="not started">Not Started</SelectItem>
                                        <SelectItem value="cooking">Cooking</SelectItem>
                                        <SelectItem value="finished">Finished</SelectItem>
                                      </SelectContent>
                                    </Select>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>

        <CreateOrderModal 
          open={createModalOpen}
          onOpenChange={setCreateModalOpen}
          onOrderCreated={handleOrderCreated}
        />

        <EditOrderModal 
          open={editModalOpen}
          onOpenChange={setEditModalOpen}
          order={selectedOrder}
          onOrderUpdated={handleOrderUpdated}
        />
      </div>
    </div>
  );
};

export default OrderManager;