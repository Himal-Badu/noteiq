import os
from typing import List
from openai import OpenAI


class AINotes:
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    def _call(self, system: str, user: str) -> str:
        """Make an API call to OpenAI."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()

    def summarize(self, note_content: str) -> str:
        """Generate a concise summary of the note."""
        system = "You are a note-taking assistant. Summarize notes in 3-5 bullet points."
        user = f"Summarize this note:\n\n{note_content}"
        return self._call(system, user)

    def extract_actions(self, note_content: str) -> List[str]:
        """Extract action items/tasks from the note."""
        system = "Extract action items from notes. Return as a numbered list. If none, say 'No action items found.'"
        user = f"Extract action items from:\n\n{note_content}"
        result = self._call(system, user)
        
        # Parse into list
        items = []
        for line in result.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                clean = line.lstrip("0123456789.-•) ").strip()
                if clean and "no action items" not in clean.lower():
                    items.append(clean)
        return items if items else [result] if result else ["No action items found"]

    def answer_question(self, note_content: str, question: str) -> str:
        """Answer a question about the note."""
        system = "Answer questions based ONLY on the provided note. If not in note, say 'I don't have that info.'"
        user = f"Note:\n{note_content}\n\nQuestion: {question}"
        return self._call(system, user)

    def generate_outline(self, note_content: str) -> List[str]:
        """Generate an outline from the note."""
        system = "Create a structured outline. Use proper indentation with → for subpoints."
        user = f"Create an outline for:\n\n{note_content}"
        result = self._call(system, user)
        
        # Parse into list
        outline = []
        for line in result.split("\n"):
            line = line.strip()
            if line:
                outline.append(line)
        return outline if outline else [result]