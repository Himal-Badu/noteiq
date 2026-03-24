"""
Enhanced storage module for NoteIQ
Handles persistence of notes to JSON file with advanced features
"""
import json
import os
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from noteiq.models import Note, NotePriority, NoteCategory, NoteStats, NoteFilter
from noteiq.utils import logger, log_info, log_error


class NoteStorage:
    """Storage handler for notes using JSON file with advanced features"""
    
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
        if isinstance(data.get("due_date"), str):
            data["due_date"] = datetime.fromisoformat(data["due_date"])
        if isinstance(data.get("completed_at"), str):
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
        
        # Handle priority enum
        if "priority" in data and isinstance(data["priority"], str):
            data["priority"] = NotePriority(data["priority"])
        
        # Handle category enum
        if "category" in data and isinstance(data["category"], str):
            data["category"] = NoteCategory(data.get("category", "general"))
        
        # Handle boolean conversions
        for bool_field in ["is_pinned", "is_archived", "is_favorite"]:
            if bool_field in data and isinstance(data[bool_field], str):
                data[bool_field] = data[bool_field].lower() == "true"
        
        return Note(**data)

    def _note_to_dict(self, note: Note) -> dict:
        """Convert Note object to dictionary"""
        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tags": note.tags,
            "category": note.category.value if hasattr(note.category, 'value') else note.category,
            "priority": note.priority.value if hasattr(note.priority, 'value') else note.priority,
            "is_pinned": note.is_pinned,
            "is_archived": note.is_archived,
            "is_favorite": note.is_favorite,
            "color": note.color,
            "created_at": note.created_at.isoformat() if note.created_at else datetime.utcnow().isoformat(),
            "updated_at": note.updated_at.isoformat() if note.updated_at else datetime.utcnow().isoformat(),
            "due_date": note.due_date.isoformat() if note.due_date else None,
            "completed_at": note.completed_at.isoformat() if note.completed_at else None
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
            List of notes sorted by pinned and update time
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

    def get_by_category(self, category: NoteCategory) -> List[Note]:
        """
        Get notes by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of notes in the category
        """
        notes = self.get_all()
        return [n for n in notes if n.category == category]

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

    def filter_notes(self, filter_params: NoteFilter) -> List[Note]:
        """
        Filter notes using advanced filter.
        
        Args:
            filter_params: NoteFilter object with filter criteria
            
        Returns:
            List of filtered notes
        """
        notes = self.get_all(include_archived=True)
        
        if filter_params.tags:
            notes = [n for n in notes if any(tag in n.tags for tag in filter_params.tags)]
        
        if filter_params.categories:
            notes = [n for n in notes if n.category in filter_params.categories]
        
        if filter_params.priorities:
            notes = [n for n in notes if n.priority in filter_params.priorities]
        
        if filter_params.is_pinned is not None:
            notes = [n for n in notes if n.is_pinned == filter_params.is_pinned]
        
        if filter_params.is_archived is not None:
            notes = [n for n in notes if n.is_archived == filter_params.is_archived]
        
        if filter_params.is_favorite is not None:
            notes = [n for n in notes if n.is_favorite == filter_params.is_favorite]
        
        if filter_params.date_from:
            notes = [n for n in notes if n.created_at >= filter_params.date_from]
        
        if filter_params.date_to:
            notes = [n for n in notes if n.created_at <= filter_params.date_to]
        
        return notes

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
        notes = self.get_all(include_archived=True)
        return [n for n in notes if n.is_archived]

    def get_favorites(self) -> List[Note]:
        """Get favorite notes"""
        notes = self.get_all()
        return [n for n in notes if n.is_favorite]

    def get_due_notes(self) -> List[Note]:
        """Get notes with due dates"""
        notes = self.get_all()
        return [n for n in notes if n.due_date is not None]

    def get_overdue_notes(self) -> List[Note]:
        """Get overdue notes"""
        notes = self.get_all()
        now = datetime.utcnow()
        return [n for n in notes if n.due_date and n.due_date < now and not n.completed_at]

    def get_notes_today(self) -> List[Note]:
        """Get notes created or updated today"""
        notes = self.get_all()
        today = datetime.utcnow().date()
        return [n for n in notes if n.created_at.date() == today or n.updated_at.date() == today]

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

    def toggle_favorite(self, note_id: str) -> Optional[Note]:
        """Toggle favorite status"""
        note = self.get_by_id(note_id)
        if note:
            note.is_favorite = not note.is_favorite
            return self.update(note_id, note)
        return None

    def set_due_date(self, note_id: str, due_date: Optional[datetime]) -> Optional[Note]:
        """Set due date for a note"""
        note = self.get_by_id(note_id)
        if note:
            note.due_date = due_date
            return self.update(note_id, note)
        return None

    def mark_completed(self, note_id: str) -> Optional[Note]:
        """Mark a note as completed"""
        note = self.get_by_id(note_id)
        if note:
            note.completed_at = datetime.utcnow()
            return self.update(note_id, note)
        return None

    def get_stats(self) -> NoteStats:
        """Get statistics about notes"""
        notes = self.get_all(include_archived=True)
        now = datetime.utcnow()
        today = now.date()
        
        # Count by priority
        priority_counts = {}
        for priority in NotePriority:
            priority_counts[priority.value] = sum(1 for n in notes if n.priority == priority)
        
        # Count by category
        category_counts = {}
        for category in NoteCategory:
            category_counts[category.value] = sum(1 for n in notes if n.category == category)
        
        # Count by tag
        tag_counts = {}
        for note in notes:
            for tag in note.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Average content length
        content_lengths = [len(n.content) for n in notes]
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        
        # Notes created/updated today
        notes_created_today = sum(1 for n in notes if n.created_at.date() == today)
        notes_updated_today = sum(1 for n in notes if n.updated_at.date() == today)
        
        return NoteStats(
            total_notes=len(notes),
            active_notes=len([n for n in notes if not n.is_archived]),
            pinned_notes=sum(1 for n in notes if n.is_pinned),
            archived_notes=sum(1 for n in notes if n.is_archived),
            favorite_notes=sum(1 for n in notes if n.is_favorite),
            notes_by_priority=priority_counts,
            notes_by_category=category_counts,
            notes_by_tag=tag_counts,
            average_content_length=avg_length,
            notes_created_today=notes_created_today,
            notes_updated_today=notes_updated_today
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

    def bulk_archive(self, note_ids: List[str]) -> int:
        """Archive multiple notes"""
        count = 0
        for note_id in note_ids:
            if self.archive(note_id):
                count += 1
        return count

    def bulk_pin(self, note_ids: List[str]) -> int:
        """Pin multiple notes"""
        count = 0
        for note_id in note_ids:
            if self.pin(note_id):
                count += 1
        return count

    def clear_all(self) -> int:
        """Clear all notes (use with caution!)"""
        notes_data = self._load_notes()
        count = len(notes_data)
        self._save_notes([])
        log_info(f"Cleared {count} notes")
        return count

    def export_to_dict(self, include_archived: bool = False) -> Dict[str, Any]:
        """Export all notes as dictionary"""
        notes = self.get_all(include_archived=include_archived)
        return {
            "export_date": datetime.utcnow().isoformat(),
            "total_notes": len(notes),
            "notes": [self._note_to_dict(n) for n in notes]
        }

    def import_from_dict(self, data: Dict[str, Any]) -> int:
        """Import notes from dictionary"""
        count = 0
        notes_data = data.get("notes", data if isinstance(data, list) else [])
        
        for item in notes_data:
            try:
                note = self._dict_to_note(item)
                self.create(note)
                count += 1
            except Exception as e:
                log_error(f"Error importing note: {e}")
        
        return count

    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        notes = self.get_all()
        tags = set()
        for note in notes:
            tags.update(note.tags)
        return sorted(list(tags))

    def get_all_categories(self) -> List[NoteCategory]:
        """Get all categories that have notes"""
        notes = self.get_all()
        categories = set()
        for note in notes:
            categories.add(note.category)
        return sorted(list(categories), key=lambda x: x.value)

    def duplicate_note(self, note_id: str) -> Optional[Note]:
        """Create a copy of an existing note"""
        original = self.get_by_id(note_id)
        if original:
            import uuid
            new_note = Note(
                title=f"{original.title} (Copy)",
                content=original.content,
                tags=original.tags.copy(),
                category=original.category,
                priority=original.priority,
                color=original.color
            )
            return self.create(new_note)
        return None

    def merge_notes(self, note_ids: List[str], new_title: str) -> Optional[Note]:
        """Merge multiple notes into one"""
        notes = [self.get_by_id(nid) for nid in note_ids]
        notes = [n for n in notes if n]
        
        if not notes:
            return None
        
        # Combine content
        combined_content = "\n\n---\n\n".join([n.content for n in notes])
        
        # Combine tags
        all_tags = set()
        for note in notes:
            all_tags.update(note.tags)
        
        # Create merged note
        merged = Note(
            title=new_title,
            content=combined_content,
            tags=list(all_tags)
        )
        
        return self.create(merged)
