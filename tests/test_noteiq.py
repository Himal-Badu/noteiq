import pytest
import os
import json
import tempfile
from datetime import datetime

# Set up test environment
os.environ["OPENAI_API_KEY"] = "test-key"

from noteiq.models import Note, NoteCreate, NoteUpdate
from noteiq.storage import NoteStorage


class TestNoteModels:
    def test_note_creation(self):
        note = Note(title="Test Note", content="Test content")
        assert note.title == "Test Note"
        assert note.content == "Test content"
        assert note.id is not None

    def test_note_create_model(self):
        note = NoteCreate(
            title="Test",
            content="Content",
            tags=["tag1", "tag2"]
        )
        assert note.title == "Test"
        assert note.tags == ["tag1", "tag2"]


class TestNoteStorage:
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        storage = NoteStorage(data_file=temp_file)
        yield storage
        os.unlink(temp_file)

    def test_create_note(self, temp_storage):
        note = Note(title="Test", content="Content", tags=["test"])
        created = temp_storage.create(note)
        assert created.id is not None
        assert created.title == "Test"

    def test_get_all_notes(self, temp_storage):
        note1 = Note(title="Note 1", content="Content 1")
        note2 = Note(title="Note 2", content="Content 2")
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        notes = temp_storage.get_all()
        assert len(notes) == 2

    def test_get_note_by_id(self, temp_storage):
        note = Note(title="Test", content="Content")
        created = temp_storage.create(note)
        
        retrieved = temp_storage.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_update_note(self, temp_storage):
        note = Note(title="Original", content="Original content")
        created = temp_storage.create(note)
        
        created.title = "Updated"
        updated = temp_storage.update(created.id, created)
        
        assert updated.title == "Updated"

    def test_delete_note(self, temp_storage):
        note = Note(title="Test", content="Content")
        created = temp_storage.create(note)
        
        success = temp_storage.delete(created.id)
        assert success is True
        
        retrieved = temp_storage.get_by_id(created.id)
        assert retrieved is None

    def test_filter_by_tag(self, temp_storage):
        note1 = Note(title="Tagged", content="Content", tags=["work"])
        note2 = Note(title="Untagged", content="Content", tags=[])
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        work_notes = temp_storage.get_all(tag="work")
        assert len(work_notes) == 1
        assert work_notes[0].title == "Tagged"


class TestAPIEndpoints:
    """Integration tests for API endpoints."""
    
    def test_root_endpoint(self):
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_create_note_endpoint(self):
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/notes",
            json={"title": "API Test", "content": "Test content", "tags": ["test"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "API Test"
        assert "id" in data