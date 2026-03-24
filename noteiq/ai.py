"""
Enhanced AI module for NoteIQ
Handles all AI-powered features using OpenAI with improved prompts and caching
"""
import os
from typing import List, Optional, Dict, Any
from openai import OpenAI, RateLimitError, APIError
from noteiq.exceptions import AIError, APIKeyError
from noteiq.utils import logger, log_info, log_error, log_warning
from noteiq.cache import cache_ai_response, get_ai_response


class AINotes:
    """AI-powered note processing with enhanced features"""
    
    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1000
    
    # Enhanced system prompts for different operations
    PROMPTS = {
        "summarize": {
            "system": "You are an expert note-taking assistant. Create concise, actionable summaries in 3-5 bullet points. Focus on key takeaways, action items, and important details. Use clear, professional language.",
            "user": "Summarize this note in bullet points:\n\n{content}"
        },
        "summarize_detailed": {
            "system": "You are an expert note-taking assistant. Create a comprehensive summary including key points, main themes, important details, and actionable items. Structure your response clearly.",
            "user": "Provide a detailed summary of:\n\n{content}"
        },
        "actions": {
            "system": "Extract actionable items from notes. Return as a numbered list with clear, specific actions. If none exist, state 'No action items found.' Mark any items that seem time-sensitive or urgent.",
            "user": "Extract all action items from:\n\n{content}"
        },
        "prioritize_actions": {
            "system": "Analyze action items and categorize them by priority (high, medium, low). Consider urgency, importance, and dependencies. Return a structured list with priority labels.",
            "user": "Prioritize these action items:\n\n{content}"
        },
        "qa": {
            "system": "Answer questions based ONLY on the provided note. If the information is not in the note, clearly state 'I don't have that information from the note.' Provide direct, accurate answers. If unsure, say so.",
            "user": "Note:\n{content}\n\nQuestion: {question}"
        },
        "outline": {
            "system": "Create a well-structured outline with proper hierarchy. Use markdown formatting (# for main sections, ## for subsections). Make it logical and easy to follow.",
            "user": "Create an outline for:\n\n{content}"
        },
        "outline_detailed": {
            "system": "Create a detailed, multi-level outline. Use markdown headers (#, ##, ###) to show hierarchy. Include brief descriptions for each section.",
            "user": "Create a detailed outline for:\n\n{content}"
        },
        "tags": {
            "system": "Suggest relevant, practical tags for notes. Return only a comma-separated list of 3-8 tags. Use lowercase, hyphenated names. Focus on categorization and discoverability.",
            "user": "Suggest relevant tags for this note:\n\n{content}"
        },
        "keywords": {
            "system": "Extract important keywords and topics from text. Return as comma-separated list. Focus on significant concepts, entities, and themes.",
            "user": "Extract key topics/keywords from:\n\n{content}"
        },
        "improve": {
            "system": "Improve the clarity, structure, and professionalism of the note. Keep the original meaning but enhance readability. Fix grammar issues. Improve organization.",
            "user": "Improve this note:\n\n{content}"
        },
        "expand": {
            "system": "Expand the note with relevant details, examples, and context. Maintain the original intent while adding value. Keep a professional tone.",
            "user": "Expand on this note with more details:\n\n{content}"
        },
        "sentiment": {
            "system": "Analyze the emotional tone of the text. Return a single word: positive, negative, neutral, or mixed. Also provide a brief explanation.",
            "user": "Analyze the sentiment of:\n\n{content}"
        },
        "writing_style": {
            "system": "Analyze the writing style and provide feedback. Consider clarity, tone, structure, and professionalism. Provide constructive suggestions.",
            "user": "Analyze the writing style of:\n\n{content}"
        },
        "questions": {
            "system": "Generate thoughtful questions that this note raises or could answer. These help with further exploration of the topic.",
            "user": "Generate questions prompted by this note:\n\n{content}"
        },
        "translate": {
            "system": "Translate the content accurately while maintaining the original meaning and tone. Preserve formatting where possible.",
            "user": "Translate this to {language}:\n\n{content}"
        },
        "tl_dr": {
            "system": "Create an extremely brief one-sentence summary (TL;DR). Capture the essence in 10-15 words maximum.",
            "user": "Create a TL;DR for:\n\n{content}"
        }
    }
    
    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        api_key: str = None,
        enable_cache: bool = True
    ):
        """
        Initialize AI handler.
        
        Args:
            model: OpenAI model to use (default: gpt-3.5-turbo)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Max tokens to generate (default: 1000)
            api_key: OpenAI API key (default: from env)
            enable_cache: Enable caching for responses (default: True)
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
        self.enable_cache = enable_cache
        
        log_info(f"AI initialized with model: {self.model}")

    def _generate_cache_key(self, prompt_key: str, **kwargs) -> str:
        """Generate cache key for a request"""
        content = kwargs.get("content", "")[:100]
        return f"{prompt_key}:{content}"

    def _call(self, system: str, user: str, use_cache: bool = True) -> str:
        """
        Make an API call to OpenAI.
        
        Args:
            system: System prompt
            user: User prompt
            use_cache: Whether to use caching
            
        Returns:
            Generated text response
            
        Raises:
            AIError: If API call fails
        """
        # Try cache first
        if use_cache and self.enable_cache:
            cache_key = f"ai:{hash(user)}"
            cached = get_ai_response(cache_key)
            if cached:
                log_info("Using cached AI response")
                return cached
        
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
            result = content.strip() if content else ""
            
            # Cache the response
            if use_cache and self.enable_cache:
                cache_key = f"ai:{hash(user)}"
                cache_ai_response(cache_key, result)
            
            return result
            
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

    def summarize(self, note_content: str, detailed: bool = False) -> str:
        """
        Generate a concise summary of the note.
        
        Args:
            note_content: Content to summarize
            detailed: Generate detailed summary
            
        Returns:
            Summary text
        """
        log_info("Generating summary...")
        prompt_key = "summarize_detailed" if detailed else "summarize"
        system, user = self._format_prompt(prompt_key, content=note_content)
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

    def prioritize_actions(self, note_content: str) -> Dict[str, List[str]]:
        """
        Prioritize action items from the note.
        
        Args:
            note_content: Content to extract from
            
        Returns:
            Dictionary with prioritized actions
        """
        log_info("Prioritizing action items...")
        system, user = self._format_prompt("prioritize_actions", content=note_content)
        result = self._call(system, user)
        
        # Parse into priority categories
        prioritized = {"high": [], "medium": [], "low": []}
        current_priority = "high"
        
        for line in result.split("\n"):
            line = line.strip().lower()
            if "high" in line and ("priority" in line or "urgent" in line):
                current_priority = "high"
            elif "medium" in line or "normal" in line:
                current_priority = "medium"
            elif "low" in line:
                current_priority = "low"
            elif line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                clean = line.lstrip("0123456789.-•) ").strip()
                if clean:
                    prioritized[current_priority].append(clean)
        
        return prioritized

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

    def generate_outline(self, note_content: str, detailed: bool = False) -> List[str]:
        """
        Generate an outline from the note.
        
        Args:
            note_content: Content to create outline from
            detailed: Generate detailed outline
            
        Returns:
            List of outline items
        """
        log_info("Generating outline...")
        prompt_key = "outline_detailed" if detailed else "outline"
        system, user = self._format_prompt(prompt_key, content=note_content)
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
        tags = [t.strip().lower() for t in result.split(",")]
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

    def expand_note(self, note_content: str) -> str:
        """
        Expand note with more details.
        
        Args:
            note_content: Original content
            
        Returns:
            Expanded content
        """
        log_info("Expanding note...")
        system, user = self._format_prompt("expand", content=note_content)
        return self._call(system, user)

    def analyze_sentiment(self, note_content: str) -> Dict[str, str]:
        """
        Analyze sentiment of note content.
        
        Args:
            note_content: Content to analyze
            
        Returns:
            Dictionary with sentiment and explanation
        """
        log_info("Analyzing sentiment...")
        system, user = self._format_prompt("sentiment", content=note_content)
        result = self._call(system, user)
        
        # Parse result
        lines = result.split("\n")
        sentiment = "neutral"
        explanation = result
        
        for line in lines:
            line_lower = line.lower().strip()
            if "positive" in line_lower:
                sentiment = "positive"
                break
            elif "negative" in line_lower:
                sentiment = "negative"
                break
            elif "mixed" in line_lower:
                sentiment = "mixed"
                break
        
        return {"sentiment": sentiment, "explanation": explanation}

    def analyze_writing_style(self, note_content: str) -> str:
        """
        Analyze writing style and provide feedback.
        
        Args:
            note_content: Content to analyze
            
        Returns:
            Style analysis
        """
        log_info("Analyzing writing style...")
        system, user = self._format_prompt("writing_style", content=note_content)
        return self._call(system, user)

    def generate_questions(self, note_content: str) -> List[str]:
        """
        Generate questions prompted by the note.
        
        Args:
            note_content: Content to generate questions from
            
        Returns:
            List of questions
        """
        log_info("Generating questions...")
        system, user = self._format_prompt("questions", content=note_content)
        result = self._call(system, user)
        
        # Parse into list
        questions = []
        for line in result.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("?")):
                clean = line.lstrip("0123456789.?- ").strip()
                if clean and clean not in questions:
                    questions.append(clean)
        
        return questions if questions else [result] if result else []

    def translate(self, note_content: str, language: str = "Spanish") -> str:
        """
        Translate note content.
        
        Args:
            note_content: Content to translate
            language: Target language
            
        Returns:
            Translated content
        """
        log_info(f"Translating to {language}...")
        system, user = self._format_prompt("translate", content=note_content, language=language)
        return self._call(system, user)

    def generate_tldr(self, note_content: str) -> str:
        """
        Generate TL;DR summary.
        
        Args:
            note_content: Content to summarize
            
        Returns:
            TL;DR summary
        """
        log_info("Generating TL;DR...")
        system, user = self._format_prompt("tl_dr", content=note_content)
        return self._call(system, user)

    def estimate_reading_time(self, note_content: str) -> int:
        """
        Estimate reading time in minutes.
        
        Args:
            note_content: Content to estimate
            
        Returns:
            Estimated minutes
        """
        words = len(note_content.split())
        # Average reading speed: 200-250 words per minute
        minutes = max(1, round(words / 225))
        return minutes

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
            "detailed_summary": self.summarize(note_content, detailed=True),
            "action_items": self.extract_actions(note_content),
            "prioritized_actions": self.prioritize_actions(note_content),
            "outline": self.generate_outline(note_content),
            "detailed_outline": self.generate_outline(note_content, detailed=True),
            "tags": self.suggest_tags(note_content),
            "keywords": self.extract_keywords(note_content),
            "sentiment": self.analyze_sentiment(note_content),
            "questions": self.generate_questions(note_content),
            "tldr": self.generate_tldr(note_content),
            "reading_time": self.estimate_reading_time(note_content)
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

    def set_max_tokens(self, max_tokens: int):
        """Change max tokens"""
        self.max_tokens = max_tokens
        log_info(f"Max tokens changed to: {max_tokens}")

    def enable_caching(self):
        """Enable response caching"""
        self.enable_cache = True
        log_info("Caching enabled")

    def disable_caching(self):
        """Disable response caching"""
        self.enable_cache = False
        log_info("Caching disabled")

    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        return [
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
