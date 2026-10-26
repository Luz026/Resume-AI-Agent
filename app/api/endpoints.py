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
    # Validación del Token Bearer
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

        query_text = "Hola"
        last_msg = raw_messages[-1]
        if isinstance(last_msg, dict):
            content = last_msg.get("content", "")
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(str(part["text"]))
                    else:
                        text_parts.append(str(part))
                query_text = " ".join(text_parts)
            else:
                query_text = str(content)
        else:
            query_text = str(last_msg)

        try:
            agent_result = run_agent_workflow(query_text)
        except Exception:
            agent_result = run_agent_workflow(raw_messages)
   
        response_text = ""
        citations = []

        if isinstance(agent_result, tuple) and len(agent_result) >= 2:
            response_text, citations = agent_result[0], agent_result[1]
        elif isinstance(agent_result, dict):
            if "messages" in agent_result and agent_result["messages"]:
                last_msg_res = agent_result["messages"][-1]
                if hasattr(last_msg_res, "content"):
                    response_text = last_msg_res.content
                elif isinstance(last_msg_res, dict):
                    response_text = last_msg_res.get("content", str(agent_result))
                else:
                    response_text = str(last_msg_res)
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