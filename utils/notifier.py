import logging
import threading
import time
from datetime import datetime
from backend.notification_service import NotificationService
from backend.email_service import EmailService

logger = logging.getLogger("nikassistant.notifier")

class SmartNotifier:
    def __init__(self):
        self.notification_service = NotificationService()
        self.email_service = EmailService()
        self.notification_queue = []
        self.running = False
        self.thread = None
        
    def start(self):
        """Start the notification service"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._process_notifications)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Smart notifier started")
    
    def stop(self):
        """Stop the notification service"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Smart notifier stopped")
    
    def _process_notifications(self):
        """Process notification queue"""
        while self.running:
            try:
                if self.notification_queue:
                    notification = self.notification_queue.pop(0)
                    self._send_notification(notification)
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error processing notifications: {e}")
    
    def _send_notification(self, notification):
        """Send a single notification"""
        try:
            # Send desktop notification
            if notification.get('desktop', True):
                self.notification_service.send_desktop_notification(
                    title=notification['title'],
                    message=notification['message'],
                    timeout=notification.get('timeout', 10)
                )
            
            # Send email notification if requested
            if notification.get('email', False):
                self.email_service.send_task_reminder_email(
                    subject=notification['title'],
                    body=notification['message']
                )
            
            # Send mobile notification if available
            if notification.get('mobile', False) and self.notification_service.firebase_available:
                self.notification_service.send_mobile_notification(
                    title=notification['title'],
                    message=notification['message']
                )
            
            logger.info(f"Notification sent: {notification['title']}")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def add_notification(self, title, message, notification_type="info", 
                        desktop=True, email=False, mobile=False, 
                        timeout=10, delay=0):
        """
        Add a notification to the queue
        
        Args:
            title (str): Notification title
            message (str): Notification message
            notification_type (str): Type of notification (info, warning, error, success)
            desktop (bool): Send desktop notification
            email (bool): Send email notification
            mobile (bool): Send mobile notification
            timeout (int): Desktop notification timeout
            delay (int): Delay before sending (seconds)
        """
        notification = {
            'title': title,
            'message': message,
            'type': notification_type,
            'desktop': desktop,
            'email': email,
            'mobile': mobile,
            'timeout': timeout,
            'scheduled_time': datetime.now().timestamp() + delay
        }
        
        self.notification_queue.append(notification)
        logger.debug(f"Notification queued: {title}")
    
    def notify_task_due(self, task):
        """Send notification for task due"""
        priority_messages = {
            'High': "🔴 High priority task is due!",
            'Medium': "🟡 Task is due today",
            'Low': "🟢 Task due reminder"
        }
        
        priority = task.get('priority', 'Medium')
        emoji = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(priority, '🟡')
        
        title = f"{emoji} Task Due: {task.get('title', 'Unknown Task')}"
        message = f"{priority_messages.get(priority, 'Task due reminder')}\n\n" \
                 f"Task: {task.get('title', 'Unknown')}\n" \
                 f"Due: {task.get('due_date', 'Today')}\n" \
                 f"Priority: {priority}"
        
        # High priority tasks get email notifications too
        send_email = priority == 'High'
        
        self.add_notification(
            title=title,
            message=message,
            notification_type="warning" if priority == 'High' else "info",
            desktop=True,
            email=send_email,
            mobile=send_email
        )
    
    def notify_task_overdue(self, task):
        """Send notification for overdue task"""
        title = f"⚠️ Overdue Task: {task.get('title', 'Unknown Task')}"
        message = f"This task is overdue!\n\n" \
                 f"Task: {task.get('title', 'Unknown')}\n" \
                 f"Was due: {task.get('due_date', 'Unknown')}\n" \
                 f"Priority: {task.get('priority', 'Medium')}"
        
        self.add_notification(
            title=title,
            message=message,
            notification_type="error",
            desktop=True,
            email=True,
            mobile=True
        )
    
    def notify_daily_summary(self, summary_data):
        """Send daily summary notification"""
        title = "📊 Daily Summary - NikAssistant"
        
        message = f"Good morning! Here's your daily summary:\n\n" \
                 f"📝 Tasks: {summary_data.get('total_tasks', 0)} total, " \
                 f"{summary_data.get('completed_tasks', 0)} completed\n" \
                 f"📅 Due Today: {summary_data.get('due_today', 0)} tasks\n" \
                 f"⚠️ Overdue: {summary_data.get('overdue', 0)} tasks\n" \
                 f"📒 Notes: {summary_data.get('total_notes', 0)} total\n\n" \
                 f"Have a productive day! 🚀"
        
        self.add_notification(
            title=title,
            message=message,
            notification_type="info",
            desktop=True,
            email=False,
            mobile=False
        )
    
    def notify_email_summary(self, important_emails):
        """Send notification about important emails"""
        if not important_emails:
            return
        
        title = f"📧 {len(important_emails)} Important Emails"
        
        email_list = []
        for email in important_emails[:3]:  # Show max 3 emails
            sender = email.get('sender', 'Unknown')
            subject = email.get('subject', 'No Subject')
            email_list.append(f"• {sender}: {subject}")
        
        message = "You have important emails:\n\n" + \
                 "\n".join(email_list)
        
        if len(important_emails) > 3:
            message += f"\n\n...and {len(important_emails) - 3} more emails"
        
        self.add_notification(
            title=title,
            message=message,
            notification_type="info",
            desktop=True,
            email=False,
            mobile=False
        )
    
    def notify_meeting_reminder(self, event):
        """Send meeting reminder notification"""
        title = f"📅 Meeting in 15 minutes: {event.get('summary', 'Meeting')}"
        
        message = f"Upcoming meeting reminder:\n\n" \
                 f"Event: {event.get('summary', 'Meeting')}\n" \
                 f"Time: {event.get('start_time', 'Unknown')}\n" \
                 f"Location: {event.get('location', 'Not specified')}"
        
        self.add_notification(
            title=title,
            message=message,
            notification_type="info",
            desktop=True,
            email=False,
            mobile=True
        )
    
    def notify_achievement(self, achievement_type, details):
        """Send achievement notification"""
        achievement_messages = {
            'tasks_completed': f"🎉 Congratulations! You've completed {details} tasks today!",
            'streak': f"🔥 Amazing! You're on a {details}-day productivity streak!",
            'weekly_goal': f"🎯 Fantastic! You've reached your weekly goal of {details} tasks!",
            'all_tasks_done': "✅ Awesome! All your tasks for today are complete!"
        }
        
        title = "🏆 Achievement Unlocked!"
        message = achievement_messages.get(achievement_type, "Great job!")
        
        self.add_notification(
            title=title,
            message=message,
            notification_type="success",
            desktop=True,
            email=False,
            mobile=False
        )
    
    def test_notifications(self):
        """Test all notification methods"""
        test_notifications = [
            {
                'title': "🧠 NikAssistant Test",
                'message': "Desktop notification test - if you see this, notifications are working!",
                'desktop': True,
                'email': False,
                'mobile': False
            },
            {
                'title': "📧 Email Test",
                'message': "Email notification test - check your inbox!",
                'desktop': False,
                'email': True,
                'mobile': False
            }
        ]
        
        for test_notif in test_notifications:
            self.add_notification(**test_notif)
        
        logger.info("Test notifications sent")

# Global instance
notifier = SmartNotifier()
