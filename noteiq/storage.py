import json
import os
from typing import List, Optional
from datetime import datetime
from noteiq.models import Note


class NoteStorage:
    def __init__(self, data_file: str = "notes.json"):
        self.data_file = data_file
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.data_file):
            self._save_notes([])

    def _load_notes(self) -> List[dict]:
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_notes(self, notes: List[dict]):
        with open(self.data_file, "w") as f:
            json.dump(notes, f, indent=2, default=str)

    def _dict_to_note(self, data: dict) -> Note:
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return Note(**data)

    def _note_to_dict(self, note: Note) -> dict:
        return {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tags": note.tags,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }

    def create(self, note: Note) -> Note:
        notes = self._load_notes()
        notes.append(self._note_to_dict(note))
        self._save_notes(notes)
        return note

    def get_all(self, tag: Optional[str] = None) -> List[Note]:
        notes_data = self._load_notes()
        notes = [self._dict_to_note(n) for n in notes_data]
        if tag:
            notes = [n for n in notes if tag in n.tags]
        return sorted(notes, key=lambda x: x.updated_at, reverse=True)

    def get_by_id(self, note_id: str) -> Optional[Note]:
        notes_data = self._load_notes()
        for n in notes_data:
            if n["id"] == note_id:
                return self._dict_to_note(n)
        return None

    def update(self, note_id: str, note: Note) -> Optional[Note]:
        notes_data = self._load_notes()
        for i, n in enumerate(notes_data):
            if n["id"] == note_id:
                note.updated_at = datetime.utcnow()
                notes_data[i] = self._note_to_dict(note)
                self._save_notes(notes_data)
                return note
        return None

    def delete(self, note_id: str) -> bool:
        notes_data = self._load_notes()
        notes_data = [n for n in notes_data if n["id"] != note_id]
        self._save_notes(notes_data)
        return True