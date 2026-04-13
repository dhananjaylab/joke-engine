# Getting Started with Giggle

## What is Giggle?

Giggle is an AI-powered joke engine that generates jokes in multiple styles using OpenAI's GPT models. It features:

- 🎭 8 comedy personas (witty, dad jokes, sarcastic, roast, haiku, brainrot, etc.)
- 🎨 Shareable joke cards (PNG images)
- 🔊 Text-to-speech audio
- 🎮 Gamification (XP, streaks, ranks)
- 📱 Progressive Web App (PWA)
- ⚡ Real-time streaming

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **OpenAI API Key** ([Get one](https://platform.openai.com/api-keys))
- **Git** (optional, for cloning)

### Optional
- **Redis** (for background workers)
- **PostgreSQL** (for production)

## Installation

### Option 1: Automated Setup (Recommended)

#### On Linux/Mac:
```bash
./setup.sh
```

#### On Windows:
```bash
setup.bat
```

This will:
1. Create Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies
4. Create `.env` file
5. Initialize database

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.template .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...

# Initialize database
alembic upgrade head
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install
```

## Configuration

### Backend Environment Variables

Edit `backend/.env`:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (defaults shown)
DATABASE_URL=sqlite+aiosqlite:///./giggle.db
SECRET_KEY=dev-secret-change-in-prod
DEBUG=False
MEDIA_DIR=./media
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# For ARQ workers (optional)
REDIS_URL=redis://localhost:6379

# For trending topics (optional)
NEWSAPI_KEY=your-newsapi-key
```

### Frontend Environment Variables

Create `frontend/.env` (optional):

```bash
# Only needed if backend is not on localhost:8000
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Development Mode

#### Terminal 1 - Backend:
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

#### Terminal 3 - ARQ Worker (Optional):
```bash
cd backend
source .venv/bin/activate
arq workers.settings.WorkerSettings
```

### Access the Application

Open your browser to: **http://localhost:5173**

## First Steps

### 1. Generate Your First Joke

1. Enter a topic (e.g., "cats", "programming", "coffee")
2. Select a style (witty, dad, sarcastic, etc.)
3. Click "Go"
4. Watch the joke stream in real-time!

### 2. Explore Features

- **History**: View all your generated jokes
- **Share**: Download PNG cards or audio
- **Heckle**: Submit your own joke for AI roasting
- **Profile**: Check your XP, streak, and rank

### 3. Try Different Personas

- **Witty**: Classic stand-up comedy
- **Dad**: Wholesome puns and groaners
- **Sarcastic**: Dry, cutting humor
- **Roast**: Insult comedy (tasteful)
- **Haiku**: 5-7-5 syllable poems
- **Brainrot**: Gen-Z internet chaos
- **No Context**: Confusing punchlines only
- **Emoji**: Pure emoji comedy

## API Testing

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Generate a Joke
```bash
curl -X POST http://localhost:8000/api/jokes/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "cats", "style": "witty"}'
```

### Stream a Joke (SSE)
```bash
curl -N http://localhost:8000/api/jokes/stream?query=dogs&style=dad
```

### Get Profile
```bash
curl http://localhost:8000/api/profile \
  -H "Cookie: giggle_session=your-session-cookie"
```

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Activate virtual environment and reinstall dependencies
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

**Error**: `openai.AuthenticationError`
- **Solution**: Check your `OPENAI_API_KEY` in `.env`

**Error**: `Database is locked`
- **Solution**: SQLite doesn't handle concurrent writes. Use PostgreSQL for production.

### Frontend won't start

**Error**: `Cannot find module 'react'`
- **Solution**: Install dependencies
  ```bash
  npm install
  ```

**Error**: `CORS error`
- **Solution**: Ensure backend is running on port 8000 and `CORS_ORIGINS` includes `http://localhost:5173`

### API calls fail

**Error**: `Network Error` or `404`
- **Solution**: Check that backend is running on port 8000
- **Solution**: Verify Vite proxy configuration in `vite.config.ts`

### No jokes generating

**Error**: Silent failure or timeout
- **Solution**: Check OpenAI API key and account credits
- **Solution**: Check backend logs for errors

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- Backend: `--reload` flag automatically reloads on file changes
- Frontend: Vite HMR updates instantly

### Database Migrations

After changing models:
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Viewing Database

SQLite:
```bash
sqlite3 backend/giggle.db
.tables
SELECT * FROM jokes LIMIT 5;
```

### Clearing Data

```bash
# Delete database
rm backend/giggle.db

# Recreate
cd backend
alembic upgrade head
```

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production setup instructions.

### Quick Docker Deploy

```bash
# Create .env with production secrets
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" > .env
echo "SECRET_KEY=$(openssl rand -base64 32)" >> .env
echo "OPENAI_API_KEY=your-key" >> .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access at: **http://localhost**

## Project Structure

```
joke-engine/
├── backend/           # FastAPI backend
│   ├── main.py       # App entry point
│   ├── routers/      # API endpoints
│   ├── services/     # Business logic
│   ├── models/       # Database models
│   └── .env          # Configuration
│
├── frontend/         # React frontend
│   ├── src/
│   │   ├── api/     # API client
│   │   ├── hooks/   # Custom hooks
│   │   └── store/   # State management
│   └── package.json
│
└── docker-compose.yml # Production setup
```

## Learning Resources

### Backend (FastAPI)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

### Frontend (React)
- [React Tutorial](https://react.dev/learn)
- [Vite Guide](https://vitejs.dev/guide/)
- [TanStack Query](https://tanstack.com/query/latest/docs/react/overview)
- [Zustand Guide](https://docs.pmnd.rs/zustand/getting-started/introduction)

### AI Integration
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Streaming Completions](https://platform.openai.com/docs/api-reference/streaming)

## Next Steps

1. ✅ Get the app running locally
2. 📝 Generate some jokes and explore features
3. 🎨 Customize personas in `backend/services/ai.py`
4. 🚀 Deploy to production (see DEPLOYMENT.md)
5. 🔧 Add custom features (see ARCHITECTURE.md)

## Getting Help

- **Documentation**: See README.md, ARCHITECTURE.md, DEPLOYMENT.md
- **Issues**: Check PROJECT_STATUS.md for known issues
- **API Docs**: http://localhost:8000/docs (when backend is running)
- **Quick Reference**: See QUICK_REFERENCE.md

## Contributing

This is a complete, production-ready codebase. Feel free to:
- Add new joke personas
- Implement battle system
- Add trending topics
- Create custom UI components
- Improve scoring algorithm
- Add tests

## License

MIT License - See LICENSE file for details

---

**Happy joke generating! 🎭**
