import React, { useState } from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Check, Clock, User, Edit, Trash2, Timer, Hash, ChefHat, Package, CreditCard, Flame, CheckCircle2 } from 'lucide-react';
import { formatOrderTime, formatDeliveryTime, ordersAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const OrderCard = ({ order, onComplete, onEdit, onCancel, onOrderUpdated, id, ...props }) => {
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const { toast } = useToast();

  const handleComplete = () => {
    onComplete(order.id);
  };

  const handleEdit = () => {
    onEdit(order);
  };

  const handleCancel = () => {
    if (window.confirm(`Are you sure you want to cancel order ticket #${order.orderNumber || order.id.slice(-6)}?`)) {
      onCancel(order.id);
    }
  };

  const handleCookingStatusUpdate = async (itemName, newStatus) => {
    if (updatingStatus) return;
    
    try {
      setUpdatingStatus(true);
      const result = await ordersAPI.updateCookingStatus(order.id, itemName, newStatus);
      
      toast({
        title: "Kitchen Update",
        description: result.message,
        variant: result.order_auto_completed ? "default" : "default",
      });

      // Notify parent component to reload orders
      if (onOrderUpdated) {
        onOrderUpdated();
      }
    } catch (error) {
      toast({
        title: "Kitchen Error",
        description: "Failed to update preparation status",
        variant: "destructive",
      });
    } finally {
      setUpdatingStatus(false);
    }
  };

  const getPaymentMethodIcon = (method) => {
    switch (method) {
      case 'zelle':
        return <CreditCard className="h-3 w-3" />;
      case 'cashapp':
        return <Package className="h-3 w-3" />;
      case 'cash':
        return '💵';
      default:
        return <CreditCard className="h-3 w-3" />;
    }
  };

  const getPaymentMethodColor = (method) => {
    switch (method) {
      case 'zelle':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'cashapp':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'cash':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getOrderPriority = () => {
    if (order.status === 'completed') return 'completed';
    
    const orderTime = new Date(order.orderTime);
    const now = new Date();
    const minutesElapsed = (now - orderTime) / (1000 * 60);
    
    if (minutesElapsed > 30) return 'urgent';
    if (minutesElapsed > 15) return 'medium';
    return 'normal';
  };

  const getPrepStatusColor = (status) => {
    switch (status) {
      case 'finished':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'in process':
      case 'cooking':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  const getPrepStatusIcon = (status) => {
    switch (status) {
      case 'finished':
        return <CheckCircle2 className="h-3 w-3" />;
      case 'in process':
      case 'cooking':
        return <Flame className="h-3 w-3" />;
      default:
        return <Clock className="h-3 w-3" />;
    }
  };

  const getDeliveryInfo = () => {
    if (order.status === 'completed' && order.orderTime && order.completedTime) {
      const orderTime = new Date(order.orderTime);
      const completedTime = new Date(order.completedTime);
      const deliveryMinutes = (completedTime - orderTime) / (1000 * 60);
      return {
        type: 'delivered',
        time: formatDeliveryTime(deliveryMinutes),
        color: 'text-emerald-600'
      };
    } else if (order.status === 'pending' && order.estimatedDeliveryTime) {
      const now = new Date();
      const estimated = new Date(order.estimatedDeliveryTime);
      const remainingMinutes = (estimated - now) / (1000 * 60);
      
      if (remainingMinutes > 0) {
        return {
          type: 'estimated',
          time: formatDeliveryTime(remainingMinutes),
          color: 'text-amber-600'
        };
      } else {
        return {
          type: 'overdue',
          time: formatDeliveryTime(Math.abs(remainingMinutes)),
          color: 'text-red-600'
        };
      }
    }
    return null;
  };

  const deliveryInfo = getDeliveryInfo();
  const priority = getOrderPriority();
  const hasItemInProcess = order.items?.some(item => item.cooking_status === 'in process') || false;

  return (
    <Card 
      id={id}
      className={`ticket-card animate-ticket-slide-in transition-all duration-300 ${
        priority === 'urgent' ? 'ticket-card-urgent' : 
        priority === 'medium' ? 'ticket-card-cooking' :
        order.status === 'completed' ? 'ticket-card-ready opacity-75' : 
        'restaurant-card-bg'
      } ${order.status === 'completed' ? 'bg-gradient-to-br from-green-50 to-emerald-50' : ''}`}
      {...props}
    >
      <CardHeader className="pb-3">
        {/* Order Ticket Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg">
              <Hash className="h-4 w-4 text-white" />
            </div>
            <div>
              <span className="text-2xl font-bold restaurant-heading">
                Ticket #{order.orderNumber || order.id.slice(-6)}
              </span>
              <div className="flex items-center gap-2 mt-1">
                <Clock className="h-3 w-3 text-gray-500" />
                <span className="text-sm text-gray-600 font-medium">
                  {formatOrderTime(order.orderTime)}
                </span>
                {priority === 'urgent' && (
                  <Badge className="bg-red-100 text-red-700 border-red-200 text-xs animate-pulse">
                    ⚡ URGENT
                  </Badge>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge 
              variant={order.status === 'completed' ? 'secondary' : 'default'}
              className={`status-badge ${
                order.status === 'completed' 
                  ? 'bg-emerald-100 text-emerald-700 border-emerald-200' 
                  : 'bg-amber-100 text-amber-700 border-amber-200'
              }`}
            >
              {order.status === 'completed' ? '✅ Served' : '🔄 In Progress'}
            </Badge>
          </div>
        </div>

        {/* Customer & Payment Info */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg">
              <User className="h-4 w-4 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-gray-900">
                {order.customerName}
              </h3>
              <p className="text-sm text-gray-600">Customer</p>
            </div>
          </div>
          
          <div className="text-right">
            <div className="flex items-center gap-2 mb-1">
              <Badge className={`${getPaymentMethodColor(order.paymentMethod)} text-xs flex items-center gap-1`}>
                {getPaymentMethodIcon(order.paymentMethod)}
                {order.paymentMethod.charAt(0).toUpperCase() + order.paymentMethod.slice(1)}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">
                {order.totalItems} items
              </span>
              {order.totalAmount && (
                <div className="text-xl font-bold text-emerald-600">
                  ${order.totalAmount.toFixed(2)}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Service Time Info */}
        {deliveryInfo && (
          <div className="flex items-center gap-2 p-2 bg-blue-50 rounded-lg">
            <Timer className="h-4 w-4 text-blue-600" />
            <span className={`text-sm font-semibold ${deliveryInfo.color}`}>
              {deliveryInfo.type === 'delivered' && `✅ Served in ${deliveryInfo.time}`}
              {deliveryInfo.type === 'estimated' && `⏱️ Est. ${deliveryInfo.time} remaining`}
              {deliveryInfo.type === 'overdue' && `🚨 Overdue by ${deliveryInfo.time}`}
            </span>
          </div>
        )}
      </CardHeader>
      
      <CardContent className="flex flex-col h-full">
        {/* Menu Items & Preparation Status */}
        <div className="flex-1 overflow-hidden mb-6">
          <h4 className="font-bold flex items-center gap-2 text-gray-800 text-lg mb-3">
            <ChefHat className="h-5 w-5 text-orange-600" />
            Kitchen Preparation Board
          </h4>
          
          {/* Fixed height container with scroll */}
          <div className="max-h-[300px] md:max-h-[250px] lg:max-h-[200px] overflow-y-auto space-y-3 pr-2">
            {order.items.map((item, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-xl p-3 bg-gradient-to-r from-white to-gray-50 transition-all duration-300 hover:shadow-md">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Package className="h-4 w-4 text-gray-600" />
                    <div>
                      <span className="font-bold text-gray-800 text-base">{item.name}</span>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="bg-white border-blue-200 text-blue-700 text-xs">
                          Qty: {item.quantity}
                        </Badge>
                        {item.subtotal && (
                          <span className="text-sm font-semibold text-emerald-600">
                            ${item.subtotal.toFixed(2)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Kitchen Prep Status Controls */}
                <div className="flex items-center justify-between p-2 bg-white rounded-lg border">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-700">Prep Status:</span>
                    <Badge 
                      className={`${getPrepStatusColor(item.cooking_status)} flex items-center gap-1 text-xs font-medium`}
                    >
                      {getPrepStatusIcon(item.cooking_status)}
                      {item.cooking_status === 'in process' ? 'Cooking' : 
                       item.cooking_status === 'finished' ? 'Ready' : 'Not Started'}
                    </Badge>
                  </div>
                  
                  {order.status === 'pending' && (
                    <Select 
                      value={item.cooking_status || 'not started'} 
                      onValueChange={(value) => handleCookingStatusUpdate(item.name, value)}
                      disabled={updatingStatus}
                    >
                      <SelectTrigger className="w-32 h-8 bg-white border-gray-300 hover:border-blue-400 transition-colors text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="not started">🔸 Not Started</SelectItem>
                        <SelectItem value="in process">🔥 Cooking</SelectItem>
                        <SelectItem value="finished">✅ Ready</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Action Buttons */}
        {order.status === 'pending' && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <Button
                onClick={handleEdit}
                variant="outline"
                className="flex-1 text-blue-600 border-blue-300 hover:bg-blue-50 hover:border-blue-400 transition-all duration-300 group"
              >
                <Edit className="h-4 w-4 mr-2 group-hover:rotate-12 transition-transform" />
                Modify Order
              </Button>
              <Button
                onClick={handleCancel}
                variant="outline"
                disabled={hasItemInProcess}
                className={`flex-1 transition-all duration-300 group ${hasItemInProcess 
                  ? 'text-gray-400 border-gray-300 cursor-not-allowed' 
                  : 'text-red-600 border-red-300 hover:bg-red-50 hover:border-red-400'}`}
              >
                <Trash2 className="h-4 w-4 mr-2 group-hover:rotate-12 transition-transform" />
                Cancel
              </Button>
            </div>
            
            <Button
              onClick={handleComplete}
              className="w-full btn-restaurant-primary text-white font-semibold py-3 text-lg transition-all duration-300 hover:shadow-xl group"
            >
              <Check className="h-5 w-5 mr-2 group-hover:scale-110 transition-transform" />
              ✨ Complete & Serve Order
            </Button>
          </div>
        )}
        
        {order.status === 'completed' && (
          <div className="flex items-center justify-center py-4 text-emerald-600 bg-emerald-50 rounded-xl border border-emerald-200">
            <CheckCircle2 className="h-6 w-6 mr-3 animate-pulse" />
            <span className="font-bold text-lg">Order Successfully Served! 🎉</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default OrderCard;