import streamlit as st
import pandas as pd
from datetime import datetime
import json
import config
import uuid

def render_notes_panel():
    """Render the notes management panel"""
    st.header("Notes Manager")
    
    # Notes tabs
    tab1, tab2, tab3 = st.tabs(["All Notes", "Categories", "Search"])
    
    with tab1:
        render_all_notes()
    
    with tab2:
        render_notes_by_category()
        
    with tab3:
        render_notes_search()

def render_all_notes():
    """Render all notes view"""
    # Add new note form
    with st.expander("Add New Note", expanded=False):
        add_note_form()
    
    # Get notes
    notes = st.session_state.notes
    
    if not notes:
        st.info("No notes found. Add some notes to get started!")
        return
    
    # Sort notes by creation date (newest first)
    sorted_notes = sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Display notes
    for note in sorted_notes:
        render_note_card(note)

def render_notes_by_category():
    """Render notes grouped by category"""
    notes = st.session_state.notes
    
    if not notes:
        st.info("No notes found.")
        return
    
    # Group notes by category
    categories = {}
    for note in notes:
        category = note.get('category', 'General')
        if category not in categories:
            categories[category] = []
        categories[category].append(note)
    
    # Display by category
    for category, category_notes in categories.items():
        st.subheader(f"📁 {category} ({len(category_notes)})")
        for note in category_notes:
            render_note_card(note, show_category=False)

def render_notes_search():
    """Render notes search functionality"""
    search_term = st.text_input("🔍 Search notes", placeholder="Enter keywords...")
    
    if search_term:
        notes = st.session_state.notes
        filtered_notes = [
            note for note in notes
            if (search_term.lower() in note.get('title', '').lower() or
                search_term.lower() in note.get('content', '').lower() or
                search_term.lower() in note.get('tags', '').lower())
        ]
        
        if filtered_notes:
            st.write(f"Found {len(filtered_notes)} notes:")
            for note in filtered_notes:
                render_note_card(note)
        else:
            st.info("No notes found matching your search.")

def add_note_form():
    """Form to add a new note"""
    with st.form("add_note_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            title = st.text_input("Note Title", placeholder="Enter note title")
        
        with col2:
            category = st.selectbox("Category", config.NOTE_CATEGORIES)
        
        content = st.text_area("Note Content", placeholder="Write your note here...", height=150)
        
        col3, col4 = st.columns([1, 1])
        with col3:
            tags = st.text_input("Tags", placeholder="tag1, tag2, tag3")
        with col4:
            is_private = st.checkbox("Private Note")
        
        submitted = st.form_submit_button("Add Note", type="primary")
        
        if submitted:
            if title and content:
                new_note = {
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "content": content,
                    "category": category,
                    "tags": tags,
                    "is_private": is_private,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                st.session_state.notes.append(new_note)
                st.success("Note added successfully!")
                st.rerun()
            else:
                st.error("Please provide both title and content for the note.")

def render_note_card(note, show_category=True):
    """Render a single note card"""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.subheader(f"📝 {note.get('title', 'Untitled')}")
            
            # Show category if requested
            if show_category:
                category = note.get('category', 'General')
                st.caption(f"📁 Category: {category}")
            
            # Show privacy status
            if note.get('is_private', False):
                st.caption("🔒 Private")
            
            # Show content (truncated)
            content = note.get('content', '')
            if len(content) > 200:
                content = content[:200] + "..."
            st.write(content)
            
            # Show tags
            tags = note.get('tags', '')
            if tags:
                st.caption(f"🏷️ Tags: {tags}")
            
            # Show timestamps
            created_at = note.get('created_at', '')
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M")
                    st.caption(f"📅 Created: {created_date}")
                except:
                    pass
        
        with col2:
            if st.button("Edit", key=f"edit_{note.get('id')}", help="Edit this note"):
                edit_note(note)
        
        with col3:
            if st.button("Delete", key=f"delete_{note.get('id')}", help="Delete this note"):
                delete_note(note.get('id'))
        
        st.divider()

def edit_note(note):
    """Edit an existing note"""
    st.subheader("Edit Note")
    
    with st.form(f"edit_note_form_{note.get('id')}"):
        title = st.text_input("Note Title", value=note.get('title', ''))
        category = st.selectbox("Category", config.NOTE_CATEGORIES, 
                               index=config.NOTE_CATEGORIES.index(note.get('category', 'General')))
        content = st.text_area("Note Content", value=note.get('content', ''), height=150)
        tags = st.text_input("Tags", value=note.get('tags', ''))
        is_private = st.checkbox("Private Note", value=note.get('is_private', False))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Update Note", type="primary"):
                update_note(note.get('id'), title, content, category, tags, is_private)
        with col2:
            if st.form_submit_button("Cancel"):
                st.rerun()

def update_note(note_id, title, content, category, tags, is_private):
    """Update an existing note"""
    for i, note in enumerate(st.session_state.notes):
        if note.get('id') == note_id:
            st.session_state.notes[i].update({
                'title': title,
                'content': content,
                'category': category,
                'tags': tags,
                'is_private': is_private,
                'updated_at': datetime.now().isoformat()
            })
            st.success("Note updated successfully!")
            st.rerun()
            break

def delete_note(note_id):
    """Delete a note"""
    st.session_state.notes = [note for note in st.session_state.notes if note.get('id') != note_id]
    st.success("Note deleted successfully!")
    st.rerun()

def get_notes_summary():
    """Get summary statistics for notes"""
    notes = st.session_state.notes
    
    total_notes = len(notes)
    categories = set(note.get('category', 'General') for note in notes)
    private_notes = sum(1 for note in notes if note.get('is_private', False))
    
    return {
        'total': total_notes,
        'categories': len(categories),
        'private': private_notes,
        'public': total_notes - private_notes
    }
