import re
import unicodedata
from typing import Dict, Any

class SecurityGuardrails:
    MAX_INPUT_LENGTH = 2000

    # Patrones de Prompt Injection / Jailbreaks
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignora\s+(todas\s+las\s+)?instrucciones",
        r"system\s*prompt",
        r"act\s+as\s+a?",
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
        r"\[system\]",
        r"\(system\)",
        r"<system>",
        r"new\s+role:"
    ]
    #injection_patterns
    CODE_INJECTION_PATTERNS = [
        r"drop\s+table",
        r"union\s+select",
        r"exec\s*\(",
        r"<script.*?>",
        r"javascript:",
        r"system\(",
        r"process\.env",
        r"os\.system"
    ]

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        """Normaliza el texto para evitar evadir filtros con unicode o acentos."""
        # Convierte caracteres unicode a ASCII simplificado (ej: fùll -> full)
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        # Pasa a minúsculas y colapsa espacios/saltos de línea repetidos
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @classmethod
    def detect_prompt_injection(cls, user_input: str) -> bool:
        """Saber si la entrada contiene intentos de Prompt Injection o Jailbreaks."""
        if not user_input or len(user_input) > cls.MAX_INPUT_LENGTH:
            return True  # Bloquea entradas excesivamente largas o vacías

        clean_text = cls._normalize_text(user_input)

        # Buscar patrones de inyección
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, clean_text):
                return True
        return False

    @classmethod
    def detect_malicious_payload(cls, user_input: str) -> bool:
        """Saber si la entrada intenta inyectar comandos o scripts SQL/Shell."""
        clean_text = cls._normalize_text(user_input)
        for pattern in cls.CODE_INJECTION_PATTERNS:
            if re.search(pattern, clean_text):
                return True
        return False

    @classmethod
    def sanitize_output(cls, output_text: str) -> str:
        """Evita la fuga accidental de claves API o tokens en las respuestas del LLM."""
        sensitive_patterns = [
            (r'sk-[a-zA-Z0-9]{32,}', '[REDACTED_API_KEY]'),
            (r'bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*', '[REDACTED_TOKEN]'),
            (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED_EMAIL]')
        ]
        sanitized = output_text
        for pattern, replacement in sensitive_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized

    @classmethod
    def validate_input(cls, user_input: str) -> Dict[str, Any]:
        """Método integral de validación antes de enviar el prompt al LLM."""
        if len(user_input) > cls.MAX_INPUT_LENGTH:
            return {"is_safe": False, "reason": "La consulta excede longitud máxima permitida"}

        if cls.detect_prompt_injection(user_input):
            return {"is_safe": False, "reason": "Entrada bloqueada por políticas de seguridad"}

        if cls.detect_malicious_payload(user_input):
            return {"is_safe": False, "reason": "Entrada bloqueada por contener código no permitido"}

        return {"is_safe": True, "reason": "OK"}