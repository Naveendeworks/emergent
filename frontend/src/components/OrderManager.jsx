import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import { ClipboardList, CheckCircle, Clock, Plus, RefreshCw, Package, Hash, ChefHat, Search, TrendingUp, Users, DollarSign, Timer, Utensils, Store } from 'lucide-react';
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
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadOrders();
    loadStats();
    if (activeTab === 'kitchen-board') {
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
        title: "System Error",
        description: "Failed to load order tickets",
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
      console.error('Failed to load restaurant metrics:', error);
    }
  };

  const loadViewOrdersData = async () => {
    try {
      setLoading(true);
      const data = await ordersAPI.getOrdersByItem();
      setViewOrdersData(data);
    } catch (error) {
      toast({
        title: "Kitchen Error",
        description: "Failed to load kitchen preparation board",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCookingStatusUpdate = async (orderId, itemName, newStatus) => {
    try {
      console.log('Updating status:', { orderId, itemName, newStatus });
      const result = await ordersAPI.updateCookingStatus(orderId, itemName, newStatus);
      console.log('Update result:', result);
      
      // Reload both views
      loadViewOrdersData();
      loadOrders();
      loadStats();
      
      toast({
        title: "Kitchen Update",
        description: `${itemName} preparation status updated to ${newStatus}`,
      });
    } catch (error) {
      console.error('Kitchen Board Status Update Error:', error);
      toast({
        title: "Kitchen Error",
        description: `Failed to update ${itemName} status: ${error.response?.data?.detail || error.message}`,
        variant: "destructive",
      });
    }
  };

  const handleCompleteOrder = async (orderId) => {
    try {
      const updatedOrder = await ordersAPI.completeOrder(orderId);
      
      setOrders(prevOrders => 
        prevOrders.map(order => 
          order.id === orderId 
            ? { ...order, status: 'completed', completedTime: updatedOrder.completedTime }
            : order
        )
      );

      await loadStats();

      const completedOrder = orders.find(order => order.id === orderId);
      toast({
        title: "Order Served! 🎉",
        description: `Ticket for ${completedOrder?.customerName} has been successfully served.`,
        duration: 4000,
      });

      const remainingPending = orders.filter(order => order.status === 'pending' && order.id !== orderId);
      if (remainingPending.length === 0) {
        setTimeout(() => setActiveTab('served'), 1500);
      }
    } catch (error) {
      toast({
        title: "Service Error",
        description: "Failed to complete order service",
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
      setOrders(prevOrders => 
        prevOrders.map(order => 
          order.id === updatedOrder.id ? updatedOrder : order
        )
      );
      
      const existingOrder = orders.find(o => o.id === updatedOrder.id);
      if (existingOrder) {
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
      loadOrders();
    }
    
    loadStats();
    
    if (activeTab === 'kitchen-board') {
      loadViewOrdersData();
    }
  };

  const handleCancelOrder = async (orderId) => {
    try {
      await ordersAPI.cancelOrder(orderId);
      
      setOrders(prevOrders => prevOrders.filter(order => order.id !== orderId));
      await loadStats();

      toast({
        title: "Order Cancelled",
        description: "Order ticket has been successfully cancelled.",
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: "Cancellation Error",
        description: "Failed to cancel order ticket",
        variant: "destructive",
      });
    }
  };

  const handleRefresh = () => {
    loadOrders();
    loadStats();
  };

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }
    
    try {
      setIsSearching(true);
      const results = await ordersAPI.searchOrders(query);
      setSearchResults(results);
    } catch (error) {
      toast({
        title: "Search Error",
        description: "Failed to search order tickets",
        variant: "destructive",
      });
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchInputChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    if (query.length >= 2) {
      const timeoutId = setTimeout(() => {
        handleSearch(query);
      }, 300);
      
      return () => clearTimeout(timeoutId);
    } else {
      setSearchResults([]);
      setIsSearching(false);
    }
  };

  const pendingOrders = orders.filter(order => order.status === 'pending')
    .sort((a, b) => new Date(a.orderTime) - new Date(b.orderTime));
  const completedOrders = orders.filter(order => order.status === 'completed');

  const statsCards = [
    {
      title: "Active Tickets",
      value: stats.pending,
      icon: Clock,
      color: "text-amber-600",
      bgColor: "bg-amber-100",
      description: "Orders in preparation"
    },
    {
      title: "Served Today",
      value: stats.completed,
      icon: CheckCircle,
      color: "text-emerald-600",
      bgColor: "bg-emerald-100",
      description: "Successfully completed"
    },
    {
      title: "Total Orders",
      value: stats.total,
      icon: TrendingUp,
      color: "text-blue-600",
      bgColor: "bg-blue-100",
      description: "Today's volume"
    },
    {
      title: "Avg Service Time",
      value: formatDeliveryTime(stats.averageDeliveryTime),
      icon: Timer,
      color: "text-purple-600",
      bgColor: "bg-purple-100",
      description: "Kitchen to customer"
    }
  ];

  return (
    <div className="p-3 sm:p-6 animate-fade-in-up">
      <div className="max-w-7xl mx-auto">
        {/* Service Station Header */}
        <div className="mb-6 sm:mb-8 animate-slide-in-left">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-2 sm:gap-4">
              <div className="p-2 sm:p-3 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl">
                <Store className="h-6 w-6 sm:h-8 sm:w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold restaurant-heading">Service Station</h1>
                <p className="text-gray-600 font-medium text-sm sm:text-base">Restaurant Order Ticket Management</p>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
              <Button 
                variant="outline" 
                onClick={handleRefresh}
                disabled={loading}
                className="group hover:bg-blue-50 hover:border-blue-300 transition-all duration-300 text-sm sm:text-base"
              >
                <RefreshCw className={`h-3 w-3 sm:h-4 sm:w-4 mr-2 ${loading ? 'animate-spin' : 'group-hover:rotate-180'} transition-transform duration-300`} />
                Refresh System
              </Button>
              <Button 
                onClick={() => setCreateModalOpen(true)}
                className="btn-restaurant-primary text-white font-semibold group text-sm sm:text-base"
              >
                <Plus className="h-3 w-3 sm:h-4 sm:w-4 mr-2 group-hover:rotate-90 transition-transform duration-300" />
                New Order Ticket
              </Button>
            </div>
          </div>
          
          {/* Advanced Search */}
          <div className="mt-4 sm:mt-6">
            <div className="relative max-w-full sm:max-w-lg">
              <Search className="absolute left-3 sm:left-4 top-1/2 transform -translate-y-1/2 h-4 w-4 sm:h-5 sm:w-5 text-gray-400" />
              <Input
                type="text"
                placeholder="Search order tickets by customer name..."
                value={searchQuery}
                onChange={handleSearchInputChange}
                className="pl-10 sm:pl-12 pr-4 py-2 sm:py-3 text-base sm:text-lg bg-white border-2 border-gray-200 rounded-xl focus:border-blue-400 transition-all duration-300"
              />
              {isSearching && (
                <div className="absolute right-3 sm:right-4 top-1/2 transform -translate-y-1/2">
                  <div className="animate-spin rounded-full h-4 w-4 sm:h-5 sm:w-5 border-b-2 border-blue-600"></div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Search Results */}
        {searchQuery && (
          <div className="mb-8 animate-fade-in-up">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Search className="h-5 w-5 text-blue-600" />
              Search Results for "{searchQuery}"
              {searchResults.length > 0 && (
                <Badge className="bg-blue-100 text-blue-700 border-blue-200">
                  {searchResults.length} found
                </Badge>
              )}
            </h3>
            {searchResults.length > 0 ? (
              <div className="grid gap-4 sm:gap-6 grid-cols-1 md:grid-cols-3">
                {searchResults.map((order, index) => (
                  <div key={order.id} className="animate-ticket-slide-in" style={{ animationDelay: `${index * 0.1}s` }}>
                    <OrderCard 
                      order={order} 
                      onComplete={handleCompleteOrder}
                      onEdit={handleEditOrder}
                      onCancel={handleCancelOrder}
                      onOrderUpdated={handleOrderUpdated}
                    />
                  </div>
                ))}
              </div>
            ) : (
              !isSearching && (
                <div className="text-center py-8 text-gray-500">
                  <Search className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No order tickets found matching "{searchQuery}"</p>
                </div>
              )
            )}
          </div>
        )}

        {/* Restaurant Metrics Dashboard */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-6 sm:mb-8">
          {statsCards.map((stat, index) => {
            const IconComponent = stat.icon;
            return (
              <Card key={stat.title} className="stats-card animate-scale-in" style={{ animationDelay: `${index * 0.1}s` }}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-xs sm:text-sm font-semibold text-gray-700">
                    {stat.title}
                  </CardTitle>
                  <div className={`p-1 sm:p-2 rounded-lg ${stat.bgColor}`}>
                    <IconComponent className={`h-3 w-3 sm:h-5 sm:w-5 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className={`text-xl sm:text-3xl font-bold ${stat.color} mb-1`}>
                    {stat.value}
                  </div>
                  <p className="text-xs text-gray-600 font-medium">
                    {stat.description}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Restaurant Operations Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4 sm:space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-white p-1 rounded-xl border-2 border-gray-100">
            <TabsTrigger 
              value="pending" 
              className="flex flex-col sm:flex-row items-center gap-1 sm:gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-amber-500 data-[state=active]:to-orange-600 data-[state=active]:text-white transition-all duration-300 text-xs sm:text-sm px-2 py-2"
            >
              <Clock className="h-3 w-3 sm:h-4 sm:w-4" />
              <span className="font-semibold">Active Kitchen</span>
              {pendingOrders.length > 0 && (
                <Badge variant="secondary" className="ml-0 sm:ml-2 bg-white text-amber-600 text-xs">
                  {pendingOrders.length}
                </Badge>
              )}
            </TabsTrigger>
            
            <TabsTrigger 
              value="served" 
              className="flex flex-col sm:flex-row items-center gap-1 sm:gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-emerald-500 data-[state=active]:to-green-600 data-[state=active]:text-white transition-all duration-300 text-xs sm:text-sm px-2 py-2"
            >
              <CheckCircle className="h-3 w-3 sm:h-4 sm:w-4" />
              <span className="font-semibold">Served Orders</span>
              {completedOrders.length > 0 && (
                <Badge variant="secondary" className="ml-0 sm:ml-2 bg-white text-emerald-600 text-xs">
                  {completedOrders.length}
                </Badge>
              )}
            </TabsTrigger>
            
            <TabsTrigger 
              value="kitchen-board" 
              className="flex flex-col sm:flex-row items-center gap-1 sm:gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-purple-600 data-[state=active]:text-white transition-all duration-300 text-xs sm:text-sm px-2 py-2"
            >
              <ChefHat className="h-3 w-3 sm:h-4 sm:w-4" />
              <span className="font-semibold">Kitchen Board</span>
              {viewOrdersData.length > 0 && (
                <Badge variant="secondary" className="ml-0 sm:ml-2 bg-white text-blue-600 text-xs">
                  {viewOrdersData.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          {/* Active Kitchen Tab */}
          <TabsContent value="pending" className="space-y-6">
            {pendingOrders.length === 0 ? (
              <Card className="restaurant-card-bg animate-fade-in-up">
                <CardContent className="flex flex-col items-center justify-center py-16">
                  <div className="p-6 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full mb-6">
                    <CheckCircle className="h-16 w-16 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">Kitchen All Clear! 🎉</h3>
                  <p className="text-gray-600 text-center text-lg">
                    No active order tickets in the kitchen. Great work team!
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 sm:gap-6 grid-cols-1 md:grid-cols-3">
                {pendingOrders.map((order, index) => (
                  <div key={order.id} className="animate-ticket-slide-in" style={{ animationDelay: `${index * 0.1}s` }}>
                    <OrderCard 
                      order={order} 
                      onComplete={handleCompleteOrder}
                      onEdit={handleEditOrder}
                      onCancel={handleCancelOrder}
                      onOrderUpdated={handleOrderUpdated}
                    />
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Served Orders Tab */}
          <TabsContent value="served" className="space-y-6">
            {completedOrders.length === 0 ? (
              <Card className="restaurant-card-bg animate-fade-in-up">
                <CardContent className="flex flex-col items-center justify-center py-16">
                  <div className="p-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mb-6">
                    <Utensils className="h-16 w-16 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">No Served Orders Yet</h3>
                  <p className="text-gray-600 text-center text-lg">
                    Completed order tickets will appear here.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 sm:gap-6 grid-cols-1 md:grid-cols-3">
                {completedOrders.map((order, index) => (
                  <div key={order.id} className="animate-ticket-slide-in" style={{ animationDelay: `${index * 0.1}s` }}>
                    <OrderCard 
                      order={order} 
                      onComplete={handleCompleteOrder}
                      onEdit={handleEditOrder}
                      onCancel={handleCancelOrder}
                      onOrderUpdated={handleOrderUpdated}
                    />
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Kitchen Preparation Board */}
          <TabsContent value="kitchen-board" className="space-y-6">
            {viewOrdersData.length === 0 ? (
              <Card className="restaurant-card-bg animate-fade-in-up">
                <CardContent className="flex flex-col items-center justify-center py-16">
                  <div className="p-6 bg-gradient-to-br from-orange-500 to-red-600 rounded-full mb-6">
                    <ChefHat className="h-16 w-16 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">Kitchen Board Empty</h3>
                  <p className="text-gray-600 text-center text-lg">
                    Menu items grouped by preparation category will appear here.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                {viewOrdersData.map((categoryGroup, categoryIndex) => (
                  <Card key={categoryGroup.category_name} className="restaurant-card-bg border-l-4 border-l-gradient-to-b from-blue-500 to-purple-600 animate-fade-in-up" style={{ animationDelay: `${categoryIndex * 0.1}s` }}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span className="flex items-center gap-3">
                          <div className="p-2 bg-gradient-to-br from-orange-500 to-red-600 rounded-lg">
                            <ChefHat className="h-5 w-5 text-white" />
                          </div>
                          <span className="text-xl font-bold restaurant-heading">
                            {categoryGroup.category_name} Station
                          </span>
                        </span>
                        <Badge className="bg-blue-100 text-blue-700 border-blue-200 text-sm font-semibold">
                          {categoryGroup.total_items} items to prepare
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {categoryGroup.items.map((itemGroup, itemIndex) => (
                          <div key={itemGroup.item_name} className="border-2 border-gray-200 rounded-xl p-4 bg-gradient-to-r from-white to-gray-50 animate-ticket-slide-in" style={{ animationDelay: `${(categoryIndex * 2 + itemIndex) * 0.1}s` }}>
                            <div className="flex items-center justify-between mb-4">
                              <div className="flex items-center gap-3">
                                <Package className="h-5 w-5 text-gray-600" />
                                <span className="font-bold text-gray-800 text-lg">{itemGroup.item_name}</span>
                              </div>
                              <Badge className="bg-amber-100 text-amber-700 border-amber-200 font-semibold">
                                Total: {itemGroup.total_quantity} portions
                              </Badge>
                            </div>
                            
                            <div className="space-y-3">
                              {itemGroup.orders.map((orderInfo, orderIndex) => (
                                <div key={orderIndex} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 sm:p-4 bg-white rounded-lg border border-gray-200 hover:shadow-md transition-all duration-300 gap-3 sm:gap-0">
                                  <div className="flex-1 w-full sm:w-auto">
                                    <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
                                      <Hash className="h-3 w-3 sm:h-4 sm:w-4 text-blue-600" />
                                      <span className="font-bold text-blue-600">#{orderInfo.orderNumber}</span>
                                      <Users className="h-3 w-3 sm:h-4 sm:w-4 text-gray-500" />
                                      <span className="text-gray-700 font-medium">{orderInfo.customerName}</span>
                                    </div>
                                    <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-600">
                                      <span className="flex items-center gap-1">
                                        <Package className="h-3 w-3" />
                                        Qty: {orderInfo.quantity}
                                      </span>
                                      <span className="flex items-center gap-1">
                                        <DollarSign className="h-3 w-3" />
                                        ${orderInfo.subtotal?.toFixed(2) || '0.00'}
                                      </span>
                                      <span className="flex items-center gap-1">
                                        <Clock className="h-3 w-3" />
                                        {formatOrderTime(orderInfo.orderTime)}
                                      </span>
                                    </div>
                                  </div>
                                  <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-3 w-full sm:w-auto">
                                    <Badge 
                                      className={`${
                                        orderInfo.cooking_status === 'finished' ? 'bg-emerald-100 text-emerald-800 border-emerald-200' :
                                        orderInfo.cooking_status === 'in process' ? 'bg-amber-100 text-amber-800 border-amber-200' :
                                        'bg-slate-100 text-slate-700 border-slate-200'
                                      } border text-xs sm:text-sm font-medium flex items-center gap-1`}
                                    >
                                      {orderInfo.cooking_status === 'finished' ? '✅' :
                                       orderInfo.cooking_status === 'in process' ? '🔥' : '🔸'}
                                      {orderInfo.cooking_status === 'in process' ? 'In Progress' :
                                       orderInfo.cooking_status === 'finished' ? 'Ready' : 'Not Started'}
                                    </Badge>
                                    <Select 
                                      value={orderInfo.cooking_status} 
                                      onValueChange={(value) => handleCookingStatusUpdate(orderInfo.order_id, itemGroup.item_name, value)}
                                    >
                                      <SelectTrigger className="w-full sm:w-40 h-8 sm:h-9 bg-white border-gray-300 hover:border-blue-400 transition-colors text-xs sm:text-sm">
                                        <SelectValue />
                                      </SelectTrigger>
                                      <SelectContent>
                                        <SelectItem value="not started">🔸 Not Started</SelectItem>
                                        <SelectItem value="in process">🔥 In Process</SelectItem>
                                        <SelectItem value="finished">✅ Ready</SelectItem>
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

        {/* Modals */}
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
        
        {/* Notification System */}
        <NotificationSystem 
          notifications={notifications}
          onDismiss={dismissNotification}
        />
      </div>
    </div>
  );
};

export default OrderManager;