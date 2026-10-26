
import os
import logging
from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.agent.graph import run_agent_workflow
from app.agent.security import SecurityGuardrails

router = APIRouter()
security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

API_SECRET_KEY = os.getenv("AGENT_API_KEY")


class OpenResponse(BaseModel):
    status: str = "success"
    response: str
    citations: list[str] = Field(default_factory=list)


def content_to_text(content: Any) -> str:
    """Convierte contenido de mensajes a texto."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])

        return " ".join(parts)

    if content is None:
        return ""

    return str(content)


def normalize_messages(raw_messages: list) -> list[dict[str, str]]:
    """Valida la estructura y normaliza los mensajes recibidos."""
    sanitized_messages = []
    allowed_roles = {"system", "user", "assistant"}

    for message in raw_messages:
        if isinstance(message, str):
            sanitized_messages.append({
                "role": "user",
                "content": message,
            })
            continue

        if not isinstance(message, dict):
            continue

        role = message.get("role", "user")
        content = content_to_text(message.get("content", ""))

        if not isinstance(role, str) or role not in allowed_roles:
            raise HTTPException(
                status_code=400,
                detail="El rol de uno de los mensajes no es válido",
            )

        sanitized_messages.append({
            "role": role,
            "content": content,
        })

    return sanitized_messages


@router.post("/responses", response_model=OpenResponse)
async def open_responses_endpoint(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    if (
        not API_SECRET_KEY
        or credentials is None
        or credentials.credentials != API_SECRET_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de API inválida o no proporcionada",
        )

    try:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="El cuerpo de la petición debe ser JSON válido",
            )

        if not isinstance(body, dict):
            raise HTTPException(
                status_code=400,
                detail="El cuerpo debe ser un objeto JSON",
            )

        raw_messages = []

        if isinstance(body.get("messages"), list):
            raw_messages = body["messages"]

        elif "input" in body:
            value = body["input"]

            if isinstance(value, str):
                raw_messages = [
                    {"role": "user", "content": value}
                ]
            elif isinstance(value, list):
                raw_messages = value
            else:
                raise HTTPException(
                    status_code=400,
                    detail="'input' debe ser texto o una lista de mensajes",
                )

        elif "prompt" in body:
            value = body["prompt"]

            if not isinstance(value, str):
                raise HTTPException(
                    status_code=400,
                    detail="'prompt' debe ser una cadena de texto",
                )

            raw_messages = [
                {"role": "user", "content": value}
            ]

        else:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar 'messages', 'input' o 'prompt'",
            )

        # Normalizar la estructura de los mensajes
        messages = normalize_messages(raw_messages)

        if not messages:
            raise HTTPException(
                status_code=400,
                detail="No se recibieron mensajes válidos",
            )

        for message in messages:
            if message["role"] != "user":
                continue

            validation = SecurityGuardrails.validate_input(
                message["content"]
            )

            if not validation["is_safe"]:
                raise HTTPException(
                    status_code=400,
                    detail=validation["reason"],
                )

        logger.info(
            "Ejecutando agente con %s mensajes",
            len(messages),
        )

        # Ejecutar el agente
        agent_result = run_agent_workflow(messages)

        response_text = ""
        citations = []

        if isinstance(agent_result, tuple):
            if len(agent_result) >= 1:
                response_text = content_to_text(agent_result[0])

            if len(agent_result) >= 2:
                citations = agent_result[1]

        elif isinstance(agent_result, dict):
            if agent_result.get("messages"):
                last_message = agent_result["messages"][-1]

                if hasattr(last_message, "content"):
                    response_text = content_to_text(
                        last_message.content
                    )

                elif isinstance(last_message, dict):
                    response_text = content_to_text(
                        last_message.get("content", "")
                    )

                else:
                    response_text = str(last_message)

            elif "response" in agent_result:
                response_text = content_to_text(
                    agent_result["response"]
                )

            elif "output" in agent_result:
                response_text = content_to_text(
                    agent_result["output"]
                )

            else:
                response_text = str(agent_result)

        else:
            response_text = content_to_text(agent_result)

        response_text = SecurityGuardrails.sanitize_output(
            response_text
        )

        # Normalizar las citas
        if not isinstance(citations, list):
            citations = []

        citations = [
            SecurityGuardrails.sanitize_output(str(citation))
            for citation in citations
        ]

        return OpenResponse(
            status="success",
            response=response_text,
            citations=citations,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error crítico durante la ejecución del agente")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno durante la ejecución del agente",
        )
