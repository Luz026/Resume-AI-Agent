
import os
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.agent.graph import run_agent_workflow
from app.core.security import SecurityGuardrails

router = APIRouter()
security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)

API_SECRET_KEY = os.getenv("AGENT_API_KEY")


class OpenResponse(BaseModel):
    # Estado terminal compatible con clientes que esperan una respuesta final.
    status: str = "completed"
    response: str
    citations: list[str] = Field(default_factory=list)


def content_to_text(content: Any) -> str:
    """Convierte contenido de mensajes a texto de forma segura."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text_value = item.get("text")
                if isinstance(text_value, str):
                    parts.append(text_value)

        return " ".join(parts)

    if content is None:
        return ""

    return str(content)


def normalize_messages(raw_messages: list) -> list[dict[str, str]]:
    """Valida y normaliza la estructura de los mensajes."""

    normalized = []
    allowed_roles = {"system", "user", "assistant"}

    for message in raw_messages:
        if isinstance(message, str):
            content = message
            role = "user"

        elif isinstance(message, dict):
            role = message.get("role", "user")
            content = content_to_text(message.get("content", ""))

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cada mensaje debe ser texto o un objeto JSON válido.",
            )

        if not isinstance(role, str) or role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rol de uno de los mensajes no es válido.",
            )

        if not content.strip():
            continue

        normalized.append({
            "role": role,
            "content": content,
        })

    return normalized


def extract_agent_result(agent_result: Any) -> tuple[str, list[str]]:
    """Extrae el texto final y las citas del resultado del agente."""

    response_text = ""
    citations: list[str] = []

    if isinstance(agent_result, tuple):
        if len(agent_result) >= 1:
            response_text = content_to_text(agent_result[0])

        if len(agent_result) >= 2 and isinstance(agent_result[1], list):
            citations = [
                content_to_text(item)
                for item in agent_result[1]
                if item is not None
            ]

    elif isinstance(agent_result, dict):
        raw_citations = agent_result.get("citations", [])

        if isinstance(raw_citations, list):
            citations = [
                content_to_text(item)
                for item in raw_citations
                if item is not None
            ]

        if "response" in agent_result:
            response_text = content_to_text(agent_result["response"])

        elif "output" in agent_result:
            response_text = content_to_text(agent_result["output"])

        elif isinstance(agent_result.get("messages"), list):
            for message in reversed(agent_result["messages"]):
                if isinstance(message, dict):
                    role = message.get("role")
                    content = content_to_text(message.get("content", ""))
                else:
                    role = getattr(message, "type", None)
                    content = content_to_text(
                        getattr(message, "content", "")
                    )

                if role in {"assistant", "ai"} and content.strip():
                    response_text = content
                    break

    else:
        response_text = content_to_text(agent_result)

    return response_text.strip(), citations


@router.post("/responses", response_model=OpenResponse)
async def open_responses_endpoint(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """Endpoint para ejecutar el agente de CV."""

    api_secret_key = os.getenv("AGENT_API_KEY")

    if (
        not api_secret_key
        or credentials is None
        or credentials.scheme.lower() != "bearer"
        or credentials.credentials != api_secret_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de API inválida o no proporcionada.",
        )

    try:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cuerpo de la petición debe ser JSON válido.",
            )

        if not isinstance(body, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cuerpo debe ser un objeto JSON.",
            )

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
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="'input' debe ser texto o una lista de mensajes.",
                )

        elif "prompt" in body:
            value = body["prompt"]

            if not isinstance(value, str):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="'prompt' debe ser una cadena de texto.",
                )

            raw_messages = [
                {"role": "user", "content": value}
            ]

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debes proporcionar 'messages', 'input' o 'prompt'.",
            )

        messages = normalize_messages(raw_messages)

        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se recibieron mensajes válidos.",
            )

        for message in messages:
            if message["role"] != "user":
                continue

            validation = SecurityGuardrails.validate_input(
                message["content"]
            )

            if not validation.get("is_safe", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=validation.get(
                        "reason",
                        "El mensaje no superó la validación de seguridad.",
                    ),
                )

        logger.info(
            "Ejecutando agente con %s mensajes",
            len(messages),
        )

        agent_result = run_agent_workflow(messages)
        response_text, citations = extract_agent_result(agent_result)

        if not response_text:
            logger.error("El agente terminó sin producir texto.")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="El agente no produjo una respuesta final.",
            )

        response_text = SecurityGuardrails.sanitize_output(response_text)

        safe_citations = [
            SecurityGuardrails.sanitize_output(citation)
            for citation in citations
            if citation.strip()
        ]

        return OpenResponse(
            status="completed",
            response=response_text,
            citations=sorted(set(safe_citations)),
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error durante la ejecución del endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno durante la ejecución del agente.",
        )
