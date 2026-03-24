"""
Storage module for NoteIQ
Handles persistence of notes to JSON file
"""
import json
import os
import shutil
from typing import List, Optional
from datetime import datetime
from noteiq.models import Note, NotePriority, NoteStats
from noteiq.utils import logger, log_info, log_error


class NoteStorage:
    """Storage handler for notes using JSON file"""
    
    def __init__(self, data_file: str = "notes.json", backup: bool = True):
        """
        Initialize storage.
        
        Args:
            data_file: Path to the JSON file for storing notes
            backup: Whether to create backups before saving
        """
        self.data_file = data_file
        self.backup_enabled = backup
        self._ensure_file()
        log_info(f"Storage initialized: {data_file}")

    def _ensure_file(self):
        """Ensure data file exists"""
        if not os.path.exists(self.data_file):
            self._save_notes([])
            log_info(f"Created new storage file: {self.data_file}")

    def _load_notes(self) -> List[dict]:
        """Load notes from file"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except json.JSONDecodeError as e:
            log_error(f"Error decoding JSON: {e}")
            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            log_error(f"Error loading notes: {e}")
            return []

    def _save_notes(self, notes: List[dict]):
        """Save notes to file"""
        # Create backup if enabled
        if self.backup_enabled and os.path.exists(self.data_file):
            self._create_backup()
        
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(notes, f, indent=2, default=str)
            log_info(f"Saved {len(notes)} notes")
        except Exception as e:
            log_error(f"Error saving notes: {e}")
            raise

    def _create_backup(self):
        """Create a backup of the current data file"""
        if os.path.exists(self.data_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{self.data_file}.backup_{timestamp}"
            try:
                shutil.copy2(self.data_file, backup_file)
                log_info(f"Created backup: {backup_file}")
                # Keep only last 5 backups
                self._cleanup_backups()
            except Exception as e:
                log_error(f"Error creating backup: {e}")

    def _cleanup_backups(self):
        """Remove old backup files"""
        import glob
        backups = sorted(glob.glob(f"{self.data_file}.backup_*"))
        # Keep only last 5 backups
        for backup in backups[:-5]:
            try:
                os.remove(backup)
                log_info(f"Removed old backup: {backup}")
            except Exception as e:
                log_error(f"Error removing backup {backup}: {e}")

    def _dict_to_note(self, data: dict) -> Note:
        """Convert dictionary to Note object"""
        # Handle datetime conversion
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("updated_at"), str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        
        # Handle priority enum
        if "priority" in data and isinstance(data["priority"], str):
            data["priority"] = NotePriority(data["priority"])
        
        return Note(**data)

    def _note_to_dict(self, note: Note) -> dict:
        """Convert Note object to dictionary"""
        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tags": note.tags,
            "priority": note.priority,
            "is_pinned": note.is_pinned,
            "is_archived": note.is_archived,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }

    def create(self, note: Note) -> Note:
        """
        Create a new note.
        
        Args:
            note: Note object to create
            
        Returns:
            Created note with ID
        """
        notes = self._load_notes()
        notes.append(self._note_to_dict(note))
        self._save_notes(notes)
        log_info(f"Created note: {note.id}")
        return note

    def get_all(self, tag: Optional[str] = None, include_archived: bool = False) -> List[Note]:
        """
        Get all notes, optionally filtered by tag.
        
        Args:
            tag: Optional tag to filter by
            include_archived: Whether to include archived notes
            
        Returns:
            List of notes sorted by update time
        """
        notes_data = self._load_notes()
        notes = [self._dict_to_note(n) for n in notes_data]
        
        # Filter by tag
        if tag:
            notes = [n for n in notes if tag in n.tags]
        
        # Filter archived
        if not include_archived:
            notes = [n for n in notes if not n.is_archived]
        
        # Sort by pinned first, then by updated_at
        return sorted(notes, key=lambda x: (not x.is_pinned, x.updated_at), reverse=True)

    def get_by_id(self, note_id: str) -> Optional[Note]:
        """
        Get a note by ID.
        
        Args:
            note_id: Note ID to search for
            
        Returns:
            Note if found, None otherwise
        """
        notes_data = self._load_notes()
        for n in notes_data:
            if n["id"] == note_id:
                return self._dict_to_note(n)
        return None

    def get_by_title(self, title: str) -> List[Note]:
        """
        Get notes by title (partial match).
        
        Args:
            title: Title to search for
            
        Returns:
            List of matching notes
        """
        notes = self.get_all()
        return [n for n in notes if title.lower() in n.title.lower()]

    def search(self, query: str, tags: Optional[List[str]] = None) -> List[Note]:
        """
        Search notes by query string.
        
        Args:
            query: Search query
            tags: Optional tags to filter by
            
        Returns:
            List of matching notes
        """
        notes = self.get_all()
        query_lower = query.lower()
        
        results = []
        for note in notes:
            # Search in title and content
            if query_lower in note.title.lower() or query_lower in note.content.lower():
                # Check tags if specified
                if tags:
                    if any(tag in note.tags for tag in tags):
                        results.append(note)
                else:
                    results.append(note)
        
        return results

    def get_by_priority(self, priority: NotePriority) -> List[Note]:
        """Get notes by priority"""
        notes = self.get_all()
        return [n for n in notes if n.priority == priority]

    def get_pinned(self) -> List[Note]:
        """Get pinned notes"""
        notes = self.get_all()
        return [n for n in notes if n.is_pinned]

    def get_archived(self) -> List[Note]:
        """Get archived notes"""
        return self.get_all(include_archived=True)

    def update(self, note_id: str, note: Note) -> Optional[Note]:
        """
        Update an existing note.
        
        Args:
            note_id: ID of note to update
            note: Updated note object
            
        Returns:
            Updated note or None if not found
        """
        notes_data = self._load_notes()
        
        for i, n in enumerate(notes_data):
            if n["id"] == note_id:
                note.updated_at = datetime.utcnow()
                notes_data[i] = self._note_to_dict(note)
                self._save_notes(notes_data)
                log_info(f"Updated note: {note_id}")
                return note
        
        return None

    def delete(self, note_id: str) -> bool:
        """
        Delete a note.
        
        Args:
            note_id: ID of note to delete
            
        Returns:
            True if deleted, False if not found
        """
        notes_data = self._load_notes()
        original_count = len(notes_data)
        notes_data = [n for n in notes_data if n["id"] != note_id]
        
        if len(notes_data) < original_count:
            self._save_notes(notes_data)
            log_info(f"Deleted note: {note_id}")
            return True
        
        return False

    def archive(self, note_id: str) -> Optional[Note]:
        """Archive a note"""
        note = self.get_by_id(note_id)
        if note:
            note.is_archived = True
            return self.update(note_id, note)
        return None

    def unarchive(self, note_id: str) -> Optional[Note]:
        """Unarchive a note"""
        note = self.get_by_id(note_id)
        if note:
            note.is_archived = False
            return self.update(note_id, note)
        return None

    def pin(self, note_id: str) -> Optional[Note]:
        """Pin a note"""
        note = self.get_by_id(note_id)
        if note:
            note.is_pinned = True
            return self.update(note_id, note)
        return None

    def unpin(self, note_id: str) -> Optional[Note]:
        """Unpin a note"""
        note = self.get_by_id(note_id)
        if note:
            note.is_pinned = False
            return self.update(note_id, note)
        return None

    def get_stats(self) -> NoteStats:
        """Get statistics about notes"""
        notes = self.get_all(include_archived=True)
        
        # Count by priority
        priority_counts = {}
        for priority in NotePriority:
            priority_counts[priority.value] = sum(1 for n in notes if n.priority == priority)
        
        # Count by tag
        tag_counts = {}
        for note in notes:
            for tag in note.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Average content length
        content_lengths = [len(n.content) for n in notes]
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        
        return NoteStats(
            total_notes=len(notes),
            pinned_notes=sum(1 for n in notes if n.is_pinned),
            archived_notes=sum(1 for n in notes if n.is_archived),
            notes_by_priority=priority_counts,
            notes_by_tag=tag_counts,
            average_content_length=avg_length
        )

    def bulk_delete(self, note_ids: List[str]) -> int:
        """Delete multiple notes"""
        notes_data = self._load_notes()
        original_count = len(notes_data)
        notes_data = [n for n in notes_data if n["id"] not in note_ids]
        deleted_count = original_count - len(notes_data)
        
        if deleted_count > 0:
            self._save_notes(notes_data)
            log_info(f"Bulk deleted {deleted_count} notes")
        
        return deleted_count

    def clear_all(self) -> int:
        """Clear all notes (use with caution!)"""
        notes_data = self._load_notes()
        count = len(notes_data)
        self._save_notes([])
        log_info(f"Cleared {count} notes")
        return count