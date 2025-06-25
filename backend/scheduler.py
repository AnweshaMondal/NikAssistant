import json
import uuid
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
import config
from backend.email_service import EmailService
from backend.notification_service import NotificationService

logger = logging.getLogger("nikassistant.scheduler")

class TaskScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.email_service = EmailService()
        self.notification_service = NotificationService()
        self.load_tasks()
        
    def start(self):
        """Start the background scheduler"""
        try:
            self.scheduler.start()
            logger.info("Scheduler started successfully")
            # Schedule daily summary for 9 AM
            self.scheduler.add_job(
                self.send_daily_summary,
                IntervalTrigger(days=1, start_date=self._get_next_time(9, 0)),
                id='daily_summary'
            )
            # Check for overdue tasks every hour
            self.scheduler.add_job(
                self.check_overdue_tasks,
                IntervalTrigger(hours=1),
                id='overdue_check'
            )
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    def stop(self):
        """Stop the background scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def load_tasks(self):
        """Load tasks from JSON and schedule reminders"""
        try:
            with open(config.TASKS_FILE, 'r') as file:
                data = json.load(file)
                tasks = data.get('tasks', [])
                
                # Clear existing task reminders
                for job in self.scheduler.get_jobs():
                    if job.id.startswith('task_'):
                        job.remove()
                
                # Schedule reminders for upcoming tasks
                for task in tasks:
                    if task.get('status') != 'Completed' and task.get('due_date') and task.get('reminder'):
                        self.schedule_task_reminder(task)
                        
            logger.info(f"Loaded and scheduled {len(tasks)} tasks")
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
    
    def schedule_task_reminder(self, task):
        """Schedule a reminder for a specific task"""
        task_id = task.get('id', str(uuid.uuid4()))
        due_date_str = task.get('due_date')
        reminder_minutes = int(task.get('reminder', 30))
        
        if not due_date_str:
            return
        
        try:
            due_date = datetime.fromisoformat(due_date_str)
            reminder_time = due_date - timedelta(minutes=reminder_minutes)
            
            # Only schedule if the reminder time is in the future
            if reminder_time > datetime.now():
                self.scheduler.add_job(
                    self.send_task_reminder,
                    DateTrigger(run_date=reminder_time),
                    args=[task],
                    id=f"task_{task_id}"
                )
                logger.info(f"Scheduled reminder for task '{task.get('title')}' at {reminder_time}")
        except Exception as e:
            logger.error(f"Error scheduling reminder for task {task_id}: {e}")
    
    def send_task_reminder(self, task):
        """Send a reminder notification for a task"""
        try:
            task_title = task.get('title', 'Untitled Task')
            due_date_str = task.get('due_date', 'Unknown')
            due_date = datetime.fromisoformat(due_date_str)
            
            # Format the time nicely
            due_time = due_date.strftime('%I:%M %p')
            
            # Send desktop notification
            message = f"Task '{task_title}' is due at {due_time}"
            self.notification_service.send_notification(
                title="Task Reminder",
                message=message
            )
            
            # Send email reminder if email is enabled for this task
            if task.get('email_reminder', False) and config.EMAIL_USER:
                self.email_service.send_email(
                    subject=f"Reminder: {task_title}",
                    body=f"""
                    <h2>Task Reminder</h2>
                    <p>Your task <strong>{task_title}</strong> is due at {due_time}.</p>
                    <p>Priority: {task.get('priority', 'Medium')}</p>
                    <p>Category: {task.get('category', 'General')}</p>
                    <p>Description: {task.get('description', '')}</p>
                    <hr>
                    <p>This is an automated reminder from NikAssistant.</p>
                    """
                )
                logger.info(f"Sent email reminder for task '{task_title}'")
        except Exception as e:
            logger.error(f"Error sending task reminder: {e}")
    
    def check_overdue_tasks(self):
        """Check for overdue tasks and send notifications"""
        try:
            with open(config.TASKS_FILE, 'r') as file:
                data = json.load(file)
                tasks = data.get('tasks', [])
                now = datetime.now()
                
                overdue_tasks = []
                for task in tasks:
                    if (
                        task.get('status') != 'Completed' and 
                        task.get('due_date') and 
                        datetime.fromisoformat(task.get('due_date')) < now
                    ):
                        overdue_tasks.append(task)
                
                if overdue_tasks:
                    titles = [t.get('title', 'Untitled') for t in overdue_tasks]
                    titles_str = "\n".join([f"- {t}" for t in titles])
                    self.notification_service.send_notification(
                        title=f"You have {len(overdue_tasks)} overdue tasks",
                        message=f"Overdue tasks:\n{titles_str}"
                    )
                    logger.info(f"Sent notification for {len(overdue_tasks)} overdue tasks")
        except Exception as e:
            logger.error(f"Error checking overdue tasks: {e}")
    
    def send_daily_summary(self):
        """Send a daily summary of tasks"""
        try:
            with open(config.TASKS_FILE, 'r') as file:
                data = json.load(file)
                tasks = data.get('tasks', [])
                today = datetime.now().date()
                tomorrow = today + timedelta(days=1)
                
                today_tasks = []
                tomorrow_tasks = []
                
                for task in tasks:
                    if task.get('status') != 'Completed' and task.get('due_date'):
                        due_date = datetime.fromisoformat(task.get('due_date')).date()
                        if due_date == today:
                            today_tasks.append(task)
                        elif due_date == tomorrow:
                            tomorrow_tasks.append(task)
                
                message_parts = []
                
                if today_tasks:
                    titles = [t.get('title', 'Untitled') for t in today_tasks]
                    titles_str = "\n".join([f"- {t}" for t in titles])
                    message_parts.append(f"Today's tasks ({len(today_tasks)}):\n{titles_str}")
                
                if tomorrow_tasks:
                    titles = [t.get('title', 'Untitled') for t in tomorrow_tasks]
                    titles_str = "\n".join([f"- {t}" for t in titles])
                    message_parts.append(f"Tomorrow's tasks ({len(tomorrow_tasks)}):\n{titles_str}")
                
                if message_parts:
                    message = "\n\n".join(message_parts)
                    self.notification_service.send_notification(
                        title="Daily Task Summary",
                        message=message
                    )
                    
                    # Send email summary
                    if config.EMAIL_USER:
                        self.email_service.send_email(
                            subject="NikAssistant Daily Task Summary",
                            body=f"""
                            <h2>Daily Task Summary</h2>
                            <h3>Today's Tasks:</h3>
                            <ul>
                                {"".join(f"<li><strong>{t.get('title')}</strong> ({t.get('priority', 'Medium')})</li>" for t in today_tasks)}
                            </ul>
                            <h3>Tomorrow's Tasks:</h3>
                            <ul>
                                {"".join(f"<li><strong>{t.get('title')}</strong> ({t.get('priority', 'Medium')})</li>" for t in tomorrow_tasks)}
                            </ul>
                            <hr>
                            <p>This is an automated summary from NikAssistant.</p>
                            """
                        )
                    logger.info("Sent daily task summary")
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")

    def _get_next_time(self, hour, minute):
        """Get the next occurrence of a specific time"""
        now = datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        return target_time
