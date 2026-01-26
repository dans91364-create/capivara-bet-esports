"""FastAPI main application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import games, players, props, health

app = FastAPI(
    title="Capivara Bet API",
    description="API for Capivara Bet Esports betting system",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(games.router, prefix="/api", tags=["games"])
app.include_router(players.router, prefix="/api", tags=["players"])
app.include_router(props.router, prefix="/api", tags=["props"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Capivara Bet API",
        "version": "1.0.0",
        "docs": "/docs"
    }
