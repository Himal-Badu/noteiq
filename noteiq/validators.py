"""
Validation utilities for NoteIQ
"""
import re
from typing import List, Optional
from noteiq.exceptions import ValidationError


class NoteValidator:
    """Validator for note data"""
    
    # Title constraints
    MIN_TITLE_LENGTH = 1
    MAX_TITLE_LENGTH = 200
    
    # Content constraints
    MIN_CONTENT_LENGTH = 1
    MAX_CONTENT_LENGTH = 100000
    
    # Tag constraints
    MAX_TAGS = 20
    MAX_TAG_LENGTH = 50
    
    @classmethod
    def validate_title(cls, title: str) -> None:
        """
        Validate note title.
        
        Args:
            title: Note title to validate
            
        Raises:
            ValidationError: If title is invalid
        """
        if not title:
            raise ValidationError("Title cannot be empty")
        
        if len(title) < cls.MIN_TITLE_LENGTH:
            raise ValidationError(f"Title must be at least {cls.MIN_TITLE_LENGTH} characters")
        
        if len(title) > cls.MAX_TITLE_LENGTH:
            raise ValidationError(f"Title cannot exceed {cls.MAX_TITLE_LENGTH} characters")
    
    @classmethod
    def validate_content(cls, content: str) -> None:
        """
        Validate note content.
        
        Args:
            content: Note content to validate
            
        Raises:
            ValidationError: If content is invalid
        """
        if not content:
            raise ValidationError("Content cannot be empty")
        
        if len(content) < cls.MIN_CONTENT_LENGTH:
            raise ValidationError(f"Content must be at least {cls.MIN_CONTENT_LENGTH} characters")
        
        if len(content) > cls.MAX_CONTENT_LENGTH:
            raise ValidationError(f"Content cannot exceed {cls.MAX_CONTENT_LENGTH} characters")
    
    @classmethod
    def validate_tags(cls, tags: List[str]) -> None:
        """
        Validate note tags.
        
        Args:
            tags: List of tags to validate
            
        Raises:
            ValidationError: If tags are invalid
        """
        if len(tags) > cls.MAX_TAGS:
            raise ValidationError(f"Cannot have more than {cls.MAX_TAGS} tags")
        
        for tag in tags:
            if len(tag) > cls.MAX_TAG_LENGTH:
                raise ValidationError(f"Tag '{tag}' exceeds maximum length of {cls.MAX_TAG_LENGTH}")
            
            if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
                raise ValidationError(f"Tag '{tag}' contains invalid characters. Use only letters, numbers, hyphens, and underscores")
    
    @classmethod
    def validate_note(cls, title: str, content: str, tags: Optional[List[str]] = None) -> None:
        """
        Validate entire note.
        
        Args:
            title: Note title
            content: Note content
            tags: Optional list of tags
            
        Raises:
            ValidationError: If any validation fails
        """
        cls.validate_title(title)
        cls.validate_content(content)
        
        if tags:
            cls.validate_tags(tags)


class APIKeyValidator:
    """Validator for API keys"""
    
    @staticmethod
    def validate_openai_key(api_key: str) -> bool:
        """
        Validate OpenAI API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not api_key:
            return False
        
        # OpenAI keys start with 'sk-' and are at least 40 characters
        return api_key.startswith("sk-") and len(api_key) >= 40
    
    @staticmethod
    def validate_env_var(var_name: str) -> bool:
        """
        Validate environment variable is set.
        
        Args:
            var_name: Name of environment variable
            
        Returns:
            True if set, False otherwise
        """
        import os
        return bool(os.getenv(var_name))