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
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          {/* Public route - accessible without authentication */}
          <Route path="/myorder" element={<MyOrder onBack={handleBackToDashboard} />} />
          
          {/* Protected routes - require authentication */}
          <Route path="/" element={
            !isAuthenticated ? (
              <LoginForm onLogin={handleLogin} />
            ) : (
              <div className="min-h-screen bg-gray-100">
                <Header 
                  onLogout={handleLogout} 
                  currentPage={currentPage}
                  onNavigate={handleNavigate}
                />
                
                {currentPage === 'orders' && <OrderManager onLogout={handleLogout} />}
                {currentPage === 'reports' && <ReportsPage />}
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