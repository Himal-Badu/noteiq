# NoteIQ Deployment Guide

This guide covers deploying NoteIQ to various platforms.

## Prerequisites

- Python 3.8+
- OpenAI API Key

## Local Development

```bash
# Clone and setup
git clone https://github.com/himalbadu/noteiq.git
cd noteiq
python -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key-here"

# Run CLI
python -m cli.main --help

# Run API
python -m api.main
```

## Docker Deployment

### Build & Run

```bash
# Build
docker build -t noteiq .

# Run
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key noteiq
```

### Docker Compose

```yaml
version: '3'
services:
  noteiq:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - notes-data:/app

volumes:
  notes-data:
```

## Cloud Deployment

### Railway

1. Connect GitHub repo to Railway
2. Set `OPENAI_API_KEY` environment variable
3. Deploy

### Render

1. Create new Web Service
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python -m api.main`
5. Add `OPENAI_API_KEY` env var

### Fly.io

```bash
fly launch
fly secrets set OPENAI_API_KEY=your-key
fly deploy
```

## Production Considerations

- Use environment variables for API keys
- Consider using a proper database (PostgreSQL) for production
- Add authentication to API endpoints
- Set up proper logging

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`