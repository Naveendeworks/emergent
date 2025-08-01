import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import OrderManager from "./components/OrderManager";
import ReportsPage from "./components/ReportsPage";
import OrderQueue from "./components/OrderQueue";
import LoginForm from "./components/LoginForm";
import MyOrder from "./components/MyOrder";
import Header from "./components/Header";
import { authService } from "./services/auth";
import { Toaster } from "./components/ui/toaster";
import { ChefHat } from "lucide-react";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState('orders');

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      if (authService.isAuthenticated()) {
        const isValid = await authService.verifyToken();
        setIsAuthenticated(isValid);
      } else {
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentPage('orders');
  };

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  const handleBackToDashboard = () => {
    window.location.href = '/';
  };

  if (loading) {
    return (
      <div className="min-h-screen restaurant-bg flex items-center justify-center">
        <div className="text-center animate-fade-in-up">
          <div className="relative">
            <div className="w-20 h-20 mx-auto mb-6 bg-white rounded-2xl shadow-2xl flex items-center justify-center animate-restaurant-pulse">
              <ChefHat className="h-10 w-10 text-blue-600" />
            </div>
            <div className="absolute inset-0 w-20 h-20 mx-auto rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 opacity-20 animate-ping" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Kitchen Management System
          </h2>
          <p className="text-blue-100 mb-4">Initializing restaurant operations...</p>
          <div className="flex justify-center space-x-1">
            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          {/* Public route - Customer Self-Service */}
          <Route path="/myorder" element={<MyOrder onBack={handleBackToDashboard} />} />
          
          {/* Protected routes - Restaurant Staff Dashboard */}
          <Route path="/" element={
            !isAuthenticated ? (
              <LoginForm onLogin={handleLogin} />
            ) : (
              <div className="min-h-screen restaurant-bg">
                <Header 
                  onLogout={handleLogout} 
                  currentPage={currentPage}
                  onNavigate={handleNavigate}
                />
                
                <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                  {currentPage === 'orders' && <OrderManager onLogout={handleLogout} />}
                  {currentPage === 'reports' && <ReportsPage />}
                  {currentPage === 'order-queue' && <OrderQueue />}
                </div>
              </div>
            )
          } />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;