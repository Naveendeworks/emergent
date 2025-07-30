import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Clock, Hash, User, ChefHat, RefreshCw, ArrowLeft } from 'lucide-react';
import { ordersAPI, formatOrderTime } from '../services/api';
import { useToast } from '../hooks/use-toast';

const OrderQueue = ({ onNavigateToOrder, onBack }) => {
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

  const handleTileClick = (order) => {
    if (onNavigateToOrder) {
      onNavigateToOrder(order);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 shadow-lg">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={onBack}
                className="text-white hover:bg-white/20"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-3xl font-bold">Mem Famous 2025 Order Queue</h1>
                <p className="text-blue-100 mt-1">Live order status and management</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-2xl font-bold">{pendingOrders.length}</div>
                <div className="text-blue-200 text-sm">Active Orders</div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={loadPendingOrders}
                disabled={loading}
                className="text-white hover:bg-white/20"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Queue Content */}
      <div className="max-w-7xl mx-auto p-6">
        {pendingOrders.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="bg-gradient-to-br from-green-400 to-blue-500 p-8 rounded-full mb-6">
              <ChefHat className="h-16 w-16 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">All Caught Up!</h2>
            <p className="text-gray-600 text-center max-w-md">
              No pending orders in the queue. All orders have been processed successfully.
            </p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {pendingOrders.map((order) => (
              <Card 
                key={order.id}
                className="hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:scale-105 border-0 shadow-lg bg-gradient-to-br from-white to-gray-50"
                onClick={() => handleTileClick(order)}
              >
                <CardContent className="p-6">
                  {/* Order Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-2 rounded-lg">
                        <Hash className="h-4 w-4 text-white" />
                      </div>
                      <div>
                        <div className="font-bold text-lg text-gray-800">#{order.orderNumber}</div>
                        <div className="text-xs text-gray-500">Order ID</div>
                      </div>
                    </div>
                    <Badge className={`px-3 py-1 font-semibold ${getElapsedTimeColor(order.orderTime)}`}>
                      <Clock className="h-3 w-3 mr-1" />
                      {calculateElapsedTime(order.orderTime)}
                    </Badge>
                  </div>

                  {/* Customer Info */}
                  <div className="flex items-center gap-2 mb-4">
                    <div className="bg-gradient-to-r from-green-400 to-teal-500 p-2 rounded-lg">
                      <User className="h-4 w-4 text-white" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">{order.customerName}</div>
                      <div className="text-xs text-gray-500">Customer</div>
                    </div>
                  </div>

                  {/* Order Items (limit to 5) */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <ChefHat className="h-4 w-4 text-gray-600" />
                      <span className="text-sm font-medium text-gray-700">Items</span>
                    </div>
                    
                    {order.items.slice(0, 5).map((item, index) => (
                      <div key={index} className="flex items-center justify-between py-2 px-3 bg-gray-100 rounded-lg">
                        <div className="flex-1">
                          <div className="text-sm font-medium text-gray-800 truncate">{item.name}</div>
                          <div className="text-xs text-gray-500">Qty: {item.quantity}</div>
                        </div>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ml-2 ${
                            item.cooking_status === 'finished' ? 'bg-green-100 text-green-700 border-green-300' :
                            item.cooking_status === 'cooking' ? 'bg-yellow-100 text-yellow-700 border-yellow-300' :
                            'bg-gray-100 text-gray-600 border-gray-300'
                          }`}
                        >
                          {item.cooking_status === 'not started' ? 'Pending' : 
                           item.cooking_status === 'cooking' ? 'Cooking' : 'Ready'}
                        </Badge>
                      </div>
                    ))}
                    
                    {order.items.length > 5 && (
                      <div className="text-center py-2">
                        <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                          +{order.items.length - 5} more items
                        </Badge>
                      </div>
                    )}
                  </div>

                  {/* Order Footer */}
                  <div className="border-t pt-4 flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      <div className="font-semibold text-green-600">
                        ${order.totalAmount?.toFixed(2) || '0.00'}
                      </div>
                      <div className="text-xs">Total Amount</div>
                    </div>
                    <div className="text-sm text-gray-600 text-right">
                      <div className="font-semibold">{order.paymentMethod}</div>
                      <div className="text-xs">Payment</div>
                    </div>
                  </div>

                  {/* Click indicator */}
                  <div className="mt-3 text-center">
                    <div className="text-xs text-blue-600 font-medium">
                      Click to view full details →
                    </div>
                  </div>
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