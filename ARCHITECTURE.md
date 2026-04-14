# Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Pages   │  │Components│  │  Hooks   │  │  Stores  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └─────────────┴─────────────┴─────────────┘           │
│                         │                                    │
│                    API Client (Axios)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/SSE/WebSocket
┌─────────────────────────┴───────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Routers  │→ │ Services │→ │  Models  │→ │ Database │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│       │             │                                        │
│       │        ┌────┴─────┐                                 │
│       │        │ OpenAI   │                                 │
│       │        │   API    │                                 │
│       │        └──────────┘                                 │
│       │                                                      │
│  ┌────┴─────────────┐                                       │
│  │  ARQ Workers     │← Redis Queue                          │
│  │ (Background)     │                                       │
│  └──────────────────┘                                       │
└──────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Layers

1. **Routers** (`routers/`)
   - HTTP endpoint definitions
   - Request validation (Pydantic)
   - Response serialization
   - Dependency injection

2. **Services** (`services/`)
   - Business logic
   - External API integration (OpenAI, NewsAPI)
   - Image generation
   - Audio generation

3. **Models** (`models/`)
   - SQLAlchemy ORM models
   - Database schema definitions
   - Relationships

4. **Schemas** (`schemas/`)
   - Pydantic models for request/response
   - Data validation
   - Serialization

5. **Dependencies** (`dependencies/`)
   - Reusable FastAPI dependencies
   - Profile management
   - Authentication helpers

6. **Middleware** (`middleware/`)
   - Session management
   - Request/response processing

7. **Workers** (`workers/`)
   - Background task definitions (ARQ)
   - Async job processing

8. **Tasks** (`tasks/`)
   - Scheduled jobs (APScheduler)
   - Periodic tasks

### Data Flow

#### Joke Generation (Streaming)

```
User Input → Router → AI Service → OpenAI API
                ↓                      ↓
            Profile Dep          Stream tokens
                ↓                      ↓
            Update XP            SSE to client
                ↓                      ↓
            Save Joke            Display tokens
                ↓
            Enqueue Score Job
                ↓
            ARQ Worker → Score → Update DB
```

#### Session Management

```
Request → Session Middleware
            ↓
        Extract/Create Session ID
            ↓
        Sign with itsdangerous
            ↓
        Set Cookie
            ↓
        Attach to request.state
            ↓
        Profile Dependency
            ↓
        Load/Create Profile
            ↓
        Update Streak/XP
```

## Frontend Architecture

### State Management

1. **Zustand Stores**
   - `themeStore`: Dark mode toggle
   - `profileStore`: User XP, streak, rank
   - `jokeStore`: Current joke, style, streaming state

2. **TanStack Query**
   - Server state caching
   - Automatic refetching
   - Optimistic updates
   - Pagination

### Component Hierarchy

```
App
├── Root Layout
│   ├── NavBar
│   ├── InstallBanner (PWA)
│   └── Outlet
│       ├── Home
│       │   ├── StyleSelect
│       │   ├── TrendChips
│       │   ├── JokeCard
│       │   │   ├── ShareButton
│       │   │   ├── AudioPlayer
│       │   │   └── ScoreBars
│       │   └── HeckleBox
│       ├── History
│       │   └── JokeCard (list)
│       ├── Battle
│       ├── Heckle
│       └── JokeDetail
└── Toaster (notifications)
```

### Custom Hooks

- `useJokeStream`: SSE streaming with abort control
- `useSwipe`: Touch gesture handling
- `useWebSocket`: WebSocket connection management
- `useAudio`: Audio playback control
- `usePWA`: Install prompt handling

## Database Schema

### Tables

#### `jokes`
```sql
id               INTEGER PRIMARY KEY
query            VARCHAR(100) INDEX
response         TEXT
created_at       DATETIME DEFAULT NOW()
share_count      INTEGER DEFAULT 0
audio_url        TEXT NULL
score_originality INTEGER NULL
score_timing     INTEGER NULL
score_cleverness INTEGER NULL
```

#### `user_profiles`
```sql
id          INTEGER PRIMARY KEY
session_key VARCHAR(64) UNIQUE INDEX
xp          INTEGER DEFAULT 0
streak      INTEGER DEFAULT 0
last_visit  DATE NULL
created_at  DATETIME DEFAULT NOW()
```

### Indexes

- `jokes.query`: Fast cache lookup
- `user_profiles.session_key`: Session-based profile retrieval

## API Design

### REST Endpoints

```
POST   /api/jokes/generate      - Generate joke (cached)
GET    /api/jokes/stream        - SSE streaming
GET    /api/jokes/history       - Paginated history
GET    /api/jokes/{id}          - Get specific joke
DELETE /api/jokes/{id}          - Delete joke
POST   /api/jokes/{id}/heckle   - AI roast
POST   /api/jokes/{id}/explain  - AI explanation

GET    /api/share/{id}/card.png - Download PNG card
GET    /api/share/{id}/audio    - Get TTS audio
POST   /api/share/{id}/increment - Track share

GET    /api/profile             - Get user profile

POST   /api/heckle              - Rate user joke

WS     /ws/joke                 - WebSocket streaming
```

### Response Formats

#### Success
```json
{
  "id": 123,
  "query": "cats [witty]",
  "response": "Why do cats...",
  "created_at": "2024-01-01T12:00:00",
  "share_count": 5,
  "audio_url": "/media/audio/joke_123.mp3",
  "score_originality": 8,
  "score_timing": 7,
  "score_cleverness": 9
}
```

#### Error
```json
{
  "detail": "Joke not found"
}
```

## Caching Strategy

### Application Level

1. **Joke Cache**: Query + style → cached joke
2. **Profile Cache**: Session ID → profile (in-memory during request)
3. **Media Cache**: Generated audio/images stored on disk

### HTTP Caching

- Static assets: 1 year (`immutable`)
- Media files: 7 days
- API responses: No cache (dynamic)
- SSE streams: No cache, no buffering

## Security

### Session Management

- Cookie-based sessions
- Signed with `itsdangerous`
- HttpOnly flag
- SameSite=Lax
- 1-year expiration

### CORS

- Configurable origins
- Credentials allowed
- All methods/headers (dev)

### Input Validation

- Pydantic schemas
- Max lengths enforced
- SQL injection prevention (ORM)
- XSS prevention (React escaping)

## Performance

### Backend

- Async/await throughout
- Connection pooling (PostgreSQL)
- Streaming responses (SSE)
- Background workers (ARQ)
- Scheduled tasks (APScheduler)

### Frontend

- Code splitting (React.lazy)
- Route-based chunks
- PWA caching
- Optimistic updates
- Debounced inputs

### Database

- Indexed queries
- Async SQLAlchemy
- Connection pooling
- Query optimization

## Scalability

### Horizontal Scaling

- Stateless API (session in cookie)
- Multiple API instances
- Load balancer
- Shared PostgreSQL
- Shared Redis

### Vertical Scaling

- Increase workers
- Increase pool size
- Increase Redis memory
- Optimize queries

## Monitoring

### Health Checks

- `/api/health`: Basic liveness
- Database connectivity
- Redis connectivity (if enabled)

### Logging

- Request/response logging
- Error tracking
- Performance metrics
- Background job status

## Future Enhancements

### Phase 4: Advanced AI
- [ ] Background joke scoring (ARQ)
- [ ] Semantic similarity (pgvector)
- [ ] Duplicate detection
- [ ] Quality filtering

### Phase 5: Real-time
- [ ] WebSocket streaming
- [ ] Live battles
- [ ] Real-time voting
- [ ] Presence indicators

### Phase 6: Production
- [ ] Rate limiting
- [ ] API authentication
- [ ] User accounts
- [ ] Analytics
- [ ] A/B testing
- [ ] CDN integration
- [ ] Multi-region deployment
