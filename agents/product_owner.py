"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'product_owner'
LABEL = 'Product Owner'
SPEC_FILE = 'product_owner_report.md'
EXTRACT_CODE = False

INSTRUCTIONS = ("Prioriza la historia, define el alcance (incluye y excluye) y reescribe cada "
                "criterio de aceptación como verificable y numerado (CA-1, CA-2...). "
                "Marca como PENDIENTE lo ambiguo; no inventes requisitos.\n"
                "Carpetas de salida en /output: specs\n"
                "Carpeta del informe en /output: specs")
agent = Agent(role='Product Owner',
              goal="Priorizar historias, definir el alcance y mantener criterios claros.",
              backstory="Eres el Product Owner del equipo: decides qué entra y qué no, "
                        "y dejas criterios claros para que nadie tenga que adivinar.",
              llm=llm, verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output='Un informe del Product Owner.', agent=agent)
