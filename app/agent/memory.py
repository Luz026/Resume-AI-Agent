import os
from typing import List, Dict

class ContextManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

    def load_semantic_memory(self) -> str:
        """Carga y estructura el conocimiento autorizado desde los archivos Markdown locales."""
        knowledge_base = ""
        files = ["experiencia.md", "proyectos.md", "habilidades.md"]
        
        for file_name in files:
            file_path = os.path.join(self.data_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Inyectar metadatos de aislamiento por archivo
                    knowledge_base += f"\n--- FUENTE: [{file_name}] ---\n{content}\n"
            else:
                knowledge_base += f"\n--- FUENTE: [{file_name}] (No disponible) ---\n"
                
        return knowledge_base

    def compress_history(self, messages: List[Dict[str, str]], max_turns: int = 6) -> List[Dict[str, str]]:
        """Aplica ventana deslizante estricta para mitigar el consumo excesivo de tokens y la contaminación de contexto."""
        if len(messages) > max_turns:
            # Conservar el contexto reciente manteniendo el historial acotado
            return messages[-max_turns:]
        return messages