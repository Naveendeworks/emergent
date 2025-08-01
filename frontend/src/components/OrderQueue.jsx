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
  const [ordersPerPage] = useState(10);
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

  const handleStatusUpdate = async (orderId, itemName, newStatus) => {
    try {
      await ordersAPI.updateCookingStatus(orderId, itemName, newStatus);
      // Reload orders to reflect changes
      loadPendingOrders();
      toast({
        title: "Kitchen Update",
        description: `${itemName} status updated to ${newStatus}`,
      });
    } catch (error) {
      toast({
        title: "Kitchen Error", 
        description: "Failed to update preparation status",
        variant: "destructive",
      });
    }
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
      <div className="p-8 border-b border-white/20 bg-black/20 backdrop-blur-md">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 animate-slide-in-left">
              <div className="p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-xl">
                <Monitor className="h-10 w-10 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-white">Kitchen Display System</h1>
                <p className="text-blue-100 text-lg font-medium flex items-center gap-2">
                  <ChefHat className="h-5 w-5" />
                  Real-time Order Processing Dashboard
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-4 animate-slide-in-right">
              <div className="text-center p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                <div className="text-2xl font-bold text-white">{orders.length}</div>
                <div className="text-blue-100 text-sm">Total Orders</div>
              </div>
              <div className="text-center p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                <div className="text-2xl font-bold text-emerald-400">
                  {currentOrders.length}
                </div>
                <div className="text-blue-100 text-sm">Showing Now</div>
              </div>
              <div className="text-center p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                <div className="text-2xl font-bold text-purple-400">
                  {totalPages > 0 ? currentPage + 1 : 0}/{totalPages}
                </div>
                <div className="text-blue-100 text-sm">Page</div>
              </div>
              <div className="text-center p-4 bg-white/10 rounded-2xl backdrop-blur-md">
                <div className="text-2xl font-bold text-emerald-400">
                  {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
                <div className="text-blue-100 text-sm">Current Time</div>
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
                    <div className="grid gap-4 grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5">
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
        return <CheckCircle2 className="h-3 w-3 text-emerald-400" />;
      case 'in process':
      case 'cooking':
        return <Flame className="h-3 w-3 text-amber-400" />;
      default:
        return <Clock className="h-3 w-3 text-slate-400" />;
    }
  };

  const getPrepStatusColor = (status) => {
    switch (status) {
      case 'finished':
        return 'bg-emerald-900/50 text-emerald-200 border-emerald-500';
      case 'in process':
      case 'cooking':
        return 'bg-amber-900/50 text-amber-200 border-amber-500';
      default:
        return 'bg-slate-900/50 text-slate-300 border-slate-500';
    }
  };

  return (
    <Card 
      className={`queue-card border-2 ${priorityClass} animate-ticket-slide-in backdrop-blur-md h-full`}
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1 bg-white/20 rounded-lg backdrop-blur-sm">
              <Hash className="h-4 w-4 text-white" />
            </div>
            <div>
              <CardTitle className="text-lg font-bold text-white">
                #{order.orderNumber || order.id.slice(-6)}
              </CardTitle>
              <div className="flex items-center gap-1 text-blue-200">
                <Clock className="h-3 w-3" />
                <span className="text-xs font-medium">
                  {formatOrderTime(order.orderTime)}
                </span>
              </div>
            </div>
          </div>
          
          {priority === 'critical' && (
            <div className="animate-pulse">
              <Badge className="bg-red-500 text-white text-xs font-bold border-red-400">
                🚨 URGENT
              </Badge>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between mt-2 p-2 bg-white/10 rounded-lg backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <div className="p-1 bg-emerald-500/20 rounded-lg">
              <User className="h-3 w-3 text-emerald-300" />
            </div>
            <div>
              <h3 className="font-bold text-white text-sm">{order.customerName}</h3>
              <p className="text-blue-200 text-xs">Customer</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-lg font-bold text-emerald-400">
              ${order.totalAmount?.toFixed(2) || '0.00'}
            </div>
            <div className="text-blue-200 text-xs">
              {order.totalItems} items
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-2">
          <h4 className="font-bold text-white flex items-center gap-1 mb-2 text-sm">
            <ChefHat className="h-4 w-4 text-orange-400" />
            Kitchen Status
          </h4>
          
          {order.items?.slice(0, 3).map((item, itemIndex) => (
            <div key={itemIndex} className="p-2 bg-white/10 rounded-lg backdrop-blur-sm border border-white/20">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <Package className="h-3 w-3 text-blue-300" />
                  <div>
                    <span className="font-bold text-white text-sm">{item.name}</span>
                    <div className="flex items-center gap-1 mt-0.5">
                      <Badge className="bg-white/20 text-blue-200 border-white/30 text-xs">
                        x{item.quantity}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <Badge 
                  className={`${getPrepStatusColor(item.cooking_status)} border text-xs font-medium flex items-center gap-1`}
                >
                  {getPrepStatusIcon(item.cooking_status)}
                  {item.cooking_status === 'in process' || item.cooking_status === 'cooking' ? 'COOKING' :
                   item.cooking_status === 'finished' ? 'READY' : 'WAITING'}
                </Badge>
                
                <div className="flex items-center gap-2">
                  {item.subtotal && (
                    <span className="text-emerald-400 font-bold text-sm">
                      ${item.subtotal.toFixed(2)}
                    </span>
                  )}
                  <select 
                    value={item.cooking_status || 'not started'} 
                    onChange={(e) => handleStatusUpdate(order.id, item.name, e.target.value)}
                    className="bg-white/10 text-white border border-white/30 rounded px-2 py-1 text-xs focus:outline-none focus:border-blue-400"
                  >
                    <option value="not started" style={{color: 'black'}}>Not Started</option>
                    <option value="cooking" style={{color: 'black'}}>Cooking</option>
                    <option value="finished" style={{color: 'black'}}>Finished</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
          
          {order.items?.length > 3 && (
            <div className="text-center p-1 bg-white/5 rounded text-blue-200 text-xs">
              +{order.items.length - 3} more items
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default OrderQueue;