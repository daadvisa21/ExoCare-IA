# 🦎 ExoCare IA: Asistente Veterinario Exótico

Es una plataforma integral diseñada para el bienestar de mascotas no convencionales (reptiles, anfibios y pequeños mamíferos). El sistema combina la potencia de los modelos de lenguaje de última generación con una base de conocimientos técnica y especializada.

## 1. Clonación del Repositorio

**Paso 1: Clonar el proyecto**

Para comenzar con la instalación local o el despliegue, primero debe obtener una copia del código fuente y organizar la estructura del proyecto.

```bash
git clone [https://github.com/daadvisa21/ExoCare-IA.git]
cd ExoCare-IA
```
**Paso 2: Estructura del Proyecto**

El proyecto está organizado de la siguiente manera para separar la lógica de microservicios:

| Recurso | Descripción |
| :--- | :--- |
| **`/frontend`** | Aplicación Next.js 14 (Interfaz de Usuario) |
| **`/backend`** | API Python/FastAPI (Agente IA y LangGraph) |
| **`/extras`** | Fuentes de conocimiento (PDFs) y Notebooks (.ipynb) |
| **`README.md`** | Documentación general del proyecto |

## 🗄️ 2. Configuración de Infraestructura de Datos

Para que el Agente IA no solo sea un chat genérico, sino un experto con memoria, se configuraron dos servicios independientes. Los scripts de inicialización están en la carpeta `/extras`.

**Paso 1: Conocimiento (Elasticsearch + RAG)**

Archivo: `/Carga_Datos_RAG.ipynb`

Se implementó un motor de búsqueda semántica para que la IA consulte fuentes técnicas antes de responder.

**Fuentes Indexadas**: 20 guías web especializadas (WPVet) y los manuales médicos `/exotic companion.pdf` y `/handbook.pdf`

**Paso 2: Memoria (PostgreSQL)**

Archivo: `/Despliegue_Checkpointer.ipynb`

## ☁️ 3. Configuración de Google Cloud Platform (GCP)

```bash
gcloud config set project [TU_PROJECT_ID]
gcloud config set run/region us-west4
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```
## ⚙️ 4. Despliegue del Backend (API)

**Paso 1: Construir y subir la imagen**

```bash
cd backend
gcloud builds submit --tag gcr.io/[TU_PROJECT_ID]/backend-exocare
```
**Paso 2: Lanzar el servicio en Cloud Run**

```bash
gcloud run deploy backend-exocare \
  --image gcr.io/[TU_PROJECT_ID]/backend-exocare \
  --update-env-vars OPENAI_API_KEY=[TU_KEY],DATABASE_URL=[TU_URL_POSTGRES],ELASTIC_URL=[TU_IP_ELASTIC] \
  --allow-unauthenticated
```
Al finalizar, guarde la Service URL generada (ej: `/https://backend-xxx.run.app`).

## 💻 5. Despliegue del Frontend (Interfaz)

**Paso 1: Construir la imagen**

```bash
cd ../frontend
gcloud builds submit --tag gcr.io/[TU_PROJECT_ID]/frontend-exocare
```
**Paso 2: Desplegar con vinculación al Backend**

```bash
gcloud run deploy frontend-exocare \
  --image gcr.io/[TU_PROJECT_ID]/frontend-exocare \
  --update-env-vars NEXT_PUBLIC_API_URL=[URL_DEL_BACKEND_GENERADA_ANTERIORMENTE] \
  --port 8080 \
  --allow-unauthenticated
```

## 🔐 6. Configuración de Seguridad (OAuth)
1. Ve a Google Cloud Console > APIs & Services > Credentials.
2. Edita tu OAuth 2.0 Client ID.
3. En Authorized JavaScript Origins, agrega la URL de tu Frontend de Cloud Run.
4. En Authorized Redirect URIs, agrega la URL de tu Frontend seguida de: /api/auth/callback/google

## 🧪 ¿Cómo probar la aplicación?
1. Acceso: Inicie el link del Frontend generado por Cloud Run.
2. Autenticación: Inicie sesión con su cuenta de Google.
3. Prueba de RAG: Pregunte: ¿Cuáles son los cuidados básicos de una Pitón Bola?. La IA debe citar datos técnicos de los manuales.
4. Prueba de Memoria: Diga: "Mi mascota se llama Koke". Luego pregunte: ¿Cómo se llama mi mascota?. La IA debe recordar el nombre gracias a la persistencia en Postgres.
