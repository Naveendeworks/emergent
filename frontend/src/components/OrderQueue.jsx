import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { ArrowLeft, Monitor, Clock, User, Hash, ChefHat, Package, Timer, Flame, CheckCircle2, AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react';
import { ordersAPI, formatOrderTime } from '../services/api';
import { useToast } from '../hooks/use-toast';

const OrderQueue = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [ordersPerPage] = useState(20);
  const { toast } = useToast();

  useEffect(() => {
    loadPendingOrders();
    const interval = setInterval(loadPendingOrders, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadPendingOrders = async () => {
    try {
      const ordersData = await ordersAPI.getOrders();
      const pendingOrders = ordersData
        .filter(order => order.status === 'pending')
        .sort((a, b) => new Date(a.orderTime) - new Date(b.orderTime));
      setOrders(pendingOrders);
    } catch (error) {
      toast({
        title: "Kitchen Display Error",
        description: "Failed to load kitchen orders",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getOrderPriority = (orderTime) => {
    const now = new Date();
    const orderDate = new Date(orderTime);
    const minutesElapsed = (now - orderDate) / (1000 * 60);
    
    if (minutesElapsed > 30) return 'critical';
    if (minutesElapsed > 15) return 'high';
    return 'normal';
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical':
        return 'border-red-500 bg-gradient-to-br from-red-100 to-red-50';
      case 'high':
        return 'border-amber-500 bg-gradient-to-br from-amber-100 to-amber-50';
      default:
        return 'border-blue-500 bg-gradient-to-br from-blue-100 to-blue-50';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'high':
        return <Timer className="h-5 w-5 text-amber-600" />;
      default:
        return <Clock className="h-5 w-5 text-blue-600" />;
    }
  };

  const getPrepStatusIcon = (status) => {
    switch (status) {
      case 'finished':
        return <CheckCircle2 className="h-4 w-4 text-emerald-600" />;
      case 'in process':
      case 'cooking':
        return <Flame className="h-4 w-4 text-amber-600" />;
      default:
        return <Clock className="h-4 w-4 text-slate-500" />;
    }
  };

  const getPrepStatusColor = (status) => {
    switch (status) {
      case 'finished':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'in process':
      case 'cooking':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  // Pagination logic
  const totalPages = Math.ceil(orders.length / ordersPerPage);
  const startIndex = currentPage * ordersPerPage;
  const endIndex = startIndex + ordersPerPage;
  const currentOrders = orders.slice(startIndex, endIndex);

  const nextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  const goToPage = (pageIndex) => {
    setCurrentPage(pageIndex);
  };

  if (loading) {
    return (
      <div className="order-queue-bg min-h-screen flex items-center justify-center">
        <div className="text-center animate-fade-in-up">
          <div className="relative">
            <div className="w-24 h-24 mx-auto mb-6 bg-white/10 rounded-3xl shadow-2xl flex items-center justify-center animate-restaurant-pulse">
              <Monitor className="h-12 w-12 text-white" />
            </div>
            <div className="absolute inset-0 w-24 h-24 mx-auto rounded-3xl bg-gradient-to-r from-blue-400 to-purple-500 opacity-20 animate-ping" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">
            Kitchen Display System
          </h2>
          <p className="text-blue-100 mb-4">Loading live order queue...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="order-queue-bg min-h-screen">
      {/* KDS Header */}
      <div className="p-4 sm:p-8 border-b border-white/20 bg-black/20 backdrop-blur-md">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div className="flex items-center gap-2 sm:gap-4 animate-slide-in-left">
              <div className="p-3 sm:p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-xl">
                <Monitor className="h-8 w-8 sm:h-10 sm:w-10 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white">Kitchen Display System</h1>
                <p className="text-blue-100 text-sm sm:text-lg font-medium flex items-center gap-1 sm:gap-2">
                  <ChefHat className="h-4 w-4 sm:h-5 sm:w-5" />
                  Real-time Order Processing Dashboard
                </p>
              </div>
            </div>
            
            <div className="flex flex-wrap items-center gap-2 sm:gap-4 animate-slide-in-right w-full lg:w-auto">
              <div className="text-center p-2 sm:p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                <div className="text-lg sm:text-2xl font-bold text-white">{orders.length}</div>
                <div className="text-blue-100 text-xs sm:text-sm">Total Orders</div>
              </div>
              <div className="text-center p-2 sm:p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                <div className="text-lg sm:text-2xl font-bold text-emerald-400">
                  {currentOrders.length}
                </div>
                <div className="text-blue-100 text-xs sm:text-sm">Showing Now</div>
              </div>
              <div className="text-center p-2 sm:p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                <div className="text-lg sm:text-2xl font-bold text-purple-400">
                  {totalPages > 0 ? currentPage + 1 : 0}/{totalPages}
                </div>
                <div className="text-blue-100 text-xs sm:text-sm">Page</div>
              </div>
              <div className="text-center p-2 sm:p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                <div className="text-lg sm:text-2xl font-bold text-emerald-400">
                  {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-blue-100 text-xs sm:text-sm">Current Time</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Order Queue Content */}
      <div className="p-8">
        <div className="max-w-7xl mx-auto">
          {orders.length === 0 ? (
            <Card className="queue-card animate-fade-in-up">
              <CardContent className="text-center py-20">
                <div className="p-8 bg-gradient-to-br from-emerald-500 to-green-600 rounded-full mx-auto mb-6 w-fit">
                  <CheckCircle2 className="h-16 w-16 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-4">Kitchen All Clear! 🎉</h2>
                <p className="text-blue-100 text-lg">
                  No pending orders in the kitchen queue. Outstanding work team!
                </p>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Pagination Controls - Top */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mb-6 animate-fade-in-up">
                  <div className="flex items-center gap-4">
                    <Button
                      onClick={prevPage}
                      disabled={currentPage === 0}
                      className="bg-white/10 text-white border-white/20 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-md"
                    >
                      <ChevronLeft className="h-5 w-5 mr-2" />
                      Previous
                    </Button>
                    <Button
                      onClick={nextPage}
                      disabled={currentPage === totalPages - 1}
                      className="bg-white/10 text-white border-white/20 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-md"
                    >
                      Next
                      <ChevronRight className="h-5 w-5 ml-2" />
                    </Button>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <span className="text-white font-medium">Go to page:</span>
                    {Array.from({ length: totalPages }, (_, i) => (
                      <Button
                        key={i}
                        onClick={() => goToPage(i)}
                        className={`w-10 h-10 ${
                          currentPage === i
                            ? 'bg-blue-500 text-white'
                            : 'bg-white/10 text-white hover:bg-white/20'
                        } backdrop-blur-md`}
                      >
                        {i + 1}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* Static Order Display - No Scrolling */}
              <div className="space-y-6">
                {/* Critical Priority Orders */}
                {currentOrders.filter(order => getOrderPriority(order.orderTime) === 'critical').length > 0 && (
                  <div className="animate-fade-in-up">
                    <div className="flex items-center gap-3 mb-4">
                      <AlertTriangle className="h-6 w-6 text-red-400" />
                      <h2 className="text-2xl font-bold text-red-400">URGENT - IMMEDIATE ATTENTION</h2>
                      <div className="flex-1 h-0.5 bg-red-400/30"></div>
                    </div>
                    <div className="grid gap-2 grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6">
                      {currentOrders
                        .filter(order => getOrderPriority(order.orderTime) === 'critical')
                        .map((order, index) => (
                          <OrderQueueCard 
                            key={order.id} 
                            order={order} 
                            priority="critical"
                            index={index}
                          />
                        ))}
                    </div>
                  </div>
                )}

                {/* High Priority Orders */}
                {currentOrders.filter(order => getOrderPriority(order.orderTime) === 'high').length > 0 && (
                  <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                    <div className="flex items-center gap-3 mb-4">
                      <Timer className="h-6 w-6 text-amber-400" />
                      <h2 className="text-2xl font-bold text-amber-400">HIGH PRIORITY</h2>
                      <div className="flex-1 h-0.5 bg-amber-400/30"></div>
                    </div>
                    <div className="grid gap-4 grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
                      {currentOrders
                        .filter(order => getOrderPriority(order.orderTime) === 'high')
                        .map((order, index) => (
                          <OrderQueueCard 
                            key={order.id} 
                            order={order} 
                            priority="high"
                            index={index}
                          />
                        ))}
                    </div>
                  </div>
                )}

                {/* Normal Priority Orders */}
                {currentOrders.filter(order => getOrderPriority(order.orderTime) === 'normal').length > 0 && (
                  <div className="animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
                    <div className="flex items-center gap-3 mb-4">
                      <Clock className="h-6 w-6 text-blue-400" />
                      <h2 className="text-2xl font-bold text-blue-400">STANDARD QUEUE</h2>
                      <div className="flex-1 h-0.5 bg-blue-400/30"></div>
                    </div>
                    <div className="grid gap-4 grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
                      {currentOrders
                        .filter(order => getOrderPriority(order.orderTime) === 'normal')
                        .map((order, index) => (
                          <OrderQueueCard 
                            key={order.id} 
                            order={order} 
                            priority="normal"
                            index={index}
                          />
                        ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Pagination Controls - Bottom */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center mt-8 animate-fade-in-up">
                  <div className="flex items-center gap-4 p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                    <Button
                      onClick={prevPage}
                      disabled={currentPage === 0}
                      className="bg-white/10 text-white border-white/20 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="h-5 w-5 mr-2" />
                      Previous
                    </Button>
                    
                    <div className="flex items-center gap-2 px-4">
                      <span className="text-white font-medium">
                        Page {currentPage + 1} of {totalPages}
                      </span>
                      <span className="text-blue-200 text-sm">
                        (Showing {currentOrders.length} of {orders.length} orders)
                      </span>
                    </div>
                    
                    <Button
                      onClick={nextPage}
                      disabled={currentPage === totalPages - 1}
                      className="bg-white/10 text-white border-white/20 hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                      <ChevronRight className="h-5 w-5 ml-2" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const OrderQueueCard = ({ order, priority, index }) => {
  const priorityClass = priority === 'critical' ? 'border-red-500 bg-gradient-to-br from-red-900/50 to-red-800/30' :
                       priority === 'high' ? 'border-amber-500 bg-gradient-to-br from-amber-900/50 to-amber-800/30' :
                       'border-blue-500 bg-gradient-to-br from-blue-900/50 to-blue-800/30';

  const getPrepStatusIcon = (status) => {
    switch (status) {
      case 'finished':
        return '✅';
      case 'in process':
      case 'cooking':
        return '🔥';
      default:
        return '⏳';
    }
  };

  const getPrepStatusColor = (status) => {
    switch (status) {
      case 'finished':
        return 'bg-emerald-900/50 text-emerald-200';
      case 'in process':
      case 'cooking':
        return 'bg-amber-900/50 text-amber-200';
      default:
        return 'bg-slate-900/50 text-slate-300';
    }
  };

  return (
    <Card 
      className={`queue-card border ${priorityClass} animate-ticket-slide-in backdrop-blur-md h-full`}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      <CardContent className="p-2">
        <div className="space-y-1">
          {/* Order Header - Compact */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1">
              <Hash className="h-3 w-3 text-white" />
              <span className="text-sm font-bold text-white">
                #{order.orderNumber || order.id.slice(-6)}
              </span>
            </div>
            {priority === 'critical' && (
              <div className="text-xs bg-red-500 text-white px-1 py-0.5 rounded animate-pulse">
                🚨
              </div>
            )}
          </div>

          {/* Customer & Amount */}
          <div className="text-xs text-blue-200">
            <div className="font-medium truncate">{order.customerName}</div>
            <div className="flex justify-between items-center">
              <span>{order.totalItems} items</span>
              <span className="text-emerald-400 font-bold">
                ${order.totalAmount?.toFixed(2) || '0.00'}
              </span>
            </div>
          </div>

          {/* Items Status - Compact */}
          <div className="space-y-1">
            {order.items?.slice(0, 5).map((item, itemIndex) => (
              <div key={itemIndex} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1 flex-1 min-w-0">
                  <span className="truncate font-medium text-white text-xs">
                    {item.name}
                  </span>
                  <span className="text-blue-300 text-xs">x{item.quantity}</span>
                </div>
                <div className={`px-1 py-0.5 rounded text-xs ${getPrepStatusColor(item.cooking_status)}`}>
                  {getPrepStatusIcon(item.cooking_status)}
                </div>
              </div>
            ))}
            
            {order.items?.length > 5 && (
              <div className="text-xs text-blue-200 text-center">
                +{order.items.length - 5} more
              </div>
            )}
          </div>

          {/* Time */}
          <div className="flex items-center justify-center gap-1 text-xs text-blue-300">
            <Clock className="h-3 w-3" />
            <span>{formatOrderTime(order.orderTime)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default OrderQueue;