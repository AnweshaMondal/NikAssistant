import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
STATIC_DIR = BASE_DIR / "static"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG") == "True" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("nikassistant")

# Data files
TASKS_FILE = DATA_DIR / "tasks.json"
NOTES_FILE = DATA_DIR / "notes.json"
CALENDAR_FILE = DATA_DIR / "calendar.json"

# Initialize default data files if they don't exist
def init_data_files():
    # Tasks JSON structure
    if not TASKS_FILE.exists():
        with open(TASKS_FILE, 'w') as f:
            f.write('{"tasks": []}')
    
    # Notes JSON structure
    if not NOTES_FILE.exists():
        with open(NOTES_FILE, 'w') as f:
            f.write('{"notes": []}')
    
    # Calendar cache structure
    if not CALENDAR_FILE.exists():
        with open(CALENDAR_FILE, 'w') as f:
            f.write('{"events": []}')

# Email configuration
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Google Calendar API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# Firebase (Optional)
FIREBASE_SERVICE_ACCOUNT_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")

# App configuration
APP_PORT = int(os.getenv("APP_PORT", 8501))
DEBUG = os.getenv("DEBUG", "False") == "True"

# UI Configuration
APP_TITLE = "🧠 NikAssistant"
APP_SUBTITLE = "Your Personal Productivity Companion"
APP_ICON = str(STATIC_DIR / "icons" / "app_icon.png")

# Theme colors
THEME = {
    "primary": "#FF6B6B",
    "secondary": "#4ECDC4",
    "background": "#F7FFF7",
    "text": "#1A535C",
    "accent": "#FFE66D"
}

# Task priority colors
PRIORITY_COLORS = {
    "High": "#FF6B6B",
    "Medium": "#FFE66D",
    "Low": "#4ECDC4"
}

# Task categories
TASK_CATEGORIES = [
    "Work",
    "Personal",
    "Health",
    "Finance",
    "Shopping",
    "Education",
    "Other"
]

# Note categories
NOTE_CATEGORIES = [
    "General",
    "Ideas",
    "Work",
    "Personal",
    "Reminder",
    "Other"
]

# Pages
PAGES = {
    "dashboard": "📊 Dashboard",
    "tasks": "📝 Tasks",
    "notes": "🗒️ Notes",
    "calendar": "📅 Calendar",
    "notifications": "🔔 Notifications",
    "settings": "⚙️ Settings"
}

# Initialize data files on import
init_data_files()
