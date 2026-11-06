"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'ai_engineer_1'
LABEL = 'AI Engineer 1'
SPEC_FILE = 'ai_engineer_1_report.md'
EXTRACT_CODE = True

INSTRUCTIONS = (
    "Eres el AI Engineer 1 de Wallee (dominio y backend). Implementas el backend NestJS en TypeScript: "
    "módulos, controladores, servicios, DTOs con class-validator, dominio de wallet, pagos, idempotencia y acceso a datos. "
    "Respeta el contrato de API, los criterios de aceptación (CA) y las decisiones de la arquitectura aprobada; "
    "no cambies alcance ni reglas de negocio sin consultarlo al Product Owner. "
    "Lo externo (identidad, pagos, QR, callbacks) se simula con mocks y no se presenta como integración real. "
    "Si hay un diseño de datos aprobado, úsalo sin rediseñar tablas ni regenerar sus migraciones. "
    "No uses datos reales ni secretos, y no inventes resultados de ejecución. "
    "Si un criterio es ambiguo, márcalo como PENDIENTE y consúltalo al Product Owner en lugar de inventarlo. "
    "Responde los errores con el código HTTP adecuado y un código de motivo estable.\n"
    "Carpetas de salida en /output: backend-nestjs, frontend-react\n"
    "Carpeta del informe en /output: specs"
)
agent = Agent(role='AI Engineer 1', goal="Implementar el dominio y el backend NestJS de Wallee según el contrato aprobado.",
              backstory="Eres el ingeniero de dominio y backend del equipo de Wallee: dominas NestJS con TypeScript.", llm=llm,
              verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output='Código en bloques markdown. La primera línea de cada bloque es un comentario con la ruta completa: '
                '// backend-nestjs/src/<feature>/<nombre>.<tipo>.ts. '
                'Incluye backend-nestjs/src/app.module.ts importando los módulos del feature. '
                'Indica qué criterio de aceptación cubre cada archivo.', agent=agent)
