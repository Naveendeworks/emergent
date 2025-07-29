import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from typing import List
from models.order import OrderItem

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.error("Twilio credentials not properly configured")
            raise ValueError("Twilio credentials missing in environment variables")
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def format_order_items(self, items: List[OrderItem]) -> str:
        """Format order items for SMS message"""
        if not items:
            return "No items"
        
        formatted_items = []
        for item in items:
            if item.quantity > 1:
                formatted_items.append(f"• {item.name} (x{item.quantity})")
            else:
                formatted_items.append(f"• {item.name}")
        
        return "\n".join(formatted_items)
    
    def send_order_ready_notification(self, customer_name: str, phone_number: str, items: List[OrderItem]) -> bool:
        """Send SMS notification when order is ready for pickup"""
        try:
            # Format the items list
            items_text = self.format_order_items(items)
            
            # Create the message
            message_body = f"""Mem Famous Stall - Your order is ready for pickup!

Hi {customer_name}, your delicious order is prepared and waiting for you:

{items_text}

Please come and collect your order. Thank you for choosing Mem Famous Stall! 🍽️"""

            # Send the SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.phone_number,
                to=phone_number
            )
            
            logger.info(f"SMS sent successfully to {phone_number}. Message SID: {message.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {phone_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {phone_number}: {str(e)}")
            return False
    
    def send_test_message(self, phone_number: str) -> bool:
        """Send a test message to verify SMS functionality"""
        try:
            message = self.client.messages.create(
                body="Test message from Mem Famous Stall order management system!",
                from_=self.phone_number,
                to=phone_number
            )
            
            logger.info(f"Test SMS sent successfully to {phone_number}. Message SID: {message.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Twilio error sending test SMS to {phone_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending test SMS to {phone_number}: {str(e)}")
            return False