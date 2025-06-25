import json
import logging
import os
from datetime import datetime
import config
from plyer import notification

logger = logging.getLogger("nikassistant.notifications")

class NotificationService:
    def __init__(self):
        self.app_name = "NikAssistant"
        self.icon_path = os.path.join(config.STATIC_DIR, "icons", "app_icon.png")
        
        # Create icon directory if it doesn't exist
        icon_dir = os.path.join(config.STATIC_DIR, "icons")
        os.makedirs(icon_dir, exist_ok=True)
        
        # Initialize Firebase (if configured)
        self.firebase_available = self._setup_firebase()
        
    def _setup_firebase(self):
        """Set up Firebase for mobile notifications if configured"""
        firebase_key = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
        
        if not firebase_key or not os.path.exists(firebase_key):
            logger.info("Firebase not configured, mobile notifications disabled")
            return False
            
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
            
            cred = credentials.Certificate(firebase_key)
            self.firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False
    
    def send_desktop_notification(self, title, message, timeout=10):
        """
        Send desktop notification using Plyer
        
        Args:
            title (str): Notification title
            message (str): Notification message
            timeout (int): Notification timeout in seconds
        """
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                timeout=timeout,
                app_icon=self.icon_path if os.path.exists(self.icon_path) else None
            )
            logger.debug(f"Desktop notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
            return False
            
    def send_mobile_notification(self, title, message, topic="all_users"):
        """
        Send mobile notification using Firebase Cloud Messaging
        
        Args:
            title (str): Notification title
            message (str): Notification message
            topic (str): Topic to send notification to
        """
        if not self.firebase_available:
            logger.warning("Mobile notifications unavailable - Firebase not configured")
            return False
            
        try:
            from firebase_admin import messaging
            
            message_payload = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                topic=topic,
            )
            
            messaging.send(message_payload)
            logger.debug(f"Mobile notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send mobile notification: {e}")
            return False
            
    def send_notification(self, title, message):
        """
        Send notification to all available channels
        
        Args:
            title (str): Notification title
            message (str): Notification message
        """
        desktop_success = self.send_desktop_notification(title, message)
        mobile_success = self.send_mobile_notification(title, message)
        
        return desktop_success or mobile_success
