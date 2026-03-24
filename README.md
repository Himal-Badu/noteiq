<p align="center">
  <img src="https://raw.githubusercontent.com/himalbadu/noteiq/main/assets/logo.png" alt="NoteIQ Logo" width="150">
</p>

<h1 align="center">NoteIQ 🤖</h1>

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
  <a href="https://github.com/himalbadu/noteiq/stargazers">
    <img src="https://img.shields.io/github/stars/himalbadu/noteiq?style=flat-square" alt="Stars">
  </a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Smart Notes** | Create, organize, and search notes with tags, priorities, and pinning |
| 📊 **AI Summarization** | Instantly summarize long notes into key bullet points |
| ✅ **Action Extraction** | Automatically find and extract actionable items from notes |
| 💬 **Note Q&A** | Ask questions about your notes and get AI-powered answers |
| 📑 **Auto Outlines** | Generate structured outlines from your notes |
| 🏷️ **Smart Tags** | AI suggests relevant tags for better organization |
| 🔍 **Full-Text Search** | Quickly find notes by title, content, or tags |
| 🔌 **REST API** | Full REST API for programmatic access |
| 🖥️ **Web UI** | Beautiful Streamlit web interface |
| 💻 **CLI** | Powerful command-line interface |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/himalbadu/noteiq.git
cd noteiq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

> 💡 Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

---

## 💻 Usage

### CLI Usage

#### Create a Note
```bash
python -m cli.main add "Meeting Notes" -c "Discussed Q1 goals, marketing budget, and team expansion plans."
```

#### List All Notes
```bash
python -m cli.main list
```

#### Search Notes
```bash
python -m cli.main search "Q1 goals"
```

#### AI Features

```bash
# Summarize a note
python -m cli.main ai summarize <note-id>

# Extract action items
python -m cli.main ai actions <note-id>

# Ask a question about a note
python -m cli.main ai ask <note-id> "What were the main topics?"

# Generate an outline
python -m cli.main ai outline <note-id>

# Get AI-suggested tags
python -m cli.main ai tags <note-id>

# Full AI analysis
python -m cli.main ai analyze <note-id>
```

#### Export & Import

```bash
# Export notes
python -m cli.main export -f json -o backup.json
python -m cli.main export -f csv -o backup.csv
python -m cli.main export -f markdown -o notes/

# Import notes
python -m cli.main import backup.json
```

### API Usage

#### Start the Server
```bash
python -m api.main
# Or: uvicorn api.main:app --host 0.0.0.0 --port 8000
```

#### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/notes` | Create a new note |
| `GET` | `/api/notes` | List all notes |
| `GET` | `/api/notes/{id}` | Get a specific note |
| `PUT` | `/api/notes/{id}` | Update a note |
| `DELETE` | `/api/notes/{id}` | Delete a note |
| `GET` | `/api/notes/search?q=query` | Search notes |
| `GET` | `/api/notes/stats` | Get note statistics |
| `GET` | `/api/notes/count` | Get note count |
| `GET` | `/api/tags` | Get all unique tags |
| `POST` | `/api/notes/{id}/summarize` | AI summary |
| `POST` | `/api/notes/{id}/actions` | Extract action items |
| `POST` | `/api/notes/{id}/ask` | Ask a question |
| `POST` | `/api/notes/{id}/outline` | Generate outline |
| `POST` | `/api/notes/{id}/pin` | Pin a note |
| `POST` | `/api/notes/{id}/archive` | Archive a note |

#### Example API Calls

```bash
# Create note
curl -X POST http://localhost:8000/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Project Plan", "content": "...", "tags": ["work"]}'

# Get all notes
curl http://localhost:8000/api/notes

# Search notes
curl "http://localhost:8000/api/notes/search?q=goals"

# Summarize note
curl -X POST http://localhost:8000/api/notes/{id}/summarize

# Get statistics
curl http://localhost:8000/api/notes/stats
```

### Web UI

```bash
# Start Streamlit app
streamlit run app.py
```

The web interface provides:
- 📋 Note management (create, edit, delete)
- 🔍 Search functionality
- 🤖 AI-powered features
- 📊 Statistics dashboard
- ⚙️ Settings page

---

## 🐳 Docker

### Using Docker Compose (Recommended)

```bash
# Clone and run
git clone https://github.com/himalbadu/noteiq.git
cd noteiq

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Using Docker

```bash
# Build the image
docker build -t noteiq .

# Run API server
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key noteiq

# Run Streamlit
docker run -p 8501:8501 -e OPENAI_API_KEY=your-key -v $(pwd)/data:/app/data noteiq streamlit run app.py
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=noteiq --cov-report=html

# Run specific test file
pytest tests/test_noteiq.py -v
```

---

## 📁 Project Structure

```
noteiq/
├── api/                 # FastAPI application
│   └── main.py         # API endpoints
├── cli/                 # CLI interface
│   └── main.py         # CLI commands
├── noteiq/              # Core package
│   ├── __init__.py     # Package exports
│   ├── models.py       # Pydantic models
│   ├── storage.py      # JSON storage
│   ├── ai.py           # LangChain AI functions
│   ├── config.py       # Configuration
│   ├── exceptions.py   # Custom exceptions
│   ├── validators.py   # Input validators
│   └── utils/          # Utility functions
├── tests/              # Test suite
├── scripts/            # Import/export scripts
├── app.py              # Streamlit web app
├── setup.py            # Package setup
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image
└── docker-compose.yml  # Docker Compose
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Required |
| `OPENAI_MODEL` | OpenAI model to use | gpt-3.5-turbo |
| `STORAGE_FILE` | Path to notes storage file | notes.json |
| `LOG_LEVEL` | Logging level | INFO |
| `API_PORT` | API server port | 8000 |

### Configuration File

Create a `.env` file:

```bash
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
STORAGE_FILE=notes.json
LOG_LEVEL=INFO
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Himal Badu, AI Founder**

- 🌐 Website: [himalbadu.com](https://himalbadu.com)
- 🐦 Twitter: [@himalbadu](https://twitter.com/himalbadu)
- 💼 LinkedIn: [himalbadu](https://linkedin.com/in/himalbadu)
- 📧 Email: himal@noteiq.app

---

## 🙏 Acknowledgments

- [OpenAI](https://openai.com) for the GPT models
- [LangChain](https://langchain.ai) for AI framework
- [FastAPI](https://fastapi.tiangolo.com) for the API framework
- [Streamlit](https://streamlit.io) for the web UI

---

<div align="center">

Made with ❤️ by **Himal Badu, AI Founder**

</div>
