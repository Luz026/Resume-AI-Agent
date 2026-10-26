import streamlit as st
import requests

# Configuración de la página
st.set_page_config(
    page_title="Agente de CV - Reto IA Banorte",
    page_icon="🤖",
    layout="centered"
)

# Estilo visual ejecutivo
st.title("🤖 Asistente Virtual Profesional (CV Agent)")
st.markdown("---")
st.markdown(
    "¡Hola! Soy el agente inteligente de representación profesional. "
    "Pregúntame sobre mi trayectoria, experiencia técnica, proyectos clave o solicita mis datos de contacto."
)

# Endpoint del backend FastAPI local
API_URL = "http://127.0.0.1:8000/api/v1/chat"

# Inicializar historial de chat en la sesión de Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Renderizar el historial de conversación anterior
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Mostrar citas si existieron en turnos anteriores
        if "citations" in message and message["citations"]:
            st.caption(f"📚 Fuentes consultadas: {', '.join(message['citations'])}")

# Capturar entrada del usuario
if prompt := st.chat_input("Escribe tu pregunta sobre mi perfil profesional..."):
    # Añadir mensaje del usuario al estado
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta del asistente mediante el backend
    with st.chat_message("assistant"):
        with st.spinner("Analizando perfil y contexto..."):
            try:
                # Construir el payload con el historial completo para mantener el contexto
                payload = {
                    "messages": [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                }

                response = requests.post(API_URL, json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("response", "Sin respuesta del agente.")
                    citations = data.get("citations", [])

                    # Mostrar la respuesta en pantalla
                    st.markdown(answer)
                    
                    if citations:
                        st.caption(f"📚 Fuentes consultadas: {', '.join(citations)}")

                    # Guardar respuesta en el historial de sesión
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "citations": citations
                    })
                else:
                    error_msg = f"Error en el servidor: Código {response.status_code}"
                    st.error(error_msg)
            except requests.exceptions.ConnectionError:
                st.error("⚠️ No se pudo conectar con el backend de FastAPI. Asegúrate de que esté ejecutándose en el puerto 8000.")
            except Exception as e:
                st.error(f"⚠️ Ocurrió un error inesperado: {str(e)}")