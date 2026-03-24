#!/usr/bin/env python3
"""
Import notes from various formats
"""
import json
import csv
import argparse
from pathlib import Path
from noteiq.models import Note
from noteiq.storage import NoteStorage


def import_json(file_path: str, storage: NoteStorage):
    """Import notes from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        notes = data
    elif isinstance(data, dict) and 'notes' in data:
        notes = data['notes']
    else:
        raise ValueError("Invalid JSON format")
    
    count = 0
    for item in notes:
        note = Note(
            title=item.get('title', 'Untitled'),
            content=item.get('content', ''),
            tags=item.get('tags', [])
        )
        storage.create(note)
        count += 1
    
    print(f"Imported {count} notes from JSON")
    return count


def import_csv(file_path: str, storage: NoteStorage):
    """Import notes from CSV file"""
    count = 0
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            note = Note(
                title=row.get('title', 'Untitled'),
                content=row.get('content', ''),
                tags=row.get('tags', '').split(',') if row.get('tags') else []
            )
            storage.create(note)
            count += 1
    
    print(f"Imported {count} notes from CSV")
    return count


def import_markdown_notes(directory: str, storage: NoteStorage):
    """Import notes from markdown files in a directory"""
    count = 0
    path = Path(directory)
    
    for md_file in path.glob("*.md"):
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Extract title from first heading or filename
        lines = content.split('\n')
        title = md_file.stem
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        note = Note(
            title=title,
            content=content
        )
        storage.create(note)
        count += 1
    
    print(f"Imported {count} notes from markdown")
    return count


def main():
    parser = argparse.ArgumentParser(description="Import notes into NoteIQ")
    parser.add_argument("file", help="File or directory to import")
    parser.add_argument("--format", choices=["json", "csv", "markdown"], default="auto", help="Import format")
    parser.add_argument("--storage", default="notes.json", help="Storage file")
    
    args = parser.parse_args()
    storage = NoteStorage(args.storage)
    
    if args.format == "auto":
        suffix = Path(args.file).suffix.lower()
        if suffix == ".json":
            args.format = "json"
        elif suffix == ".csv":
            args.format = "csv"
        elif Path(args.file).is_dir():
            args.format = "markdown"
    
    if args.format == "json":
        import_json(args.file, storage)
    elif args.format == "csv":
        import_csv(args.file, storage)
    elif args.format == "markdown":
        import_markdown_notes(args.file, storage)


if __name__ == "__main__":
    main()