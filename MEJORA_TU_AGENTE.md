# Mejora tu agente

Los agentes de `agents/` parten con instrucciones mínimas. El flujo, las pausas humanas, los formatos de salida y los controles siguen funcionando. El ejercicio consiste en mejorar la responsabilidad, los entregables y las instrucciones del rol que te asignó el equipo.

1. Edita las instrucciones de tu archivo `agents/<rol>.py`. Puedes ampliar `INSTRUCTIONS` y, en CrewAI, el objetivo, contexto y salida de la tarea.
2. Especifica entregables verificables y evidencia para comprobarlos. Indica qué hacer con errores y observaciones. Prohíbe inventar pruebas o resultados.
3. Conserva firmas, claves de estado, imports, nombres de artefactos y formatos que consume el flujo.
4. Publica el cambio en tu rama y abre un PR para revisión del equipo.
5. Abre «Mi equipo» en el portal. Consulta el overview y ejecuta la evaluación de tu equipo sobre el código publicado en su rama principal.

El dashboard separa pruebas del flujo, cobertura de instrucciones por agente y total del equipo. El template básico puede aprobar el flujo y obtener una puntuación baja en instrucciones. Esa es la situación inicial esperada.

La rúbrica estática busca responsabilidades del rol, entregables, evidencia, honestidad y correcciones con feedback. Es orientativa: no mide las respuestas reales del modelo ni garantiza calidad del código generado. El instructor revisa los casos no reconocidos.


## De dónde partir según tu rol

Antes de escribir instrucciones, lean el mismo Issue, sus criterios de aceptación y el código del producto de los días anteriores. Identifiquen qué existe y qué falta. Amplíen `INSTRUCTIONS`, `goal`, `backstory` y `build_task` de su archivo; no cambien `KEY`, `SPEC_FILE`, `EXTRACT_CODE` ni la firma de `build_task`.

| Rol y archivo | Qué hace | Por dónde empezar | Qué debe pedir como entregable |
| --- | --- | --- | --- |
| Product Owner, `agents/product_owner.py` | Prioriza la historia, define el alcance (incluye y excluye) y reescribe cada criterio de aceptación como verificable y numerado (CA-1, CA-2...). Decide en las aprobaciones humanas. | Lee el Issue y el discovery de `challenge/docs/discovery`. Marca como PENDIENTE lo ambiguo; no inventa requisitos. | `product_owner_report.md`: alcance, criterios numerados y decisiones pendientes. |
| Architect, `agents/architect.py` | Define componentes, límites y contrato de API: entradas, respuestas y errores. Alinea la solución con los criterios de aceptación y fija qué es real y qué es mock. | Lee el Issue y las interfaces existentes; escribe el recorrido de una petición y un ejemplo de petición y respuesta. Señala supuestos pendientes. | `architect_report.md`: solución propuesta, módulos, contrato, criterios verificables y decisiones que necesitan Datos y los AI Engineers. |
| AI Engineer 1, `agents/ai_engineer_1.py` | Implementa el dominio y el backend NestJS: módulos, controladores, servicios, DTOs con class-validator, idempotencia y acceso a datos según los contratos aprobados. | Parte de la API del Architect y, cuando esté activo, del modelo de Datos. Traza un caso válido y un error desde la entrada hasta la persistencia. | `ai_engineer_1_report.md` y código TypeScript en bloques cuya primera línea es la ruta completa (`// backend-nestjs/src/<feature>/...`), incluido `app.module.ts`. Usa el contrato de Datos sin rediseñar tablas ni regenerar sus migraciones. En equipos de seis, también cubre la persistencia necesaria. |
| AI Engineer 2, `agents/ai_engineer_2.py` | Implementa el frontend React (carga, vacío, errores y accesibilidad) y el agente de excepciones: interpretar, recomendar, explicar y escalar con humano en el circuito. | Parte del contrato de API y del backend de AI Engineer 1. Lista campos, validaciones visibles, acciones, estados de la pantalla y qué acciones requieren un humano. | `ai_engineer_2_report.md` y código en bloques con la ruta completa (`// frontend-react/src/<feature>/...`), incluido `App.tsx`. El cliente no reemplaza la validación ni la autorización del servidor. |
| QA & Security, `agents/qa_security.py` | Convierte criterios de aceptación en casos verificables (positivos, negativos, límites e integración) y revisa autenticación, autorización, entradas, secretos, datos sensibles e inyección. | Relaciona cada criterio con una entrada, una acción y un resultado esperado; recorre las fronteras de confianza de la petición. Incluye integridad y migración si Datos las propone. | `qa_security_report.md`, pruebas y comandos reproducibles, y hallazgos con ubicación, impacto, corrección y comprobación. Distingue resultados ejecutados de propuestas marcadas NO EJECUTADO; la persona ejecuta las pruebas y conserva su salida. |
| Presenter, `agents/presenter.py` | Controla tiempos, evidencia y pitch. Contrasta las entregas aprobadas con los criterios y defiende qué se simuló y qué queda pendiente. | Parte de las entregas aprobadas y de la frontera real vs mock. Busca contratos incompatibles, pruebas pendientes y hallazgos sin resolver. | `presenter_report.md`: guion de demo, evidencia, pendientes y correcciones concretas. No reemplaza las aprobaciones humanas ni inventa ejecuciones. |

La secuencia es Product Owner → Architect → AI Engineer 1 → AI Engineer 2 → QA & Security → Presenter. Cada etapa usa el contexto aprobado anteriormente.

Como primer ejercicio, tomen un solo criterio del Issue. Escriban en las instrucciones qué recibe su agente, qué decisión le corresponde, qué formato debe devolver y cómo comprobarlo. Por ejemplo, si el criterio exige un título único, Datos define la restricción y la migración; AI Engineer 1 traduce el conflicto a un error de API en NestJS; AI Engineer 2 lo muestra en React; QA & Security verifica el duplicado y revisa entradas y permisos; el Presenter comprueba que la entrega completa lo demuestre.
