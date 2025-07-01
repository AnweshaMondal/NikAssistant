import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import config
import plotly.express as px

def render_dashboard():
    """Render the main dashboard screen"""
    st.header("Dashboard")
    
    # Layout for dashboard widgets
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_tasks_summary()
        render_activity_chart()
    
    with col2:
        render_quick_add()
        render_upcoming_events()
        render_quick_notes()
        render_notes_summary()

def render_tasks_summary():
    """Render task summary section"""
    st.subheader("Tasks Summary")
    
    # Get tasks data
    tasks = st.session_state.tasks
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.get('completed', False))
    due_today = sum(1 for task in tasks 
                   if task.get('due_date') == datetime.now().strftime("%Y-%m-%d") 
                   and not task.get('completed', False))
    overdue = sum(1 for task in tasks 
                 if task.get('due_date') and 
                 task.get('due_date') < datetime.now().strftime("%Y-%m-%d") 
                 and not task.get('completed', False))
    
    # Display metrics
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric("Total", total_tasks)
    with metrics_col2:
        st.metric("Completed", completed_tasks)
    with metrics_col3:
        st.metric("Due Today", due_today)
    with metrics_col4:
        st.metric("Overdue", overdue, delta=overdue, delta_color="inverse")
    
    # Show recent tasks
    if tasks:
        st.subheader("Recent Tasks")
        
        # Filter and sort tasks
        active_tasks = [task for task in tasks if not task.get('completed', False)]
        recent_tasks = sorted(
            active_tasks, 
            key=lambda x: x.get('due_date', '9999-12-31')
        )[:5]
        
        # Convert to DataFrame for display
        if recent_tasks:
            df = pd.DataFrame(recent_tasks)
            if 'due_date' in df.columns:
                df['due_date'] = pd.to_datetime(df['due_date']).dt.strftime('%b %d')
            
            cols_to_show = ['title', 'due_date', 'priority']
            cols = [col for col in cols_to_show if col in df.columns]
            
            st.dataframe(df[cols], use_container_width=True, hide_index=True)
        else:
            st.info("No active tasks")
    else:
        st.info("No tasks found. Add some tasks to get started!")

def render_activity_chart():
    """Render activity chart"""
    tasks = st.session_state.tasks
    
    if not tasks:
        return
    
    # Prepare data for chart
    date_counts = {}
    today = datetime.now().date()
    
    # Initialize last 14 days with zero counts
    for i in range(-7, 7):
        date_key = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        date_counts[date_key] = 0
    
    # Count tasks by date
    for task in tasks:
        if 'due_date' in task:
            date_key = task['due_date']
            if date_key in date_counts:
                date_counts[date_key] += 1
    
    # Convert to DataFrame for Plotly
    chart_data = pd.DataFrame({
        'Date': list(date_counts.keys()),
        'Tasks': list(date_counts.values())
    })
    
    # Convert dates to datetime for sorting
    chart_data['Date'] = pd.to_datetime(chart_data['Date'])
    chart_data = chart_data.sort_values('Date')
    
    # Format dates for display
    chart_data['Date'] = chart_data['Date'].dt.strftime('%b %d')
    
    # Create chart
    fig = px.bar(
        chart_data, 
        x='Date', 
        y='Tasks',
        title="Task Distribution",
        color='Tasks',
        color_continuous_scale=['#90CAF9', '#1976D2', '#0D47A1']
    )
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title=None,
        yaxis_title=None
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_quick_add():
    """Render quick add task widget"""
    st.subheader("Quick Add")
    
    with st.form("quick_add_form", clear_on_submit=True):
        task_title = st.text_input("New Task")
        
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due Date", datetime.now())
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        submitted = st.form_submit_button("Add Task")
        
        if submitted and task_title:
            # Create new task
            new_task = {
                "id": len(st.session_state.tasks) + 1,
                "title": task_title,
                "description": "",
                "due_date": due_date.strftime("%Y-%m-%d"),
                "priority": priority,
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to session state
            st.session_state.tasks.append(new_task)
            
            # Show success message
            st.success(f"Added: {task_title}")

def render_upcoming_events():
    """Render upcoming calendar events"""
    st.subheader("Upcoming Events")
    
    # Try to import calendar service
    try:
        from backend.calendar_service import CalendarService
        calendar = CalendarService()
        
        if calendar.is_available():
            events = calendar.get_upcoming_events(days=7, max_results=5)
            if events:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    
                    with st.container():
                        st.markdown(f"**{event['summary']}**")
                        st.caption(f"{start_dt.strftime('%b %d, %H:%M')}")
            else:
                st.info("No upcoming events")
        else:
            st.info("Calendar not configured")
            
    except Exception as e:
        st.warning(f"Calendar service unavailable")

def render_quick_notes():
    """Render quick notes section"""
    st.subheader("Quick Notes")
    
    note_text = st.text_area("Add a note", height=100)
    
    if st.button("Save Note"):
        if note_text:
            # Create new note
            new_note = {
                "id": len(st.session_state.notes) + 1,
                "content": note_text,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to session state
            st.session_state.notes.append(new_note)
            
            # Show success message
            st.success("Note saved!")
    
    # Display recent notes
    if st.session_state.notes:
        st.caption("Recent Notes")
        
        for note in sorted(st.session_state.notes, 
                         key=lambda x: x.get('created_at', ''), 
                         reverse=True)[:3]:
            with st.expander(note.get('content', '')[:50] + "..."):
                st.write(note.get('content', ''))
                st.caption(f"Created: {note.get('created_at', '')}")

def render_notes_summary():
    """Render notes summary widget"""
    st.subheader("📒 Notes Summary")
    
    # Get notes data
    notes = st.session_state.notes
    
    if not notes:
        st.info("No notes yet. Create your first note!")
        return
    
    # Calculate statistics
    total_notes = len(notes)
    private_notes = sum(1 for note in notes if note.get('is_private', False))
    categories = set(note.get('category', 'General') for note in notes)
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Notes", total_notes)
    with col2:
        st.metric("Categories", len(categories))
    
    # Show recent notes
    st.write("**Recent Notes:**")
    recent_notes = sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
    
    for note in recent_notes:
        title = note.get('title', 'Untitled')
        if len(title) > 30:
            title = title[:30] + "..."
        
        category = note.get('category', 'General')
        privacy = "🔒" if note.get('is_private', False) else "🔓"
        
        st.write(f"{privacy} **{title}** ({category})")
