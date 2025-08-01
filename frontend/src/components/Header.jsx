import React from 'react';
import { Button } from './ui/button';
import { LogOut, User, BarChart3, ClipboardList, Monitor, ChefHat, Store } from 'lucide-react';
import { authService } from '../services/auth';

const Header = ({ onLogout, currentPage, onNavigate }) => {
  const username = authService.getUsername();

  const handleLogout = () => {
    authService.logout();
    onLogout();
  };

  const navigationItems = [
    {
      key: 'orders',
      icon: ClipboardList,
      label: 'Service Station',
      description: 'Order Ticket Management'
    },
    {
      key: 'reports',
      icon: BarChart3,
      label: 'Analytics Hub',
      description: 'Business Intelligence'
    },
    {
      key: 'order-queue',
      icon: Monitor,
      label: 'Kitchen Display',
      description: 'Real-time Order Queue'
    }
  ];

  return (
    <div className="bg-white shadow-lg border-b border-gray-100 animate-fade-in-up">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Restaurant Branding */}
          <div className="animate-slide-in-left">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl">
                <Store className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold restaurant-heading">
                  Mem Famous Stall 2025
                </h1>
                <p className="text-gray-600 font-medium flex items-center gap-2">
                  <ChefHat className="h-4 w-4" />
                  Professional Kitchen Management System
                </p>
              </div>
            </div>
          </div>
          
          {/* Navigation & User Controls */}
          <div className="flex items-center gap-6 animate-slide-in-right">
            {/* Professional Navigation */}
            <div className="flex items-center gap-3">
              {navigationItems.map((item, index) => {
                const IconComponent = item.icon;
                const isActive = currentPage === item.key;
                
                return (
                  <div key={item.key} className="animate-scale-in" style={{ animationDelay: `${index * 0.1}s` }}>
                    <Button
                      variant={isActive ? 'default' : 'outline'}
                      onClick={() => onNavigate(item.key)}
                      className={`group relative overflow-hidden transition-all duration-300 ${
                        isActive 
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg' 
                          : 'hover:bg-gray-50 hover:border-blue-300 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center gap-2 relative z-10">
                        <IconComponent className={`h-4 w-4 transition-all duration-300 ${
                          isActive ? 'text-white' : 'text-gray-600 group-hover:text-blue-600'
                        }`} />
                        <div className="text-left">
                          <div className={`font-semibold text-sm ${
                            isActive ? 'text-white' : 'text-gray-800'
                          }`}>
                            {item.label}
                          </div>
                          <div className={`text-xs opacity-75 ${
                            isActive ? 'text-blue-100' : 'text-gray-500'
                          }`}>
                            {item.description}
                          </div>
                        </div>
                      </div>
                      
                      {/* Hover effect overlay */}
                      {!isActive && (
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>
            
            {/* User Profile & Logout */}
            <div className="flex items-center gap-4 pl-6 border-l border-gray-200">
              <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 rounded-xl animate-scale-in">
                <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg">
                  <User className="h-4 w-4 text-white" />
                </div>
                <div className="text-right">
                  <div className="font-semibold text-gray-800 text-sm">
                    {username || 'Kitchen Manager'}
                  </div>
                  <div className="text-xs text-gray-500">Restaurant Staff</div>
                </div>
              </div>
              
              <Button
                variant="outline"
                onClick={handleLogout}
                className="group relative overflow-hidden border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 transition-all duration-300 animate-scale-in"
                style={{ animationDelay: '0.3s' }}
              >
                <LogOut className="h-4 w-4 mr-2 group-hover:rotate-12 transition-transform duration-300" />
                <span className="font-medium">Sign Out</span>
                
                <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </Button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Subtle bottom gradient */}
      <div className="h-1 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600" />
    </div>
  );
};

export default Header;