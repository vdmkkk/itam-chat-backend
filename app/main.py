from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

app = FastAPI(
    title="ITAM Chat Backend",
    version="0.1.0",
    description=(
        "Backend for a messenger app. Provides JWT auth, user search, chats with previews, "
        "chat contents with pagination, and real-time messaging via WebSockets."
    ),
    openapi_version="3.0.3",
)

# Respect X-Forwarded-* from Caddy to get correct scheme/host for URL generation
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers.auth import router as auth_router
from app.routers.search import router as search_router
from app.routers.chats import router as chats_router
from app.routers.ws import router as ws_router
from app.routers.asyncapi_docs import router as asyncapi_router

app.include_router(auth_router)
app.include_router(search_router)
app.include_router(chats_router)
app.include_router(ws_router)
app.include_router(asyncapi_router)


@app.get("/health", tags=["Health"], summary="Health check")
async def health() -> dict:
    return {"status": "ok"}


