import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { X, Package, Clock, Hash } from 'lucide-react';
import { formatOrderTime } from '../services/api';

const NotificationSystem = ({ notifications, onDismiss }) => {
  if (!notifications || notifications.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-20 right-4 z-50 space-y-2 max-w-md">
      {notifications.map((notification) => (
        <Card key={notification.id} className="bg-white shadow-lg border-l-4 border-l-blue-500 animate-slide-in">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1 pr-2">
                <div className="flex items-center gap-2 mb-2">
                  <Package className="h-4 w-4 text-blue-600" />
                  <span className="font-semibold text-blue-800">Item Added to Order</span>
                  <Badge variant="outline" className="text-xs">
                    <Hash className="h-3 w-3 mr-1" />
                    {notification.orderNumber}
                  </Badge>
                </div>
                
                <div className="space-y-1">
                  <p className="text-sm text-gray-800">
                    <strong>{notification.itemName}</strong> (x{notification.quantity})
                  </p>
                  <p className="text-sm text-gray-600">
                    Customer: {notification.customerName}
                  </p>
                  <p className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatOrderTime(notification.timestamp)}
                  </p>
                </div>
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDismiss(notification.id)}
                className="h-6 w-6 p-0 hover:bg-gray-100"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default NotificationSystem;