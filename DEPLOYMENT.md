# Deployment Guide

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (optional, for ARQ workers)

### Quick Start

```bash
# Run the setup script
./setup.sh

# Or manually:

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env and add OPENAI_API_KEY
alembic upgrade head
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

## Production Deployment

### Option 1: Docker Compose (Recommended)

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
docker-compose logs -f api

# Stop
docker-compose down
```

Services will be available at:
- Frontend: http://localhost
- API: http://localhost/api
- Health check: http://localhost/api/health

### Option 2: Manual Production Setup

#### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/giggle"
export REDIS_URL="redis://localhost:6379"
export OPENAI_API_KEY="your_key"
export SECRET_KEY="your_secret_key"
export DEBUG="false"

# Run migrations
alembic upgrade head

# Start with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

#### ARQ Worker (Optional)

```bash
cd backend
arq workers.settings.WorkerSettings
```

#### Frontend

```bash
cd frontend

# Build
npm run build

# Serve with nginx or any static file server
# The dist/ folder contains the built SPA
```

### Option 3: Platform-as-a-Service

#### Railway / Render / Fly.io

**Backend:**
- Build command: `pip install -r requirements.txt && alembic upgrade head`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables: Set all from .env.template

**Frontend:**
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Set `VITE_API_URL` to your backend URL

#### Vercel (Frontend only)

```bash
cd frontend
vercel --prod
```

Set environment variable:
- `VITE_API_URL`: Your backend API URL

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Environment Variables

### Backend (.env)

```bash
# Required
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./giggle.db  # Dev
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/giggle  # Prod

# Redis (optional, for ARQ workers)
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=["http://localhost:5173","https://yourdomain.com"]

# Media storage
MEDIA_DIR=./media

# Optional
NEWSAPI_KEY=your_newsapi_key
DEBUG=false
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000  # Dev
# VITE_API_URL=https://api.yourdomain.com  # Prod
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/api/health
```

### Logs

```bash
# Docker
docker-compose logs -f api
docker-compose logs -f worker

# Manual
# Check your process manager logs (systemd, pm2, etc.)
```

## Scaling

### Horizontal Scaling

- Run multiple API instances behind a load balancer
- Use PostgreSQL instead of SQLite
- Use Redis for session storage (future enhancement)
- Run multiple ARQ workers for background tasks

### Vertical Scaling

- Increase Gunicorn workers: `-w 8`
- Increase database connection pool: `pool_size=20`
- Increase Redis memory: `--maxmemory 256mb`

## Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS (set `secure=True` in session cookie)
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Restrict CORS origins to your domain
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets (never commit .env)
- [ ] Enable rate limiting (future enhancement)
- [ ] Set up database backups

## Troubleshooting

### Database locked (SQLite)

SQLite doesn't handle concurrent writes well. Use PostgreSQL in production.

### CORS errors

Check `CORS_ORIGINS` in backend/.env matches your frontend URL.

### OpenAI API errors

Verify `OPENAI_API_KEY` is set correctly and has credits.

### Media files not loading

Ensure `MEDIA_DIR` exists and is writable. Check nginx proxy configuration.

### ARQ worker not processing tasks

Ensure Redis is running and `REDIS_URL` is correct.

## Backup & Restore

### PostgreSQL

```bash
# Backup
pg_dump -U giggle giggle > backup.sql

# Restore
psql -U giggle giggle < backup.sql
```

### Media files

```bash
# Backup
tar -czf media-backup.tar.gz backend/media/

# Restore
tar -xzf media-backup.tar.gz -C backend/
```
