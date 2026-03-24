"""
AI module for NoteIQ
Handles all AI-powered features using OpenAI
"""
import os
from typing import List, Optional, Dict, Any
from openai import OpenAI, RateLimitError, APIError
from noteiq.exceptions import AIError, APIKeyError
from noteiq.utils import logger, log_info, log_error, log_warning


class AINotes:
    """AI-powered note processing"""
    
    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1000
    
    # System prompts for different operations
    PROMPTS = {
        "summarize": {
            "system": "You are a note-taking assistant. Create concise summaries in 3-5 bullet points. Focus on key takeaways and action items.",
            "user": "Summarize this note in bullet points:\n\n{content}"
        },
        "actions": {
            "system": "Extract actionable items from notes. Return as a numbered list with clear, specific actions. If none exist, state 'No action items found.'",
            "user": "Extract all action items from:\n\n{content}"
        },
        "qa": {
            "system": "Answer questions based ONLY on the provided note. If the information is not in the note, clearly state 'I don't have that information from the note.' Provide direct answers.",
            "user": "Note:\n{content}\n\nQuestion: {question}"
        },
        "outline": {
            "system": "Create a structured outline. Use proper markdown formatting with headers and subpoints. Make it logical and easy to follow.",
            "user": "Create an outline for:\n\n{content}"
        },
        "tags": {
            "system": "Suggest relevant tags for notes. Return only a comma-separated list of tags. Be concise and practical.",
            "user": "Suggest 3-5 relevant tags for this note:\n\n{content}"
        },
        "keywords": {
            "system": "Extract important keywords from text. Return as comma-separated list.",
            "user": "Extract key topics/keywords from:\n\n{content}"
        },
        "improve": {
            "system": "Improve the clarity and structure of the note. Keep the original meaning but make it more readable.",
            "user": "Improve this note:\n\n{content}"
        }
    }
    
    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        api_key: str = None
    ):
        """
        Initialize AI handler.
        
        Args:
            model: OpenAI model to use (default: gpt-3.5-turbo)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Max tokens to generate (default: 1000)
            api_key: OpenAI API key (default: from env)
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise APIKeyError("OpenAI")
        
        # Initialize client
        self.client = OpenAI(api_key=self.api_key)
        
        # Set defaults
        self.model = model or self.DEFAULT_MODEL
        self.temperature = temperature or self.DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        
        log_info(f"AI initialized with model: {self.model}")

    def _call(self, system: str, user: str) -> str:
        """
        Make an API call to OpenAI.
        
        Args:
            system: System prompt
            user: User prompt
            
        Returns:
            Generated text response
            
        Raises:
            AIError: If API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else ""
            
        except RateLimitError as e:
            log_error(f"Rate limit exceeded: {e}")
            raise AIError("Rate limit exceeded. Please try again later.")
        except APIError as e:
            log_error(f"API error: {e}")
            raise AIError(f"API error: {str(e)}")
        except Exception as e:
            log_error(f"Unexpected error: {e}")
            raise AIError(f"Unexpected error: {str(e)}")

    def _format_prompt(self, prompt_key: str, **kwargs) -> tuple:
        """
        Format a prompt with variables.
        
        Args:
            prompt_key: Key from PROMPTS dict
            **kwargs: Variables to format prompt with
            
        Returns:
            Tuple of (system, user) prompts
        """
        prompt = self.PROMPTS.get(prompt_key, {})
        system = prompt.get("system", "")
        user_template = prompt.get("user", "{content}")
        
        # Format user prompt with provided variables
        user = user_template.format(**kwargs)
        
        return system, user

    def summarize(self, note_content: str) -> str:
        """
        Generate a concise summary of the note.
        
        Args:
            note_content: Content to summarize
            
        Returns:
            Summary text
        """
        log_info("Generating summary...")
        system, user = self._format_prompt("summarize", content=note_content)
        return self._call(system, user)

    def extract_actions(self, note_content: str) -> List[str]:
        """
        Extract action items/tasks from the note.
        
        Args:
            note_content: Content to extract from
            
        Returns:
            List of action items
        """
        log_info("Extracting action items...")
        system, user = self._format_prompt("actions", content=note_content)
        result = self._call(system, user)
        
        # Parse into list
        items = []
        for line in result.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                # Remove leading numbers/bullets
                clean = line.lstrip("0123456789.-•) ").strip()
                if clean and "no action items" not in clean.lower():
                    items.append(clean)
        
        return items if items else [result] if result else ["No action items found"]

    def answer_question(self, note_content: str, question: str) -> str:
        """
        Answer a question about the note.
        
        Args:
            note_content: Note content
            question: Question to answer
            
        Returns:
            Answer text
        """
        log_info(f"Answering question: {question}")
        system, user = self._format_prompt("qa", content=note_content, question=question)
        return self._call(system, user)

    def generate_outline(self, note_content: str) -> List[str]:
        """
        Generate an outline from the note.
        
        Args:
            note_content: Content to create outline from
            
        Returns:
            List of outline items
        """
        log_info("Generating outline...")
        system, user = self._format_prompt("outline", content=note_content)
        result = self._call(system, user)
        
        # Parse into list
        outline = []
        for line in result.split("\n"):
            line = line.strip()
            if line:
                outline.append(line)
        
        return outline if outline else [result]

    def suggest_tags(self, note_content: str) -> List[str]:
        """
        Suggest tags for a note.
        
        Args:
            note_content: Content to suggest tags for
            
        Returns:
            List of suggested tags
        """
        log_info("Suggesting tags...")
        system, user = self._format_prompt("tags", content=note_content)
        result = self._call(system, user)
        
        # Parse into list
        tags = [t.strip() for t in result.split(",")]
        return [t for t in tags if t]

    def extract_keywords(self, note_content: str) -> List[str]:
        """
        Extract keywords from note content.
        
        Args:
            note_content: Content to extract keywords from
            
        Returns:
            List of keywords
        """
        log_info("Extracting keywords...")
        system, user = self._format_prompt("keywords", content=note_content)
        result = self._call(system, user)
        
        # Parse into list
        keywords = [k.strip() for k in result.split(",")]
        return [k for k in keywords if k]

    def improve_note(self, note_content: str) -> str:
        """
        Improve note clarity and structure.
        
        Args:
            note_content: Original content
            
        Returns:
            Improved content
        """
        log_info("Improving note...")
        system, user = self._format_prompt("improve", content=note_content)
        return self._call(system, user)

    def analyze_note(self, note_content: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a note.
        
        Args:
            note_content: Content to analyze
            
        Returns:
            Dictionary with analysis results
        """
        log_info("Analyzing note...")
        
        return {
            "summary": self.summarize(note_content),
            "action_items": self.extract_actions(note_content),
            "outline": self.generate_outline(note_content),
            "tags": self.suggest_tags(note_content),
            "keywords": self.extract_keywords(note_content)
        }

    def set_model(self, model: str):
        """Change the AI model"""
        self.model = model
        log_info(f"Model changed to: {model}")

    def set_temperature(self, temperature: float):
        """Change the temperature"""
        if 0 <= temperature <= 2:
            self.temperature = temperature
            log_info(f"Temperature changed to: {temperature}")
        else:
            log_warning("Temperature must be between 0 and 2")

    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        return [
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo"
        ]