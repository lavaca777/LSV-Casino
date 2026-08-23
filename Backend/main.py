from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, users, wallet


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Casino Virtual API",
    description="Backend para el casino virtual ficticio",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuración de CORS para conectar con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto por defecto de Vite/React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wallet.router)


@app.get("/")
def read_root():
    return {"message": "API del Casino Virtual funcionando correctamente"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
