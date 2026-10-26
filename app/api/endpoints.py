import os
from fastapi import APIRouter, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from app.agent.graph import run_agent_workflow

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Mantiene tu clave de API configurada
API_SECRET_KEY = os.getenv("AGENT_API_KEY", "banorte_secure_agent_2026")

class OpenResponseRequest(BaseModel):
    # Ignora campos extra que mande la plataforma para evitar errores 422
    model_config = ConfigDict(extra="ignore")
    
    messages: Optional[List[Dict[str, Any]]] = None
    input: Optional[Any] = None  # Soporta si la plataforma envía 'input'

class OpenResponse(BaseModel):
    status: str = "success"
    response: str
    citations: list[str] = []

@router.post("/responses", response_model=OpenResponse)
def open_responses_endpoint(
    body: OpenResponseRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Validación estricta del Token Bearer (Clave de API) que ya configuraste
    if not credentials or credentials.credentials != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de API inválida o no proporcionada"
        )
    
    try:
        # Normalizar la entrada para extraer los mensajes correctamente
        messages_to_process = []
        if body.messages:
            messages_to_process = body.messages
        elif body.input:
            if isinstance(body.input, str):
                messages_to_process = [{"role": "user", "content": body.input}]
            elif isinstance(body.input, list):
                messages_to_process = body.input
        else:
            messages_to_process = [{"role": "user", "content": "Hola"}]

        # Ejecutar el flujo de tu agente de CV
        answer, citations = run_agent_workflow(messages_to_process)
        
        return OpenResponse(
            status="success",
            response=str(answer),
            citations=citations if citations else []
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en la ejecución del agente: {str(e)}"
        )