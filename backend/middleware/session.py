import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from itsdangerous import TimestampSigner, BadSignature

class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.signer = TimestampSigner(secret_key)

    async def dispatch(self, request: Request, call_next):
        # Extremely simple cookie-based session ID
        session_id = request.cookies.get("session_id")
        
        if session_id:
            try:
                # Basic validation (could be more robust)
                unsigned = self.signer.unsign(session_id, max_age=3600*24*30).decode()
                request.state.session_id = unsigned
            except BadSignature:
                session_id = None

        if not session_id:
            new_id = str(uuid.uuid4())
            request.state.session_id = new_id
            session_id = self.signer.sign(new_id).decode()

        # Attach session dict to request (Starlette style)
        request.scope["session"] = {"session_id": request.state.session_id}
        
        response = await call_next(request)
        response.set_cookie("session_id", session_id, httponly=True, samesite="lax")
        return response
