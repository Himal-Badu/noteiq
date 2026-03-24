import click
import os
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

import json
from noteiq.models import Note, NoteCreate, NoteUpdate, NotePriority
from noteiq.storage import NoteStorage
from noteiq.ai import AINotes
from noteiq.exceptions import APIKeyError, NoteNotFoundError
from noteiq.utils import logger


storage = NoteStorage()


@click.group()
@click.version_option(version="1.1.0")
def cli():
    """NoteIQ - AI-Powered Notes Application
    
    Create, organize, and interact with your notes using AI.
    """
    pass


@cli.command()
@click.argument("title")
@click.option("--content", "-c", "content", required=True, help="Note content")
@click.option("--tags", "-t", help="Tags for the note (comma-separated)")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high"]), default="medium", help="Note priority")
def add(title, content, tags, priority):
    """Add a new note."""
    try:
        note = Note(
            title=title,
            content=content,
            tags=[t.strip() for t in tags.split(",")] if tags else [],
            priority=NotePriority(priority)
        )
        created = storage.create(note)
        click.echo(f"✓ Note created: {created.id}")
        click.echo(f"  Title: {created.title}")
        if created.tags:
            click.echo(f"  Tags: {', '.join(created.tags)}")
        click.echo(f"  Priority: {created.priority}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option("--tag", "-t", help="Filter by tag")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high"]), help="Filter by priority")
@click.option("--archived", is_flag=True, help="Include archived notes")
@click.option("--limit", "-l", type=int, default=50, help="Limit number of notes")
def list(tag, priority, archived, limit):
    """List all notes."""
    try:
        notes = storage.get_all(tag=tag, include_archived=archived)
        
        if priority:
            notes = [n for n in notes if n.priority == priority]
        
        notes = notes[:limit]
        
        if not notes:
            click.echo("No notes found.")
            return
        
        click.echo(f"\nFound {len(notes)} note(s):\n")
        
        for n in notes:
            pin_indicator = "📌 " if n.is_pinned else "  "
            priority_indicator = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(n.priority, "  ")
            
            tags_str = f" [{', '.join(n.tags)}]" if n.tags else ""
            click.echo(f"{pin_indicator}{priority_indicator} {n.id[:8]} | {n.title}{tags_str}")
            click.echo(f"        {n.content[:80]}{'...' if len(n.content) > 80 else ''}")
            click.echo("")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("note_id")
def get(note_id):
    """View a specific note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
            return
        
        click.echo(f"\n{click.style('Title:', bold=True)} {note.title}")
        
        priority_emoji = {
            "high": "🔴 High",
            "medium": "🟡 Medium",
            "low": "🟢 Low"
        }.get(note.priority, note.priority)
        
        click.echo(f"{click.style('Priority:', bold=True)} {priority_emoji}")
        click.echo(f"{click.style('Tags:', bold=True)} {', '.join(note.tags) if note.tags else 'None'}")
        click.echo(f"{click.style('Pinned:', bold=True)} {'Yes' if note.is_pinned else 'No'}")
        click.echo(f"{click.style('Created:', bold=True)} {note.created_at}")
        click.echo(f"{click.style('Updated:', bold=True)} {note.updated_at}")
        click.echo(f"\n{click.style('Content:', bold=True)}\n{note.content}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("note_id")
def delete(note_id):
    """Delete a note."""
    try:
        success = storage.delete(note_id)
        if success:
            click.echo(f"✓ Note deleted: {note_id[:8]}")
        else:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("note_id")
@click.option("--title", "-t", help="New title")
@click.option("--content", "-c", help="New content")
@click.option("--tags", help="New tags (comma-separated)")
@click.option("--priority", "-p", type=click.Choice(["low", "medium", "high"]), help="New priority")
def update(note_id, title, content, tags, priority):
    """Update a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
            return
        
        # Apply updates
        if title:
            note.title = title
        if content:
            note.content = content
        if tags:
            note.tags = [t.strip() for t in tags.split(",")]
        if priority:
            note.priority = NotePriority(priority)
        
        updated = storage.update(note_id, note)
        click.echo(f"✓ Note updated: {note_id[:8]}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("note_id")
def pin(note_id):
    """Pin a note."""
    try:
        note = storage.pin(note_id)
        if note:
            click.echo(f"✓ Note pinned: {note_id[:8]}")
        else:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("note_id")
def unpin(note_id):
    """Unpin a note."""
    try:
        note = storage.unpin(note_id)
        if note:
            click.echo(f"✓ Note unpinned: {note_id[:8]}")
        else:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("note_id")
def archive(note_id):
    """Archive a note."""
    try:
        note = storage.archive(note_id)
        if note:
            click.echo(f"✓ Note archived: {note_id[:8]}")
        else:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("note_id")
def unarchive(note_id):
    """Unarchive a note."""
    try:
        note = storage.unarchive(note_id)
        if note:
            click.echo(f"✓ Note unarchived: {note_id[:8]}")
        else:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("query")
@click.option("--tags", "-t", help="Filter by tags (comma-separated)")
def search(query, tags):
    """Search notes."""
    try:
        tag_list = [t.strip() for t in tags.split(",")] if tags else None
        results = storage.search(query, tags=tag_list)
        
        if not results:
            click.echo("No results found.")
            return
        
        click.echo(f"Found {len(results)} result(s):\n")
        for n in results:
            click.echo(f"{n.id[:8]} | {n.title}")
            click.echo(f"   {n.content[:60]}...")
            click.echo("")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
def stats():
    """Show note statistics."""
    try:
        stats = storage.get_stats()
        
        click.echo(f"\n{click.style('Note Statistics:', bold=True)}\n")
        click.echo(f"Total Notes: {stats.total_notes}")
        click.echo(f"Pinned: {stats.pinned_notes}")
        click.echo(f"Archived: {stats.archived_notes}")
        
        click.echo(f"\n{click.style('By Priority:', bold=True)}")
        for priority, count in stats.notes_by_priority.items():
            click.echo(f"  {priority}: {count}")
        
        if stats.notes_by_tag:
            click.echo(f"\n{click.style('By Tag:', bold=True)}")
            for tag, count in sorted(stats.notes_by_tag.items(), key=lambda x: x[1], reverse=True):
                click.echo(f"  {tag}: {count}")
        
        click.echo(f"\nAvg. Content Length: {stats.average_content_length:.0f} chars")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.group()
def ai():
    """AI-powered features"""
    pass


@ai.command()
@click.argument("note_id")
def summarize(note_id):
    """Generate AI summary of a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
            return
        
        click.echo("🤖 Generating summary...")
        ai = AINotes()
        summary = ai.summarize(note.content)
        
        click.echo(f"\n{click.style('Summary:', bold=True)}\n{summary}")
    except APIKeyError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@ai.command()
@click.argument("note_id")
def actions(note_id):
    """Extract action items from a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
            return
        
        click.echo("🤖 Extracting action items...")
        ai = AINotes()
        action_items = ai.extract_actions(note.content)
        
        click.echo(f"\n{click.style('Action Items:', bold=True)}")
        for item in action_items:
            click.echo(f"  • {item}")
    except APIKeyError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@ai.command()
@click.argument("note_id")
@click.argument("question")
def ask(note_id, question):
    """Ask a question about a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
            return
        
        click.echo(f"🤖 Asking: {question}")
        ai = AINotes()
        answer = ai.answer_question(note.content, question)
        
        click.echo(f"\n{click.style('Answer:', bold=True)}\n{answer}")
    except APIKeyError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@ai.command()
@click.argument("note_id")
def outline(note_id):
    """Generate an outline from a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
            return
        
        click.echo("🤖 Generating outline...")
        ai = AINotes()
        outline = ai.generate_outline(note.content)
        
        click.echo(f"\n{click.style('Outline:', bold=True)}")
        for item in outline:
            click.echo(f"  {item}")
    except APIKeyError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@ai.command()
@click.argument("note_id")
def tags(note_id):
    """Suggest tags for a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
            return
        
        click.echo("🤖 Suggesting tags...")
        ai = AINotes()
        tags = ai.suggest_tags(note.content)
        
        click.echo(f"\n{click.style('Suggested Tags:', bold=True)}")
        for tag in tags:
            click.echo(f"  • {tag}")
    except APIKeyError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@ai.command()
@click.argument("note_id")
def analyze(note_id):
    """Perform comprehensive AI analysis of a note."""
    try:
        note = storage.get_by_id(note_id)
        if not note:
            click.echo(f"Error: Note '{note_id}' not found.", err=True)
            return
        
        click.echo("🤖 Analyzing note...")
        ai = AINotes()
        analysis = ai.analyze_note(note.content)
        
        click.echo(f"\n{click.style('Summary:', bold=True)}")
        click.echo(analysis.get("summary", "N/A"))
        
        click.echo(f"\n{click.style('Action Items:', bold=True)}")
        for item in analysis.get("action_items", []):
            click.echo(f"  • {item}")
        
        click.echo(f"\n{click.style('Outline:', bold=True)}")
        for item in analysis.get("outline", []):
            click.echo(f"  • {item}")
        
        click.echo(f"\n{click.style('Suggested Tags:', bold=True)}")
        for tag in analysis.get("tags", []):
            click.echo(f"  • {tag}")
        
        click.echo(f"\n{click.style('Keywords:', bold=True)}")
        for keyword in analysis.get("keywords", []):
            click.echo(f"  • {keyword}")
    except APIKeyError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()