import re
import email
import imaplib
import logging
from email.header import decode_header
from datetime import datetime, timedelta
import config

logger = logging.getLogger("nikassistant.email_parser")

class EmailParser:
    def __init__(self):
        self.email_user = config.EMAIL_USER
        self.email_pass = config.EMAIL_PASS
        self.imap_server = "imap.gmail.com"
        
    def connect_to_inbox(self):
        """Connect to email inbox"""
        if not self.email_user or not self.email_pass:
            logger.error("Email credentials not configured")
            return None
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_user, self.email_pass)
            mail.select("inbox")
            return mail
        except Exception as e:
            logger.error(f"Failed to connect to email: {e}")
            return None
    
    def fetch_recent_emails(self, days=7, max_emails=20):
        """
        Fetch recent emails from inbox
        
        Args:
            days (int): Number of days to look back
            max_emails (int): Maximum number of emails to fetch
            
        Returns:
            list: List of email dictionaries
        """
        mail = self.connect_to_inbox()
        if not mail:
            return []
        
        try:
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            
            # Search for emails
            status, messages = mail.search(None, f'SINCE {since_date}')
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            email_ids = email_ids[-max_emails:]  # Get most recent emails
            
            emails = []
            for email_id in email_ids:
                email_data = self.parse_email(mail, email_id)
                if email_data:
                    emails.append(email_data)
            
            mail.close()
            mail.logout()
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def parse_email(self, mail, email_id):
        """Parse a single email"""
        try:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                return None
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Extract email details
            subject = self.decode_header_value(msg["Subject"])
            sender = self.decode_header_value(msg["From"])
            date = msg["Date"]
            
            # Get email body
            body = self.extract_body(msg)
            
            # Check if email is important
            importance = self.assess_importance(subject, sender, body)
            
            return {
                "id": email_id.decode(),
                "subject": subject,
                "sender": sender,
                "date": date,
                "body": body[:500],  # First 500 characters
                "importance": importance,
                "is_read": False  # You can implement read status checking
            }
            
        except Exception as e:
            logger.error(f"Error parsing email {email_id}: {e}")
            return None
    
    def decode_header_value(self, header_value):
        """Decode email header value"""
        if not header_value:
            return ""
        
        try:
            decoded_parts = decode_header(header_value)
            decoded_value = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_value += part.decode(encoding)
                    else:
                        decoded_value += part.decode('utf-8', errors='ignore')
                else:
                    decoded_value += str(part)
            
            return decoded_value
        except Exception as e:
            logger.error(f"Error decoding header: {e}")
            return str(header_value)
    
    def extract_body(self, msg):
        """Extract email body text"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)
                        if body:
                            return body.decode('utf-8', errors='ignore')
            else:
                body = msg.get_payload(decode=True)
                if body:
                    return body.decode('utf-8', errors='ignore')
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting email body: {e}")
            return ""
    
    def assess_importance(self, subject, sender, body):
        """
        Assess the importance of an email based on content
        
        Returns:
            str: 'high', 'medium', or 'low'
        """
        # Keywords that indicate high importance
        high_importance_keywords = [
            'urgent', 'asap', 'emergency', 'critical', 'deadline',
            'meeting', 'interview', 'invoice', 'payment', 'action required'
        ]
        
        # Keywords that indicate medium importance
        medium_importance_keywords = [
            'update', 'reminder', 'notice', 'announcement', 'schedule',
            'appointment', 'confirm', 'booking', 'reservation'
        ]
        
        # Check subject and body
        content = f"{subject} {body}".lower()
        
        # Check for high importance
        for keyword in high_importance_keywords:
            if keyword in content:
                return 'high'
        
        # Check for medium importance
        for keyword in medium_importance_keywords:
            if keyword in content:
                return 'medium'
        
        # Check sender patterns (you can customize this)
        if any(domain in sender.lower() for domain in ['noreply', 'no-reply', 'newsletter']):
            return 'low'
        
        return 'medium'  # Default importance
    
    def extract_task_suggestions(self, emails):
        """
        Extract potential task suggestions from emails
        
        Args:
            emails (list): List of email dictionaries
            
        Returns:
            list: List of suggested tasks
        """
        task_suggestions = []
        
        # Keywords that suggest actionable items
        action_keywords = [
            'review', 'respond', 'reply', 'call', 'schedule', 'book',
            'confirm', 'pay', 'submit', 'complete', 'finish', 'send'
        ]
        
        for email_data in emails:
            subject = email_data.get('subject', '').lower()
            body = email_data.get('body', '').lower()
            
            # Look for action items
            for keyword in action_keywords:
                if keyword in subject or keyword in body:
                    task_suggestions.append({
                        'title': f"Follow up: {email_data.get('subject', 'Email')}",
                        'description': f"Action needed for email from {email_data.get('sender', 'Unknown')}",
                        'source_email': email_data.get('id'),
                        'priority': 'Medium' if email_data.get('importance') == 'medium' else 'High',
                        'category': 'Email',
                        'suggested_due_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
                    })
                    break  # Only suggest one task per email
        
        return task_suggestions
    
    def search_emails(self, query, max_results=10):
        """
        Search emails by query
        
        Args:
            query (str): Search query
            max_results (int): Maximum results to return
            
        Returns:
            list: List of matching emails
        """
        mail = self.connect_to_inbox()
        if not mail:
            return []
        
        try:
            # Search for emails containing the query
            status, messages = mail.search(None, f'TEXT "{query}"')
            if status != "OK":
                return []
            
            email_ids = messages[0].split()
            email_ids = email_ids[-max_results:]  # Get most recent matching emails
            
            emails = []
            for email_id in email_ids:
                email_data = self.parse_email(mail, email_id)
                if email_data:
                    emails.append(email_data)
            
            mail.close()
            mail.logout()
            return emails
            
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
