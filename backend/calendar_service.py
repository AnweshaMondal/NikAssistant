import os
import logging
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config

logger = logging.getLogger("nikassistant.calendar")

class CalendarService:
    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.service = self._authenticate_google()
        self.cache_file = config.CALENDAR_FILE

    def _authenticate_google(self):
        """Authenticate with Google Calendar API"""
        credentials_file = os.getenv("GOOGLE_API_KEY")
        
        if not credentials_file or not os.path.exists(credentials_file):
            logger.warning("Google Calendar credentials not found")
            return None
            
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            service = build('calendar', 'v3', credentials=credentials)
            logger.info("Successfully authenticated with Google Calendar API")
            return service
        except Exception as e:
            logger.error(f"Google Calendar authentication failed: {e}")
            return None
    
    def is_available(self):
        """Check if Google Calendar service is available"""
        return self.service is not None
        
    def get_upcoming_events(self, days=7, max_results=10):
        """
        Get upcoming calendar events
        
        Args:
            days (int): Number of days to look ahead
            max_results (int): Maximum number of events to return
            
        Returns:
            list: List of upcoming events
        """
        if not self.service:
            logger.warning("Calendar service not available")
            return self._get_cached_events()
            
        try:
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            future = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                timeMax=future,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Cache events for offline access
            self._cache_events(events)
            
            return events
        except HttpError as e:
            logger.error(f"Error fetching calendar events: {e}")
            return self._get_cached_events()
    
    def add_event(self, summary, start_time, end_time, description="", location=""):
        """
        Add event to Google Calendar
        
        Args:
            summary (str): Event title/summary
            start_time (datetime): Event start time
            end_time (datetime): Event end time
            description (str): Event description
            location (str): Event location
            
        Returns:
            dict: Created event or None if failed
        """
        if not self.service:
            logger.warning("Calendar service not available")
            return None
            
        try:
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': True
                },
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            logger.info(f"Event created: {created_event.get('htmlLink')}")
            return created_event
        except HttpError as e:
            logger.error(f"Error creating calendar event: {e}")
            return None
    
    def _cache_events(self, events):
        """Cache events to local file"""
        try:
            with open(self.cache_file, 'w') as file:
                json.dump({'events': events, 'cached_at': datetime.datetime.now().isoformat()}, file)
        except Exception as e:
            logger.error(f"Error caching events: {e}")
    
    def _get_cached_events(self):
        """Get events from local cache"""
        try:
            with open(self.cache_file, 'r') as file:
                cache = json.load(file)
                return cache.get('events', [])
        except Exception as e:
            logger.error(f"Error reading cached events: {e}")
            return []
    
    def create_event(self, event_data):
        """
        Create a new calendar event
        
        Args:
            event_data (dict): Event data with summary, description, start, end
            
        Returns:
            bool: Success status
        """
        if not self.service:
            logger.warning("Google Calendar service not available")
            return False
        
        try:
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_data
            ).execute()
            
            logger.info(f"Event created successfully: {created_event.get('id')}")
            return True
            
        except HttpError as e:
            logger.error(f"Error creating calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating event: {e}")
            return False
    
    def update_event(self, event_id, event_data):
        """
        Update an existing calendar event
        
        Args:
            event_id (str): Event ID to update
            event_data (dict): Updated event data
            
        Returns:
            bool: Success status
        """
        if not self.service:
            logger.warning("Google Calendar service not available")
            return False
        
        try:
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            logger.info(f"Event updated successfully: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Error updating calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating event: {e}")
            return False
    
    def delete_event(self, event_id):
        """
        Delete a calendar event
        
        Args:
            event_id (str): Event ID to delete
            
        Returns:
            bool: Success status
        """
        if not self.service:
            logger.warning("Google Calendar service not available")
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Event deleted successfully: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Error deleting calendar event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting event: {e}")
            return False
