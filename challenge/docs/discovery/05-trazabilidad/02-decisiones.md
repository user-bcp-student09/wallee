---
id: DISC-05-02
titulo: Decisiones y preguntas abiertas
estado: aprobado
responsable: Product Owner
actualizado: 2026-11-06 12:58
fuentes: [challenge/user-stories/*.sp.md (Preguntas abiertas y Supuestos), base de hechos del prompt]
depende_de: [DISC-01-05]
lo_consumen: [Arquitecto/a, AI Engineer A, AI Engineer B, QA & Security, Presenter/Timekeeper]
---

## Resumen
Todas las preguntas abiertas de las historias tienen un supuesto que el Product Owner aprobó (DEC-04 y DEC-05, 2026-11-06).

## Preguntas abiertas
| ID | Pregunta | HU | Supuesto aprobado | Impacto si cambia | Estado |
|---|---|---|---|---|---|
| PA-01 | ¿Qué frontera de eventos define la duración del onboarding? | W1 | Inicio `onboarding_started`; fin `onboarding_completed` con wallet ACTIVA (SUP-09) | Evento W1-AC4 | Resuelta (DEC-04) |
| PA-02 | ¿Qué regla de monto bajo se configura por proveedor/canal? | W2 | S/ 500 por transacción (SUP-01) | RN-01, tests de borde | Resuelta (DEC-05) |
| PA-03 | ¿Conjunto mínimo de estados del comercio y canal de consulta? | W3 | Cuatro estados del mock; misma app web (SUP-10) | Solo stretch | Resuelta (DEC-05) |
| PA-04 | ¿Ventana de retención de claves de idempotencia por canal? | W4 | 24 h para ambos canales (SUP-02) | RN-02, W4-AC2 | Resuelta (DEC-05) |
| PA-05 | ¿Categorías de disputa en MVP y cuáles se difieren? | W5 | Se clasifica y registra la ruta; resolución diferida (SUP-11) | W5-AC2, W5-AC3 | Resuelta (DEC-05) |
| PA-06 | Niveles de escalamiento y SLA de soporte | W5 | Sin SLA formal; escalamiento HITL (SUP-12) | W5-AC4 | Resuelta (DEC-05) |
| PA-07 | ¿Tasa máxima diaria de descalce aceptable? | W6 | Sin tasa; todo descalce se marca (SUP-13) | Solo stretch | Resuelta (DEC-05) |
| PA-08 | (nueva) ¿Hay validación de saldo antes de pagar? | W2 | No se ejecuta si saldo < monto (SUP-15) | RN-18 | Resuelta (DEC-05) |
| PA-09 | Confirmar el stack propuesto | Base | Node.js, React, CrewAI, SQLite (SUP-08) | Base | Resuelta (DEC-05) |
| PA-10 | Confirmar compromiso de HU, AC comprometidos y owners | Todas | W1, W2, W4, W5; 17 de 28 AC (ver mapa) | Alcance y plan | Resuelta (DEC-05) |

Las fuentes también dejan por definir las etiquetas finales de estados terminales (supuesto: exitoso, fallido, expirado) y las herramientas de conciliación (supuesto: fixtures y script local).

## Log de decisiones
| ID | Fecha y hora | Decisión | Quién | Alternativas | Impacto |
|---|---|---|---|---|---|
| DEC-01 | 2026-11-06 10:20 | Generar el discovery con todos los supuestos como PROPUESTO | Product Owner (agente) | Esperar confirmación humana de cada supuesto | Evita frenar la construcción; el humano confirma en el G1 |
| DEC-02 | 2026-11-06 10:20 | Comprometer AC1–AC4 de W1, AC1–AC4 y AC6 parcial de W2, W4 completo (AC4 parcial) y W5 completo; diferir AC de KPI | Product Owner (agente) | Comprometer también los AC de KPI | Los KPI no se miden hoy (RN-17); requiere confirmación (PA-10) |
| DEC-03 | 2026-11-06 10:20 | Asignar owners: AI Engineer A para W1, W2, W4; AI Engineer B para W5 | Product Owner (agente) | Otra asignación | Plan de sprints; requiere confirmación (PA-10) |
| DEC-04 | 2026-11-06 12:57 | Confirmar PA-01: el onboarding inicia con `onboarding_started` y termina con `onboarding_completed` con wallet ACTIVA (SUP-09), tal como adopta `openspec/changes/w1-onboarding-guiado/design.md` | Product Owner (agente, por instrucción del usuario) | Otra frontera de inicio o fin | Define los eventos de W1-AC4 (tarea 5.1); sin cambio de alcance |
| DEC-05 | 2026-11-06 12:58 | Aprobar todos los supuestos propuestos de PA-02 a PA-10 tal como están redactados (SUP-01, SUP-02, SUP-08, SUP-10 a SUP-13, SUP-15), incluido el compromiso de HU/AC y los owners de DEC-02 y DEC-03 | Product Owner (agente, por instrucción del usuario: «aprueba todo») | Corregir cada supuesto por separado | Desbloquea la construcción; cualquier cambio posterior de alcance, cifras o AC se vuelve a consultar al PO |

## Decisiones pendientes
- Ninguna. PA-01 a PA-10 resueltas (DEC-04 y DEC-05).

## Siguiente paso para el rol consumidor
Arquitecto/a y AI Engineers: construir sobre las decisiones aprobadas. Si algo las contradice, consultar al PO.
