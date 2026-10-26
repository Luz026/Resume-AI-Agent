from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Enterprise Resume Agent",
    version="3.0.0",
    description="Agente de CV con arquitectura segura y gobernanza de memoria."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": "Enterprise Resume Agent - Reto IA Banorte",
        "docs": "/docs"
    }