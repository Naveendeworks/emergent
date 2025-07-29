import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { ClipboardList, CheckCircle, Clock, Plus, RefreshCw, Package, Hash } from 'lucide-react';
import OrderCard from './OrderCard';
import CreateOrderModal from './CreateOrderModal';
import EditOrderModal from './EditOrderModal';
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

  const handleOrderUpdated = (updatedOrder) => {
    setOrders(prevOrders => 
      prevOrders.map(order => 
        order.id === updatedOrder.id ? updatedOrder : order
      )
    );
    loadStats();
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
                  />
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