import pytest
import os
import json
import tempfile
from datetime import datetime

# Set up test environment
os.environ["OPENAI_API_KEY"] = "test-key"

from noteiq.models import Note, NoteCreate, NoteUpdate, NotePriority
from noteiq.storage import NoteStorage
from noteiq.exceptions import NoteNotFoundError, ValidationError


class TestNoteModels:
    """Test cases for Note models"""
    
    def test_note_creation(self):
        """Test basic note creation"""
        note = Note(title="Test Note", content="Test content")
        assert note.title == "Test Note"
        assert note.content == "Test content"
        assert note.id is not None
        assert note.priority == NotePriority.MEDIUM
        assert note.is_pinned == False
        assert note.is_archived == False
    
    def test_note_with_tags(self):
        """Test note creation with tags"""
        note = Note(title="Test", content="Content", tags=["work", "important"])
        assert len(note.tags) == 2
        assert "work" in note.tags
    
    def test_note_with_priority(self):
        """Test note with priority"""
        note = Note(title="Test", content="Content", priority=NotePriority.HIGH)
        assert note.priority == NotePriority.HIGH
    
    def test_note_pinning(self):
        """Test note pinning"""
        note = Note(title="Test", content="Content", is_pinned=True)
        assert note.is_pinned == True
    
    def test_note_create_model(self):
        """Test NoteCreate model"""
        note = NoteCreate(
            title="Test",
            content="Content",
            tags=["tag1", "tag2"]
        )
        assert note.title == "Test"
        assert note.tags == ["tag1", "tag2"]
    
    def test_note_create_with_string_tags(self):
        """Test NoteCreate with comma-separated tags"""
        note = NoteCreate(
            title="Test",
            content="Content",
            tags="tag1, tag2, tag3"
        )
        assert len(note.tags) == 3
    
    def test_note_update_model(self):
        """Test NoteUpdate model"""
        update = NoteUpdate(
            title="Updated Title",
            tags=["new", "tags"]
        )
        assert update.title == "Updated Title"
        assert update.tags == ["new", "tags"]


class TestNoteStorage:
    """Test cases for NoteStorage"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        storage = NoteStorage(data_file=temp_file, backup=False)
        yield storage
        os.unlink(temp_file)
    
    def test_create_note(self, temp_storage):
        """Test creating a note"""
        note = Note(title="Test", content="Content", tags=["test"])
        created = temp_storage.create(note)
        assert created.id is not None
        assert created.title == "Test"
    
    def test_get_all_notes(self, temp_storage):
        """Test getting all notes"""
        note1 = Note(title="Note 1", content="Content 1")
        note2 = Note(title="Note 2", content="Content 2")
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        notes = temp_storage.get_all()
        assert len(notes) == 2
    
    def test_get_note_by_id(self, temp_storage):
        """Test getting note by ID"""
        note = Note(title="Test", content="Content")
        created = temp_storage.create(note)
        
        retrieved = temp_storage.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.title == "Test"
    
    def test_get_note_by_id_not_found(self, temp_storage):
        """Test getting non-existent note"""
        result = temp_storage.get_by_id("non-existent-id")
        assert result is None
    
    def test_update_note(self, temp_storage):
        """Test updating a note"""
        note = Note(title="Original", content="Original content")
        created = temp_storage.create(note)
        
        created.title = "Updated"
        updated = temp_storage.update(created.id, created)
        
        assert updated.title == "Updated"
        assert updated.updated_at > created.created_at
    
    def test_delete_note(self, temp_storage):
        """Test deleting a note"""
        note = Note(title="Test", content="Content")
        created = temp_storage.create(note)
        
        success = temp_storage.delete(created.id)
        assert success is True
        
        retrieved = temp_storage.get_by_id(created.id)
        assert retrieved is None
    
    def test_filter_by_tag(self, temp_storage):
        """Test filtering notes by tag"""
        note1 = Note(title="Tagged", content="Content", tags=["work"])
        note2 = Note(title="Untagged", content="Content", tags=[])
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        work_notes = temp_storage.get_all(tag="work")
        assert len(work_notes) == 1
        assert work_notes[0].title == "Tagged"
    
    def test_search_notes(self, temp_storage):
        """Test searching notes"""
        note1 = Note(title="Python Guide", content="Learn Python programming")
        note2 = Note(title="JavaScript Guide", content="Learn JavaScript")
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        results = temp_storage.search("Python")
        assert len(results) == 1
        assert results[0].title == "Python Guide"
    
    def test_get_by_priority(self, temp_storage):
        """Test getting notes by priority"""
        note1 = Note(title="High Priority", content="Content", priority=NotePriority.HIGH)
        note2 = Note(title="Low Priority", content="Content", priority=NotePriority.LOW)
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        high_notes = temp_storage.get_by_priority(NotePriority.HIGH)
        assert len(high_notes) == 1
        assert high_notes[0].title == "High Priority"
    
    def test_pin_note(self, temp_storage):
        """Test pinning a note"""
        note = Note(title="Test", content="Content")
        created = temp_storage.create(note)
        
        pinned = temp_storage.pin(created.id)
        assert pinned.is_pinned == True
    
    def test_archive_note(self, temp_storage):
        """Test archiving a note"""
        note = Note(title="Test", content="Content")
        created = temp_storage.create(note)
        
        archived = temp_storage.archive(created.id)
        assert archived.is_archived == True
    
    def test_get_stats(self, temp_storage):
        """Test getting note statistics"""
        note1 = Note(title="Note 1", content="Content 1", priority=NotePriority.HIGH)
        note2 = Note(title="Note 2", content="Content 2", priority=NotePriority.LOW)
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        stats = temp_storage.get_stats()
        assert stats.total_notes == 2
        assert "high" in stats.notes_by_priority
        assert "low" in stats.notes_by_priority
    
    def test_bulk_delete(self, temp_storage):
        """Test bulk deleting notes"""
        note1 = Note(title="Note 1", content="Content 1")
        note2 = Note(title="Note 2", content="Content 2")
        note3 = Note(title="Note 3", content="Content 3")
        
        created1 = temp_storage.create(note1)
        created2 = temp_storage.create(note2)
        temp_storage.create(note3)
        
        deleted = temp_storage.bulk_delete([created1.id, created2.id])
        assert deleted == 2
        
        remaining = temp_storage.get_all()
        assert len(remaining) == 1
    
    def test_clear_all(self, temp_storage):
        """Test clearing all notes"""
        note1 = Note(title="Note 1", content="Content 1")
        note2 = Note(title="Note 2", content="Content 2")
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        count = temp_storage.clear_all()
        assert count == 2
        
        remaining = temp_storage.get_all()
        assert len(remaining) == 0


class TestExceptions:
    """Test cases for exceptions"""
    
    def test_note_not_found_error(self):
        """Test NoteNotFoundError"""
        error = NoteNotFoundError("test-id")
        assert "test-id" in str(error)
    
    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError("Invalid input")
        assert "Invalid input" in str(error)


class TestAPIEndpoints:
    """Integration tests for API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_create_note_endpoint(self):
        """Test creating note via API"""
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        response = client.post(
            "/api/notes",
            json={"title": "API Test", "content": "Test content", "tags": ["test"]}
        )
        
        # API returns 201 Created for new resources
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API Test"
        assert "id" in data
    
    def test_list_notes_endpoint(self):
        """Test listing notes via API"""
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        
        # Create a note first
        client.post(
            "/api/notes",
            json={"title": "Test Note", "content": "Test content"}
        )
        
        # List notes
        response = client.get("/api/notes")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_note_endpoint(self):
        """Test getting a single note"""
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        
        # Create a note
        create_response = client.post(
            "/api/notes",
            json={"title": "Test", "content": "Content"}
        )
        note_id = create_response.json()["id"]
        
        # Get the note
        response = client.get(f"/api/notes/{note_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test"
    
    def test_update_note_endpoint(self):
        """Test updating a note"""
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        
        # Create a note
        create_response = client.post(
            "/api/notes",
            json={"title": "Original", "content": "Original content"}
        )
        note_id = create_response.json()["id"]
        
        # Update the note
        response = client.put(
            f"/api/notes/{note_id}",
            json={"title": "Updated"}
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
    
    def test_delete_note_endpoint(self):
        """Test deleting a note"""
        from fastapi.testclient import TestClient
        from api.main import app
        
        client = TestClient(app)
        
        # Create a note
        create_response = client.post(
            "/api/notes",
            json={"title": "To Delete", "content": "Content"}
        )
        note_id = create_response.json()["id"]
        
        # Delete the note
        response = client.delete(f"/api/notes/{note_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/notes/{note_id}")
        assert get_response.status_code == 404


class TestValidators:
    """Test cases for validators"""
    
    def test_note_validator_valid(self):
        """Test validation with valid data"""
        from noteiq.validators import NoteValidator
        
        # Should not raise
        NoteValidator.validate_note("Title", "Content", ["tag1", "tag2"])
    
    def test_note_validator_empty_title(self):
        """Test validation with empty title"""
        from noteiq.validators import NoteValidator
        
        with pytest.raises(ValidationError):
            NoteValidator.validate_title("")
    
    def test_note_validator_long_title(self):
        """Test validation with long title"""
        from noteiq.validators import NoteValidator
        
        with pytest.raises(ValidationError):
            NoteValidator.validate_title("a" * 201)
    
    def test_note_validator_too_many_tags(self):
        """Test validation with too many tags"""
        from noteiq.validators import NoteValidator
        
        with pytest.raises(ValidationError):
            NoteValidator.validate_tags(["tag"] * 21)
    
    def test_api_key_validator(self):
        """Test API key validation"""
        from noteiq.validators import APIKeyValidator
        
        assert APIKeyValidator.validate_openai_key("sk-abc123defghijklmnopqrstuvwxyz1234567890") == True
        assert APIKeyValidator.validate_openai_key("") == False
        assert APIKeyValidator.validate_openai_key("invalid") == False
    
    def test_note_validator_content(self):
        """Test content validation"""
        from noteiq.validators import NoteValidator
        
        # Valid content should not raise
        NoteValidator.validate_content("Some content")
        
        # Empty content should raise
        with pytest.raises(ValidationError):
            NoteValidator.validate_content("")
    
    def test_note_validator_tag_characters(self):
        """Test tag character validation"""
        from noteiq.validators import NoteValidator
        
        # Valid tags should not raise
        NoteValidator.validate_tags(["tag1", "tag_2", "tag-3"])
        
        # Invalid tag characters should raise
        with pytest.raises(ValidationError):
            NoteValidator.validate_tags(["tag with spaces"])
    
    def test_note_validator_tag_length(self):
        """Test tag length validation"""
        from noteiq.validators import NoteValidator
        
        # Valid tag length should not raise
        NoteValidator.validate_tags(["a" * 50])
        
        # Too long tag should raise
        with pytest.raises(ValidationError):
            NoteValidator.validate_tags(["a" * 51])


class TestAI:
    """Test cases for AI module"""
    
    def test_ai_init_without_key(self):
        """Test AI initialization without API key"""
        import os
        # Save original value
        original = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = ""
        
        from noteiq.ai import AINotes
        from noteiq.exceptions import APIKeyError
        
        with pytest.raises(APIKeyError):
            AINotes()
        
        # Restore
        if original:
            os.environ["OPENAI_API_KEY"] = original
    
    def test_prompt_formatting(self):
        """Test prompt formatting"""
        from noteiq.ai import AINotes
        
        # Mock the API key for testing
        import os
        os.environ["OPENAI_API_KEY"] = "sk-test12345678901234567890123456789012"
        
        ai = AINotes()
        system, user = ai._format_prompt("summarize", content="Test content")
        
        assert "summarize" in system.lower() or "note" in system.lower()
        assert "Test content" in user


class TestConfig:
    """Test cases for configuration"""
    
    def test_config_defaults(self):
        """Test default configuration"""
        from noteiq.config import Config
        
        config = Config()
        
        assert config.openai_model == "gpt-3.5-turbo"
        assert config.openai_temperature == 0.7
        assert config.openai_max_tokens == 1000
        assert config.storage_file == "notes.json"
        assert config.api_port == 8000
    
    def test_config_set_api_key(self):
        """Test setting API key"""
        from noteiq.config import Config
        import os
        
        config = Config()
        test_key = "sk-test12345678901234567890123456789012"
        config.set_api_key(test_key)
        
        assert config.openai_api_key == test_key
        assert config.enable_ai == True


class TestStorageAdvanced:
    """Advanced storage test cases"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        storage = NoteStorage(data_file=temp_file, backup=False)
        yield storage
        os.unlink(temp_file)
    
    def test_get_by_title(self, temp_storage):
        """Test getting notes by title"""
        note1 = Note(title="Python Tutorial", content="Learn Python")
        note2 = Note(title="JavaScript Guide", content="Learn JavaScript")
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        results = temp_storage.get_by_title("python")
        assert len(results) == 1
        assert results[0].title == "Python Tutorial"
    
    def test_get_pinned(self, temp_storage):
        """Test getting pinned notes"""
        note1 = Note(title="Pinned Note", content="Content", is_pinned=True)
        note2 = Note(title="Regular Note", content="Content", is_pinned=False)
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        pinned = temp_storage.get_pinned()
        assert len(pinned) == 1
        assert pinned[0].title == "Pinned Note"
    
    def test_get_archived(self, temp_storage):
        """Test getting archived notes"""
        note1 = Note(title="Active Note", content="Content", is_archived=False)
        note2 = Note(title="Archived Note", content="Content", is_archived=True)
        temp_storage.create(note1)
        temp_storage.create(note2)
        
        archived = temp_storage.get_archived()
        assert len(archived) == 1
        assert archived[0].title == "Archived Note"
    
    def test_unarchive_note(self, temp_storage):
        """Test unarchiving a note"""
        note = Note(title="Test", content="Content")
        created = temp_storage.create(note)
        
        # Archive
        temp_storage.archive(created.id)
        archived = temp_storage.get_archived()
        assert len(archived) == 1
        
        # Unarchive
        temp_storage.unarchive(created.id)
        archived = temp_storage.get_archived()
        assert len(archived) == 0
    
    def test_unpin_note(self, temp_storage):
        """Test unpinning a note"""
        note = Note(title="Test", content="Content")
        created = temp_storage.create(note)
        
        # Pin
        temp_storage.pin(created.id)
        pinned = temp_storage.get_pinned()
        assert len(pinned) == 1
        
        # Unpin
        temp_storage.unpin(created.id)
        pinned = temp_storage.get_pinned()
        assert len(pinned) == 0