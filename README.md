# Agente de Consulta Profesional - Sandra Cervantes

## 1. Descripción del Proyecto
Este proyecto consiste en un agente conversacional inteligente diseñado para actuar como el representante virtual del perfil profesional de Sandra Cervantes. El sistema expone una arquitectura basada en un modelo de lenguaje con un diseño riguroso de ingeniería de contexto, gobernanza de datos y principios de IA confiable. 

El agente responde preguntas sobre la trayectoria laboral, habilidades técnicas, proyectos académicos y experiencia en ingeniería de software e inteligencia artificial, asegurando que la información sea verificable y delimitada estrictamente al contexto proporcionado.

---

## 2. Arquitectura del Sistema
El proyecto opera mediante un microservicio expuesto a través de una API REST compatible con el estándar Open Responses / OpenAPI.

### Componentes Clave
* **Capa de Entrada (API Endpoint):** Recibe solicitudes HTTP POST con el payload de la consulta.
* **Módulo de Autenticación:** Validación opcional mediante encabezado HTTP x-api-key o Bearer Token.
* **Orquestación y RAG (Retrieval-Augmented Generation):** Carga y formateo dinámico del conocimiento autorizado ({semantic_knowledge}).
* **Gobernanza y Guardrails (Boundary Controls):** Reglas estrictas en el Prompt del Sistema que previenen alucinaciones, respuestas fuera de dominio, fuga de instrucciones (Jailbreak) y tutoriales no autorizados.
* **Modelo de Lenguaje Integrado:** Procesamiento de inferencia a través de APIs de modelos de frontera (LLMs).

---

## 3. Estructura del Repositorio

```text
.
├── README.md
├── requirements.txt
├── main.py
├── config.py
└── data/
    ├── cv_oficial.pdf
    ├── experiencia.md
    └── proyectos_sandra.md
```

---

## 4. Requisitos Previos e Instalación

### Requisitos Técnicos
* Python 3.10 o superior
* Git
* Cuenta activa en el proveedor del modelo de lenguaje (ej. OpenAI, Google Gemini, Anthropic)

### Pasos de Instalación
1. Clonar el repositorio:
   git clone https://github.com/tu-usuario/agente-sandra-cervantes.git
   cd agente-sandra-cervantes

2. Crear y activar un entorno virtual:
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate

3. Instalar dependencias:
   pip install -r requirements.txt

4. Configurar variables de entorno:
   Crear un archivo .env en la raíz del proyecto con la siguiente estructura:
   PORT=8000
   API_KEY_SECRET=tu_clave_secreta_aqui
   LLM_API_KEY=tu_api_key_del_proveedor

---

## 5. Ejecución en Entorno Local

Para iniciar el servidor localmente, ejecute:
python main.py

El servidor quedará disponible en http://localhost:8000.

---

## 6. Configuración de Prompt y Reglas de Gobernanza

El agente funciona bajo un prompt de sistema cerrado diseñado para mitigar desviaciones.

### Extracto de Reglas de Inferencia
1. Exclusividad de Dominio: El agente solo responde consultas vinculadas al perfil profesional de Sandra Cervantes.
2. Manejo de Vacíos de Información: Si la consulta del usuario no se encuentra en la base de conocimientos, el agente responde de forma unívoca:
   "No dispongo de registro de esa información en el perfil profesional autorizado de Sandra Cervantes. Mi función se limita estrictamente a responder sobre su trayectoria y experiencia."
3. Prohibición de Tutoriales o Asistencia General: Queda estrictamente prohibido responder dudas de programación general o guías sobre herramientas externas.
4. Trazabilidad: Las afirmaciones factuales incluyen citación a la fuente correspondiente.

---

## 7. Despliegue en Producción y Endpoint Público

Este proyecto está preparado para ser desplegado en plataformas como Render, Railway o Vercel.

### Pasos para Despliegue en Render
1. Conectar el repositorio de GitHub a la plataforma Render.
2. Crear un nuevo Web Service seleccionado el repositorio.
3. Configurar el comando de inicio: uvicorn main:app --host 0.0.0.0 --port $PORT
4. Registrar las Variables de Entorno en el panel de administración.
5. Copiar la URL pública generada (ej. https://agente-sandra.onrender.com/api/v1/chat).

---

## 8. Especificación de la API (Open Responses)

### Endpoint de Consulta

* URL: /api/v1/chat
* Método: POST
* Headers:
  Content-Type: application/json
  x-api-key: <TU_API_KEY>

### Ejemplo de Solicitud (Request)

```json
{
  "message": "¿Cuál es la experiencia de Sandra en arquitectura de microservicios e Inteligencia Artificial?"
}
```

### Ejemplo de Respuesta Exitosa (Response 200 OK)

```json
{
  "status": "success",
  "response": "Sandra Cervantes cuenta con experiencia en el rediseño y modernización de arquitecturas hacia plataformas distribuidas en Java, Spring Boot y Spring Cloud, así como desarrollo de soluciones RAG y evaluación de modelos multilingües de voz a texto [experiencia.md]."
}
```

### Ejemplo de Respuesta Fuera de Alcance (Response 200 OK)

```json
{
  "status": "success",
  "response": "No dispongo de registro de esa información en el perfil profesional autorizado de Sandra Cervantes. Mi función se limita strictly a responder sobre su trayectoria y experiencia."
}
```

---

## 9. Licencia y Uso
Este repositorio forma parte de la entrega del reto de desarrollo de agentes conversacionales y su uso está limitado a fines de evaluación profesional.
