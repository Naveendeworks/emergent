import React from 'react';
import { Button } from './ui/button';
import { LogOut, User, BarChart3, ClipboardList } from 'lucide-react';
import { authService } from '../services/auth';

const Header = ({ onLogout, currentPage, onNavigate }) => {
  const username = authService.getUsername();

  const handleLogout = () => {
    authService.logout();
    onLogout();
  };

  return (
    <div className="bg-white shadow-sm border-b">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Order Management</h1>
            <p className="text-gray-600">Track and manage customer orders efficiently</p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Navigation Buttons */}
            <div className="flex items-center gap-2">
              <Button
                variant={currentPage === 'orders' ? 'default' : 'outline'}
                onClick={() => onNavigate('orders')}
                className="flex items-center gap-2"
              >
                <ClipboardList className="h-4 w-4" />
                Orders
              </Button>
              <Button
                variant={currentPage === 'reports' ? 'default' : 'outline'}
                onClick={() => onNavigate('reports')}
                className="flex items-center gap-2"
              >
                <BarChart3 className="h-4 w-4" />
                Reports
              </Button>
            </div>
            
            <div className="flex items-center gap-2 text-gray-600">
              <User className="h-4 w-4" />
              <span className="font-medium">{username}</span>
            </div>
            <Button
              variant="outline"
              onClick={handleLogout}
              className="flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;