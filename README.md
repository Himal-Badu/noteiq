# NoteIQ 🤖
<p align="center">
  <img src="https://raw.githubusercontent.com/himalbadu/noteiq/main/assets/logo.png" alt="NoteIQ Logo" width="150">
</p>

<p align="center">
  <strong>AI-Powered Notes That Think With You</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/noteiq/">
    <img src="https://img.shields.io/pypi/v/noteiq?color=blue&style=flat-square" alt="PyPI Version">
  </a>
  <a href="https://github.com/himalbadu/noteiq/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/himalbadu/noteiq?color=green&style=flat-square" alt="License">
  </a>
  <a href="https://github.com/himalbadu/noteiq/actions">
    <img src="https://img.shields.io/github/actions/status/himalbadu/noteiq/main?color=orange&style=flat-square" alt="Build">
  </a>
  <a href="https://twitter.com/himalbadu">
    <img src="https://img.shields.io/twitter/follow/himalbadu?color=cyan&style=flat-square" alt="Twitter">
  </a>
  <a href="https://github.com/himalbadu/noteiq/fork">
    <img src="https://img.shields.io/github/forks/himalbadu/noteiq?color=purple&style=flat-square" alt="Forks">
  </a>
  <a href="https://github.com/himalbadu/noteiq/stargazers">
    <img src="https://img.shields.io/github/stars/himalbadu/noteiq?color=yellow&style=flat-square" alt="Stars">
  </a>
</p>

---

## ✨ Why NoteIQ?

> **Your second brain, powered by AI.** NoteIQ transforms how you capture, organize, and interact with your notes. It's not just a note-taking app — it's an intelligent companion that helps you extract insights, find patterns, and never lose track of what matters.

### What Makes NoteIQ Different?

- 🧠 **AI-First Design** — Every feature is enhanced with AI to boost productivity
- 🔄 **Multi-Interface** — CLI, REST API, and Web UI — use it your way
- 🔌 **Fully Extensible** — Build on top of NoteIQ with a robust API
- 🚀 **Zero Setup** — Works out of the box with minimal configuration

---

## 🚀 Features

### Core Features

| Feature | Description |
|---------|-------------|
| 📝 **Smart Notes** | Create, organize, and search notes with powerful tagging system |
| 📌 **Pinning** | Pin important notes to keep them at the top |
| 📦 **Archiving** | Archive notes you want to keep but don't need visible |
| 🔍 **Full-Text Search** | Search through all your notes instantly |
| 📊 **Statistics** | Track your note-taking habits with detailed stats |

### AI-Powered Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Summarization** | Get concise 3-5 bullet point summaries of any note |
| ✅ **Action Extraction** | Automatically extract todo items and action items |
| 💬 **Note Q&A** | Ask questions about your notes and get instant answers |
| 📑 **Auto Outlines** | Generate structured outlines from messy notes |
| 🏷️ **Smart Tags** | AI suggests relevant tags for your notes |
| 🔑 **Keyword Extraction** | Auto-discover key topics and themes |
| ✨ **Note Improvement** | AI rewrites notes for clarity and structure |
| 📈 **Comprehensive Analysis** | Full analysis combining all AI features |

### Interfaces

| Interface | Description |
|---------|-------------|
| 🖥️ **Web UI** | Beautiful Streamlit-based web interface |
| ⌨️ **CLI** | Full-featured command-line interface |
| 🌐 **REST API** | Programmatic access for developers |

---

## 📦 Installation

### Quick Install

```bash
# Install from PyPI
pip install noteiq

# Or install from source
git clone https://github.com/himalbadu/noteiq.git
cd noteiq
pip install -e .
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/himalbadu/noteiq.git
cd noteiq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt
```

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required for AI features
OPENAI_API_KEY=your-openai-api-key

# Optional: Customize storage
STORAGE_FILE=notes.json

# Optional: API configuration
API_HOST=0.0.0.0
API_PORT=8000

# Optional: Logging
LOG_LEVEL=INFO
```

> 💡 Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

---

## 🖥️ Web UI (Streamlit)

### Start the Web Interface

```bash
# Using streamlit directly
streamlit run app.py

# Or use the installed command
noteiq web
```

The web interface provides:
- 📝 Create and edit notes
- 🔍 Search notes
- 🤖 AI-powered features (summarize, ask, extract actions)
- 📊 View statistics
- 🎨 Dark/Light theme support

![Web UI Screenshot](assets/screenshot.png)

---

## ⌨️ CLI Usage

### Basic Commands

```bash
# Create a note
noteiq add "Meeting Notes" -c "Discussed Q1 goals, marketing budget, and team expansion plans. Action items: create budget proposal, schedule team meeting, review marketing strategy."

# List all notes
noteiq list

# List notes with tag filter
noteiq list --tag work

# View a specific note
noteiq get <note-id>

# Update a note
noteiq update <note-id> --title "New Title"

# Delete a note
noteiq delete <note-id>
```

### Organization Commands

```bash
# Pin/Unpin a note
noteiq pin <note-id>
noteiq unpin <note-id>

# Archive/Unarchive a note
noteiq archive <note-id>
noteiq unarchive <note-id>

# Search notes
noteiq search "budget"

# View statistics
noteiq stats
```

### AI Commands

```bash
# Summarize a note
noteiq ai summarize <note-id>

# Extract action items
noteiq ai actions <note-id>

# Ask a question about a note
noteiq ai ask <note-id> "What were the main topics discussed?"

# Generate an outline
noteiq ai outline <note-id>

# Suggest tags
noteiq ai tags <note-id>

# Full AI analysis
noteiq ai analyze <note-id>
```

---

## 🌐 REST API

### Start the API Server

```bash
# Using Python
python -m api.main

# Or using uvicorn directly
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Notes CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/notes` | Create a new note |
| `GET` | `/api/notes` | List all notes |
| `GET` | `/api/notes/{id}` | Get a specific note |
| `PUT` | `/api/notes/{id}` | Update a note |
| `DELETE` | `/api/notes/{id}` | Delete a note |

#### Organization

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/notes/{id}/pin` | Pin a note |
| `POST` | `/api/notes/{id}/unpin` | Unpin a note |
| `POST` | `/api/notes/{id}/archive` | Archive a note |
| `POST` | `/api/notes/{id}/unarchive` | Unarchive a note |

#### AI Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/notes/{id}/summarize` | Generate AI summary |
| `POST` | `/api/notes/{id}/actions` | Extract action items |
| `POST` | `/api/notes/{id}/ask` | Ask a question |
| `POST` | `/api/notes/{id}/outline` | Generate outline |
| `POST` | `/api/notes/{id}/suggest-tags` | Suggest tags |
| `POST` | `/api/notes/{id}/analyze` | Full AI analysis |

#### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/notes/search?q=` | Search notes |
| `GET` | `/api/notes/stats` | Get statistics |
| `DELETE` | `/api/notes` | Clear all notes |
| `POST` | `/api/notes/bulk-delete` | Bulk delete |

### Example API Usage

```bash
# Create a note
curl -X POST http://localhost:8000/api/notes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Project Plan",
    "content": "Launch new product by Q2. Tasks: finalize design, development sprint, marketing campaign.",
    "tags": ["work", "product"],
    "priority": "high"
  }'

# List all notes
curl http://localhost:8000/api/notes

# Get a specific note
curl http://localhost:8000/api/notes/{note-id}

# Summarize a note
curl -X POST http://localhost:8000/api/notes/{note-id}/summarize

# Ask a question
curl -X POST http://localhost:8000/api/notes/{note-id}/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the timeline?"}'
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🐳 Docker Deployment

### Using Docker

```bash
# Build the image
docker build -t noteiq .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key noteiq

# Run with volume for persistence
docker run -p 8000:8000 -v $(pwd)/notes.json:/app/notes.json -e OPENAI_API_KEY=your-key noteiq
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=noteiq --cov-report=html

# Run specific test file
pytest tests/test_noteiq.py

# Run tests matching pattern
pytest -k "test_model"
```

---

## 📁 Project Structure

```
noteiq/
├── api/                 # FastAPI REST API
│   └── main.py
├── cli/                 # CLI interface
│   └── main.py
├── noteiq/              # Core package
│   ├── __init__.py      # Package exports
│   ├── ai.py            # AI-powered features
│   ├── config.py        # Configuration management
│   ├── exceptions.py    # Custom exceptions
│   ├── models.py        # Pydantic data models
│   ├── storage.py       # JSON-based persistence
│   ├── validators.py    # Input validation
│   └── utils/           # Utilities (logging, etc.)
├── tests/               # Test suite
│   └── test_noteiq.py
├── scripts/             # Utility scripts
├── assets/              # Images and static assets
├── app.py               # Streamlit web UI
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── setup.py             # Package configuration
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose config
├── DEPLOY.md            # Deployment guide
└── README.md            # This file
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **🐛 Report Bugs** — Open an issue with detailed reproduction steps
2. **💡 Suggest Features** — Open an issue describing your idea
3. **📝 Improve Documentation** — Fix typos, add examples, improve clarity
4. **💻 Write Code** — Pick up an issue and submit a PR

### Development Workflow

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/YOUR_USERNAME/noteiq.git

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes
# Write tests for new functionality

# Run tests
pytest

# Commit with clear messages
git commit -m "Add amazing feature"

# Push to your fork
git push origin feature/amazing-feature

# Open a Pull Request
```

### Coding Standards

- ✅ Use type hints where possible
- ✅ Write docstrings for all public functions
- ✅ Add tests for new features
- ✅ Follow PEP 8 style guide
- ✅ Keep functions small and focused

---

## 📈 Roadmap

### v1.1.0 (Current)
- ✅ REST API with full CRUD operations
- ✅ AI-powered features (summarize, actions, Q&A, outline)
- ✅ CLI with full feature set
- ✅ Docker support

### v1.2.0 (Planned)
- [ ] Markdown support with preview
- [ ] Note categories/folders
- [ ] Export to various formats (PDF, Markdown, HTML)
- [ ] Rich text editor in web UI

### v2.0.0 (Future)
- [ ] Multiple AI provider support (Anthropic, Google)
- [ ] Plugin system for extensions
- [ ] Team collaboration features
- [ ] Note sharing and collaboration

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for the GPT API
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Streamlit](https://streamlit.io/) for the web UI
- [Click](https://click.palletsprojects.com/) for the CLI
- All contributors and users of NoteIQ

---

## 👤 Author

**Himal Badu, AI Founder**

<div align="center">

🌐 [Website](https://himalbadu.com) | 🐦 [Twitter](https://twitter.com/himalbadu) | 💼 [LinkedIn](https://linkedin.com/in/himalbadu) | 📧 [Email](mailto:himal@noteiq.app)

</div>

---

<div align="center">

Made with ❤️ by **Himal Badu, AI Founder**

*If you find this project useful, please consider giving it a ⭐ on GitHub!*

</div>