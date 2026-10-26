from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any
from app.agent.graph import run_agent_workflow

router = APIRouter()

security = HTTPBearer(auto_error=False)

class OpenResponseRequest(BaseModel):
    messages: List[Dict[str, Any]]

class OpenResponse(BaseModel):
    status: str = "success"
    response: str
    citations: list[str] = []

@router.post("/responses", response_model=OpenResponse)
def open_responses_endpoint(
    body: OpenResponseRequest,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    
    try:

        answer, citations = run_agent_workflow(body.messages)
        
        return OpenResponse(
            status="success",
            response=answer,
            citations=citations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la ejecución del agente: {str(e)}")