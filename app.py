import streamlit as st
import os
import config
import json
from datetime import datetime, timedelta
from ui.dashboard import render_dashboard
from ui.task_panel import render_task_panel
from backend.scheduler import TaskScheduler
import logging

# Initialize logging
logger = logging.getLogger("nikassistant.app")

# Initialize data files
config.init_data_files()

# Application title and configuration
st.set_page_config(
    page_title="NikAssistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Customization
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        background-color: #f0f2f6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8df5;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

def load_data(file_path):
    """Load data from JSON file"""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None

def save_data(data, file_path):
    """Save data to JSON file"""
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

def init_session_state():
    """Initialize session state variables"""
    if "tasks" not in st.session_state:
        task_data = load_data(config.TASKS_FILE)
        st.session_state.tasks = task_data.get("tasks", []) if task_data else []
        
    if "notes" not in st.session_state:
        notes_data = load_data(config.NOTES_FILE)
        st.session_state.notes = notes_data.get("notes", []) if notes_data else []
        
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Dashboard"
        
    if "scheduler" not in st.session_state:
        st.session_state.scheduler = TaskScheduler()
        st.session_state.scheduler.start()

def main():
    """Main application entry point"""
    st.title("🧠 NikAssistant")
    
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    selected = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Tasks", "Notes", "Calendar", "Settings"],
        key="sidebar_selection"
    )
    
    st.session_state.active_tab = selected
    
    # Main content area
    if selected == "Dashboard":
        render_dashboard()
    elif selected == "Tasks":
        render_task_panel()
    elif selected == "Notes":
        st.header("Notes")
        st.info("Notes feature is under development")
    elif selected == "Calendar":
        st.header("Calendar")
        st.info("Calendar integration is under development")
    elif selected == "Settings":
        st.header("Settings")
        st.info("Settings page is under development")
    
    # Save data on app state change
    save_data({"tasks": st.session_state.tasks}, config.TASKS_FILE)
    save_data({"notes": st.session_state.notes}, config.NOTES_FILE)

if __name__ == "__main__":
    main()
