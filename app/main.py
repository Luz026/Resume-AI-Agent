from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.endpoints import router as api_router

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Enterprise Resume Agent",
    version="3.0.0",
    description="Agente de CV con arquitectura segura y gobernanza de memoria."
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Registrar rutas
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)