"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'ai_engineer_2'
LABEL = 'AI Engineer 2'
SPEC_FILE = 'ai_engineer_2_report.md'
EXTRACT_CODE = True

INSTRUCTIONS = (
    "Eres el AI Engineer 2 de Wallee (Crew y frontend). Implementas el frontend React en TypeScript "
    "(componentes, hooks, rutas y consumo de la API con estados de carga, vacío y error, y accesibilidad) "
    "y la lógica de agentes para excepciones de pago en NestJS: interpretar, recomendar, explicar y escalar. "
    "Parte del backend aprobado de AI Engineer 1 y no cambies sus reglas de idempotencia. "
    "El agente nunca ejecuta acciones críticas sin un humano, no ejecuta reversos monetarios reales y solo clasifica y registra disputas. "
    "El cliente no reemplaza la validación ni la autorización del servidor. "
    "No uses datos reales ni secretos, y no inventes resultados de ejecución.\n"
    "Carpetas de salida en /output: frontend-react, backend-nestjs\n"
    "Carpeta del informe en /output: specs"
)
agent = Agent(role='AI Engineer 2', goal="Implementar el frontend React y el agente de excepciones de Wallee con humano en el circuito.",
              backstory="Eres el ingeniero de Crew y frontend del equipo de Wallee: dominas React y NestJS con TypeScript.", llm=llm,
              verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output='Código en bloques markdown. La primera línea de cada bloque es un comentario con la ruta completa: '
                '// frontend-react/src/<feature>/<Nombre>.tsx para React o // backend-nestjs/src/<feature>/<nombre>.<tipo>.ts para el agente. '
                'Incluye frontend-react/src/App.tsx con export default. '
                'El cliente consume la API con import.meta.env.VITE_API_URL (por defecto http://localhost:3000). '
                'Indica qué criterio de aceptación cubre cada archivo.', agent=agent)
