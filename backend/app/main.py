"""FastAPI entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import DISCLOSURE
from backend.app.db.database import init_db
from backend.app.routes.paper_trade_routes import router as paper_trade_router
from backend.app.routes.portfolio_routes import router as portfolio_router
from backend.app.routes.scan_routes import router as scan_router
from backend.app.routes.settings_routes import router as settings_router

app = FastAPI(title="QuanTrade AI Agent", version="0.1.0")
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    """Initialize local database."""
    init_db()


@app.get("/health")
def health() -> dict[str, object]:
    """Health check."""
    return {"ok": True, "app": "QuanTrade AI Agent", "paper_mode": True, "disclosure": DISCLOSURE}


app.include_router(scan_router)
app.include_router(settings_router)
app.include_router(paper_trade_router)
app.include_router(portfolio_router)
