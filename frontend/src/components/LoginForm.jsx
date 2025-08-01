import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { User, Lock, ChefHat, Store, Shield, ArrowRight } from 'lucide-react';
import { authService } from '../services/auth';
import { useToast } from '../hooks/use-toast';

const LoginForm = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const success = await authService.login(credentials.username, credentials.password);
      if (success) {
        toast({
          title: "Welcome to Kitchen Management! 👨‍🍳",
          description: "Successfully authenticated. Loading your dashboard...",
          duration: 3000,
        });
        setTimeout(() => onLogin(), 500);
      } else {
        toast({
          title: "Authentication Failed",
          description: "Invalid credentials. Please check your username and password.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "System Error",
        description: "Unable to connect to authentication service.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="min-h-screen restaurant-bg flex items-center justify-center p-6">
      {/* Background Design Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-10 left-10 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute top-1/2 right-20 w-48 h-48 bg-blue-500/10 rounded-full blur-2xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-20 left-1/4 w-24 h-24 bg-purple-500/10 rounded-full blur-xl animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="relative z-10 w-full max-w-md animate-fade-in-up">
        {/* Restaurant Branding Header */}
        <div className="text-center mb-8 animate-slide-in-left">
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-white rounded-3xl shadow-2xl">
              <div className="p-3 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl">
                <Store className="h-12 w-12 text-white" />
              </div>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Mem Famous Stall 2025
          </h1>
          <p className="text-blue-100 text-lg font-medium flex items-center justify-center gap-2">
            <ChefHat className="h-5 w-5" />
            Professional Kitchen Management System
          </p>
        </div>

        {/* Professional Login Card */}
        <Card className="restaurant-card-bg shadow-2xl border-0 animate-scale-in" style={{ animationDelay: '0.3s' }}>
          <CardHeader className="text-center pb-6">
            <div className="flex justify-center mb-4">
              <div className="p-3 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl">
                <Shield className="h-8 w-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-gray-800 mb-2">
              Staff Authentication
            </CardTitle>
            <p className="text-gray-600 font-medium">
              Secure access to restaurant operations
            </p>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username Input */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                  <User className="h-4 w-4 text-blue-600" />
                  Staff Username
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <Input
                    type="text"
                    name="username"
                    placeholder="Enter your username"
                    value={credentials.username}
                    onChange={handleInputChange}
                    className="pl-12 pr-4 py-3 text-lg bg-white border-2 border-gray-200 rounded-xl focus:border-blue-400 transition-all duration-300"
                    required
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                  <Lock className="h-4 w-4 text-blue-600" />
                  Access Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <Input
                    type="password"
                    name="password"
                    placeholder="Enter your password"
                    value={credentials.password}
                    onChange={handleInputChange}
                    className="pl-12 pr-4 py-3 text-lg bg-white border-2 border-gray-200 rounded-xl focus:border-blue-400 transition-all duration-300"
                    required
                  />
                </div>
              </div>

              {/* Professional Login Button */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full btn-restaurant-primary text-white font-bold py-4 text-lg transition-all duration-300 hover:shadow-xl group"
              >
                {loading ? (
                  <div className="flex items-center gap-3">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Authenticating...</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-3">
                    <Shield className="h-5 w-5 group-hover:rotate-12 transition-transform" />
                    <span>Access Kitchen Dashboard</span>
                    <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </div>
                )}
              </Button>
            </form>

            {/* Login Credentials Info */}
            <div className="mt-8 p-4 bg-blue-50 rounded-xl border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <div className="p-1 bg-blue-100 rounded-lg">
                  <Shield className="h-4 w-4 text-blue-600" />
                </div>
                <span className="text-sm font-semibold text-blue-800">Demo Credentials</span>
              </div>
              <div className="text-sm text-blue-700 space-y-1">
                <div className="flex justify-between">
                  <span className="font-medium">Username:</span>
                  <code className="bg-blue-100 px-2 py-1 rounded font-mono">admin</code>
                </div>
                <div className="flex justify-between">
                  <span className="font-medium">Password:</span>
                  <code className="bg-blue-100 px-2 py-1 rounded font-mono">memfamous2025</code>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 animate-slide-in-right" style={{ animationDelay: '0.6s' }}>
          <p className="text-blue-100 text-sm">
            © 2025 Mem Famous Stall • Professional Restaurant Management
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;