import json
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("nikassistant.utils")

def load_json_file(file_path):
    """
    Load data from a JSON file
    
    Args:
        file_path (str): Path to JSON file
        
    Returns:
        dict: Loaded JSON data or empty dict if file not found
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            logger.warning(f"File not found: {file_path}")
            return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return {}
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return {}

def save_json_file(file_path, data):
    """
    Save data to a JSON file
    
    Args:
        file_path (str): Path to JSON file
        data (dict): Data to save
        
    Returns:
        bool: Success status
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving to {file_path}: {e}")
        return False

def format_date(date_str, format_str="%Y-%m-%d", output_format="%b %d, %Y"):
    """
    Format a date string
    
    Args:
        date_str (str): Date string to format
        format_str (str): Input date format
        output_format (str): Output date format
        
    Returns:
        str: Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, format_str)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_str
    except Exception as e:
        logger.error(f"Date formatting error: {e}")
        return date_str

def get_relative_date(date_str, format_str="%Y-%m-%d"):
    """
    Get a relative date description (e.g., "Today", "Tomorrow", "Yesterday")
    
    Args:
        date_str (str): Date string
        format_str (str): Date format
        
    Returns:
        str: Relative date description
    """
    try:
        date_obj = datetime.strptime(date_str, format_str).date()
        today = datetime.now().date()
        
        delta = (date_obj - today).days
        
        if delta == 0:
            return "Today"
        elif delta == 1:
            return "Tomorrow"
        elif delta == -1:
            return "Yesterday"
        elif delta > 1 and delta < 7:
            return f"In {delta} days"
        elif delta < 0 and delta > -7:
            return f"{abs(delta)} days ago"
        else:
            return date_obj.strftime("%b %d, %Y")
    except Exception as e:
        logger.error(f"Error getting relative date: {e}")
        return date_str

def generate_id():
    """
    Generate a simple unique ID based on timestamp
    
    Returns:
        str: Unique ID
    """
    import uuid
    return str(uuid.uuid4())[:8]
