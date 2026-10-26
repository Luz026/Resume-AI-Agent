# Portafolio de Proyectos

## 1. Proyectos Profesionales (Experiencia Laboral)

### Modernización y Desarrollo de Microservicios (BBVA / BMV / Sector Financiero)
* **Descripción:** Rediseño, refactorización y modernización de arquitecturas legadas (monolitos y sistemas basados en Cobol/CICS/JCL) hacia plataformas distribuidas de alto rendimiento en Java.
* **Componentes clave:**
  * Implementación y soporte para el sistema de pagos de alto valor **SPEI 2.0** en BBVA.
  * Desarrollo de microservicios usando **Java (8, 11)**, **Spring Boot**, **Spring Cloud**, **Spring Data** y **Spring Integration**.
  * Construcción de APIs bajo enfoques **RESTful** y **GraphQL**, aplicando principios de **Arquitectura Hexagonal**, **MVC** y **CQRS**.
  * Construcción de interfaces web interactivas utilizando **React** y **Redux**.
  * Diseño y optimización de bases de datos relacionales (**Oracle**, **MySQL**, **DB2**), incluyendo vistas materializadas y tuneo de consultas.
  * Despliegue en contenedores **Docker**, pipeline de integración continua (CI/CD) con Maven/Gradle y metodología ágil **SCRUM / SAFe**.

---

## 2. Proyectos de Inteligencia Artificial

### Arquitectura de Agentes Inteligentes, Memoria y Optimización Logística 
* **Descripción:** Diseño e implementación de un sistema basado en agentes para la gestión de contextos, políticas de memoria episódica/semántica y verificación de acciones sobre un conjunto de datos masivo de cadena de suministro (ventas, inventarios, precios de competencia y preventistas).
* **Componentes clave:**
  * **Gestión de Contexto y Presupuesto de Tokens:** Estructuración de paquetes de contexto eficientes limitados a ventanas temporales críticas y umbrales de costos mínimos para optimizar inferencias.
  * **Políticas de Memoria y Prevención:** Implementación de memoria episódica (historial de 90 días), semántica (umbrales y reglas de negocio) y procedimental (bitácoras por versión) con detección de casos duplicados y manejo seguro de conflictos de fecha.
  * **Sistema de Verificación y Control Adversarial:** Catálogo de herramientas y validadores estrictos para bloquear acciones prohibidas o fuera de contrato, integrando protocolos de escalamiento y simulación de flujos de trabajo (*silla vacía*).

### Evaluación de Modelos Multilingües de Voz a Texto (ASR Equity Benchmark - FLEURS)
* **Descripción:** Desarrollo e implementación de un pipeline de evaluación automatizada (ASR) a gran escala utilizando conjuntos de datos multilingües heterogéneos (FLEURS) sobre múltiples idiomas y sistemas de frontera (OpenAI, Google Gemini, Meta SeamlessM4T).
* **Componentes clave:**
  * **Procesamiento y Almacenamiento Persistente:** Carga modular, segmentación y almacenamiento estructurado de clips de audio y transcripciones de referencia con soporte de caché en Google Drive y manejo de metadatos/manifiestos.
  * **Adaptadores e Interfaz de APIs:** Integración de APIs de transcripción avanzada y modelos multimodales nativos con gestión de claves secretas y control de errores por cuotas o latencias.
  * **Métricas de Rendimiento y Equidad Lingüística:** Cálculo formal de la tasa de error por palabras (**WER**) y caracteres (**CER**), auditoría de fallos y análisis de brechas de rendimiento a nivel macro y por idioma.

### Pronósticos y Análisis de Series de Tiempo (M.S. Applied AI - Tec de Monterrey)
* **Descripción:** Evaluación comparativa y modelado predictivo para problemas secuenciales y temporales.
* **Componentes clave:**
  * **Modelado Predictivo:** Implementación, validación y ajuste de modelos para series de tiempo utilizando técnicas clásicas, estocásticas y de aprendizaje profundo (**Modelo Ingenuo**, **ARIMA**, **Prophet**, **LSTM**).
  * **Análisis Exploratorio:** Evaluación de tendencias, estacionalidad y componentes de autocorrelación para la toma de decisiones informada.

### Clasificación y Análisis de Sentimientos con Embeddings y Machine Learning (M.S. Applied AI - Tec de Monterrey)
* **Descripción:** Pipeline end-to-end de Procesamiento de Lenguaje Natural (NLP) para la extracción de características y clasificación automatizada sobre corpus de reseñas en texto masivo (Yelp, Amazon, IMDb).
* **Técnicas y Herramientas:**
  * **Preprocesamiento:** Limpieza de texto y extracción de patrones mediante expresiones regulares (`re`) y estructuras de datos optimizadas en **Python**.
  * **Vectorización y Embeddings:** Uso de modelos Transformer preentrenados (`bge-base-en-v1.5`, `bge-large-en-v1.5`, `e5-base-v2`) mediante la librería `sentence-transformers` de **Hugging Face**.
  * **Clasificación y Analítica:** Entrenamiento, afinación y evaluación comparativa de algoritmos de **Regresión Logística** y **Random Forest**.
  * **Evaluación:** Evaluación formal del rendimiento utilizando curvas ROC/AUC, matrices de confusión, Accuracy, Precision, Recall y F1-Score en conjuntos de prueba independientes.

### Desarrollo de Aplicación Educativa Interactiva (UPIICSA - IPN)
* **Descripción:** Proyecto de titulación para el desarrollo de una herramienta interactiva de apoyo al aprendizaje basada en metodologías ágiles de desarrollo de software.
* **Tecnologías:** Integración de hardware y software mediante **Arduino** y **Arduino Studio**.
* **Resultados:** Definición de requerimientos funcionales/no funcionales, creación de módulos interactivos de enseñanza en sistemas embebidos y diseño de esquemas de evaluación formativa.

---

## 3. Resumen Tecnológico

| Área | Tecnologías y Herramientas |
| :--- | :--- |
| **IA & Machine Learning** | Python, Hugging Face (`sentence-transformers`), Scikit-learn, NLP, Word Embeddings, Evaluaciones ASR, Arquitectura de Agentes, Series de Tiempo (ARIMA, Prophet, LSTM) |
| **Desarrollo Software** | Java (8/11), Spring Boot, Spring Cloud, React, Redux, REST API, GraphQL, Pandas, NumPy |
| **Bases de Datos** | Oracle, MySQL, DB2, Parquet, Optimización SQL |
| **Cloud & DevOps** | GCP, Docker, Git, Maven, Gradle, CI/CD, Google Drive / Colab Workflows |
| **Metodologías** | SCRUM, SAFe, Arquitectura Hexagonal, Clean Code, Control Adversarial y Verificación de Estado |