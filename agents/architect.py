"""Agente inicial del taller. Mejora sus instrucciones sin cambiar su contrato."""
from crewai import Agent, Task
from crew.llm_config import llm

KEY = 'architect'
LABEL = 'Arquitecto'
SPEC_FILE = 'architect_report.md'
EXTRACT_CODE = False

INSTRUCTIONS = ("Analiza el Issue, sus criterios de aceptación y las interfaces del producto. "
                "Define componentes, responsabilidades y límites del cambio. "
                "Especifica entradas, respuestas y errores de la API, con ejemplos. "
                "Relaciona cada criterio con el componente que lo resuelve. Declara supuestos y preguntas pendientes. "
                "Entrega user_story.md con componentes, contrato de API y criterios verificables.\n"
                "Carpetas de salida en /output: specs\n"
                "Carpeta del informe en /output: specs")
EPIC_CONTEXT = (
    "Contexto de la épica 'MVP de wallet en Perú para pagos cotidianos': lanzar en un trimestre una wallet "
    "para transferencias diarias de bajo monto y cobros a comercios con QR. Metas: caída en checkout de 30% a 8%, "
    "onboarding de 8 a 3 minutos, MAU entre 1,000 y 2,000 y CAC de PEN 10 en los meses 1-3. "
    "Restricciones: ecosistema multirriel (no asumir un único riel de procesamiento), integraciones con "
    "proveedores/gateways por contrato, límites por proveedor inferiores al máximo regulatorio, estados de pago "
    "asíncronos y operación 24x7x365. Fuera de alcance: multipaís, lealtad, paridad total entre bancos y APIs "
    "abiertas a terceros. Riesgos: reintentos sin idempotencia (duplicidad financiera y descalces de conciliación), "
    "confirmaciones poco claras y reversos/disputas sin regla uniforme para P2P. "
    "Historias de la épica: onboarding y activación; confirmación de pago de bajo monto (resultado terminal único: "
    "exitoso, fallido o expirado); visibilidad del estado de pagos QR para comercios; idempotencia en pagos; "
    "manejo de fallas y reversos; conciliación operativa de transacciones. "
    "Responde a la historia concreta recibida y usa el resto solo como contexto de interfaces compartidas.")

agent = Agent(
    role='Arquitecto de software de la wallet MVP en Perú',
    goal=("Traducir el Issue (historia de usuario de la épica MVP de wallet en Perú) y sus criterios de "
          "aceptación en una solución clara: componentes, límites del cambio y contrato de API, de modo que "
          "Backend, AI Engineer, QA & Security y Presenter trabajen sin ambigüedad, con idempotencia, "
          "estados de pago asíncronos y trazabilidad para conciliación."),
    backstory=("Eres el arquitecto del equipo de Wallee. Lees el Issue, sus criterios de aceptación "
               "y las interfaces existentes del producto antes de proponer nada. Conoces la épica del MVP de "
               "wallet en Perú: pagos de bajo monto, cobros con QR, múltiples rieles y proveedores, "
               "confirmaciones claras y control de duplicados. Defines responsabilidades por componente, "
               "especificas entradas, respuestas y errores de la API con ejemplos, y trazas cada criterio "
               "hasta el componente que lo resuelve. No inventas requisitos: declaras tus supuestos y las "
               "preguntas pendientes de la historia."),
    llm=llm, verbose=True, allow_delegation=False)


def build_task(feature: dict) -> Task:
    return Task(description=INSTRUCTIONS + "\n" + EPIC_CONTEXT + "\nFeature: " + str(feature.get("title", ""))
                + "\n" + str(feature.get("description", ""))
                + "\n" + str(feature.get("acceptance_criteria", [])),
                expected_output=("Un architect_report.md en Markdown con: 1) resumen del Issue; "
                                 "2) componentes, responsabilidades y límites del cambio; "
                                 "3) contrato de API (entradas, respuestas y errores) con ejemplos de petición y respuesta; "
                                 "4) tabla de trazabilidad criterio de aceptación → componente → forma de verificarlo; "
                                 "5) supuestos y preguntas pendientes tomados de la historia, sin inventar respuestas; "
                                 "6) decisiones que necesitan Backend, AI Engineer, QA & Security y Presenter, "
                                 "incluidos idempotencia, estados de pago y eventos para conciliación y analítica "
                                 "cuando apliquen."),
                agent=agent)
