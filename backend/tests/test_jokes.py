"""
Core test suite — covers the three highest-risk paths identified in the
architecture review, plus regression tests for each fix applied.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.joke import Joke
from services.joke_store import save_joke


# ═══════════════════════════════════════════════════════════════════════════════
# Phase-2 regression: cache hit uses index (normalised query)
# ═══════════════════════════════════════════════════════════════════════════════

class TestJokeCacheHit:
    @pytest.mark.asyncio
    async def test_same_query_returns_same_id(self, async_client: AsyncClient):
        """Two generate requests with identical query+style must return the same joke id."""
        payload = {"query": "cats", "style": "witty"}

        with patch("routers.jokes.ai.get_joke", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = "Why do cats knock things off tables? Science."

            r1 = await async_client.post("/api/jokes/generate", json=payload)
            r2 = await async_client.post("/api/jokes/generate", json=payload)

        assert r1.status_code == 200
        assert r2.status_code == 200
        # Second call must be a cache hit — same DB row, AI called only once
        assert r1.json()["id"] == r2.json()["id"]
        mock_ai.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_stored_lowercase(self, db_session: AsyncSession):
        """Jokes must be stored with a lower-cased query for index lookup."""
        joke = await save_joke(
            db_session,
            query="Working From HOME [Witty]",
            response="Some joke",
            source="ai_generated",
            enqueue_scoring=False,
        )
        assert joke.query == "working from home [witty]"

    @pytest.mark.asyncio
    async def test_regenerate_flag_bypasses_cache(self, async_client: AsyncClient):
        """regenerate=True must skip the cache and call the AI again."""
        payload = {"query": "dogs", "style": "dad", "regenerate": False}

        with patch("routers.jokes.ai.get_joke", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = "A fresh dog joke."
            r1 = await async_client.post("/api/jokes/generate", json=payload)

        with patch("routers.jokes.ai.get_joke", new_callable=AsyncMock) as mock_ai2:
            mock_ai2.return_value = "Another dog joke."
            r2 = await async_client.post(
                "/api/jokes/generate", json={**payload, "regenerate": True}
            )

        assert r1.status_code == 200
        assert r2.status_code == 200
        mock_ai2.assert_called_once()           # AI called despite existing cached joke
        assert r2.json()["id"] != r1.json()["id"]


# ═══════════════════════════════════════════════════════════════════════════════
# Phase-3 regression: JOTD race condition (atomic upsert)
# ═══════════════════════════════════════════════════════════════════════════════

class TestJokeOfTheDay:
    @pytest.mark.asyncio
    async def test_concurrent_requests_all_succeed(self, async_client: AsyncClient):
        """10 simultaneous JOTD requests must all return 200 and the same joke."""
        with patch("services.daily_joke.fetch_joke_from_api", new_callable=AsyncMock) as mock_fetch, \
             patch("services.daily_joke.enhance_joke_with_emojis", new_callable=AsyncMock) as mock_enhance, \
             patch("services.cache.cache_get", new_callable=AsyncMock) as mock_cget, \
             patch("services.cache.cache_set", new_callable=AsyncMock):

            mock_cget.return_value = None          # force cache miss → DB path
            mock_fetch.return_value = "Why did the chicken cross the road?"
            mock_enhance.return_value = "Why did the chicken cross the road? 🐔"

            results = await asyncio.gather(*[
                async_client.get("/api/jokes/joke-of-the-day")
                for _ in range(10)
            ])

        assert all(r.status_code == 200 for r in results), [r.text for r in results]
        jokes = {r.json()["joke"] for r in results}
        assert len(jokes) == 1, f"Expected 1 unique joke, got {len(jokes)}: {jokes}"

    @pytest.mark.asyncio
    async def test_redis_cache_hit_skips_db(self, async_client: AsyncClient):
        """A Redis cache hit must not touch the DB at all."""
        cached_joke = "Cached joke from Redis 😄"

        with patch("services.daily_joke.cache_get", new_callable=AsyncMock) as mock_cget, \
             patch("services.daily_joke.fetch_joke_from_api", new_callable=AsyncMock) as mock_fetch:

            mock_cget.return_value = {"joke": cached_joke}

            r = await async_client.get("/api/jokes/joke-of-the-day")

        assert r.status_code == 200
        assert r.json()["joke"] == cached_joke
        mock_fetch.assert_not_called()


# ═══════════════════════════════════════════════════════════════════════════════
# Phase-3 regression: unified transaction (joke + XP)
# ═══════════════════════════════════════════════════════════════════════════════

class TestUnifiedTransaction:
    @pytest.mark.asyncio
    async def test_xp_awarded_with_joke(self, async_client: AsyncClient):
        """XP must be awarded in the same request that creates the joke."""
        with patch("routers.jokes.ai.get_joke", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = "A funny joke about trees."
            r = await async_client.post(
                "/api/jokes/generate",
                json={"query": "trees", "style": "witty"},
            )

        assert r.status_code == 200
        # Profile endpoint should reflect +5 XP from the generate call
        profile_r = await async_client.get("/api/profile")
        assert profile_r.status_code == 200
        assert profile_r.json()["xp"] >= 5


# ═══════════════════════════════════════════════════════════════════════════════
# Phase-4 regression: keyset pagination
# ═══════════════════════════════════════════════════════════════════════════════

class TestKeysetPagination:
    @pytest.mark.asyncio
    async def test_first_page_returns_next_cursor(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """A full first page must include a next_cursor for subsequent pages."""
        # Seed 10 jokes directly into DB
        for i in range(10):
            await save_joke(
                db_session,
                query=f"seed joke {i} [witty]",
                response=f"Seed joke number {i}",
                source="ai_generated",
                enqueue_scoring=False,
                auto_commit=False,
            )
        await db_session.commit()

        r = await async_client.get("/api/jokes/history?page_size=5")
        assert r.status_code == 200
        data = r.json()
        assert len(data["jokes"]) == 5
        assert data["next_cursor"] is not None

    @pytest.mark.asyncio
    async def test_cursor_returns_different_page(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Passing next_cursor must return the next distinct set of jokes."""
        for i in range(12):
            await save_joke(
                db_session,
                query=f"cursor test {i} [witty]",
                response=f"Cursor test joke {i}",
                source="ai_generated",
                enqueue_scoring=False,
                auto_commit=False,
            )
        await db_session.commit()

        r1 = await async_client.get("/api/jokes/history?page_size=5")
        assert r1.status_code == 200
        cursor = r1.json()["next_cursor"]
        ids_page1 = {j["id"] for j in r1.json()["jokes"]}

        r2 = await async_client.get(f"/api/jokes/history?page_size=5&cursor={cursor}")
        assert r2.status_code == 200
        ids_page2 = {j["id"] for j in r2.json()["jokes"]}

        assert ids_page1.isdisjoint(ids_page2), "Pages must not overlap"

    @pytest.mark.asyncio
    async def test_last_page_has_no_cursor(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """The final page must return next_cursor=None."""
        # Seed exactly 3 jokes so the last page has fewer than page_size
        for i in range(3):
            await save_joke(
                db_session,
                query=f"last page {i} [witty]",
                response=f"Last page joke {i}",
                source="ai_generated",
                enqueue_scoring=False,
                auto_commit=False,
            )
        await db_session.commit()

        # Get all with a large page_size
        r = await async_client.get("/api/jokes/history?page_size=50")
        assert r.status_code == 200
        assert r.json()["next_cursor"] is None


# ═══════════════════════════════════════════════════════════════════════════════
# Phase-1 regression: style field validation
# ═══════════════════════════════════════════════════════════════════════════════

class TestStyleValidation:
    @pytest.mark.asyncio
    async def test_invalid_style_returns_422(self, async_client: AsyncClient):
        """An unknown style value must be rejected with a 422 Unprocessable Entity."""
        r = await async_client.post(
            "/api/jokes/generate",
            json={"query": "cats", "style": "completely_invalid_style_xyz"},
        )
        assert r.status_code == 422

    @pytest.mark.asyncio
    async def test_valid_style_accepted(self, async_client: AsyncClient):
        """All known style values must be accepted."""
        valid_styles = ["witty", "dad", "sarcastic", "roast", "haiku"]
        with patch("routers.jokes.ai.get_joke", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = "A valid joke."
            for style in valid_styles:
                r = await async_client.post(
                    "/api/jokes/generate",
                    json={"query": "test", "style": style, "regenerate": True},
                )
                assert r.status_code == 200, f"Style {style!r} was rejected: {r.text}"


# ═══════════════════════════════════════════════════════════════════════════════
# Phase-3 regression: typed error responses
# ═══════════════════════════════════════════════════════════════════════════════

class TestTypedErrors:
    @pytest.mark.asyncio
    async def test_joke_not_found_returns_error_code(self, async_client: AsyncClient):
        """A missing joke must return a typed error envelope with code=joke_not_found."""
        r = await async_client.get("/api/jokes/999999")
        assert r.status_code == 404
        detail = r.json()["detail"]
        assert detail["code"] == "joke_not_found"
        assert "message" in detail

    @pytest.mark.asyncio
    async def test_ai_failure_returns_error_code(self, async_client: AsyncClient):
        """An AI service failure must return code=ai_unavailable."""
        with patch("routers.jokes.ai.get_joke", side_effect=Exception("OpenAI down")):
            r = await async_client.post(
                "/api/jokes/generate",
                json={"query": "test", "style": "witty"},
            )
        assert r.status_code == 503
        detail = r.json()["detail"]
        assert detail["code"] == "ai_unavailable"


# ═══════════════════════════════════════════════════════════════════════════════
# Health endpoint
# ═══════════════════════════════════════════════════════════════════════════════

class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_ok_when_db_reachable(self, async_client: AsyncClient):
        """Health must return 200 when the DB is reachable."""
        with patch("main.aioredis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_instance.aclose = AsyncMock()
            mock_redis.from_url.return_value = mock_instance

            r = await async_client.get("/api/health")

        assert r.status_code == 200
        assert r.json()["db"] == "ok"

    @pytest.mark.asyncio
    async def test_health_degraded_when_redis_down(self, async_client: AsyncClient):
        """Health must return 503 when Redis is unreachable."""
        with patch("main.aioredis") as mock_redis:
            mock_redis.from_url.side_effect = Exception("Redis unreachable")
            r = await async_client.get("/api/health")

        assert r.status_code == 503
        body = r.json()
        assert body["status"] == "degraded"
        assert body["redis"] == "error"
