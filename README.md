<p align="center">
  <img src="https://raw.githubusercontent.com/himalbadu/noteiq/main/assets/logo.png" alt="NoteIQ Logo" width="120">
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
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **Smart Notes** | Create, organize, and search notes with tags |
| 📊 **AI Summarization** | Instantly summarize long notes into key points |
| ✅ **Action Extraction** | Automatically find and list action items |
| 💬 **Note Q&A** | Ask questions about your notes and get answers |
| 📑 **Auto Outlines** | Generate structured outlines from notes |
| 🔌 **REST API** | Full REST API for programmatic access |
| 🖥️ **CLI** | Beautiful command-line interface |

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/himalbadu/noteiq.git
cd noteiq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scriptsctivate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

> 💡 Get your API key from [OpenAI](https://platform.openai.com/api-keys)

---

## 💻 CLI Usage

### Create a Note
```bash
python -m cli.main add "Meeting Notes" -c "Discussed Q1 goals, marketing budget, and team expansion plans. Action items: create budget proposal, schedule team meeting, review marketing strategy."
```

### List All Notes
```bash
python -m cli.main list
```

### View a Note
```bash
python -m cli.main get <note-id>
```

### AI Features

```bash
# Summarize a note
python -m cli.main summarize <note-id>

# Extract action items
python -m cli.main actions <note-id>

# Ask a question about a note
python -m cli.main ask <note-id> "What were the main topics discussed?"

# Generate an outline
python -m cli.main outline <note-id>
```

---

## 🌐 API Usage

### Start the Server
```bash
python -m api.main
# Or: uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/notes` | Create a new note |
| `GET` | `/api/notes` | List all notes |
| `GET` | `/api/notes/{id}` | Get a specific note |
| `PUT` | `/api/notes/{id}` | Update a note |
| `DELETE` | `/api/notes/{id}` | Delete a note |
| `POST` | `/api/notes/{id}/summarize` | AI summary |
| `POST` | `/api/notes/{id}/actions` | Extract action items |
| `POST` | `/api/notes/{id}/ask` | Ask a question |
| `POST` | `/api/notes/{id}/outline` | Generate outline |

### Example API Calls

```bash
# Create note
curl -X POST http://localhost:8000/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Project Plan", "content": "...", "tags": ["work"]}'

# Summarize note
curl -X POST http://localhost:8000/api/notes/{id}/summarize
```

---

## 🐳 Docker

```bash
# Build the image
docker build -t noteiq .

# Run the container
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key noteiq
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=noteiq
```

---

## 📁 Project Structure

```
noteiq/
├── api/                 # FastAPI application
│   └── main.py
├── cli/                 # CLI interface
│   └── main.py
├── noteiq/              # Core package
│   ├── __init__.py
│   ├── models.py        # Pydantic models
│   ├── storage.py       # JSON storage
│   └── ai.py            # LangChain AI functions
├── tests/               # Test suite
├── requirements.txt
├── setup.py
├── Dockerfile
└── README.md
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

<div align="center">

Made with ❤️ by **Himal Badu, AI Founder**

</div>
