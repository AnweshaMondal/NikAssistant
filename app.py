import streamlit as st
import os
import config
import json
from datetime import datetime, timedelta
from ui.dashboard import render_dashboard
from ui.task_panel import render_task_panel
from ui.notes_panel import render_notes_panel
from ui.calendar_view import render_calendar_view
from backend.scheduler import TaskScheduler
from utils.notifier import notifier
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
st.markdown(
    """
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
    html, body, .main {
        background-color: #ffffff !important; /* Force background color to white */
    }
    </style>
""",
    unsafe_allow_html=True,
)


def load_data(file_path):
    """Load data from JSON file"""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return None


def save_data(data, file_path):
    """Save data to JSON file"""
    try:
        with open(file_path, "w") as file:
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

    if "notifier" not in st.session_state:
        st.session_state.notifier = notifier
        st.session_state.notifier.start()


def render_settings_page():
    """Render the settings page"""
    st.header("⚙️ Settings")

    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["General", "Notifications", "Email", "Advanced"])

    with tab1:
        render_general_settings()

    with tab2:
        render_notification_settings()

    with tab3:
        render_email_settings()

    with tab4:
        render_advanced_settings()


def render_general_settings():
    """Render general settings"""
    st.subheader("General Settings")

    # Theme settings
    st.write("**Appearance**")
    col1, col2 = st.columns(2)

    with col1:
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
        st.session_state.theme = theme

    with col2:
        language = st.selectbox("Language", ["English", "Spanish", "French"], index=0)
        st.session_state.language = language

    # Default settings
    st.write("**Default Task Settings**")
    col3, col4 = st.columns(2)

    with col3:
        default_priority = st.selectbox(
            "Default Priority", ["Low", "Medium", "High"], index=1
        )
        st.session_state.default_priority = default_priority

    with col4:
        default_category = st.selectbox(
            "Default Category", config.TASK_CATEGORIES, index=0
        )
        st.session_state.default_category = default_category

    # Time zone
    timezone = st.selectbox(
        "Timezone",
        ["UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific"],
        index=0,
    )
    st.session_state.timezone = timezone

    if st.button("Save General Settings"):
        st.success("General settings saved!")


def render_notification_settings():
    """Render notification settings"""
    st.subheader("Notification Settings")

    # Desktop notifications
    st.write("**Desktop Notifications**")
    desktop_enabled = st.checkbox("Enable desktop notifications", value=True)

    if desktop_enabled:
        col1, col2 = st.columns(2)
        with col1:
            notification_sound = st.checkbox("Play notification sound", value=True)
        with col2:
            notification_timeout = st.slider(
                "Notification timeout (seconds)", 5, 30, 10
            )

    # Email notifications
    st.write("**Email Notifications**")
    email_enabled = st.checkbox("Enable email notifications", value=False)

    if email_enabled:
        daily_summary = st.checkbox("Daily summary email", value=True)
        if daily_summary:
            summary_time = st.time_input(
                "Daily summary time", value=datetime.strptime("09:00", "%H:%M").time()
            )

    # Task reminders
    st.write("**Task Reminders**")
    reminder_enabled = st.checkbox("Enable task reminders", value=True)

    if reminder_enabled:
        col3, col4 = st.columns(2)
        with col3:
            reminder_advance = st.slider("Remind me (minutes before due)", 15, 120, 30)
        with col4:
            overdue_reminders = st.checkbox("Overdue task reminders", value=True)

    # Test notifications
    st.write("**Test Notifications**")
    col5, col6 = st.columns(2)

    with col5:
        if st.button("Test Desktop Notification"):
            st.session_state.notifier.add_notification(
                "🧠 Test Notification",
                "This is a test desktop notification from NikAssistant!",
                desktop=True,
            )
            st.success("Test notification sent!")

    with col6:
        if st.button("Test Email Notification"):
            if config.EMAIL_USER and config.EMAIL_PASS:
                st.session_state.notifier.add_notification(
                    "📧 Test Email",
                    "This is a test email notification from NikAssistant!",
                    email=True,
                )
                st.success("Test email queued!")
            else:
                st.error("Email not configured. Please set up email in the Email tab.")

    if st.button("Save Notification Settings"):
        st.success("Notification settings saved!")


def render_email_settings():
    """Render email settings"""
    st.subheader("Email Configuration")

    st.warning(
        "⚠️ Email configuration requires editing the .env file. The settings below are for reference only."
    )

    # Display current email configuration
    st.write("**Current Configuration**")

    if config.EMAIL_USER:
        st.success(f"✅ Email configured: {config.EMAIL_USER}")
    else:
        st.error("❌ Email not configured")

    # Instructions
    st.write("**Setup Instructions**")

    with st.expander("How to configure Gmail"):
        st.markdown(
            """
        **Step 1: Enable 2-Factor Authentication**
        1. Go to [Google Account Settings](https://myaccount.google.com/)
        2. Select "Security" → "2-Step Verification"
        3. Follow the setup process
        
        **Step 2: Generate App Password**
        1. In Google Account Settings, go to "Security"
        2. Under "2-Step Verification", click "App passwords"
        3. Select "Mail" and your device
        4. Copy the generated 16-character password
        
        **Step 3: Update .env file**
        ```
        EMAIL_USER=your_email@gmail.com
        EMAIL_PASS=your_16_character_app_password
        ```
        
        **Step 4: Restart the application**
        """
        )

    # Email test
    st.write("**Email Test**")
    if config.EMAIL_USER and config.EMAIL_PASS:
        if st.button("Send Test Email"):
            try:
                from backend.email_service import EmailService

                email_service = EmailService()
                success = email_service.send_email(
                    subject="NikAssistant Test Email",
                    body="<h2>🧠 NikAssistant Test</h2><p>If you receive this email, your email configuration is working correctly!</p>",
                )
                if success:
                    st.success("Test email sent successfully!")
                else:
                    st.error(
                        "Failed to send test email. Please check your configuration."
                    )
            except Exception as e:
                st.error(f"Email test failed: {e}")
    else:
        st.info("Configure email settings to test email functionality.")


def render_advanced_settings():
    """Render advanced settings"""
    st.subheader("Advanced Settings")

    # Data management
    st.write("**Data Management**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Export Data"):
            export_data()

    with col2:
        uploaded_file = st.file_uploader("Import Data", type=["json"])
        if uploaded_file and st.button("Import"):
            import_data(uploaded_file)

    # System information
    st.write("**System Information**")

    info_data = {
        "Tasks": len(st.session_state.tasks),
        "Notes": len(st.session_state.notes),
        "Data Directory": str(config.DATA_DIR),
        "Logs Directory": str(config.LOGS_DIR),
        "Email Configured": "Yes" if config.EMAIL_USER else "No",
        "Calendar Configured": "Yes" if config.GOOGLE_API_KEY else "No",
    }

    for key, value in info_data.items():
        st.write(f"**{key}:** {value}")

    # Maintenance
    st.write("**Maintenance**")
    col3, col4 = st.columns(2)

    with col3:
        if st.button("Clear Completed Tasks"):
            clear_completed_tasks()

    with col4:
        if st.button("Reset All Data", type="secondary"):
            if st.checkbox("I understand this will delete all data"):
                reset_all_data()

    # Debug information
    if config.DEBUG:
        st.write("**Debug Information**")
        st.json(
            {
                "Session State Keys": list(st.session_state.keys()),
                "Config Values": {
                    "DEBUG": config.DEBUG,
                    "APP_PORT": config.APP_PORT,
                    "DATA_DIR": str(config.DATA_DIR),
                },
            }
        )


def export_data():
    """Export all application data"""
    import json
    from datetime import datetime

    export_data = {
        "export_date": datetime.now().isoformat(),
        "tasks": st.session_state.tasks,
        "notes": st.session_state.notes,
        "version": "1.0",
    }

    export_json = json.dumps(export_data, indent=2)
    st.download_button(
        label="Download Data",
        data=export_json,
        file_name=f"nikassistant_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
    )
    st.success("Data export ready for download!")


def import_data(uploaded_file):
    """Import application data"""
    try:
        import json

        data = json.load(uploaded_file)

        if "tasks" in data:
            st.session_state.tasks = data["tasks"]

        if "notes" in data:
            st.session_state.notes = data["notes"]

        st.success("Data imported successfully!")
        st.rerun()

    except Exception as e:
        st.error(f"Import failed: {e}")


def clear_completed_tasks():
    """Clear all completed tasks"""
    before_count = len(st.session_state.tasks)
    st.session_state.tasks = [
        task for task in st.session_state.tasks if not task.get("completed", False)
    ]
    after_count = len(st.session_state.tasks)

    st.success(f"Cleared {before_count - after_count} completed tasks!")
    st.rerun()


def reset_all_data():
    """Reset all application data"""
    st.session_state.tasks = []
    st.session_state.notes = []
    st.success("All data has been reset!")
    st.rerun()


def main():
    """Main application entry point"""
    st.title("🧠 NikAssistant")

    # Initialize session state
    init_session_state()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    selected = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Tasks", "Notes", "Calendar", "Settings", "Widgets"],
        key="sidebar_selection",
    )

    st.session_state.active_tab = selected

    # Main content area
    if selected == "Dashboard":
        render_dashboard()
    elif selected == "Tasks":
        render_task_panel()
    elif selected == "Notes":
        render_notes_panel()
    elif selected == "Calendar":
        render_calendar_view()
    elif selected == "Settings":
        render_settings_page()
    elif selected == "Widgets":
        from ui.widgets_panel import render_widgets_panel

        render_widgets_panel()

    # Save data on app state change
    save_data({"tasks": st.session_state.tasks}, config.TASKS_FILE)
    save_data({"notes": st.session_state.notes}, config.NOTES_FILE)


if __name__ == "__main__":
    main()
