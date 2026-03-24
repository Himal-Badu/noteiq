"""
NoteIQ - Streamlit Web Application
AI-Powered Notes That Think With You
"""

import streamlit as st
import os
import json
import tempfile
from datetime import datetime
from typing import List, Optional

# Set up environment
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

from noteiq.models import Note, NoteCreate, NoteUpdate
from noteiq.storage import NoteStorage
from noteiq.ai import AINotes


# Configure page
st.set_page_config(
    page_title="NoteIQ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        background-color: #4CAF50;
        color: white;
    }
    .note-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .tag {
        background-color: #e3f2fd;
        padding: 3px 8px;
        border-radius: 15px;
        font-size: 12px;
        margin-right: 5px;
    }
    h1, h2, h3 {
        color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)


class NoteIQApp:
    """NoteIQ Streamlit Application"""
    
    def __init__(self):
        # Use session state for storage to persist across reruns
        if "storage" not in st.session_state:
            # Create a temp file for storage
            if "storage_file" not in st.session_state:
                temp_dir = tempfile.gettempdir()
                st.session_state.storage_file = os.path.join(temp_dir, "noteiq_streamlit.json")
            st.session_state.storage = NoteStorage(data_file=st.session_state.storage_file)
        
        self.storage = st.session_state.storage
        
        # Initialize AI if API key available
        self.ai_enabled = bool(os.getenv("OPENAI_API_KEY"))
        if self.ai_enabled:
            try:
                self.ai = AINotes()
            except Exception as e:
                self.ai_enabled = False
                st.error(f"AI initialization failed: {e}")
    
    def render_header(self):
        """Render the header"""
        st.title("🤖 NoteIQ")
        st.markdown("**AI-Powered Notes That Think With You**")
        
        # Status indicator
        if self.ai_enabled:
            st.success("✅ AI Features Enabled")
        else:
            st.warning("⚠️ AI Features Disabled - Set OPENAI_API_KEY")
        
        st.divider()
    
    def render_sidebar(self):
        """Render sidebar navigation"""
        st.sidebar.title("📝 Navigation")
        
        # Navigation options
        page = st.sidebar.radio(
            "Go to",
            ["📋 All Notes", "➕ Create Note", "🔍 Search", "⚙️ Settings"]
        )
        
        # Show stats
        st.sidebar.divider()
        notes = self.storage.get_all()
        st.sidebar.metric("Total Notes", len(notes))
        
        # Show tags
        if notes:
            all_tags = set()
            for note in notes:
                all_tags.update(note.tags)
            if all_tags:
                st.sidebar.subheader("🏷️ Tags")
                for tag in sorted(all_tags):
                    count = sum(1 for n in notes if tag in n.tags)
                    st.sidebar.write(f"- {tag} ({count})")
        
        return page
    
    def render_all_notes(self):
        """Render all notes page"""
        st.header("📋 All Notes")
        
        # Filter by tag
        notes = self.storage.get_all()
        
        # Tag filter
        all_tags = set()
        for note in notes:
            all_tags.update(note.tags)
        
        if all_tags:
            selected_tag = st.selectbox("Filter by tag", ["All"] + sorted(all_tags))
            if selected_tag != "All":
                notes = [n for n in notes if selected_tag in n.tags]
        
        if not notes:
            st.info("No notes yet. Create one!")
            return
        
        # Display notes
        for note in notes:
            with st.expander(f"📝 {note.title} ({note.created_at.strftime('%Y-%m-%d')})"):
                # Tags
                if note.tags:
                    tags_html = " ".join([f`<span class="tag">#{tag}</span>` for tag in note.tags])
                    st.markdown(tags_html, unsafe_allow_html=True)
                
                # Content
                st.markdown(f"**Content:**")
                st.write(note.content)
                
                # Metadata
                st.caption(f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M')} | Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M')}")
                
                # Actions
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("View", key=f"view_{note.id}"):
                        st.session_state.view_note = note
                        st.rerun()
                
                with col2:
                    if st.button("Edit", key=f"edit_{note.id}"):
                        st.session_state.edit_note = note
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"del_{note.id}"):
                        self.storage.delete(note.id)
                        st.success("Note deleted!")
                        st.rerun()
                
                with col4:
                    if st.button("AI Actions", key=f"ai_{note.id}"):
                        st.session_state.ai_note = note
                        st.rerun()
    
    def render_create_note(self):
        """Render create note page"""
        st.header("➕ Create New Note")
        
        with st.form("create_note_form"):
            title = st.text_input("Title", placeholder="Enter note title")
            content = st.text_area("Content", height=200, placeholder="Enter note content")
            tags = st.text_input("Tags", placeholder="Comma-separated tags (e.g., work, ideas, meeting)")
            
            submitted = st.form_submit_button("Create Note")
            
            if submitted:
                if not title:
                    st.error("Title is required!")
                elif not content:
                    st.error("Content is required!")
                else:
                    # Parse tags
                    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                    
                    # Create note
                    note = Note(
                        title=title,
                        content=content,
                        tags=tag_list
                    )
                    
                    created = self.storage.create(note)
                    st.success(f"✅ Note created: {created.id}")
                    
                    # Clear form
                    st.rerun()
    
    def render_search(self):
        """Render search page"""
        st.header("🔍 Search Notes")
        
        query = st.text_input("Search query", placeholder="Enter search terms...")
        
        if query:
            notes = self.storage.get_all()
            results = [
                n for n in notes 
                if query.lower() in n.title.lower() or query.lower() in n.content.lower()
            ]
            
            if results:
                st.write(f"Found {len(results)} result(s):")
                for note in results:
                    with st.expander(f"📝 {note.title}"):
                        st.write(note.content[:200] + "..." if len(note.content) > 200 else note.content)
            else:
                st.info("No results found.")
        else:
            st.info("Enter a search term to find notes.")
    
    def render_settings(self):
        """Render settings page"""
        st.header("⚙️ Settings")
        
        st.subheader("API Key Configuration")
        
        api_key = os.getenv("OPENAI_API_KEY", "")
        
        new_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=api_key,
            help="Get your API key from https://platform.openai.com/api-keys"
        )
        
        if new_key != api_key:
            os.environ["OPENAI_API_KEY"] = new_key
            st.success("API key updated! Restart the app to apply changes.")
        
        st.divider()
        
        st.subheader("About")
        st.write("**NoteIQ** - AI-Powered Notes Application")
        st.write("Version: 1.0.0")
        st.write("Built by Himal Badu, AI Founder")
        
        st.divider()
        
        st.subheader("Data Management")
        
        if st.button("Export All Notes"):
            notes = self.storage.get_all()
            export_data = {
                "export_date": datetime.now().isoformat(),
                "notes": [
                    {
                        "id": n.id,
                        "title": n.title,
                        "content": n.content,
                        "tags": n.tags,
                        "created_at": n.created_at.isoformat(),
                        "updated_at": n.updated_at.isoformat()
                    }
                    for n in notes
                ]
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name="noteiq_export.json",
                mime="application/json"
            )
        
        if st.button("Clear All Notes"):
            notes = self.storage.get_all()
            for note in notes:
                self.storage.delete(note.id)
            st.success("All notes cleared!")
            st.rerun()
    
    def render_note_view(self, note: Note):
        """Render single note view"""
        st.header(f"📝 {note.title}")
        
        # Tags
        if note.tags:
            tags_html = " ".join([f`<span class="tag">#{tag}</span>` for tag in note.tags])
            st.markdown(tags_html, unsafe_allow_html=True)
        
        # Content
        st.markdown("### Content")
        st.write(note.content)
        
        # Metadata
        st.caption(f"Created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.caption(f"Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # AI Actions
        if self.ai_enabled:
            st.divider()
            st.subheader("🤖 AI Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📝 Summarize"):
                    with st.spinner("Generating summary..."):
                        try:
                            summary = self.ai.summarize(note.content)
                            st.success("Summary:")
                            st.write(summary)
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            with col2:
                if st.button("✅ Extract Actions"):
                    with st.spinner("Extracting action items..."):
                        try:
                            actions = self.ai.extract_actions(note.content)
                            st.success("Action Items:")
                            for action in actions:
                                st.write(f"- {action}")
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            st.divider()
            
            # Ask question
            st.subheader("❓ Ask a Question")
            question = st.text_input("Ask about this note:", placeholder="What is this note about?")
            
            if st.button("Ask") and question:
                with st.spinner("Getting answer..."):
                    try:
                        answer = self.ai.answer_question(note.content, question)
                        st.success("Answer:")
                        st.write(answer)
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    def render_note_edit(self, note: Note):
        """Render note edit form"""
        st.header(f"✏️ Edit Note: {note.title}")
        
        with st.form("edit_note_form"):
            new_title = st.text_input("Title", value=note.title)
            new_content = st.text_area("Content", value=note.content, height=200)
            new_tags = st.text_input("Tags", value=", ".join(note.tags))
            
            submitted = st.form_submit_button("Save Changes")
            
            if submitted:
                if not new_title:
                    st.error("Title is required!")
                elif not new_content:
                    st.error("Content is required!")
                else:
                    # Update note
                    note.title = new_title
                    note.content = new_content
                    note.tags = [t.strip() for t in new_tags.split(",") if t.strip()]
                    
                    self.storage.update(note.id, note)
                    st.success("Note updated!")
                    st.rerun()
    
    def render_ai_actions(self, note: Note):
        """Render AI actions page"""
        st.header(f"🤖 AI Actions: {note.title}")
        
        if not self.ai_enabled:
            st.error("AI features are disabled. Set OPENAI_API_KEY to enable.")
            return
        
        # Tabs for different AI features
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "✅ Actions", "❓ Q&A", "📑 Outline"])
        
        with tab1:
            st.subheader("Summary")
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    try:
                        summary = self.ai.summarize(note.content)
                        st.success(summary)
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with tab2:
            st.subheader("Action Items")
            if st.button("Extract Actions"):
                with st.spinner("Extracting actions..."):
                    try:
                        actions = self.ai.extract_actions(note.content)
                        for action in actions:
                            st.write(f"- {action}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with tab3:
            st.subheader("Ask a Question")
            question = st.text_input("Your question:", key="ai_question")
            if st.button("Get Answer"):
                if question:
                    with st.spinner("Getting answer..."):
                        try:
                            answer = self.ai.answer_question(note.content, question)
                            st.success(answer)
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please enter a question.")
        
        with tab4:
            st.subheader("Outline")
            if st.button("Generate Outline"):
                with st.spinner("Generating outline..."):
                    try:
                        outline = self.ai.generate_outline(note.content)
                        for item in outline:
                            st.write(f"- {item}")
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    def run(self):
        """Run the application"""
        # Check for special states
        if "view_note" in st.session_state:
            self.render_note_view(st.session_state.view_note)
            if st.button("← Back"):
                del st.session_state.view_note
                st.rerun()
            return
        
        if "edit_note" in st.session_state:
            self.render_note_edit(st.session_state.edit_note)
            if st.button("← Back"):
                del st.session_state.edit_note
                st.rerun()
            return
        
        if "ai_note" in st.session_state:
            self.render_ai_actions(st.session_state.ai_note)
            if st.button("← Back"):
                del st.session_state.ai_note
                st.rerun()
            return
        
        # Normal navigation
        page = self.render_sidebar()
        
        if page == "📋 All Notes":
            self.render_all_notes()
        elif page == "➕ Create Note":
            self.render_create_note()
        elif page == "🔍 Search":
            self.render_search()
        elif page == "⚙️ Settings":
            self.render_settings()


if __name__ == "__main__":
    app = NoteIQApp()
    app.run()