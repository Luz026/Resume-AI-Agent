
import os
import logging
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from app.agent.graph import run_agent_workflow
from app.core.security import SecurityGuardrails

router = APIRouter()
security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


class OutputText(BaseModel):
    type: str = "output_text"
    text: str
    annotations: list[dict[str, Any]] = Field(default_factory=list)
    logprobs: list[dict[str, Any]] = Field(default_factory=list)


class OutputMessage(BaseModel):
    id: str
    type: str = "message"
    status: str = "completed"
    role: str = "assistant"
    content: list[OutputText]


class OpenResponse(BaseModel):
    id: str
    object: str = "response"
    created_at: int
    status: str = "completed"
    output: list[OutputMessage]
    error: Any = None
    incomplete_details: Any = None
    citations: list[str] = Field(default_factory=list)


def content_to_text(content: Any) -> str:
    """Convierte el contenido del agente a texto."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                value = item.get("text")
                if isinstance(value, str):
                    parts.append(value)

        return " ".join(parts)

    if content is None:
        return ""

    return str(content)


def normalize_messages(raw_messages: list) -> list[dict[str, str]]:
    """Valida y normaliza los mensajes recibidos."""

    normalized = []
    allowed_roles = {"system", "user", "assistant"}

    for message in raw_messages:
        if isinstance(message, str):
            role = "user"
            content = message

        elif isinstance(message, dict):
            role = message.get("role", "user")

            if not isinstance(role, str) or role not in allowed_roles:
                raise HTTPException(
                    status_code=400,
                    detail="El rol de uno de los mensajes no es válido.",
                )

            # Admite mensajes de formato Open Responses y chat tradicional.
            content = content_to_text(
                message.get("content", message.get("text", ""))
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Cada mensaje debe ser texto o un objeto JSON válido.",
            )

        if not isinstance(content, str):
            raise HTTPException(
                status_code=400,
                detail="El contenido de cada mensaje debe ser texto.",
            )

        if content.strip():
            normalized.append({
                "role": role,
                "content": content,
            })

    return normalized


def extract_agent_result(agent_result: Any) -> tuple[str, list[str]]:
    """Extrae la respuesta final y las citas del agente."""

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

        elif isinstance(agent_result.get("output"), list):
            # Admite output con mensajes de Open Responses.
            for item in reversed(agent_result["output"]):
                if not isinstance(item, dict):
                    continue

                if item.get("type") != "message":
                    continue

                if item.get("role") != "assistant":
                    continue

                response_text = content_to_text(item.get("content", []))
                if response_text.strip():
                    break

        elif "output" in agent_result:
            response_text = content_to_text(agent_result["output"])

        elif isinstance(agent_result.get("messages"), list):
            for message in reversed(agent_result["messages"]):
                if isinstance(message, dict):
                    role = message.get("role", message.get("type"))
                    content = content_to_text(
                        message.get("content", "")
                    )
                else:
                    role = getattr(
                        message, "type",
                        getattr(message, "role", None)
                    )
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
    """Endpoint compatible con respuestas JSON de Open Responses."""

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
                status_code=400,
                detail="El cuerpo de la petición debe ser JSON válido.",
            )

        if not isinstance(body, dict):
            raise HTTPException(
                status_code=400,
                detail="El cuerpo debe ser un objeto JSON.",
            )

        if isinstance(body.get("messages"), list):
            raw_messages = body["messages"]

        elif "input" in body:
            value = body["input"]

            if isinstance(value, str):
                raw_messages = [{"role": "user", "content": value}]

            elif isinstance(value, list):
                raw_messages = value

            else:
                raise HTTPException(
                    status_code=400,
                    detail="'input' debe ser texto o una lista de mensajes.",
                )

        elif "prompt" in body:
            value = body["prompt"]

            if not isinstance(value, str):
                raise HTTPException(
                    status_code=400,
                    detail="'prompt' debe ser una cadena de texto.",
                )

            raw_messages = [{"role": "user", "content": value}]

        else:
            raise HTTPException(
                status_code=400,
                detail="Debes proporcionar 'input', 'messages' o 'prompt'.",
            )

        messages = normalize_messages(raw_messages)

        if not messages:
            raise HTTPException(
                status_code=400,
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
                    status_code=400,
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
                status_code=502,
                detail="El agente no produjo una respuesta final.",
            )

        response_text = SecurityGuardrails.sanitize_output(response_text)

        safe_citations = sorted({
            SecurityGuardrails.sanitize_output(str(citation))
            for citation in citations
            if citation is not None and str(citation).strip()
        })

        response_id = uuid.uuid4().hex

        return OpenResponse(
            id=f"resp_{response_id}",
            object="response",
            created_at=int(time.time()),
            status="completed",
            output=[
                OutputMessage(
                    id=f"msg_{response_id}",
                    type="message",
                    status="completed",
                    role="assistant",
                    content=[
                        OutputText(
                            type="output_text",
                            text=response_text,
                            annotations=[],
                            logprobs=[],
                        )
                    ],
                )
            ],
            error=None,
            incomplete_details=None,
            citations=safe_citations,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Error durante la ejecución del endpoint")
        raise HTTPException(
            status_code=500,
            detail="Error interno durante la ejecución del agente.",
        )
