# Joke of the Day Feature

## Overview
The Joke of the Day feature displays a daily joke from API Ninjas when users open the app. The joke is **fetched once per day** and **cached in the database** (PostgreSQL), so all users see the same joke without making repeated API calls.

## Implementation

### Backend

#### Database Model
- **Table**: `daily_jokes`
- **Fields**:
  - `id`: Primary key
  - `joke_date`: Date (unique, indexed) - UTC timezone
  - `joke_text`: The joke content
  - `source`: Source identifier (default: "api_ninjas")

#### Service Layer (`backend/services/daily_joke.py`)
- `get_or_fetch_daily_joke()`: Checks database first, fetches from API if needed
- `fetch_joke_from_api()`: Calls API Ninjas endpoint
- `cleanup_old_jokes()`: Removes jokes older than 7 days

#### API Endpoint
- **Route**: `GET /api/jokes/joke-of-the-day`
- **Response**: `{"joke": "string"}`
- **Caching**: Checks database for today's joke (UTC), fetches from API Ninjas only if not cached

#### Scheduled Tasks (`backend/tasks/scheduler.py`)
- Daily cleanup at 1 AM UTC to remove jokes older than 7 days
- Prevents database bloat

### Frontend
- **Location**: Home page (`frontend/src/pages/Home.tsx`)
- **Display**: Prominent gradient banner at the top of the home page
- **Loading State**: Skeleton loader while fetching
- **Error Handling**: Silent failure (banner doesn't show if API fails)

## API Details

**External API**: `https://api.api-ninjas.com/v1/jokeoftheday`

**Headers**:
- `X-Api-Key`: Your API Ninjas key

**Response**:
```json
[
  {
    "joke": "Why did the scarecrow win an award? He was outstanding in his field."
  }
]
```

## Configuration

Add to your `.env` file:
```env
API_NINJAS_KEY=Xypg6eCJJYyF6p4EgJOC4SFdi81clB0bJu6lYfJL
```

## Database Migration

Run the migration to create the `daily_jokes` table:
```bash
cd backend
alembic upgrade head
```

## How It Works

1. **First Request of the Day**:
   - User opens the app
   - Frontend calls `/api/jokes/joke-of-the-day`
   - Backend checks database for today's joke (UTC date)
   - Not found → Fetches from API Ninjas
   - Stores in database with today's date
   - Returns joke to frontend

2. **Subsequent Requests**:
   - User opens the app
   - Frontend calls `/api/jokes/joke-of-the-day`
   - Backend finds today's joke in database
   - Returns cached joke (no API call)

3. **Next Day**:
   - Date changes (UTC timezone)
   - First request triggers new API fetch
   - New joke cached for the new day

4. **Cleanup**:
   - Scheduled task runs daily at 1 AM UTC
   - Removes jokes older than 7 days
   - Keeps database lean

## Benefits

✅ **Reduced API Calls**: Only 1 API call per day instead of per user  
✅ **Consistent Experience**: All users see the same joke  
✅ **Fast Loading**: Cached jokes load instantly  
✅ **Cost Efficient**: Minimizes external API usage  
✅ **Reliable**: Works even if API Ninjas is slow  
✅ **Automatic Cleanup**: Old jokes are removed automatically  

## Timezone

Uses **UTC timezone** to determine when to fetch a new joke. This ensures consistent behavior across all users regardless of their location.

## Dependencies
- `httpx>=0.27.0` - HTTP client for API requests
- PostgreSQL database (already configured)
- APScheduler (already configured)

