# AI Novel Writing Application

A sophisticated AI-powered novel writing application that helps authors create compelling stories with advanced AI assistance and meticulously engineered prompts for human-like, original prose.

## 🚀 Features

- **📚 Story Management**: Create and organize multiple novel projects with detailed metadata
- **🎯 AI-Powered Outline Generation**: Generate detailed story outlines with multi-layered narratives and complex plot structures
- **👥 Character Development**: Create rich, psychologically complex characters with detailed profiles and authentic contradictions
- **📝 Chapter Writing**: AI-assisted chapter generation with sophisticated prose and narrative restraint
- **🌍 World Building**: Develop immersive fictional worlds with detailed cultural, historical, and societal elements
- **💬 Dialogue Crafting**: Generate authentic, character-specific dialogue with emotional subtext
- **🔄 Plot Twist Generation**: Create sophisticated, believable plot twists that recontextualize previous events
- **📤 Export Options**: Export completed works in various formats (PDF, DOCX, TXT)
- **⚙️ Complexity Control**: Adjustable writing complexity from simple to literary sophistication

## 🛠 Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs with automatic documentation
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) for database operations
- **SQLite**: Lightweight database for development and small-scale deployment
- **Pydantic**: Data validation using Python type annotations for robust API contracts

### Frontend
- **React 18**: Modern JavaScript library for building user interfaces
- **TypeScript**: Typed superset of JavaScript for better development experience
- **Material-UI (MUI)**: React components implementing Google's Material Design
- **Vite**: Fast build tool and development server with hot module replacement

### AI Integration
- **OpenAI API**: GPT-4 and GPT-3.5 models for sophisticated text generation
- **Ollama**: Local AI model support for privacy and cost control
- **Advanced Prompt Engineering**: Meticulously crafted prompts for human-like, original writing
- **Anti-Generic Safeguards**: Built-in protection against repetitive and clichéd AI writing patterns

## 🎨 Advanced Prompt Engineering

This application features sophisticated prompt engineering designed to produce human-like, original writing:

### Core Principles
- **Narrative Restraint**: Implies rather than explicitly states character intentions
- **Emotional Subtext**: Layers meaning beneath surface conversations and actions
- **Authentic Dialogue**: Realistic conversational rhythms with character-specific voices
- **Anti-Cliché Protection**: Explicit avoidance of common literary tropes and AI writing patterns
- **Psychological Realism**: Characters with believable contradictions and complex motivations

### Quality Safeguards
- **Anti-Repetition Rules**: Prevents word repetition and synonym lists
- **Sentence Structure Control**: Varied length with readability limits
- **Punctuation Enforcement**: Proper grammar and sentence completion
- **Stream-of-Consciousness Prevention**: Blocks rambling, unfocused prose
- **Thematic Coherence**: Ensures every element serves the narrative purpose

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (3.9+ recommended)
- Node.js 16+ (18+ recommended)
- npm or yarn package manager
- OpenAI API key (optional: for cloud AI) or Ollama (for local AI)

### Quick Start

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/ai-novel-app.git
cd ai-novel-app
```

2. **Backend Setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
python -c "from db.database import init_db; init_db()"
uvicorn app:app --reload
```

3. **Frontend Setup** (in a new terminal):
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application**:
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./ai_novel_app.db

# AI Provider Settings
AI_PROVIDER=openai  # Options: openai, ollama
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# Ollama Settings (for local AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2  # or other supported models

# API Configuration
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3001"]

# Generation Settings
MAX_CHAPTERS_PER_STORY=50
DEFAULT_CHAPTER_LENGTH=2000
GENERATION_TIMEOUT=300

# Writing Complexity
NOVEL_COMPLEXITY=standard  # simple, standard, complex, literary
```

### Complexity Levels

Choose from four sophistication levels:

| Level | Description | Use Case |
|-------|-------------|----------|
| **Simple** | Clear, straightforward storytelling | Young adult, accessible fiction |
| **Standard** | Balanced complexity with moderate depth | Most commercial fiction |
| **Complex** | Multi-layered narratives with advanced techniques | Literary fiction, complex plots |
| **Literary** | Artistic prose with experimental elements | High literary fiction, artistic works |

## 📖 Usage Guide

### 1. Create a New Story
- Set title, description, genre, and target specifications
- Choose complexity level for AI generation
- Configure chapter count and word targets

### 2. Generate Story Outline
- AI creates detailed chapter-by-chapter breakdown
- Multi-layered narrative with character arcs
- Avoids predictable plot structures and clichés

### 3. Develop Characters
- Generate psychologically complex character profiles
- Includes contradictions, secrets, and growth potential
- Distinctive voices and realistic motivations

### 4. Build the World
- Create immersive settings and cultures
- Develop unique societal structures and histories
- Avoid typical fantasy/sci-fi tropes

### 5. Write Chapters
- AI-assisted chapter generation with sophisticated prose
- Maintains character voices and thematic coherence
- Built-in quality controls prevent generic AI writing

### 6. Refine and Export
- Edit and enhance generated content
- Export in multiple formats (PDF, DOCX, TXT)
- Maintain version control and backups

## 🔧 API Documentation

Interactive API documentation is available when the backend is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/stories/` - Create new story
- `POST /api/v1/generate/stories/{id}/outline` - Generate story outline
- `POST /api/v1/generate/stories/{id}/characters` - Generate characters
- `POST /api/v1/generate/stories/{id}/world` - Generate world elements
- `POST /api/v1/generate/stories/{id}/chapters/{number}` - Generate chapter
- `GET /api/v1/generate/complexity` - Get complexity settings
- `POST /api/v1/generate/complexity/{level}` - Set complexity level

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper testing
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request** with detailed description

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all new frontend code
- Add tests for new features
- Update documentation for API changes
- Ensure prompt engineering maintains quality standards

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing powerful language models
- **Ollama Project** for local AI model support
- **FastAPI Community** for excellent web framework
- **React Team** for robust frontend library
- **Material-UI** for beautiful, accessible components

## 📞 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions
- **Documentation**: Comprehensive guides in the `/docs` directory

---

**Built with ❤️ for writers who demand sophisticated, original AI assistance**
