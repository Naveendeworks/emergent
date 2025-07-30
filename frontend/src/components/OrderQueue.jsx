import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Clock, Hash, User, ChefHat, RefreshCw } from 'lucide-react';
import { ordersAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const OrderQueue = () => {
  const [pendingOrders, setPendingOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadPendingOrders();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadPendingOrders, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadPendingOrders = async () => {
    try {
      setLoading(true);
      const allOrders = await ordersAPI.getOrders();
      const pending = allOrders.filter(order => order.status === 'pending');
      setPendingOrders(pending);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load pending orders",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const calculateElapsedTime = (orderTime) => {
    const now = new Date();
    const orderDate = new Date(orderTime);
    const diffMs = now - orderDate;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 60) {
      return `${diffMins}m`;
    } else {
      const hours = Math.floor(diffMins / 60);
      const remainingMins = diffMins % 60;
      return `${hours}h ${remainingMins}m`;
    }
  };

  const getElapsedTimeColor = (orderTime) => {
    const now = new Date();
    const orderDate = new Date(orderTime);
    const diffMs = now - orderDate;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 15) return 'text-green-600 bg-green-100';
    if (diffMins < 30) return 'text-yellow-600 bg-yellow-100';
    if (diffMins < 60) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  // Duplicate orders for continuous scrolling effect
  const duplicatedOrders = [...pendingOrders, ...pendingOrders, ...pendingOrders];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden relative">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-t from-blue-600/10 via-purple-600/5 to-transparent"></div>
      
      {/* Header */}
      <div className="relative z-10 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-2xl">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Mem Famous 2025 Order Queue</h1>
              <p className="text-blue-100 text-lg">Live Order Display • Real-time Updates</p>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-right">
                <div className="text-3xl font-bold">{pendingOrders.length}</div>
                <div className="text-blue-200">Active Orders</div>
              </div>
              <Button
                variant="ghost"
                size="lg"
                onClick={loadPendingOrders}
                disabled={loading}
                className="text-white hover:bg-white/20 border-white/30 border"
              >
                <RefreshCw className={`h-5 w-5 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Scrolling Queue Content */}
      <div className="relative h-[calc(100vh-140px)] overflow-hidden">
        {pendingOrders.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-white">
            <div className="bg-gradient-to-br from-green-500 to-blue-600 p-12 rounded-full mb-8 shadow-2xl">
              <ChefHat className="h-20 w-20 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">All Caught Up!</h2>
            <p className="text-blue-200 text-center text-lg max-w-md">
              No pending orders in the queue. All orders have been processed successfully.
            </p>
          </div>
        ) : (
          <div 
            className="animate-scroll-up flex flex-col gap-6 p-6"
            style={{
              animation: 'scrollUp 60s linear infinite',
            }}
          >
            {duplicatedOrders.map((order, index) => (
              <Card 
                key={`${order.id}-${index}`}
                className="bg-white/95 backdrop-blur border-0 shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105 mx-auto w-full max-w-4xl"
              >
                <CardContent className="p-8">
                  {/* Order Header */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-4">
                      <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-4 rounded-xl shadow-lg">
                        <Hash className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-gray-800">#{order.orderNumber}</div>
                        <div className="text-sm text-gray-500">Order Number</div>
                      </div>
                    </div>
                    <Badge className={`px-4 py-2 text-lg font-bold ${getElapsedTimeColor(order.orderTime)}`}>
                      <Clock className="h-4 w-4 mr-2" />
                      {calculateElapsedTime(order.orderTime)}
                    </Badge>
                  </div>

                  {/* Customer & Order Info */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div className="flex items-center gap-3">
                      <div className="bg-gradient-to-r from-green-400 to-teal-500 p-3 rounded-xl shadow-lg">
                        <User className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <div className="text-xl font-semibold text-gray-800">{order.customerName}</div>
                        <div className="text-sm text-gray-500">Customer Name</div>
                      </div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        ${order.totalAmount?.toFixed(2) || '0.00'}
                      </div>
                      <div className="text-sm text-gray-500">Total Amount</div>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-lg font-semibold text-blue-600">{order.paymentMethod}</div>
                      <div className="text-sm text-gray-500">Payment Method</div>
                    </div>
                  </div>

                  {/* Order Items */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-3 mb-4">
                      <ChefHat className="h-5 w-5 text-gray-600" />
                      <span className="text-lg font-semibold text-gray-700">Order Items</span>
                    </div>
                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      {order.items.slice(0, 5).map((item, itemIndex) => (
                        <div key={itemIndex} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border">
                          <div className="flex-1">
                            <div className="text-lg font-semibold text-gray-800">{item.name}</div>
                            <div className="text-sm text-gray-500">Quantity: {item.quantity} • ${item.subtotal?.toFixed(2) || '0.00'}</div>
                          </div>
                          <Badge 
                            variant="outline" 
                            className={`text-sm px-3 py-1 font-semibold ${
                              item.cooking_status === 'finished' ? 'bg-green-100 text-green-700 border-green-300' :
                              item.cooking_status === 'cooking' ? 'bg-yellow-100 text-yellow-700 border-yellow-300' :
                              'bg-gray-100 text-gray-600 border-gray-300'
                            }`}
                          >
                            {item.cooking_status === 'not started' ? 'PENDING' : 
                             item.cooking_status === 'cooking' ? 'COOKING' : 'READY'}
                          </Badge>
                        </div>
                      ))}
                    </div>
                    
                    {order.items.length > 5 && (
                      <div className="text-center py-3">
                        <Badge className="bg-blue-100 text-blue-700 px-4 py-2 text-lg">
                          +{order.items.length - 5} more items
                        </Badge>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* CSS Animation Styles */}
      <style jsx>{`
        @keyframes scrollUp {
          0% {
            transform: translateY(100vh);
          }
          100% {
            transform: translateY(-100%);
          }
        }
        
        .animate-scroll-up {
          animation: scrollUp 60s linear infinite;
        }
        
        /* Pause animation on hover */
        .animate-scroll-up:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};

export default OrderQueue;