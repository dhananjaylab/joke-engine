# Giggle — AI Joke Engine

> **Backend:** Python 3.11 · FastAPI · SQLAlchemy 2 async · Alembic · ARQ · uvicorn  
> **Frontend:** React 18 · Vite 5 · TypeScript · Tailwind CSS · TanStack Query · Zustand  
> **DB:** SQLite (dev) → PostgreSQL + pgvector (prod)

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.template .env
# Edit .env and add your OPENAI_API_KEY

# Initialize database
alembic revision --autogenerate -m "initial tables"
alembic upgrade head

# Run development server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:5173
```

The Vite dev server automatically proxies `/api/*` requests to `localhost:8000`.

### Optional: ARQ Worker (for background scoring)

Requires Redis running locally:

```bash
# In a separate terminal
cd backend
arq workers.settings.WorkerSettings
```

## Production Deployment

### Using Docker Compose

```bash
# Create .env file with production secrets
echo "POSTGRES_PASSWORD=your_secure_password" > .env
echo "SECRET_KEY=your_secret_key" >> .env
echo "OPENAI_API_KEY=your_openai_key" >> .env

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f api
```

Services:
- **Frontend:** http://localhost (nginx)
- **API:** http://localhost/api (proxied through nginx)
- **PostgreSQL:** Internal only
- **Redis:** Internal only
- **ARQ Worker:** Background task processor

## Project Structure

```
joke-engine/
├── backend/                 # FastAPI service
│   ├── main.py             # App entry point
│   ├── core/               # Config & database
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic (AI, image, etc.)
│   ├── middleware/         # Session management
│   ├── dependencies/       # FastAPI dependencies
│   ├── workers/            # ARQ background tasks
│   ├── tasks/              # APScheduler jobs
│   └── alembic/            # Database migrations
│
├── frontend/               # React + Vite SPA
│   ├── src/
│   │   ├── api/           # API client & hooks
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── pages/         # Route pages
│   │   ├── store/         # Zustand state
│   │   └── lib/           # Utilities
│   └── public/            # Static assets
│
├── docker-compose.yml     # Production orchestration
├── nginx.conf             # Reverse proxy config
└── README.md
```

## Features

### Phase 0-1: Core Functionality ✅
- Joke generation with multiple personas (witty, dad, sarcastic, roast, haiku, brainrot, etc.)
- SSE streaming for real-time joke delivery
- Joke history with pagination
- Session-based user profiles

### Phase 2: Viral Features ✅
- Share cards (PNG generation)
- Text-to-speech audio
- Heckle mode (AI roasts your jokes)
- Explain mode (over-analytical joke explanations)

### Phase 3: Gamification ✅
- XP system
- Daily streak tracking
- Rank progression (Open Mic → Club Regular → Headliner → Legend → GOAT)

### Phase 4: Advanced AI (Optional)
- Background joke scoring (ARQ workers)
- 3-dimensional ratings (originality, timing, cleverness)

### Phase 5: Real-time (Optional)
- WebSocket support for streaming
- PWA capabilities

### Phase 6: Production (Optional)
- PostgreSQL with pgvector
- Semantic deduplication
- Full Docker deployment

## API Endpoints

### Jokes
- `POST /api/jokes/generate` - Generate a new joke
- `GET /api/jokes/stream` - SSE streaming endpoint
- `GET /api/jokes/history` - Paginated joke history
- `GET /api/jokes/{id}` - Get specific joke
- `DELETE /api/jokes/{id}` - Delete joke
- `POST /api/jokes/{id}/heckle` - Get AI roast
- `POST /api/jokes/{id}/explain` - Get explanation

### Share
- `GET /api/share/{id}/card.png` - Download joke card
- `GET /api/share/{id}/audio` - Get TTS audio
- `POST /api/share/{id}/increment` - Track share count

### Profile
- `GET /api/profile` - Get user profile (XP, streak, rank)

### WebSocket
- `WS /ws/joke` - Real-time joke streaming

## Environment Variables

See `backend/.env.template` for all available options.

Required:
- `OPENAI_API_KEY` - Your OpenAI API key
- `SECRET_KEY` - Session signing key (production)

Optional:
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection for ARQ workers
- `NEWSAPI_KEY` - For trending topics feature

## Development Tips

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing API

```bash
# Health check
curl http://localhost:8000/api/health

# Generate joke
curl -X POST http://localhost:8000/api/jokes/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "cats", "style": "witty"}'
```

## License

MIT
