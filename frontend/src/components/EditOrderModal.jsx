import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent } from './ui/card';
import { Plus, Minus, Edit, X, CreditCard } from 'lucide-react';
import { menuAPI, ordersAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const EditOrderModal = ({ open, onOpenChange, order, onOrderUpdated }) => {
  const [customerName, setCustomerName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [menu, setMenu] = useState({ items: [], categories: [] });
  const [selectedCategory, setSelectedCategory] = useState('');
  const [orderItems, setOrderItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (open && order) {
      setCustomerName(order.customerName);
      setPhoneNumber(order.phoneNumber || '');
      setPaymentMethod(order.paymentMethod || 'cash');
      setOrderItems(order.items.map(item => ({
        id: item.name.toLowerCase().replace(/\s+/g, '_'),
        name: item.name,
        quantity: item.quantity
      })));
      loadMenu();
    }
  }, [open, order]);

  const loadMenu = async () => {
    try {
      setLoading(true);
      const menuData = await menuAPI.getMenu();
      setMenu(menuData);
      if (menuData.categories.length > 0) {
        setSelectedCategory(menuData.categories[0]);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load menu items",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addItemToOrder = (menuItem) => {
    const existingItem = orderItems.find(item => item.name === menuItem.name);
    if (existingItem) {
      setOrderItems(orderItems.map(item => 
        item.name === menuItem.name 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setOrderItems([...orderItems, {
        id: menuItem.id,
        name: menuItem.name,
        quantity: 1,
        chef: menuItem.chef
      }]);
    }
  };

  const removeItemFromOrder = (itemName) => {
    setOrderItems(orderItems.filter(item => item.name !== itemName));
  };

  const updateItemQuantity = (itemName, newQuantity) => {
    if (newQuantity <= 0) {
      removeItemFromOrder(itemName);
    } else {
      setOrderItems(orderItems.map(item => 
        item.name === itemName 
          ? { ...item, quantity: newQuantity }
          : item
      ));
    }
  };

  const handleUpdateOrder = async () => {
    if (!customerName.trim()) {
      toast({
        title: "Error",
        description: "Please enter customer name",
        variant: "destructive",
      });
      return;
    }

    // Phone number is optional, but if provided, validate it
    if (phoneNumber.trim() && phoneNumber.trim().length < 10) {
      toast({
        title: "Error",
        description: "Please enter a valid phone number (at least 10 digits)",
        variant: "destructive",
      });
      return;
    }

    if (orderItems.length === 0) {
      toast({
        title: "Error",
        description: "Please add at least one item to the order",
        variant: "destructive",
      });
      return;
    }

    try {
      setUpdating(true);
      const orderData = {
        customerName: customerName.trim(),
        paymentMethod: paymentMethod,
        items: orderItems.map(item => ({
          name: item.name,
          quantity: item.quantity
        }))
      };

      // Only include phone number if provided
      if (phoneNumber.trim()) {
        orderData.phoneNumber = phoneNumber.trim();
      }

      const updatedOrder = await ordersAPI.updateOrder(order.id, orderData);
      
      toast({
        title: "Success",
        description: `Order updated for ${customerName}`,
      });

      onOrderUpdated(updatedOrder);
      onOpenChange(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update order",
        variant: "destructive",
      });
    } finally {
      setUpdating(false);
    }
  };

  const filteredMenuItems = selectedCategory 
    ? menu.items.filter(item => item.category === selectedCategory)
    : menu.items;

  // Filter out items already in order to avoid duplicates in the menu
  const availableMenuItems = filteredMenuItems.filter(
    menuItem => !orderItems.some(orderItem => orderItem.name === menuItem.name)
  );

  const totalItems = orderItems.reduce((sum, item) => sum + item.quantity, 0);

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

  if (!order) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Edit className="h-5 w-5" />
            Edit Order
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Customer Name */}
          <div className="space-y-2">
            <Label htmlFor="customerName">Customer Name</Label>
            <Input
              id="customerName"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              placeholder="Enter customer name"
              className="w-full"
            />
          </div>

          {/* Phone Number */}
          <div className="space-y-2">
            <Label htmlFor="phoneNumber">Phone Number</Label>
            <Input
              id="phoneNumber"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="Enter phone number (e.g., 1234567890)"
              className="w-full"
              type="tel"
            />
          </div>

          {/* Payment Method */}
          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <CreditCard className="h-4 w-4" />
              Payment Method
            </Label>
            <Select value={paymentMethod} onValueChange={setPaymentMethod}>
              <SelectTrigger>
                <SelectValue placeholder="Select payment method" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="cash">
                  <span className="flex items-center gap-2">
                    💵 Cash
                  </span>
                </SelectItem>
                <SelectItem value="zelle">
                  <span className="flex items-center gap-2">
                    💳 Zelle
                  </span>
                </SelectItem>
                <SelectItem value="cashapp">
                  <span className="flex items-center gap-2">
                    💰 Cash App
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Current Order Items */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label>Current Order Items ({totalItems} items)</Label>
              <Badge variant="outline" className="flex items-center gap-1">
                {getPaymentMethodIcon(paymentMethod)}
                {paymentMethod.charAt(0).toUpperCase() + paymentMethod.slice(1)}
              </Badge>
            </div>
            {orderItems.length === 0 ? (
              <div className="text-center py-4 text-gray-500">
                No items in order
              </div>
            ) : (
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {orderItems.map(item => (
                  <div key={item.name} className="flex items-center justify-between bg-blue-50 p-3 rounded-lg">
                    <div>
                      <span className="font-medium">{item.name}</span>
                      {item.chef && <p className="text-xs text-gray-600">Chef: {item.chef}</p>}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateItemQuantity(item.name, item.quantity - 1)}
                      >
                        <Minus className="h-3 w-3" />
                      </Button>
                      <span className="w-8 text-center font-medium">{item.quantity}</span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateItemQuantity(item.name, item.quantity + 1)}
                      >
                        <Plus className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => removeItemFromOrder(item.name)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Add More Items */}
          <div className="space-y-4">
            <Label>Add More Items</Label>
            
            {/* Category Filter */}
            <div className="space-y-2">
              <Label>Food Category</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {menu.categories.map(category => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Available Menu Items */}
            {loading ? (
              <div className="text-center py-8">Loading menu...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-60 overflow-y-auto">
                {availableMenuItems.length === 0 ? (
                  <div className="col-span-2 text-center py-4 text-gray-500">
                    All items from this category are already in the order
                  </div>
                ) : (
                  availableMenuItems.map(item => (
                    <Card key={item.id} className="cursor-pointer hover:shadow-md transition-shadow">
                      <CardContent className="p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-medium text-sm">{item.name}</h4>
                            <p className="text-xs text-gray-600">
                              Chef: {item.chef}
                              {item.sousChef && ` • Sous: ${item.sousChef}`}
                            </p>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {item.category}
                          </Badge>
                        </div>
                        <Button
                          size="sm"
                          className="w-full"
                          onClick={() => addItemToOrder(item)}
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Add
                        </Button>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleUpdateOrder}
              disabled={updating || !customerName.trim() || !phoneNumber.trim() || orderItems.length === 0}
              className="flex-1"
            >
              {updating ? 'Updating...' : `Update Order (${totalItems} items)`}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default EditOrderModal;