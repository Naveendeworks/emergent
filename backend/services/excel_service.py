import io
import pandas as pd
from datetime import datetime
from typing import List
from models.order import PaymentReport, ItemReport, EASTERN_TZ
import logging

logger = logging.getLogger(__name__)

class ExcelService:
    def __init__(self):
        pass
    
    def create_payment_report_excel(self, payment_reports: List[PaymentReport]) -> io.BytesIO:
        """Create Excel file for payment reports"""
        try:
            # Convert payment reports to DataFrame
            data = []
            for report in payment_reports:
                data.append({
                    'Payment Method': report.paymentMethod.upper(),
                    'Total Orders': report.orderCount,
                    'Total Items Sold': report.totalItems,
                    'Pending Orders': report.pendingOrders,
                    'Completed Orders': report.completedOrders,
                    'Average Delivery Time (minutes)': round(report.averageDeliveryTime, 2) if report.averageDeliveryTime else 'N/A',
                    'Completion Rate (%)': round((report.completedOrders / report.orderCount) * 100, 1) if report.orderCount > 0 else 0
                })
            
            df = pd.DataFrame(data)
            
            # Create Excel file in memory
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Write main report
                df.to_excel(writer, sheet_name='Payment Methods Report', index=False)
                
                # Create summary sheet
                summary_data = {
                    'Metric': [
                        'Total Orders',
                        'Total Items Sold',
                        'Total Pending Orders',
                        'Total Completed Orders',
                        'Overall Completion Rate (%)',
                        'Average Delivery Time (minutes)'
                    ],
                    'Value': [
                        sum(r.orderCount for r in payment_reports),
                        sum(r.totalItems for r in payment_reports),
                        sum(r.pendingOrders for r in payment_reports),
                        sum(r.completedOrders for r in payment_reports),
                        round((sum(r.completedOrders for r in payment_reports) / sum(r.orderCount for r in payment_reports)) * 100, 1) if sum(r.orderCount for r in payment_reports) > 0 else 0,
                        round(sum(r.averageDeliveryTime or 0 for r in payment_reports) / len(payment_reports), 2) if payment_reports else 'N/A'
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Add metadata sheet
                current_time = datetime.now(EASTERN_TZ)
                metadata = {
                    'Report Information': [
                        'Report Generated',
                        'Time Zone',
                        'Report Type',
                        'Total Payment Methods',
                        'Data Source'
                    ],
                    'Details': [
                        current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                        'Eastern Time (US/Eastern)',
                        'Payment Methods Analysis',
                        len(payment_reports),
                        'Order Management System'
                    ]
                }
                metadata_df = pd.DataFrame(metadata)
                metadata_df.to_excel(writer, sheet_name='Report Info', index=False)
            
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Error creating payment report Excel: {str(e)}")
            raise e
    
    def create_item_report_excel(self, item_reports: List[ItemReport]) -> io.BytesIO:
        """Create Excel file for item reports"""
        try:
            # Convert item reports to DataFrame
            data = []
            for report in item_reports:
                data.append({
                    'Item Name': report.itemName,
                    'Total Quantity Ordered': report.totalOrdered,
                    'Number of Orders': report.orderCount,
                    'Average Quantity per Order': round(report.averageQuantityPerOrder, 2),
                    'Most Popular Payment Method': report.popularPaymentMethod.upper(),
                    'Recent Customers': ', '.join(report.recentOrders[:5]),  # First 5 customers
                    'Total Recent Customers': len(report.recentOrders)
                })
            
            df = pd.DataFrame(data)
            
            # Create Excel file in memory
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Write main report
                df.to_excel(writer, sheet_name='Menu Items Report', index=False)
                
                # Create top items sheet (top 10)
                top_items = df.nlargest(10, 'Total Quantity Ordered')[['Item Name', 'Total Quantity Ordered', 'Number of Orders']]
                top_items.to_excel(writer, sheet_name='Top 10 Items', index=False)
                
                # Create payment method analysis
                payment_analysis = df.groupby('Most Popular Payment Method').agg({
                    'Item Name': 'count',
                    'Total Quantity Ordered': 'sum',
                    'Number of Orders': 'sum'
                }).reset_index()
                payment_analysis.columns = ['Payment Method', 'Number of Items', 'Total Quantity', 'Total Orders']
                payment_analysis.to_excel(writer, sheet_name='Payment Analysis', index=False)
                
                # Create summary sheet
                summary_data = {
                    'Metric': [
                        'Total Menu Items',
                        'Total Items Sold',
                        'Total Orders',
                        'Most Popular Item',
                        'Highest Quantity Item',
                        'Average Items per Order'
                    ],
                    'Value': [
                        len(item_reports),
                        sum(r.totalOrdered for r in item_reports),
                        sum(r.orderCount for r in item_reports),
                        max(item_reports, key=lambda x: x.orderCount).itemName if item_reports else 'N/A',
                        max(item_reports, key=lambda x: x.totalOrdered).itemName if item_reports else 'N/A',
                        round(sum(r.averageQuantityPerOrder for r in item_reports) / len(item_reports), 2) if item_reports else 'N/A'
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Add metadata sheet
                current_time = datetime.now(EASTERN_TZ)
                metadata = {
                    'Report Information': [
                        'Report Generated',
                        'Time Zone',
                        'Report Type',
                        'Total Menu Items',
                        'Data Source'
                    ],
                    'Details': [
                        current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                        'Eastern Time (US/Eastern)',
                        'Menu Items Performance Analysis',
                        len(item_reports),
                        'Order Management System'
                    ]
                }
                metadata_df = pd.DataFrame(metadata)
                metadata_df.to_excel(writer, sheet_name='Report Info', index=False)
            
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Error creating item report Excel: {str(e)}")
            raise e
    
    def get_filename(self, report_type: str) -> str:
        """Generate filename with timestamp"""
        current_time = datetime.now(EASTERN_TZ)
        timestamp = current_time.strftime('%Y%m%d_%H%M%S')
        return f"{report_type}_report_{timestamp}.xlsx"