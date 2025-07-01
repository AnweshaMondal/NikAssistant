import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import json
import config
from backend.calendar_service import CalendarService

def render_calendar_view():
    """Render the calendar interface"""
    st.header("Calendar")
    
    # Initialize calendar service
    cal_service = CalendarService()
    
    # Calendar tabs
    tab1, tab2, tab3 = st.tabs(["Monthly View", "Upcoming Events", "Add Event"])
    
    with tab1:
        render_monthly_view(cal_service)
    
    with tab2:
        render_upcoming_events(cal_service)
        
    with tab3:
        render_add_event_form(cal_service)

def render_monthly_view(cal_service):
    """Render monthly calendar view"""
    st.subheader("Monthly Calendar")
    
    # Date selector
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_date = st.date_input("Select Month", datetime.now())
    
    # Get current month details
    year = selected_date.year
    month = selected_date.month
    
    # Create calendar
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    st.subheader(f"{month_name} {year}")
    
    # Get events for the month if service is available
    events = []
    if cal_service.is_available():
        try:
            start_date = datetime(year, month, 1)
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            events = cal_service.get_events_in_range(start_date, end_date)
        except Exception as e:
            st.warning(f"Could not fetch Google Calendar events: {e}")
    
    # Get tasks for the month
    tasks = get_tasks_for_month(year, month)
    
    # Render calendar grid
    render_calendar_grid(cal, events, tasks, year, month)

def render_calendar_grid(cal, events, tasks, year, month):
    """Render the calendar grid with events and tasks"""
    # Calendar header
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Create header
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"**{day}**")
    
    # Render calendar weeks
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")  # Empty cell for days not in current month
                else:
                    # Check if this day has events or tasks
                    day_str = f"{year}-{month:02d}-{day:02d}"
                    day_events = [e for e in events if day_str in e.get('start', {}).get('date', e.get('start', {}).get('dateTime', ''))]
                    day_tasks = [t for t in tasks if t.get('due_date') == day_str]
                    
                    # Day number
                    st.markdown(f"**{day}**")
                    
                    # Show events
                    for event in day_events[:2]:  # Show max 2 events
                        st.markdown(f"🗓️ {event.get('summary', 'Event')[:15]}...")
                    
                    # Show tasks
                    for task in day_tasks[:2]:  # Show max 2 tasks
                        priority_emoji = get_priority_emoji(task.get('priority', 'Medium'))
                        st.markdown(f"{priority_emoji} {task.get('title', 'Task')[:15]}...")
                    
                    # Show indicator if more items exist
                    total_items = len(day_events) + len(day_tasks)
                    if total_items > 4:
                        st.caption(f"+{total_items - 4} more")

def render_upcoming_events(cal_service):
    """Render upcoming events"""
    st.subheader("Upcoming Events")
    
    # Time range selector
    col1, col2 = st.columns(2)
    with col1:
        days_ahead = st.selectbox("Show events for", [7, 14, 30], index=0, format_func=lambda x: f"Next {x} days")
    
    # Get events
    events = []
    if cal_service.is_available():
        try:
            events = cal_service.get_upcoming_events(days=days_ahead, max_results=20)
        except Exception as e:
            st.error(f"Error fetching events: {e}")
    else:
        st.warning("Google Calendar not configured. Set up Google Calendar API in settings.")
    
    # Get upcoming tasks
    upcoming_tasks = get_upcoming_tasks(days_ahead)
    
    # Combine and sort by date
    all_items = []
    
    # Add events
    for event in events:
        start_time = event.get('start', {})
        date_str = start_time.get('date') or start_time.get('dateTime', '')
        if date_str:
            all_items.append({
                'type': 'event',
                'title': event.get('summary', 'Untitled Event'),
                'date': date_str,
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'data': event
            })
    
    # Add tasks
    for task in upcoming_tasks:
        all_items.append({
            'type': 'task',
            'title': task.get('title', 'Untitled Task'),
            'date': task.get('due_date', ''),
            'priority': task.get('priority', 'Medium'),
            'category': task.get('category', 'Other'),
            'data': task
        })
    
    # Sort by date
    all_items.sort(key=lambda x: x['date'])
    
    if not all_items:
        st.info("No upcoming events or tasks found.")
        return
    
    # Display items
    for item in all_items:
        render_calendar_item(item)

def render_calendar_item(item):
    """Render a single calendar item (event or task)"""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if item['type'] == 'event':
                st.markdown(f"🗓️ **{item['title']}**")
                if item.get('location'):
                    st.caption(f"📍 {item['location']}")
                if item.get('description'):
                    desc = item['description']
                    if len(desc) > 100:
                        desc = desc[:100] + "..."
                    st.caption(desc)
            else:  # task
                priority_emoji = get_priority_emoji(item.get('priority', 'Medium'))
                st.markdown(f"{priority_emoji} **{item['title']}**")
                st.caption(f"📂 {item.get('category', 'Other')} • Priority: {item.get('priority', 'Medium')}")
        
        with col2:
            # Format and display date
            try:
                if 'T' in item['date']:  # datetime
                    dt = datetime.fromisoformat(item['date'].replace('Z', '+00:00'))
                    st.caption(f"📅 {dt.strftime('%m/%d/%Y')}")
                    st.caption(f"⏰ {dt.strftime('%I:%M %p')}")
                else:  # date only
                    dt = datetime.strptime(item['date'], '%Y-%m-%d')
                    st.caption(f"📅 {dt.strftime('%m/%d/%Y')}")
            except:
                st.caption(f"📅 {item['date']}")
        
        with col3:
            if item['type'] == 'task':
                if st.button("Complete", key=f"complete_{item['data'].get('id')}"):
                    complete_task(item['data'].get('id'))
        
        st.divider()

def render_add_event_form(cal_service):
    """Render form to add new calendar event"""
    st.subheader("Add New Event")
    
    if not cal_service.is_available():
        st.warning("Google Calendar not configured. You can still create tasks with due dates.")
    
    with st.form("add_event_form"):
        title = st.text_input("Event Title")
        description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        with col1:
            event_date = st.date_input("Date")
            start_time = st.time_input("Start Time")
        
        with col2:
            end_date = st.date_input("End Date", value=event_date)
            end_time = st.time_input("End Time")
        
        location = st.text_input("Location (Optional)")
        
        col3, col4 = st.columns(2)
        with col3:
            create_task = st.checkbox("Also create as task")
        with col4:
            if create_task:
                task_priority = st.selectbox("Task Priority", ["Low", "Medium", "High"])
        
        submitted = st.form_submit_button("Create Event", type="primary")
        
        if submitted and title:
            # Create datetime objects
            start_datetime = datetime.combine(event_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            
            # Try to create calendar event
            event_created = False
            if cal_service.is_available():
                try:
                    event_created = cal_service.create_event(
                        title=title,
                        description=description,
                        start_time=start_datetime,
                        end_time=end_datetime,
                        location=location
                    )
                    if event_created:
                        st.success("Event created successfully in Google Calendar!")
                except Exception as e:
                    st.error(f"Failed to create calendar event: {e}")
            
            # Create task if requested
            if create_task:
                task_created = create_task_from_event(
                    title, description, event_date.strftime('%Y-%m-%d'), 
                    task_priority, location
                )
                if task_created:
                    st.success("Task created successfully!")
            
            if event_created or create_task:
                st.rerun()

def get_tasks_for_month(year, month):
    """Get tasks for a specific month"""
    tasks = st.session_state.tasks
    month_str = f"{year}-{month:02d}"
    return [task for task in tasks if task.get('due_date', '').startswith(month_str)]

def get_upcoming_tasks(days):
    """Get tasks due in the next N days"""
    tasks = st.session_state.tasks
    today = datetime.now().date()
    future_date = today + timedelta(days=days)
    
    upcoming = []
    for task in tasks:
        if task.get('completed', False):
            continue
        
        due_date_str = task.get('due_date')
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                if today <= due_date <= future_date:
                    upcoming.append(task)
            except:
                continue
    
    return upcoming

def get_priority_emoji(priority):
    """Get emoji for task priority"""
    return {
        'High': '🔴',
        'Medium': '🟡',
        'Low': '🟢'
    }.get(priority, '🟡')

def complete_task(task_id):
    """Mark a task as completed"""
    for task in st.session_state.tasks:
        if task.get('id') == task_id:
            task['completed'] = True
            task['completed_at'] = datetime.now().isoformat()
            st.success("Task completed!")
            st.rerun()
            break

def create_task_from_event(title, description, due_date, priority, location):
    """Create a task from calendar event"""
    import uuid
    
    new_task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "due_date": due_date,
        "priority": priority,
        "category": "Events",
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "location": location
    }
    
    st.session_state.tasks.append(new_task)
    return True
