# -*- coding: utf-8 -*-
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Optional
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent
from psycopg_pool import ConnectionPool

# --- CONFIGURACIÓN DE TRAZABILIDAD Y API ---
os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "lsv2_"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "gcpcragent"
os.environ["OPENAI_API_KEY"] ="sk-proj-T2dK8Y5NlBgsw53Z19BJ"

app = Flask(__name__)
CORS(app)

# --- HERRAMIENTAS ---

# Conexión a tu Elasticsearch para el RAG
db_query = ElasticsearchStore(
    es_url="http://34.172.224.63:9200",
    es_user="elastic",
    es_password="vaCrgB0nZZcW2IrqMTGO",
    index_name="indx_app",
    embedding=OpenAIEmbeddings(model="text-embedding-3-large")
)

@tool
def consultar_manuales_expertos(query: str) -> str:
    """Consulta manuales técnicos y guías web sobre medicina de mascotas exóticas."""
    docs = db_query.similarity_search(query, k=4)
    return "\n\n".join([d.page_content for d in docs])

@tool
def guia_cuidados_mascota(especie: str) -> str:
    """Genera una guía de cuidados básicos (Alimentación, Temperatura, Hábitat)."""
    llm_tool = ChatOpenAI(model="gpt-4o", temperature=0)
    return llm_tool.predict(f"Genera una guía amigable con emojis para cuidar un {especie}.")

@tool
def checklist_compras_iniciales(especie: str) -> str:
    """Genera lista de compras necesarias (terrarios, luces, sustrato)."""
    llm_tool = ChatOpenAI(model="gpt-4o", temperature=0)
    return llm_tool.predict(f"Haz una checklist de compras para alguien que tendrá un {especie} por primera vez.")

@tool
def diagnostico_problemas_mascota(especie: str, sintomas: str) -> str:
    """Orienta sobre posibles causas de salud y acciones de primeros auxilios."""
    llm_tool = ChatOpenAI(model="gpt-4o", temperature=0)
    return llm_tool.predict(f"Para un {especie} con {sintomas}, indica posibles causas y pasos a seguir.")

@tool
def comparador_especies_exoticas(especie1: str, especie2: str) -> str:
    """Compara dos especies para elegir cuál es más adecuada como mascota."""
    llm_tool = ChatOpenAI(model="gpt-4o", temperature=0)
    return llm_tool.predict(f"Compara {especie1} vs {especie2} en dificultad de cuidado y costo.")

# --- RUTA PRINCIPAL DEL AGENTE ---

@app.route('/agent', methods=['GET'])
def main():
    # Capturamos variables enviadas desde el frontend
    id_usuario = request.args.get('idagente')
    msg = request.args.get('msg')

    if not id_usuario or not msg:
        return jsonify({"error": "Faltan parámetros idagente o msg"}), 400

    # Datos de configuración de tu Postgres
    DB_URI = "postgresql://postgres:Daniela21#@34.134.238.105:5432/postgres?sslmode=disable"

    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    # Inicializamos la memoria con el pool de conexiones
    with ConnectionPool(conninfo=DB_URI, max_size=20, kwargs=connection_kwargs) as pool:
        checkpointer = PostgresSaver(pool)
        # checkpointer.setup() # Descomentar si es la primera vez que se usa la tabla

        # Inicializamos el modelo (usando gpt-4o para mejor razonamiento)
        model = ChatOpenAI(model="gpt-4o", temperature=0)

        # Agrupamos todas tus herramientas
        toolkit = [
            consultar_manuales_expertos,
            guia_cuidados_mascota,
            checklist_compras_iniciales,
            diagnostico_problemas_mascota,
            comparador_especies_exoticas
        ]

        # Definimos tu personalidad de Veterinario
        system_prompt = """Eres el 'Veterinario Exótico IA', un asistente médico de élite especializado en especies no convencionales (reptiles, aves, pequeños mamíferos y anfibios).

--- TU MISIÓN ---
Tu objetivo es proporcionar asesoría técnica, educativa y de salud animal utilizando tus herramientas especializadas. Debes ser el puente entre los manuales técnicos y el dueño de la mascota.

--- PROTOCOLO DE RAZONAMIENTO (PASO A PASO) ---
1. ANALIZAR: ¿La pregunta es técnica (patologías, anatomía, datos de libros)?
   -> Usa 'consultar_manuales_expertos'.
2. ESTRUCTURAR: ¿El usuario quiere saber cómo mantener a su mascota (dieta, terrario, luz)?
   -> Usa 'guia_cuidados_mascota'.
3. EMERGENCIA: ¿El usuario reporta síntomas o decaimiento?
   -> Usa 'diagnostico_problemas_mascota' e incluye SIEMPRE la advertencia: "Esta es una orientación basada en IA y no sustituye la consulta presencial".
4. COMPARAR: ¿Duda entre dos especies?
   -> Usa 'comparador_especies_exoticas'.

--- REGLAS DE ORO DE RESPUESTA ---
- TONO: Profesional, empático y clínico. Usa emojis relacionados (🐢, 🦎, 🦜, 🐹) para separar secciones.
- PRIORIDAD: Si la información está en los manuales (RAG), esa información es la VERDAD ABSOLUTA sobre tu conocimiento general.
- SEGURIDAD: Si detectas señales de muerte inminente (no respira, sangrado profuso, convulsiones), tu primera frase debe ser: "🚨 ESTA ES UNA EMERGENCIA. Acuda al veterinario de exóticos más cercano de inmediato".
- CONVERSACIÓN: Saluda al usuario por su nombre si el historial (thread_id) te lo permite. Sé breve pero completo.

--- RESTRICCIONES ---
- No inventes dosis de medicamentos químicos (solo sugiere suplementos naturales si los manuales lo indican).
- No recomiendes especies ilegales o protegidas por CITES como mascotas.
"""

        # Inicializamos el agente con la estructura del profe
        agent_executor = create_react_agent(
            model,
            toolkit,
            checkpointer=checkpointer,
            prompt=system_prompt
        )

        # Ejecutamos el agente con el thread_id para la memoria
        config = {"configurable": {"thread_id": id_usuario}}
        response = agent_executor.invoke({"messages": [HumanMessage(content=msg)]}, config=config)

        return response['messages'][-1].content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
