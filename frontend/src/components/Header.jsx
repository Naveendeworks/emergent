import React from 'react';
import { Button } from './ui/button';
import { LogOut, User } from 'lucide-react';
import { authService } from '../services/auth';

const Header = ({ onLogout }) => {
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