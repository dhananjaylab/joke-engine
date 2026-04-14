# Quick Reference Guide

## 🚀 Common Commands

### Development

```bash
# Start backend
cd backend && source .venv/bin/activate && uvicorn main:app --reload

# Start frontend
cd frontend && npm run dev

# Start worker (optional)
cd backend && source .venv/bin/activate && arq workers.settings.WorkerSettings
```

### Database

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
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

## 📡 API Endpoints

### Jokes
```
POST   /api/jokes/generate       Generate joke (cached)
GET    /api/jokes/stream         SSE streaming
GET    /api/jokes/history        Paginated list
GET    /api/jokes/{id}           Get specific joke
DELETE /api/jokes/{id}           Delete joke
POST   /api/jokes/{id}/heckle    AI roast
POST   /api/jokes/{id}/explain   AI explanation
```

### Share
```
GET    /api/share/{id}/card.png  Download PNG
GET    /api/share/{id}/audio     Get TTS audio
POST   /api/share/{id}/increment Track share
```

### Profile
```
GET    /api/profile              User stats
```

### Heckle
```
POST   /api/heckle               Rate user joke
```

### WebSocket
```
WS     /ws/joke                  Real-time streaming
```

## 🎭 Joke Personas

| Style | Description |
|-------|-------------|
| `witty` | Classic stand-up comedy |
| `dad` | Wholesome puns and groaners |
| `sarcastic` | Dry, cutting humor |
| `roast` | Insult comedy (tasteful) |
| `haiku` | 5-7-5 syllable poems |
| `brainrot` | Gen-Z internet chaos |
| `nocontext` | Confusing punchlines only |
| `emoji` | Pure emoji comedy |

## 🏆 Rank System

| XP Required | Rank |
|-------------|------|
| 0 | Open Mic |
| 50 | Club Regular |
| 150 | Headliner |
| 400 | Legend |
| 1000 | GOAT |

## 📁 Key Files

### Backend
```
backend/
├── main.py                    # App entry point
├── core/config.py             # Settings
├── core/database.py           # DB connection
├── models/joke.py             # Joke model
├── models/profile.py          # Profile model
├── routers/jokes.py           # Joke endpoints
├── services/ai.py             # OpenAI integration
├── middleware/session.py      # Session management
└── .env                       # Configuration
```

### Frontend
```
frontend/
├── src/
│   ├── api/client.ts         # Axios instance
│   ├── api/jokes.ts          # API functions
│   ├── hooks/useJokeStream.ts # SSE streaming
│   ├── store/jokeStore.ts    # Joke state
│   └── store/profileStore.ts # Profile state
└── vite.config.ts            # Vite config
```

## 🔧 Environment Variables

### Backend (.env)
```bash
OPENAI_API_KEY=sk-...          # Required
SECRET_KEY=random-string       # Required for prod
DATABASE_URL=sqlite+...        # Default: SQLite
REDIS_URL=redis://...          # Optional
CORS_ORIGINS=["http://..."]    # Frontend URLs
DEBUG=false                    # Production
```

### Frontend (.env)
```bash
VITE_API_URL=http://...        # Backend URL
```

## 🐛 Debugging

### Check Backend Health
```bash
curl http://localhost:8000/api/health
```

### View Backend Logs
```bash
# Development
# Logs appear in terminal

# Docker
docker-compose logs -f api
```

### View Database
```bash
sqlite3 backend/giggle.db
.tables
SELECT * FROM jokes LIMIT 5;
.quit
```

### Test API
```bash
# Generate joke
curl -X POST http://localhost:8000/api/jokes/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "cats", "style": "witty"}'

# Stream joke
curl -N http://localhost:8000/api/jokes/stream?query=dogs&style=dad
```

## 📦 Dependencies

### Backend (Python)
- fastapi - Web framework
- uvicorn - ASGI server
- sqlalchemy - ORM
- alembic - Migrations
- openai - AI integration
- pillow - Image generation
- itsdangerous - Session signing
- arq - Background tasks
- apscheduler - Scheduled tasks

### Frontend (Node)
- react - UI library
- vite - Build tool
- axios - HTTP client
- zustand - State management
- @tanstack/react-query - Server state
- tailwindcss - Styling
- vite-plugin-pwa - PWA support

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS (set `secure=True` in cookies)
- [ ] Restrict `CORS_ORIGINS` to your domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong database password
- [ ] Keep dependencies updated
- [ ] Never commit `.env` files

## 🚀 Deployment Checklist

- [ ] Set all environment variables
- [ ] Run database migrations
- [ ] Build frontend (`npm run build`)
- [ ] Configure nginx/reverse proxy
- [ ] Set up SSL certificate
- [ ] Configure firewall
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test all endpoints
- [ ] Load test

## 📊 Performance Tips

### Backend
- Use PostgreSQL for production
- Enable connection pooling
- Use Redis for caching
- Run multiple workers
- Enable gzip compression

### Frontend
- Enable PWA caching
- Use code splitting
- Optimize images
- Enable CDN
- Minimize bundle size

## 🔗 Useful Links

- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Health Check: http://localhost:8000/api/health

## 💡 Tips & Tricks

### Custom Personas
Edit `backend/services/ai.py` and add to `PERSONAS` dict:
```python
"custom": "Your custom system prompt here"
```

### Change Joke Model
Edit `backend/services/ai.py`:
```python
model="gpt-4o-mini"  # or "gpt-4", "gpt-3.5-turbo"
```

### Adjust Creativity
Edit `backend/services/ai.py`:
```python
temperature=0.65  # 0.0 = deterministic, 1.0 = creative
```

### Add New Endpoint
1. Create function in `backend/routers/`
2. Add router to `backend/main.py`
3. Create API function in `frontend/src/api/`
4. Use in component with TanStack Query

### Database Reset
```bash
rm backend/giggle.db
cd backend && alembic upgrade head
```

## 🎯 Common Tasks

### Add a new joke style
1. Edit `backend/services/ai.py`
2. Add to `PERSONAS` dict
3. Update frontend style selector

### Change XP rewards
1. Edit `backend/dependencies/profile.py`
2. Modify XP values in profile logic

### Customize rank thresholds
1. Edit `backend/models/profile.py`
2. Update `RANK_THRESHOLDS` list

### Add new API endpoint
1. Create in `backend/routers/`
2. Add to `backend/main.py`
3. Create client function in `frontend/src/api/`

---

**For detailed information, see:**
- [README.md](README.md) - Overview
- [GETTING_STARTED.md](GETTING_STARTED.md) - Setup guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current status
