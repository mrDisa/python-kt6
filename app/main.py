from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.core.config import get_settings
from app.core.limiter import limiter
from app.modules.auth.router import router as auth_router
from app.modules.projects.router import router as projects_router
from app.modules.todos.router import router as todos_router

app = FastAPI(title="TaskBoard | KT6", version="1.0.0", description="Final course project: modular API, PostgreSQL, JWT, Celery")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=get_settings().allowed_origins, allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(todos_router)

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
