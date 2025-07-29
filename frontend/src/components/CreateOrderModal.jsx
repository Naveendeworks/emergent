import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent } from './ui/card';
import { Plus, Minus, ShoppingCart, X, CreditCard, Phone } from 'lucide-react';
import { menuAPI, ordersAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const CreateOrderModal = ({ open, onOpenChange, onOrderCreated }) => {
  const [customerName, setCustomerName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [menu, setMenu] = useState({ items: [], categories: [] });
  const [selectedCategory, setSelectedCategory] = useState('');
  const [orderItems, setOrderItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (open) {
      loadMenu();
    }
  }, [open]);

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
    const existingItem = orderItems.find(item => item.id === menuItem.id);
    if (existingItem) {
      setOrderItems(orderItems.map(item => 
        item.id === menuItem.id 
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

  const removeItemFromOrder = (itemId) => {
    setOrderItems(orderItems.filter(item => item.id !== itemId));
  };

  const updateItemQuantity = (itemId, newQuantity) => {
    if (newQuantity <= 0) {
      removeItemFromOrder(itemId);
    } else {
      setOrderItems(orderItems.map(item => 
        item.id === itemId 
          ? { ...item, quantity: newQuantity }
          : item
      ));
    }
  };

  const formatPhoneNumber = (value) => {
    // Remove all non-numeric characters
    const cleaned = value.replace(/\D/g, '');
    
    // Format based on length
    if (cleaned.length <= 3) {
      return cleaned;
    } else if (cleaned.length <= 6) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3)}`;
    } else if (cleaned.length <= 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    } else {
      // Handle numbers with country code
      return `+${cleaned.slice(0, 1)} (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7, 11)}`;
    }
  };

  const handlePhoneChange = (e) => {
    const formatted = formatPhoneNumber(e.target.value);
    setPhoneNumber(formatted);
  };

  const validatePhoneNumber = (phone) => {
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length === 10 || (cleaned.length === 11 && cleaned.startsWith('1'));
  };

  const handleCreateOrder = async () => {
    if (!customerName.trim()) {
      toast({
        title: "Error",
        description: "Please enter customer name",
        variant: "destructive",
      });
      return;
    }

    if (!phoneNumber.trim()) {
      toast({
        title: "Error",
        description: "Please enter phone number",
        variant: "destructive",
      });
      return;
    }

    if (!validatePhoneNumber(phoneNumber)) {
      toast({
        title: "Error",
        description: "Please enter a valid US phone number",
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
      setCreating(true);
      
      // Clean phone number for API
      const cleanedPhone = phoneNumber.replace(/\D/g, '');
      const apiPhoneNumber = cleanedPhone.length === 10 ? `+1${cleanedPhone}` : `+${cleanedPhone}`;
      
      const orderData = {
        customerName: customerName.trim(),
        phoneNumber: apiPhoneNumber,
        paymentMethod: paymentMethod,
        items: orderItems.map(item => ({
          name: item.name,
          quantity: item.quantity
        }))
      };

      const createdOrder = await ordersAPI.createOrder(orderData);
      
      toast({
        title: "Success",
        description: `Order created for ${customerName}. SMS notification will be sent when ready!`,
      });

      // Reset form
      setCustomerName('');
      setPhoneNumber('');
      setPaymentMethod('cash');
      setOrderItems([]);
      onOrderCreated(createdOrder);
      onOpenChange(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create order",
        variant: "destructive",
      });
    } finally {
      setCreating(false);
    }
  };

  const filteredMenuItems = selectedCategory 
    ? menu.items.filter(item => item.category === selectedCategory)
    : menu.items;

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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" />
            Create New Order
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Customer Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            
            <div className="space-y-2">
              <Label htmlFor="phoneNumber" className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                Phone Number (for pickup notification)
              </Label>
              <Input
                id="phoneNumber"
                type="tel"
                value={phoneNumber}
                onChange={handlePhoneChange}
                placeholder="(555) 123-4567"
                className="w-full"
                maxLength={18}
              />
              <p className="text-xs text-gray-600">SMS notification will be sent when order is ready</p>
            </div>
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

          {/* Menu Items */}
          <div className="space-y-4">
            <Label>Select Food Items</Label>
            {loading ? (
              <div className="text-center py-8">Loading menu...</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-60 overflow-y-auto">
                {filteredMenuItems.map(item => (
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
                ))}
              </div>
            )}
          </div>

          {/* Selected Items */}
          {orderItems.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Order Items ({totalItems} items)</Label>
                <Badge variant="outline" className="flex items-center gap-1">
                  {getPaymentMethodIcon(paymentMethod)}
                  {paymentMethod.charAt(0).toUpperCase() + paymentMethod.slice(1)}
                </Badge>
              </div>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {orderItems.map(item => (
                  <div key={item.id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                    <div>
                      <span className="font-medium">{item.name}</span>
                      <p className="text-xs text-gray-600">Chef: {item.chef}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateItemQuantity(item.id, item.quantity - 1)}
                      >
                        <Minus className="h-3 w-3" />
                      </Button>
                      <span className="w-8 text-center font-medium">{item.quantity}</span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => updateItemQuantity(item.id, item.quantity + 1)}
                      >
                        <Plus className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => removeItemFromOrder(item.id)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

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
              onClick={handleCreateOrder}
              disabled={creating || !customerName.trim() || !phoneNumber.trim() || orderItems.length === 0}
              className="flex-1"
            >
              {creating ? 'Creating...' : `Create Order (${totalItems} items)`}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default CreateOrderModal;