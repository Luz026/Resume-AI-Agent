
import re
import unicodedata
from typing import Any, Dict


class SecurityGuardrails:
    MAX_INPUT_LENGTH = 2000

    # Patrones de Prompt Injection / Jailbreaks
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignora\s+(todas\s+las\s+)?instrucciones",
        r"system\s*prompt",
        r"act\s+as\s+a?\s*\w*",
        r"act[úu]a\s+como",
        r"reveal\s+(your\s+)?rules",
        r"revela\s+(tus\s+)?reglas",
        r"olvida\s+todo",
        r"forget\s+everything",
        r"dan\s+mode",
        r"developer\s+mode",
        r"modo\s+desarrollador",
        r"override\s+system",
        r"bypass\s+restrictions",
        r"\[\s*system\s*\]",
        r"\(\s*system\s*\)",
        r"<\s*system\s*>",
        r"new\s+role\s*:",
    ]

    CODE_INJECTION_PATTERNS = [
        r"\bdrop\s+table\b",
        r"\bunion\s+select\b",
        r"\bexec\s*\(",
        r"<\s*script\b[^>]*>",
        r"javascript\s*:",
        r"system\s*\(",
        r"process\s*\.\s*env\b",
        r"os\s*\.\s*system\s*\(",
    ]

    # Patrones para detectar datos sensibles en respuestas.
    SENSITIVE_PATTERNS = [
        (
            re.compile(r"\bsk-[a-zA-Z0-9]{32,}\b"),
            "[REDACTED_API_KEY]",
        ),
        (
            re.compile(
                r"\bbearer\s+[a-zA-Z0-9._~+/\-=]+",
                re.IGNORECASE,
            ),
            "[REDACTED_TOKEN]",
        ),
        (
            re.compile(
                r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
            ),
            "[REDACTED_EMAIL]",
        ),
    ]

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        """
        Normaliza una cadena Unicode para facilitar la detección
        de patrones sospechosos.

        Lanza TypeError si recibe un tipo distinto de str.
        """
        if not isinstance(text, str):
            raise TypeError(
                "SecurityGuardrails._normalize_text esperaba str; "
                f"recibió {type(text).__name__}"
            )

        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ASCII", "ignore").decode("ASCII")
        text = text.lower()
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @classmethod
    def _coerce_input(cls, user_input: Any) -> str:
        """
        Convierte entradas de texto habituales a una cadena.

        Acepta strings y listas de mensajes con contenido textual.
        No convierte diccionarios arbitrarios a texto.
        """
        if isinstance(user_input, str):
            return user_input

        if isinstance(user_input, list):
            parts = []

            for item in user_input:
                if isinstance(item, str):
                    parts.append(item)

                elif isinstance(item, dict):
                    content = item.get("content", "")

                    if isinstance(content, str):
                        parts.append(content)

                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, str):
                                parts.append(block)
                            elif (
                                isinstance(block, dict)
                                and isinstance(block.get("text"), str)
                            ):
                                parts.append(block["text"])

            return "\n".join(parts)

        raise TypeError(
            "La entrada debe ser str o una lista de mensajes; "
            f"se recibió {type(user_input).__name__}"
        )

    @classmethod
    def detect_prompt_injection(cls, user_input: Any) -> bool:
        """
        Detecta patrones conocidos de Prompt Injection y Jailbreak.
        Las entradas vacías, inválidas o excesivamente largas
        se bloquean.
        """
        try:
            user_input = cls._coerce_input(user_input)
        except (TypeError, ValueError):
            return True

        if not user_input.strip():
            return True

        if len(user_input) > cls.MAX_INPUT_LENGTH:
            return True

        clean_text = cls._normalize_text(user_input)

        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, clean_text, flags=re.IGNORECASE):
                return True

        return False

    @classmethod
    def detect_malicious_payload(cls, user_input: Any) -> bool:
        """
        Detecta patrones potencialmente peligrosos relacionados
        con SQL, JavaScript y comandos del sistema.
        """
        try:
            user_input = cls._coerce_input(user_input)
        except (TypeError, ValueError):
            return True

        if not user_input.strip():
            return True

        if len(user_input) > cls.MAX_INPUT_LENGTH:
            return True

        clean_text = cls._normalize_text(user_input)

        for pattern in cls.CODE_INJECTION_PATTERNS:
            if re.search(pattern, clean_text, flags=re.IGNORECASE):
                return True

        return False

    @classmethod
    def sanitize_output(cls, output_text: Any) -> str:
        """
        Redacta posibles claves API, tokens Bearer y correos
        electrónicos de una respuesta.

        Convierte valores no textuales a una representación segura
        para evitar errores de tipo.
        """
        if not isinstance(output_text, str):
            if output_text is None:
                return ""

            output_text = str(output_text)

        sanitized = output_text

        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)

        return sanitized

    @classmethod
    def validate_input(cls, user_input: Any) -> Dict[str, Any]:
        """
        Valida una entrada antes de enviarla al agente.

        Admite texto o listas de mensajes compatibles con
        _coerce_input().
        """
        try:
            user_input = cls._coerce_input(user_input)
        except (TypeError, ValueError):
            return {
                "is_safe": False,
                "reason": "Formato de entrada no válido",
            }

        if not user_input.strip():
            return {
                "is_safe": False,
                "reason": "La consulta está vacía",
            }

        if len(user_input) > cls.MAX_INPUT_LENGTH:
            return {
                "is_safe": False,
                "reason": (
                    "La consulta excede la longitud máxima permitida"
                ),
            }

        if cls.detect_prompt_injection(user_input):
            return {
                "is_safe": False,
                "reason": (
                    "Entrada bloqueada por políticas de seguridad"
                ),
            }

        if cls.detect_malicious_payload(user_input):
            return {
                "is_safe": False,
                "reason": (
                    "Entrada bloqueada por contener un patrón "
                    "de código potencialmente peligroso"
                ),
            }

        return {
            "is_safe": True,
            "reason": "OK",
        }
