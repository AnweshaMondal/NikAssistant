import smtplib
import logging
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import config
import time

logger = logging.getLogger("nikassistant.email")

class EmailService:
    def __init__(self):
        self.email = config.EMAIL_USER
        self.password = config.EMAIL_PASS
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
    def send_email(self, to_email=None, subject="Notification from NikAssistant", body=""):
        """
        Send an email notification
        
        Args:
            to_email (str): Recipient email. If None, sends to the configured email
            subject (str): Email subject
            body (str): Email body (HTML format supported)
        
        Returns:
            bool: Success status
        """
        if not self.email or not self.password:
            logger.warning("Email service not configured. Set EMAIL_USER and EMAIL_PASS in .env")
            return False
            
        recipient = to_email if to_email else self.email
        
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.email
            message["To"] = recipient
            message["Subject"] = subject
            
            # Attach HTML body
            message.attach(MIMEText(body, "html"))
            
            # Connect to server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(message)
                
            logger.info(f"Email sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def fetch_important_emails(self, max_emails=5):
        """
        Fetch important emails using Gmail API
        Note: This is a simplified version. Full implementation would require 
        Google API authentication and Gmail API integration
        
        Args:
            max_emails (int): Maximum number of emails to fetch
            
        Returns:
            list: List of important email data
        """
        # This is a mock implementation
        # In a real implementation, you would use the Gmail API to fetch emails
        
        logger.info("Fetching important emails (mock implementation)")
        
        # Simulate API delay
        time.sleep(1)
        
        # Mock data
        mock_emails = [
            {
                "id": "email1",
                "sender": "boss@company.com",
                "subject": "Important meeting tomorrow",
                "snippet": "We need to discuss the project status...",
                "date": datetime.now().isoformat(),
                "importance": "high"
            },
            {
                "id": "email2",
                "sender": "team@company.com",
                "subject": "Weekly update",
                "snippet": "Here are this week's accomplishments...",
                "date": (datetime.now().isoformat()),
                "importance": "medium"
            },
            {
                "id": "email3",
                "sender": "notifications@service.com",
                "subject": "Your subscription renewal",
                "snippet": "Your service subscription will expire soon...",
                "date": (datetime.now().isoformat()),
                "importance": "medium"
            }
        ]
        
        return mock_emails[:max_emails]
        
    def send_test_email(self):
        """Send a test email to verify configuration"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.send_email(
            subject="Test Email from NikAssistant",
            body=f"""
            <h2>NikAssistant Email System Test</h2>
            <p>This is a test email sent on {current_time}.</p>
            <p>If you're seeing this email, your email configuration is working correctly.</p>
            <hr>
            <p><em>This is an automated test message from NikAssistant.</em></p>
            """
        )
