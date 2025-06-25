import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import config

def render_task_panel():
    """Render the task management panel"""
    st.header("Task Manager")
    
    # Task tabs
    tab1, tab2, tab3 = st.tabs(["All Tasks", "Today", "Completed"])
    
    with tab1:
        render_all_tasks()
    
    with tab2:
        render_today_tasks()
        
    with tab3:
        render_completed_tasks()

def render_all_tasks():
    """Render all tasks view"""
    # Add new task form
    with st.expander("Add New Task", expanded=False):
        add_task_form()
    
    # Get tasks
    tasks = st.session_state.tasks
    
    if not tasks:
        st.info("No tasks found. Add some tasks to get started!")
        return
    
    # Filter for active tasks
    active_tasks = [task for task in tasks if not task.get('completed', False)]
    
    if not active_tasks:
        st.success("No active tasks! All caught up.")
        return
    
    # Group by priority
    high_priority = [t for t in active_tasks if t.get('priority') == 'High']
    medium_priority = [t for t in active_tasks if t.get('priority') == 'Medium']
    low_priority = [t for t in active_tasks if t.get('priority') == 'Low']
    
    # Render priority sections
    if high_priority:
        st.subheader("High Priority")
        render_task_list(high_priority)
    
    if medium_priority:
        st.subheader("Medium Priority")
        render_task_list(medium_priority)
    
    if low_priority:
        st.subheader("Low Priority")
        render_task_list(low_priority)

def render_today_tasks():
    """Render tasks due today"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get tasks
    tasks = st.session_state.tasks
    
    # Filter for today's tasks that are not completed
    today_tasks = [
        task for task in tasks 
        if task.get('due_date') == today and not task.get('completed', False)
    ]
    
    if today_tasks:
        render_task_list(today_tasks)
    else:
        st.success("No tasks due today!")

def render_completed_tasks():
    """Render completed tasks"""
    # Get tasks
    tasks = st.session_state.tasks
    
    # Filter for completed tasks
    completed_tasks = [task for task in tasks if task.get('completed', True)]
    
    if completed_tasks:
        # Sort by completion date if available
        completed_tasks.sort(
            key=lambda x: x.get('completed_at', x.get('created_at', '')), 
            reverse=True
        )
        
        render_task_list(completed_tasks, show_completed=True)
    else:
        st.info("No completed tasks yet!")

def render_task_list(tasks, show_completed=False):
    """Render a list of tasks with interactive elements"""
    for i, task in enumerate(tasks):
        with st.container():
            col1, col2, col3 = st.columns([0.1, 3, 0.5])
            
            with col1:
                # Checkbox for task completion
                key = f"task_{task.get('id')}_{i}"
                completed = st.checkbox("", task.get('completed', False), key=key)
                
                # Update task completion status
                if completed != task.get('completed', False):
                    for t in st.session_state.tasks:
                        if t.get('id') == task.get('id'):
                            t['completed'] = completed
                            t['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            break
            
            with col2:
                # Task details
                if completed or show_completed:
                    st.markdown(f"~~{task.get('title', '')}~~")
                else:
                    st.markdown(f"**{task.get('title', '')}**")
                
                if task.get('description'):
                    st.caption(task.get('description', ''))
                
                # Due date with conditional formatting
                due_date = task.get('due_date', '')
                if due_date:
                    due_date_dt = datetime.strptime(due_date, '%Y-%m-%d').date()
                    today = datetime.now().date()
                    
                    if due_date_dt < today and not task.get('completed', False):
                        st.caption(f"🚨 **Overdue**: {due_date}")
                    elif due_date_dt == today and not task.get('completed', False):
                        st.caption(f"⚠️ **Due today**: {due_date}")
                    else:
                        st.caption(f"📅 Due: {due_date}")
            
            with col3:
                # Task actions
                if st.button("Edit", key=f"edit_{task.get('id')}_{i}"):
                    st.session_state.edit_task_id = task.get('id')
                
                if st.button("Delete", key=f"delete_{task.get('id')}_{i}"):
                    st.session_state.delete_task_id = task.get('id')
        
        st.divider()
    
    # Handle edit task
    if hasattr(st.session_state, 'edit_task_id') and st.session_state.edit_task_id:
        edit_task(st.session_state.edit_task_id)
    
    # Handle delete task
    if hasattr(st.session_state, 'delete_task_id') and st.session_state.delete_task_id:
        delete_task(st.session_state.delete_task_id)

def add_task_form():
    """Form for adding a new task"""
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            title = st.text_input("Task Title")
        
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        description = st.text_area("Description", height=100)
        
        col3, col4 = st.columns(2)
        
        with col3:
            due_date = st.date_input("Due Date")
        
        with col4:
            reminder = st.checkbox("Set Reminder")
            reminder_time = None
            if reminder:
                reminder_time = st.time_input("Reminder Time")
        
        submitted = st.form_submit_button("Add Task")
        
        if submitted and title:
            # Create new task
            new_task = {
                "id": len(st.session_state.tasks) + 1,
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_date.strftime("%Y-%m-%d"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add reminder if set
            if reminder and reminder_time:
                reminder_dt = datetime.combine(due_date, reminder_time)
                new_task["reminder"] = reminder_dt.strftime("%Y-%m-%d %H:%M:%S")
                
                # Schedule reminder if available
                if hasattr(st.session_state, 'scheduler'):
                    st.session_state.scheduler.schedule_reminder(new_task)
            
            # Add to session state
            st.session_state.tasks.append(new_task)
            
            # Show success message
            st.success(f"Task added: {title}")

def edit_task(task_id):
    """Edit an existing task"""
    # Find task by ID
    task = next((t for t in st.session_state.tasks if t.get('id') == task_id), None)
    
    if not task:
        st.error(f"Task with ID {task_id} not found")
        st.session_state.edit_task_id = None
        return
    
    st.subheader("Edit Task")
    
    with st.form("edit_task_form"):
        title = st.text_input("Task Title", value=task.get('title', ''))
        description = st.text_area("Description", value=task.get('description', ''), height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            due_date_str = task.get('due_date', datetime.now().strftime("%Y-%m-%d"))
            due_date = st.date_input(
                "Due Date", 
                value=datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else datetime.now()
            )
        
        with col2:
            priority = st.selectbox(
                "Priority", 
                ["Low", "Medium", "High"],
                index=["Low", "Medium", "High"].index(task.get('priority', 'Medium'))
            )
        
        update_submitted = st.form_submit_button("Update Task")
        cancel_button = st.form_submit_button("Cancel")
        
        if update_submitted:
            # Update task
            task['title'] = title
            task['description'] = description
            task['priority'] = priority
            task['due_date'] = due_date.strftime("%Y-%m-%d")
            task['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Clear edit state
            st.session_state.edit_task_id = None
            
            # Show success message
            st.success(f"Task updated: {title}")
            st.experimental_rerun()
        
        elif cancel_button:
            # Clear edit state
            st.session_state.edit_task_id = None
            st.experimental_rerun()

def delete_task(task_id):
    """Delete a task"""
    # Show confirmation dialog
    st.warning("Are you sure you want to delete this task?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, Delete"):
            # Remove task
            st.session_state.tasks = [
                t for t in st.session_state.tasks if t.get('id') != task_id
            ]
            
            # Clear delete state
            st.session_state.delete_task_id = None
            
            # Show success message
            st.success("Task deleted")
            st.experimental_rerun()
    
    with col2:
        if st.button("Cancel"):
            # Clear delete state
            st.session_state.delete_task_id = None
            st.experimental_rerun()
