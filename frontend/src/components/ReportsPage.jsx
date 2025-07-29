import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { BarChart3, TrendingUp, DollarSign, Clock, Users, RefreshCw, Download, FileSpreadsheet } from 'lucide-react';
import { reportsAPI, ordersAPI, formatDeliveryTime } from '../services/api';
import { useToast } from '../hooks/use-toast';

const ReportsPage = () => {
  const [paymentReports, setPaymentReports] = useState([]);
  const [itemReports, setItemReports] = useState([]);
  const [priceAnalysis, setPriceAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloadingPayment, setDownloadingPayment] = useState(false);
  const [downloadingItems, setDownloadingItems] = useState(false);
  const [downloadingPriceAnalysis, setDownloadingPriceAnalysis] = useState(false);
  const [selectedPaymentFilter, setSelectedPaymentFilter] = useState('all');
  const [selectedItemFilter, setSelectedItemFilter] = useState('all');
  const { toast } = useToast();

  useEffect(() => {
    loadReports();
    loadPriceAnalysis();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      const [paymentData, itemData] = await Promise.all([
        reportsAPI.getPaymentReports(),
        reportsAPI.getItemReports()
      ]);
      setPaymentReports(paymentData);
      setItemReports(itemData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load reports",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadPriceAnalysis = async () => {
    try {
      const priceData = await ordersAPI.getPriceAnalysis();
      setPriceAnalysis(priceData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load price analysis",
        variant: "destructive",
      });
    }
  };

  const handleDownloadPaymentReports = async () => {
    try {
      setDownloadingPayment(true);
      const result = await reportsAPI.downloadPaymentReports();
      toast({
        title: "Download Successful",
        description: `Payment reports exported as ${result.filename}`,
        duration: 4000,
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Failed to export payment reports",
        variant: "destructive",
      });
    } finally {
      setDownloadingPayment(false);
    }
  };

  const handleDownloadItemReports = async () => {
    try {
      setDownloadingItems(true);
      const result = await reportsAPI.downloadItemReports();
      toast({
        title: "Download Successful",
        description: `Item reports exported as ${result.filename}`,
        duration: 4000,
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Failed to export item reports",
        variant: "destructive",
      });
    } finally {
      setDownloadingItems(false);
    }
  };

  const handleDownloadPriceAnalysis = async () => {
    try {
      setDownloadingPriceAnalysis(true);
      const result = await reportsAPI.downloadPriceAnalysis();
      toast({
        title: "Download Successful",
        description: `Price analysis exported as ${result.filename}`,
        duration: 4000,
      });
    } catch (error) {
      toast({
        title: "Download Failed",
        description: "Failed to export price analysis",
        variant: "destructive",
      });
    } finally {
      setDownloadingPriceAnalysis(false);
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

  const filteredPaymentReports = selectedPaymentFilter === 'all' 
    ? paymentReports 
    : paymentReports.filter(report => report.paymentMethod === selectedPaymentFilter);

  const filteredItemReports = selectedItemFilter === 'all' 
    ? itemReports 
    : itemReports.filter(report => report.popularPaymentMethod === selectedItemFilter);

  const totalOrders = paymentReports.reduce((sum, report) => sum + report.orderCount, 0);
  const totalItems = paymentReports.reduce((sum, report) => sum + report.totalItems, 0);
  const avgDeliveryTime = paymentReports.reduce((sum, report) => 
    sum + (report.averageDeliveryTime || 0), 0) / paymentReports.length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports & Analytics</h1>
          <p className="text-gray-600">Comprehensive analysis of orders and performance</p>
        </div>
        <Button 
          onClick={loadReports}
          disabled={loading}
          variant="outline"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Orders</CardTitle>
            <BarChart3 className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{totalOrders}</div>
            <p className="text-xs text-gray-600">All time orders</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Items Sold</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{totalItems}</div>
            <p className="text-xs text-gray-600">Items delivered</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Delivery Time</CardTitle>
            <Clock className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {formatDeliveryTime(avgDeliveryTime)}
            </div>
            <p className="text-xs text-gray-600">Order to completion</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Menu Items</CardTitle>
            <Users className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{itemReports.length}</div>
            <p className="text-xs text-gray-600">Items ordered</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="payment" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="payment">Payment Reports</TabsTrigger>
          <TabsTrigger value="items">Item Reports</TabsTrigger>
          <TabsTrigger value="price-analysis">Price Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="payment" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-semibold">Payment Method Analysis</h2>
              <Select value={selectedPaymentFilter} onValueChange={setSelectedPaymentFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by payment method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Payment Methods</SelectItem>
                  <SelectItem value="cash">Cash Only</SelectItem>
                  <SelectItem value="zelle">Zelle Only</SelectItem>
                  <SelectItem value="cashapp">Cash App Only</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={handleDownloadPaymentReports}
              disabled={downloadingPayment || loading}
              className="bg-green-600 hover:bg-green-700"
            >
              <Download className={`h-4 w-4 mr-2 ${downloadingPayment ? 'animate-spin' : ''}`} />
              {downloadingPayment ? 'Exporting...' : 'Export Excel'}
            </Button>
          </div>

          <div className="grid gap-4">
            {loading ? (
              <Card>
                <CardContent className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2">Loading reports...</span>
                </CardContent>
              </Card>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Payment Method</TableHead>
                    <TableHead>Total Orders</TableHead>
                    <TableHead>Total Items</TableHead>
                    <TableHead>Pending</TableHead>
                    <TableHead>Completed</TableHead>
                    <TableHead>Avg Delivery Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredPaymentReports.map((report) => (
                    <TableRow key={report.paymentMethod}>
                      <TableCell>
                        <Badge className={`${getPaymentMethodColor(report.paymentMethod)} text-xs`}>
                          {getPaymentMethodIcon(report.paymentMethod)}
                          {report.paymentMethod.charAt(0).toUpperCase() + report.paymentMethod.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-medium">{report.orderCount}</TableCell>
                      <TableCell>{report.totalItems}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-orange-600">
                          {report.pendingOrders}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-green-600">
                          {report.completedOrders}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDeliveryTime(report.averageDeliveryTime)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </TabsContent>

        <TabsContent value="items" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h2 className="text-xl font-semibold">Menu Item Performance</h2>
              <Select value={selectedItemFilter} onValueChange={setSelectedItemFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filter by payment method" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Items</SelectItem>
                  <SelectItem value="cash">Cash Orders</SelectItem>
                  <SelectItem value="zelle">Zelle Orders</SelectItem>
                  <SelectItem value="cashapp">Cash App Orders</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button
              onClick={handleDownloadItemReports}
              disabled={downloadingItems || loading}
              className="bg-green-600 hover:bg-green-700"
            >
              <Download className={`h-4 w-4 mr-2 ${downloadingItems ? 'animate-spin' : ''}`} />
              {downloadingItems ? 'Exporting...' : 'Export Excel'}
            </Button>
          </div>

          <div className="grid gap-4">
            {loading ? (
              <Card>
                <CardContent className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2">Loading reports...</span>
                </CardContent>
              </Card>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Item Name</TableHead>
                    <TableHead>Total Ordered</TableHead>
                    <TableHead>Order Count</TableHead>
                    <TableHead>Avg per Order</TableHead>
                    <TableHead>Popular Payment</TableHead>
                    <TableHead>Recent Customers</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredItemReports.map((report) => (
                    <TableRow key={report.itemName}>
                      <TableCell className="font-medium">{report.itemName}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="text-blue-600">
                          {report.totalOrdered}
                        </Badge>
                      </TableCell>
                      <TableCell>{report.orderCount}</TableCell>
                      <TableCell>{report.averageQuantityPerOrder.toFixed(1)}</TableCell>
                      <TableCell>
                        <Badge className={`${getPaymentMethodColor(report.popularPaymentMethod)} text-xs`}>
                          {getPaymentMethodIcon(report.popularPaymentMethod)}
                          {report.popularPaymentMethod.charAt(0).toUpperCase() + report.popularPaymentMethod.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {report.recentOrders.slice(0, 3).map((customer, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {customer}
                            </Badge>
                          ))}
                          {report.recentOrders.length > 3 && (
                            <Badge variant="secondary" className="text-xs">
                              +{report.recentOrders.length - 3}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReportsPage;