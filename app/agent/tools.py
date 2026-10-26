import json

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "get_contact_info",
            "description": "Proporciona canales oficiales de contacto profesional",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_resume_link",
            "description": "Devuelve el enlace seguro para descargar el CV oficial en PDF",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

def execute_tool(tool_name: str) -> str:
    if tool_name == "get_contact_info":
        return json.dumps({
            "email": "candidato.senior@ia-banorte.com",
            "linkedin": "linkedin.com/in/candidato-senior-ia"
        })
    elif tool_name == "download_resume_link":
        return json.dumps({
            "download_url": "https://api.candidato-ia.com/static/cv_oficial.pdf",
            "format": "PDF"
        })
    return json.dumps({"error": "Herramienta no autorizada o fuera de rango."})