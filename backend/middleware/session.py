import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from itsdangerous import URLSafeSerializer

COOKIE_NAME = "giggle_session"


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.signer = URLSafeSerializer(secret_key, salt="giggle-session")

    async def dispatch(self, request: Request, call_next):
        raw = request.cookies.get(COOKIE_NAME)
        try:
            session_id: str = self.signer.loads(raw) if raw else None
        except Exception:
            session_id = None

        if not session_id:
            session_id = str(uuid.uuid4())

        request.state.session_id = session_id
        response = await call_next(request)

        # Re-set cookie with fresh signed value
        signed = self.signer.dumps(session_id)
        response.set_cookie(
            COOKIE_NAME, signed,
            httponly=True,
            samesite="lax",
            secure=False,           # set True in production (HTTPS)
            max_age=60 * 60 * 24 * 365,
        )
        return response
