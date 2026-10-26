import os
from fastapi import APIRouter, HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any
from app.agent.graph import run_agent_workflow

router = APIRouter()
security = HTTPBearer(auto_error=False)

API_SECRET_KEY = os.getenv("AGENT_API_KEY", "banorte_secure_agent_2026")

class OpenResponse(BaseModel):
    status: str = "success"
    response: str
    citations: list[str] = []

@router.post("/responses", response_model=OpenResponse)
async def open_responses_endpoint(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security)
):

    if not credentials or credentials.credentials != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de API inválida o no proporcionada"
        )
    
    try:
        try:
            body = await request.json()
        except Exception:
            body = {}

        raw_messages = []
        if isinstance(body, dict):
            if "messages" in body and isinstance(body["messages"], list):
                raw_messages = body["messages"]
            elif "input" in body:
                inp = body["input"]
                if isinstance(inp, str):
                    raw_messages = [{"role": "user", "content": inp}]
                elif isinstance(inp, list):
                    raw_messages = inp
            elif "prompt" in body:
                raw_messages = [{"role": "user", "content": str(body["prompt"])}]
        
        if not raw_messages:
            raw_messages = [{"role": "user", "content": "¿Cuál es la experiencia de Sandra?"}]

        sanitized_messages = []
        for m in raw_messages:
            if isinstance(m, dict):
                role = str(m.get("role", "user"))
                content = m.get("content", "")
                
                if isinstance(content, list):
                    flat_content = " ".join(
                        str(p.get("text", p)) if isinstance(p, dict) else str(p) 
                        for p in content
                    )
                else:
                    flat_content = str(content)
                    
                sanitized_messages.append({"role": role, "content": flat_content})
            elif isinstance(m, str):
                sanitized_messages.append({"role": "user", "content": m})

        agent_result = run_agent_workflow(sanitized_messages)

        response_text = ""
        citations = []

        if isinstance(agent_result, tuple) and len(agent_result) >= 2:
            response_text, citations = agent_result[0], agent_result[1]
        elif isinstance(agent_result, dict):
            if "messages" in agent_result and agent_result["messages"]:
                last_msg = agent_result["messages"][-1]
                if hasattr(last_msg, "content"):
                    response_text = last_msg.content
                elif isinstance(last_msg, dict):
                    response_text = last_msg.get("content", str(agent_result))
                else:
                    response_text = str(last_msg)
            elif "response" in agent_result:
                response_text = agent_result["response"]
            elif "output" in agent_result:
                response_text = agent_result["output"]
            else:
                response_text = str(agent_result)
        else:
            response_text = str(agent_result)

        if not isinstance(citations, list):
            citations = []
        citations = [str(c) for c in citations]

        return OpenResponse(
            status="success",
            response=str(response_text),
            citations=citations
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error en la ejecución del agente: {str(e)}"
        )