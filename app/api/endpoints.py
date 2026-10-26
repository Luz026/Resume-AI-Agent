import os
from fastapi import APIRouter, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from app.agent.graph import run_agent_workflow

router = APIRouter()
security = HTTPBearer(auto_error=False)

API_SECRET_KEY = os.getenv("AGENT_API_KEY", "banorte_secure_agent_2026")

class OpenResponseRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    messages: Optional[List[Dict[str, Any]]] = None
    input: Optional[Any] = None 

class OpenResponse(BaseModel):
    status: str = "success"
    response: str
    citations: list[str] = []

@router.post("/responses", response_model=OpenResponse)
def open_responses_endpoint(
    body: OpenResponseRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Validación estricta del Token Bearer (Clave de API)
    if not credentials or credentials.credentials != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de API inválida o no proporcionada"
        )
    
    try:
        raw_messages = []
        if body.messages:
            raw_messages = body.messages
        elif body.input:
            if isinstance(body.input, str):
                raw_messages = [{"role": "user", "content": body.input}]
            elif isinstance(body.input, list):
                raw_messages = body.input
        else:
            raw_messages = [{"role": "user", "content": "Hola"}]

        messages_to_process = []
        for msg in raw_messages:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, dict) and "text" in part:
                            text_parts.append(str(part["text"]))
                        else:
                            text_parts.append(str(part))
                    content = " ".join(text_parts)
                elif not isinstance(content, str):
                    content = str(content)
                
                messages_to_process.append({"role": role, "content": content})
            else:
                messages_to_process.append({"role": "user", "content": str(msg)})

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