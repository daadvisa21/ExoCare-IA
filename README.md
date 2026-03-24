# 🦎 ExoCare IA: Asistente Veterinario Exótico

## 1. Clonación del Repositorio

**Paso 1: Clonar el proyecto**
Para comenzar con la instalación local o el despliegue, primero debe obtener una copia del código fuente y organizar la estructura del proyecto.

```bash
git clone [https://github.com/daadvisa21/ExoCare-IA.git](https://github.com/daadvisa21/ExoCare-IA.git)
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



