from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import SessionLocal, init_db
from app.routers import auth, games, users, wallet
from app.utils.seed import seed_games


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_games(db)
    yield


app = FastAPI(
    title="Casino Virtual API",
    description="Backend para el casino virtual ficticio",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wallet.router)
app.include_router(games.router)


@app.get("/")
def read_root():
    return {"message": "API del Casino Virtual funcionando correctamente"}


@app.get("/health")
def health_check():
    return {"status": "ok"}