import click
import os
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

import json
from noteiq.models import Note, NoteCreate
from noteiq.storage import NoteStorage
from noteiq.ai import AINotes


storage = NoteStorage()


@click.group()
def cli():
    """NoteIQ - AI-Powered Notes Application"""
    pass


@cli.command()
@click.argument("title")
@click.option("--content", "-c", required=True, help="Note content")
@click.option("--tags", "-t", help="Tags for the note (comma-separated)")
def add(title, content, tags):
    """Add a new note."""
    note = Note(
        title=title,
        content=content,
        tags=[t.strip() for t in tags.split(",")] if tags else []
    )
    created = storage.create(note)
    click.echo(f"✓ Note created: {created.id}")
    click.echo(f"  Title: {created.title}")
    if created.tags:
        click.echo(f"  Tags: {', '.join(created.tags)}")


@cli.command()
@click.option("--tag", "-t", help="Filter by tag")
def list(tag):
    """List all notes."""
    notes = storage.get_all(tag=tag)
    if not notes:
        click.echo("No notes found.")
        return
    
    for n in notes:
        tags_str = f" [{', '.join(n.tags)}]" if n.tags else ""
        click.echo(f"\n{n.id[:8]} | {n.title}{tags_str}")
        click.echo(f"  {n.content[:100]}{'...' if len(n.content) > 100 else ''}")


@cli.command()
@click.argument("note_id")
def get(note_id):
    """View a specific note."""
    note = storage.get_by_id(note_id)
    if not note:
        click.echo(f"Error: Note '{note_id}' not found.")
        return
    
    click.echo(f"\n{click.style('Title:', bold=True)} {note.title}")
    click.echo(f"{click.style('Tags:', bold=True)} {', '.join(note.tags) if note.tags else 'None'}")
    click.echo(f"{click.style('Created:', bold=True)} {note.created_at}")
    click.echo(f"\n{click.style('Content:', bold=True)}\n{note.content}")


@cli.command()
@click.argument("note_id")
def delete(note_id):
    """Delete a note."""
    success = storage.delete(note_id)
    if success:
        click.echo(f"✓ Note deleted: {note_id[:8]}")
    else:
        click.echo(f"Error: Note '{note_id}' not found.")


@cli.command()
@click.argument("note_id")
def summarize(note_id):
    """Generate AI summary of a note."""
    note = storage.get_by_id(note_id)
    if not note:
        click.echo(f"Error: Note '{note_id}' not found.")
        return
    
    click.echo("🤖 Generating summary...")
    ai = AINotes()
    summary = ai.summarize(note.content)
    click.echo(f"\n{click.style('Summary:', bold=True)}\n{summary}")


@cli.command()
@click.argument("note_id")
def actions(note_id):
    """Extract action items from a note."""
    note = storage.get_by_id(note_id)
    if not note:
        click.echo(f"Error: Note '{note_id}' not found.")
        return
    
    click.echo("🤖 Extracting action items...")
    ai = AINotes()
    action_items = ai.extract_actions(note.content)
    click.echo(f"\n{click.style('Action Items:', bold=True)}")
    for item in action_items:
        click.echo(f"  • {item}")


@cli.command()
@click.argument("note_id")
@click.argument("question")
def ask(note_id, question):
    """Ask a question about a note."""
    note = storage.get_by_id(note_id)
    if not note:
        click.echo(f"Error: Note '{note_id}' not found.")
        return
    
    click.echo(f"🤖 Asking: {question}")
    ai = AINotes()
    answer = ai.answer_question(note.content, question)
    click.echo(f"\n{click.style('Answer:', bold=True)}\n{answer}")


@cli.command()
@click.argument("note_id")
def outline(note_id):
    """Generate an outline from a note."""
    note = storage.get_by_id(note_id)
    if not note:
        click.echo(f"Error: Note '{note_id}' not found.")
        return
    
    click.echo("🤖 Generating outline...")
    ai = AINotes()
    outline = ai.generate_outline(note.content)
    click.echo(f"\n{click.style('Outline:', bold=True)}")
    for item in outline:
        click.echo(f"  {item}")


if __name__ == "__main__":
    cli()