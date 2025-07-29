import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Hash, Clock, Package, CreditCard, Search, ArrowLeft, CheckCircle } from 'lucide-react';
import { ordersAPI, formatOrderTime } from '../services/api';
import { useToast } from '../hooks/use-toast';

const MyOrder = ({ onBack }) => {
  const [orderNumber, setOrderNumber] = useState('');
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!phoneNumber.trim()) {
      toast({
        title: "Error",
        description: "Please enter your phone number",
        variant: "destructive",
      });
      return;
    }

    if (phoneNumber.trim().length < 10) {
      toast({
        title: "Error",
        description: "Please enter a valid phone number (at least 10 digits)",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      const customerOrders = await ordersAPI.getOrdersByPhone(phoneNumber.trim());
      setOrders(customerOrders);
      setSearched(true);
      
      if (customerOrders.length === 0) {
        toast({
          title: "No Orders Found",
          description: "No orders found for this phone number",
          variant: "default",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch orders. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleNewSearch = () => {
    setPhoneNumber('');
    setOrders([]);
    setSearched(false);
  };

  const getPaymentMethodIcon = (method) => {
    switch (method) {
      case 'zelle':
        return '💳';
      case 'cashapp':
        return '💰';
      case 'cash':
        return '💵';
      default:
        return '💳';
    }
  };

  const getPaymentMethodColor = (method) => {
    switch (method) {
      case 'zelle':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'cashapp':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cash':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="outline" onClick={onBack} className="flex items-center gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Orders</h1>
          <p className="text-gray-600">Track your food orders by entering your phone number</p>
        </div>
      </div>

      {/* Phone Number Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Phone className="h-5 w-5" />
            Enter Your Phone Number
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number</Label>
            <div className="flex gap-3">
              <Input
                id="phone"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="Enter your phone number (e.g., 1234567890)"
                type="tel"
                className="flex-1"
              />
              <Button 
                onClick={handleSearch}
                disabled={loading}
                className="flex items-center gap-2"
              >
                {loading ? (
                  <>Loading...</>
                ) : (
                  <>
                    <Search className="h-4 w-4" />
                    Search Orders
                  </>
                )}
              </Button>
            </div>
          </div>
          
          {searched && (
            <div className="flex items-center justify-between pt-2 border-t">
              <p className="text-sm text-gray-600">
                Found {orders.length} order{orders.length !== 1 ? 's' : ''} for {phoneNumber}
              </p>
              <Button variant="outline" size="sm" onClick={handleNewSearch}>
                New Search
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Orders Display */}
      {searched && orders.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">Your Orders</h2>
          {orders.map((order) => (
            <Card key={order.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                  {/* Order Info */}
                  <div className="flex-1 space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">{order.customerName}</h3>
                        <p className="text-sm text-gray-600 flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          Ordered: {formatOrderTime(order.orderTime)}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Badge className={`${getStatusColor(order.status)} border`}>
                          {order.status === 'completed' && <CheckCircle className="h-3 w-3 mr-1" />}
                          {order.status === 'pending' && <Clock className="h-3 w-3 mr-1" />}
                          {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                        </Badge>
                        <Badge className={`${getPaymentMethodColor(order.paymentMethod)} border`}>
                          {getPaymentMethodIcon(order.paymentMethod)}
                          {order.paymentMethod.charAt(0).toUpperCase() + order.paymentMethod.slice(1)}
                        </Badge>
                      </div>
                    </div>

                    {/* Order Items */}
                    <div className="space-y-2">
                      <h4 className="font-medium flex items-center gap-2">
                        <Package className="h-4 w-4" />
                        Items ({order.totalItems} total)
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {order.items.map((item, index) => (
                          <div key={index} className="flex justify-between items-center bg-gray-50 p-2 rounded">
                            <div>
                              <span className="font-medium">{item.name}</span>
                              {item.price && (
                                <p className="text-xs text-green-600">
                                  ${item.price.toFixed(2)} each
                                </p>
                              )}
                            </div>
                            <div className="text-right">
                              <Badge variant="outline" className="text-xs">
                                Qty: {item.quantity}
                              </Badge>
                              {item.subtotal && (
                                <p className="text-xs font-medium text-green-600">
                                  ${item.subtotal.toFixed(2)}
                                </p>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Order Total */}
                    {order.totalAmount && (
                      <div className="bg-green-50 p-3 rounded-lg border border-green-200">
                        <div className="flex justify-between items-center">
                          <span className="font-semibold text-green-800">Order Total:</span>
                          <span className="text-lg font-bold text-green-800">
                            ${order.totalAmount.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Delivery Info */}
                    {order.estimatedDeliveryTime && (
                      <div className="bg-blue-50 p-3 rounded-lg">
                        <p className="text-sm text-blue-800">
                          <Clock className="h-4 w-4 inline mr-1" />
                          Estimated delivery: {formatOrderTime(order.estimatedDeliveryTime)}
                        </p>
                        {order.status === 'completed' && order.completedTime && (
                          <p className="text-sm text-green-800 mt-1">
                            <CheckCircle className="h-4 w-4 inline mr-1" />
                            Completed: {formatOrderTime(order.completedTime)}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* No Results State */}
      {searched && orders.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Orders Found</h3>
            <p className="text-gray-600 mb-4">
              We couldn't find any orders associated with this phone number.
            </p>
            <p className="text-sm text-gray-500">
              Make sure you entered the same phone number used when placing the order.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MyOrder;