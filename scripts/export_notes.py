#!/usr/bin/env python3
"""
Export notes to various formats
"""
import json
import csv
import argparse
from datetime import datetime
from noteiq.storage import NoteStorage


def export_json(storage: NoteStorage, output_file: str, include_archived: bool = False):
    """Export notes to JSON file"""
    notes = storage.get_all(include_archived=include_archived)
    
    data = {
        "export_date": datetime.now().isoformat(),
        "count": len(notes),
        "notes": [
            {
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "tags": n.tags,
                "priority": n.priority,
                "is_pinned": n.is_pinned,
                "is_archived": n.is_archived,
                "created_at": n.created_at.isoformat(),
                "updated_at": n.updated_at.isoformat()
            }
            for n in notes
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Exported {len(notes)} notes to {output_file}")


def export_csv(storage: NoteStorage, output_file: str, include_archived: bool = False):
    """Export notes to CSV file"""
    notes = storage.get_all(include_archived=include_archived)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'title', 'content', 'tags', 'priority', 'is_pinned', 'is_archived', 'created_at', 'updated_at'])
        
        for note in notes:
            writer.writerow([
                note.id,
                note.title,
                note.content,
                ','.join(note.tags),
                note.priority,
                note.is_pinned,
                note.is_archived,
                note.created_at.isoformat(),
                note.updated_at.isoformat()
            ])
    
    print(f"Exported {len(notes)} notes to {output_file}")


def export_markdown(storage: NoteStorage, output_dir: str, include_archived: bool = False):
    """Export notes to markdown files"""
    import os
    notes = storage.get_all(include_archived=include_archived)
    
    os.makedirs(output_dir, exist_ok=True)
    
    for note in notes:
        # Sanitize filename
        filename = "".join(c for c in note.title if c.isalnum() or c in ' -_')[:50]
        filepath = os.path.join(output_dir, f"{filename}.md")
        
        with open(filepath, 'w') as f:
            f.write(f"# {note.title}\n\n")
            f.write(f"**Tags:** {', '.join(note.tags) if note.tags else 'None'}\n\n")
            f.write(f"**Priority:** {note.priority}\n\n")
            f.write(f"**Created:** {note.created_at}\n\n")
            f.write(f"**Updated:** {note.updated_at}\n\n")
            f.write(f"---\n\n")
            f.write(note.content)
    
    print(f"Exported {len(notes)} notes to {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Export notes from NoteIQ")
    parser.add_argument("output", help="Output file or directory")
    parser.add_argument("--format", choices=["json", "csv", "markdown"], default="json", help="Export format")
    parser.add_argument("--storage", default="notes.json", help="Storage file")
    parser.add_argument("--archived", action="store_true", help="Include archived notes")
    
    args = parser.parse_args()
    storage = NoteStorage(args.storage)
    
    if args.format == "json":
        export_json(storage, args.output, args.archived)
    elif args.format == "csv":
        export_csv(storage, args.output, args.archived)
    elif args.format == "markdown":
        export_markdown(storage, args.output, args.archived)


if __name__ == "__main__":
    main()