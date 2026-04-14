# ARQ Worker Guide

## Overview

The ARQ worker handles background joke scoring. If the worker is unavailable, the app automatically falls back to synchronous scoring.

## Quick Start

```bash
cd backend
python start_worker.py
```

## Redis Cloud Connection Issues

**Common Issue**: `ConnectionError: Connection closed by server`

This happens with Redis cloud instances (Redis Labs, Upstash) due to:
- Idle connection timeouts
- Network latency
- Free tier connection limits

### Solution 1: Automatic Fallback (Already Implemented)

The app now automatically falls back to synchronous scoring if the worker fails. **No action needed!**

### Solution 2: Use Local Redis (Recommended for Development)

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

### Solution 3: Keep Using Cloud Redis

The worker will attempt to reconnect automatically. Expect occasional disconnections with cloud Redis free tiers.

## Testing

### Test Redis Connection
```bash
cd backend
python test_redis.py
```

### Test Worker Imports
```bash
cd backend
python test_worker.py
```

### Test Scoring
1. Start the worker (or don't - fallback will work)
2. Generate a joke via the API
3. Check the joke scores in the database or UI

## How It Works

1. **With Worker**: Jokes are scored asynchronously in the background
2. **Without Worker**: Jokes are scored synchronously (still non-blocking for the user)

Both methods work fine - the worker just allows better scalability.

## Production Deployment

For production, run the worker as a separate service:

### Docker Compose
```yaml
worker:
  build: ./backend
  command: python start_worker.py
  environment:
    - REDIS_URL=redis://redis:6379
    - DATABASE_URL=postgresql://...
  depends_on:
    - redis
    - db
  restart: unless-stopped
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: giggle-worker
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: worker
        image: giggle-backend
        command: ["python", "start_worker.py"]
        env:
        - name: REDIS_URL
          value: redis://redis:6379
```

## Monitoring

Check Redis queue:
```bash
redis-cli
> LLEN arq:queue
> KEYS arq:*
```

Check worker logs for:
- `✓ Enqueued scoring task` - Task added to queue
- `✓ Scored joke` - Task completed
- `Using fallback scoring` - Worker unavailable, using fallback
