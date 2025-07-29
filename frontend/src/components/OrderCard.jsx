import React from 'react';
import { Card, CardContent, CardHeader } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Check, Clock, User, Edit, Trash2, Timer, Hash } from 'lucide-react';
import { formatOrderTime, formatDeliveryTime } from '../services/api';

const OrderCard = ({ order, onComplete, onEdit, onCancel }) => {
  const handleComplete = () => {
    onComplete(order.id);
  };

  const handleEdit = () => {
    onEdit(order);
  };

  const handleCancel = () => {
    if (window.confirm(`Are you sure you want to cancel ${order.customerName}'s order?`)) {
      onCancel(order.id);
    }
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
        return 'bg-blue-100 text-blue-700';
      case 'cashapp':
        return 'bg-green-100 text-green-700';
      case 'cash':
        return 'bg-gray-100 text-gray-700';
      default:
        return 'bg-gray-100 text-gray-700';
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
        color: 'text-green-600'
      };
    } else if (order.status === 'pending' && order.estimatedDeliveryTime) {
      const now = new Date();
      const estimated = new Date(order.estimatedDeliveryTime);
      const remainingMinutes = (estimated - now) / (1000 * 60);
      
      if (remainingMinutes > 0) {
        return {
          type: 'estimated',
          time: formatDeliveryTime(remainingMinutes),
          color: 'text-orange-600'
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

  return (
    <Card className={`transition-all duration-200 hover:shadow-lg ${
      order.status === 'completed' ? 'opacity-60 bg-gray-50' : 'bg-white'
    }`}>
      <CardHeader className="pb-3">
        {/* Order Number - Prominent Display */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Hash className="h-5 w-5 text-blue-600" />
            <span className="text-xl font-bold text-blue-600">
              Order #{order.orderNumber || order.id.slice(-6)}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-600">
              {formatOrderTime(order.orderTime)}
            </span>
          </div>
        </div>

        {/* Customer Name */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-gray-600" />
            <h3 className="font-semibold text-lg text-gray-900">
              {order.customerName}
            </h3>
          </div>
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center gap-2">
            <Badge variant={order.status === 'completed' ? 'secondary' : 'default'}>
              {order.status === 'completed' ? 'Completed' : 'Pending'}
            </Badge>
            <Badge className={`${getPaymentMethodColor(order.paymentMethod)} text-xs`}>
              {getPaymentMethodIcon(order.paymentMethod)}
              {order.paymentMethod.charAt(0).toUpperCase() + order.paymentMethod.slice(1)}
            </Badge>
          </div>
          <span className="text-sm text-gray-500">
            {order.totalItems} items total
          </span>
        </div>

        {/* Delivery Time Info */}
        {deliveryInfo && (
          <div className="flex items-center gap-2 mt-2">
            <Timer className="h-4 w-4 text-gray-500" />
            <span className={`text-sm font-medium ${deliveryInfo.color}`}>
              {deliveryInfo.type === 'delivered' && `Delivered in ${deliveryInfo.time}`}
              {deliveryInfo.type === 'estimated' && `Est. ${deliveryInfo.time} remaining`}
              {deliveryInfo.type === 'overdue' && `Overdue by ${deliveryInfo.time}`}
            </span>
          </div>
        )}
      </CardHeader>
      
      <CardContent>
        <div className="space-y-2 mb-4">
          {order.items.map((item, index) => (
            <div key={index} className="flex justify-between items-center py-1 px-2 rounded bg-gray-50">
              <span className="text-gray-800 font-medium">{item.name}</span>
              <Badge variant="outline" className="bg-white">
                x{item.quantity}
              </Badge>
            </div>
          ))}
        </div>
        
        {order.status === 'pending' && (
          <div className="space-y-2">
            <div className="flex gap-2">
              <Button
                onClick={handleEdit}
                variant="outline"
                className="flex-1 text-blue-600 border-blue-600 hover:bg-blue-50"
              >
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button
                onClick={handleCancel}
                variant="outline"
                className="flex-1 text-red-600 border-red-600 hover:bg-red-50"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Cancel
              </Button>
            </div>
            <Button
              onClick={handleComplete}
              className="w-full bg-green-600 hover:bg-green-700 text-white transition-colors duration-200"
            >
              <Check className="h-4 w-4 mr-2" />
              Mark as Complete
            </Button>
          </div>
        )}
        
        {order.status === 'completed' && (
          <div className="flex items-center justify-center py-2 text-green-600">
            <Check className="h-4 w-4 mr-2" />
            <span className="font-medium">Order Completed</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default OrderCard;