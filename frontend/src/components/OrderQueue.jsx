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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative">
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

      {/* Static Queue Content */}
      <div className="relative overflow-y-auto max-h-[calc(100vh-140px)]">
        {pendingOrders.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-[calc(100vh-200px)] text-white">
            <div className="bg-gradient-to-br from-green-500 to-blue-600 p-12 rounded-full mb-8 shadow-2xl">
              <ChefHat className="h-20 w-20 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">All Caught Up!</h2>
            <p className="text-blue-200 text-center text-lg max-w-md">
              No pending orders in the queue. All orders have been processed successfully.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-3 p-4">
            {pendingOrders.map((order, index) => (
              <Card 
                key={order.id}
                className="bg-white/95 backdrop-blur border-0 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-[1.02]"
              >
                <CardContent className="p-4">
                  {/* Header Row - Order # and Time */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-2 rounded-lg shadow-md">
                        <Hash className="h-4 w-4 text-white" />
                      </div>
                      <div>
                        <div className="text-lg font-bold text-gray-800">#{order.orderNumber}</div>
                        <div className="text-xs text-gray-500">{order.customerName}</div>
                      </div>
                    </div>
                    <Badge className={`px-2 py-1 text-xs font-bold ${getElapsedTimeColor(order.orderTime)}`}>
                      <Clock className="h-3 w-3 mr-1" />
                      {calculateElapsedTime(order.orderTime)}
                    </Badge>
                  </div>

                  {/* Items Summary */}
                  <div className="space-y-2">
                    {order.items.slice(0, 3).map((item, itemIndex) => (
                      <div key={itemIndex} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg border">
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-gray-800 truncate">{item.name}</div>
                          <div className="text-xs text-gray-500">Qty: {item.quantity} • ${item.subtotal?.toFixed(2) || '0.00'}</div>
                        </div>
                        <Badge 
                          variant="outline" 
                          className={`text-xs px-2 py-1 font-medium ml-2 ${
                            item.cooking_status === 'finished' ? 'bg-green-100 text-green-700 border-green-300' :
                            item.cooking_status === 'in process' ? 'bg-yellow-100 text-yellow-700 border-yellow-300' :
                            'bg-gray-100 text-gray-600 border-gray-300'
                          }`}
                        >
                          {item.cooking_status === 'not started' ? 'PENDING' : 
                           item.cooking_status === 'in process' ? 'IN PROCESS' : 'READY'}
                        </Badge>
                      </div>
                    ))}
                    
                    {order.items.length > 3 && (
                      <div className="text-center py-1">
                        <Badge className="bg-blue-100 text-blue-700 px-2 py-1 text-xs">
                          +{order.items.length - 3} more items
                        </Badge>
                      </div>
                    )}
                  </div>

                  {/* Footer - Total Amount */}
                  {order.totalAmount && (
                    <div className="flex justify-between items-center mt-3 pt-2 border-t">
                      <span className="text-xs text-gray-500">Total:</span>
                      <span className="text-sm font-bold text-green-600">${order.totalAmount.toFixed(2)}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderQueue;