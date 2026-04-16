# Giggle — AI Joke Engine

> **Backend:** Python 3.11 · FastAPI · SQLAlchemy 2 async · Alembic · ARQ · uvicorn  
> **Frontend:** React 18 · Vite 5 · TypeScript · Tailwind CSS · TanStack Query · Zustand  
> **DB:** SQLite (dev) → PostgreSQL + pgvector (prod)

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Development Tips](#development-tips)
- [ARQ Worker Setup](#arq-worker-setup)
- [Cloud Storage Setup](#cloud-storage-setup)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)
- [License](#license)

## Quick Start

### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **OpenAI API Key** ([Get one](https://platform.openai.com/api-keys))
- **Redis** (optional, for background workers)

### Automated Setup

**Linux/Mac:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

### Manual Setup

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.template .env
# Edit .env and add your OPENAI_API_KEY

# Initialize database
alembic upgrade head

# Run development server
uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev  # Starts on http://localhost:5173
```

The Vite dev server automatically proxies `/api/*` requests to `localhost:8000`.

#### Optional: ARQ Worker (for background scoring)

```bash
# Start Redis (if not running)
redis-server

# In a separate terminal
cd backend
source .venv/bin/activate
python start_worker.py
```

**Note:** If the worker is unavailable, the app automatically falls back to synchronous scoring.

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

# View history
alembic history
```

### Testing API

```bash
# Health check
curl http://localhost:8000/api/health

# Generate joke
curl -X POST http://localhost:8000/api/jokes/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "cats", "style": "witty"}'

# Stream joke (SSE)
curl -N http://localhost:8000/api/jokes/stream?query=dogs&style=dad
```

### Viewing Database

```bash
# SQLite
sqlite3 backend/giggle.db
.tables
SELECT * FROM jokes LIMIT 5;
.quit
```

### Custom Joke Personas

Edit `backend/services/ai.py` and add to `PERSONAS` dict:
```python
"custom": "Your custom system prompt here"
```

## ARQ Worker Setup

The ARQ worker handles background joke scoring. If unavailable, the app automatically falls back to synchronous scoring.

### Quick Start

```bash
cd backend
python start_worker.py
```

### Redis Connection Issues

**Common Issue**: `ConnectionError: Connection closed by server` with cloud Redis instances.

**Solution 1**: Use local Redis (recommended for development)
```bash
# Install Redis locally
# Windows: choco install redis-64 or scoop install redis
# Linux: sudo apt install redis-server
# Mac: brew install redis

# Start Redis
redis-server

# Update .env
REDIS_URL=redis://localhost:6379
```

**Solution 2**: The app automatically falls back to synchronous scoring if worker fails.

### Testing Worker

```bash
# Test Redis connection
cd backend
python -c "import redis; r = redis.from_url('redis://localhost:6379'); print(r.ping())"

# Check worker logs for:
# ✓ Enqueued scoring task - Task added to queue
# ✓ Scored joke - Task completed
# Using fallback scoring - Worker unavailable
```

## Cloud Storage Setup

By default, the app uses local filesystem storage. For production, you can use Cloudflare R2 or AWS S3.

### Local Storage (Default)

```env
USE_CLOUD_STORAGE=False
MEDIA_DIR=./media
```

### Cloudflare R2 (Recommended for Production)

1. Create R2 bucket at [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Create API token with Object Read & Write permissions
3. Enable public access and copy the public bucket URL
4. Update `backend/.env`:

```env
USE_CLOUD_STORAGE=True
S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=your-access-key-id
S3_SECRET_ACCESS_KEY=your-secret-access-key
S3_BUCKET_NAME=giggle-media
S3_PUBLIC_URL=https://pub-abc123.r2.dev
```

5. Install boto3: `pip install boto3`
6. Restart the app

### AWS S3

Similar setup to R2, but leave `S3_ENDPOINT_URL` empty and use your S3 bucket URL for `S3_PUBLIC_URL`.

**Cost Comparison:**
- **Cloudflare R2**: $0.015/GB/month, no egress fees
- **AWS S3**: $0.023/GB/month, $0.09/GB egress
- **Local**: Free but limited by disk space

## Common Commands

### Development

```bash
# Start backend
cd backend && source .venv/bin/activate && uvicorn main:app --reload

# Start frontend
cd frontend && npm run dev

# Start worker (optional)
cd backend && source .venv/bin/activate && python start_worker.py
```

### Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all
docker-compose down

# Rebuild
docker-compose up -d --build
```

### Database

```bash
# Reset database
rm backend/giggle.db
cd backend && alembic upgrade head
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
- **Solution**: SQLite doesn't handle concurrent writes well. Use PostgreSQL for production.

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

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed production setup instructions.

### Quick Docker Deploy

```bash
# Create production .env
cat > .env << EOF
POSTGRES_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -base64 32)
OPENAI_API_KEY=your_openai_key_here
EOF

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f
```

Access at: **http://localhost**

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS (set `secure=True` in session cookie)
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Restrict CORS origins to your domain
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets (never commit .env)
- [ ] Enable rate limiting (future enhancement)
- [ ] Set up database backups

## Additional Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Comprehensive production deployment guide

## Contributing

This is a complete, production-ready codebase. Feel free to:
- Add new joke personas
- Implement battle system
- Add trending topics
- Create custom UI components
- Improve scoring algorithm
- Add tests

## License

MIT
