from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Casino Virtual API",
    description="Backend para el casino virtual ficticio",
    version="1.0.0"
)

# Configuración de CORS para conectar con React más adelante
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto por defecto de Vite/React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API del Casino Virtual funcionando correctamente"}

@app.get("/health")
def health_check():
    return {"status": "ok"}