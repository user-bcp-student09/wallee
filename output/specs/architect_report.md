# `specs/architect_report.md`
## Análisis de historia y contrato propuesto

> Este informe también sirve como contenido de `specs/user_story.md`. No se declara ninguna tarea completada ni se afirma que se haya generado, instalado o compilado el andamiaje.

## 1. Resumen del Issue

**Feature:** [W1] 1. Andamiaje del proyecto  
**Rol asignado:** Architect. La asignación general de roles sigue siendo propuesta y PA-10 está pendiente.

El Issue pide:

1. Generar `backend-nestjs/` y `frontend-react/` en la raíz mediante `ensure_scaffolding` y comprobar que ambos contienen `package.json`.
2. Instalar dependencias y verificar que `npm run build` finaliza sin errores en ambos proyectos.

El cambio OpenSpec asociado es `openspec/changes/w1-onboarding-guiado`. El andamiaje es la entrega de esta historia; no equivale a implementar el flujo de onboarding ni pagos.

### Contexto funcional compartido

El cambio OpenSpec propone un onboarding secuencial con validación en servidor, una wallet que se activa al completar el flujo y eventos para analítica. Propone tres pasos: `datos`, `identidad` y `verificacion`. La verificación de identidad es simulada, no una integración con proveedores reales.

Estos elementos describen el destino funcional de W1 y orientan las interfaces del proyecto, pero no amplían por sí solos el alcance de las tareas 1.1 y 1.2. El pago, sus rieles, sus estados y la conciliación pertenecen a historias posteriores.

## 2. Componentes, responsabilidades y límites del cambio

### Componentes propuestos para el producto

| Componente | Responsabilidad | Límite |
|---|---|---|
| Frontend React | Presentar la secuencia de onboarding, paso actual, validaciones y mensajes accionables; consumir la API backend. | No decide si un paso es válido ni activa la wallet por cuenta propia. |
| Adaptadores de entrada REST (NestJS) | Recibir solicitudes HTTP, validar DTOs y traducirlas a llamadas a casos de uso. | No contienen reglas de negocio ni acceden directamente a TypeORM. |
| Casos de uso de onboarding | Iniciar y consultar un onboarding, aceptar un paso válido, registrar su avance y activar la wallet al finalizar. | Dependen de puertos del dominio; no dependen de controladores, ORM ni clientes HTTP. |
| Dominio de onboarding/wallet | Modelar estados, pasos y transiciones: `EN_CURSO`/`COMPLETADO` y `PENDIENTE_ONBOARDING`/`ACTIVA`. | Entidades y reglas puras; no importan infraestructura. |
| Puerto de verificación simulada | Abstraer la verificación KYC/OTP para que sea reproducible y sustituible. | No representa una integración real ni invoca proveedores externos. La biometría se menciona como simulada en la propuesta, pero su comportamiento concreto queda por definir. |
| Adaptadores de salida de persistencia | Implementar los puertos de repositorio y persistir onboarding, wallet y eventos. | SQLite con TypeORM es una propuesta pendiente de confirmación en G1; no debe tratarse como decisión aprobada. |
| Registro de eventos | Registrar inicio, paso completado y cierre del onboarding con marca de tiempo. | No calcula KPI ni sustituye la conciliación financiera. |

### Organización hexagonal requerida

El diseño de implementación debe respetar estas dependencias, sin dependencias desde el dominio hacia infraestructura:

```text
backend-nestjs/
  src/
    domain/
      model/
      port/
        input/
        output/
    application/
      service/
    infrastructure/
      adapter/
        input/
        output/
      config/
```

- `domain/model/`: entidades y reglas puras.
- `domain/port/input/`: interfaces de los casos de uso invocables desde el exterior.
- `domain/port/output/`: interfaces para repositorios y servicios externos.
- `application/service/`: implementación de casos de uso, dependiente solo de puertos del dominio.
- `infrastructure/adapter/input/`: controladores REST.
- `infrastructure/adapter/output/`: persistencia y adaptadores del mock.
- `infrastructure/config/`: configuración y composición de dependencias.

El frontend es un consumidor de la API; no forma parte del dominio backend.

### Límites del cambio

**Incluido en el Issue:** andamiaje de ambos proyectos, existencia de sus `package.json`, instalación de dependencias y builds verificables.

**Especificado por el cambio OpenSpec, pero no por las tareas actuales 1.1 y 1.2:** flujo de onboarding, persistencia, validación, activación y eventos.

**Fuera del cambio de onboarding según la propuesta:** pagos, saldos, autenticación posterior, KPI y proveedores reales de identidad.

**Fuera del Issue de andamiaje:** implementación o integración de pagos, elección de riel, reversos, disputas y conciliación. Se mantienen como interfaces compartidas futuras de la épica, no como entregables de este Issue.

## 3. Contrato de API

El diseño identifica `POST /onboarding` y `GET /onboarding/:id`, pero el fragmento disponible no define sus esquemas completos ni el endpoint para enviar cada paso. Por ello, los ejemplos siguientes son **propuesta de contrato para revisión**, no un contrato aprobado. No se debe inferir que el andamiaje solicitado ya los implementa.

### 3.1 Iniciar onboarding

**Propuesta:** `POST /onboarding`

El diseño indica una respuesta `201` con `onboardingId`, `walletId`, pasos y `currentStep`. No define el cuerpo de entrada. El ejemplo usa un cuerpo vacío únicamente para ilustrar el contrato pendiente de confirmar.

```http
POST /onboarding
Content-Type: application/json
```

```json
{}
```

**Respuesta propuesta — `201 Created`:**

```json
{
  "onboardingId": "onb_123",
  "walletId": "wal_456",
  "status": "EN_CURSO",
  "currentStep": "datos",
  "steps": [
    { "id": "datos", "status": "PENDIENTE" },
    { "id": "identidad", "status": "PENDIENTE" },
    { "id": "verificacion", "status": "PENDIENTE" }
  ],
  "walletStatus": "PENDIENTE_ONBOARDING"
}
```

Los tres pasos y los estados de este ejemplo proceden de decisiones propuestas en `design.md`, no de una definición aprobada de los campos de la API.

### 3.2 Consultar progreso

**Propuesta:** `GET /onboarding/:id`

El diseño indica una respuesta `200` con el progreso actual, pero no detalla el esquema.

```http
GET /onboarding/onb_123
```

**Respuesta propuesta — `200 OK`:**

```json
{
  "onboardingId": "onb_123",
  "walletId": "wal_456",
  "status": "EN_CURSO",
  "currentStep": "identidad",
  "steps": [
    { "id": "datos", "status": "COMPLETADO" },
    { "id": "identidad", "status": "PENDIENTE" },
    { "id": "verificacion", "status": "PENDIENTE" }
  ],
  "walletStatus": "PENDIENTE_ONBOARDING"
}
```

### 3.3 Enviar un paso

La ruta no está confirmada en el material disponible. Como propuesta a revisar, se podría usar:

**Propuesta:** `PUT /onboarding/:id/steps/:step`

Ejemplo para el paso de datos:

```http
PUT /onboarding/onb_123/steps/datos
Content-Type: application/json
```

```json
{
  "nombre": "Ana Ejemplo",
  "celular": "912345678"
}
```

La regla disponible para celular exige 9 dígitos y que comience por `9`. Los nombres de campos y las reglas del documento de identidad están pendientes de confirmación.

Ejemplo para identidad:

```http
PUT /onboarding/onb_123/steps/identidad
Content-Type: application/json
```

```json
{
  "documento": "12345678"
}
```

El formato de documento es ilustrativo: la historia no especifica tipo, longitud ni algoritmo de validación.

Ejemplo para verificación:

```http
PUT /onboarding/onb_123/steps/verificacion
Content-Type: application/json
```

```json
{
  "codigo": "123456"
}
```

La tarea 2.2 propone que el OTP válido sea `123456`, configurable y solo fuera de producción. Esta conducta y sus pruebas pertenecen a la tarea 2.2, no a las tareas de andamiaje.

**Respuesta propuesta para paso completado — `200 OK`:**

```json
{
  "onboardingId": "onb_123",
  "status": "EN_CURSO",
  "completedStep": "datos",
  "currentStep": "identidad",
  "walletStatus": "PENDIENTE_ONBOARDING"
}
```

Para el último paso, la propuesta OpenSpec requiere que onboarding quede `COMPLETADO`, la wallet `ACTIVA` y se registre el evento de cierre. El acceso concreto al punto de entrada de pagos no está definido por el contrato disponible.

### 3.4 Errores

El diseño especifica `409` con código `STEP_OUT_OF_ORDER` si se intenta enviar un paso antes de completar los anteriores. La forma común de los errores no está definida; este ejemplo es una propuesta:

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
  "code": "STEP_OUT_OF_ORDER",
  "message": "Completa primero el paso datos.",
  "details": {
    "currentStep": "datos",
    "requestedStep": "verificacion"
  }
}
```

Otros errores necesarios para cubrir el comportamiento de la historia, con códigos HTTP propuestos pendientes de aprobación:

| Caso | Comportamiento requerido | Respuesta propuesta |
|---|---|---|
| Falta un campo obligatorio o un dato es inválido | No avanzar; conservar el paso actual y explicar qué corregir. | `400 Bad Request` con errores por campo. |
| Celular inválido | Bloquear avance e indicar el formato esperado: 9 dígitos, comienza por 9. | `400 Bad Request`. |
| Código OTP incorrecto | Bloquear avance y permitir reintentar. | `400 Bad Request`; límites de reintento no definidos. |
| Paso fuera de orden | Bloquear avance. | `409 Conflict`, `STEP_OUT_OF_ORDER`, especificado por D3. |
| Onboarding inexistente | El comportamiento y formato no están definidos. | `404 Not Found` propuesto. |

Ejemplo propuesto para validación:

```json
{
  "code": "VALIDATION_FAILED",
  "message": "Corrige los campos indicados para continuar.",
  "fieldErrors": [
    {
      "field": "celular",
      "message": "Ingresa un celular de 9 dígitos que empiece con 9."
    }
  ]
}
```

### 3.5 Idempotencia y límites de otros contratos

La historia de andamiaje no define claves de idempotencia ni un contrato de reintento para `POST /onboarding`. Se debe decidir si iniciar repetidamente crea múltiples onboardings o si se requiere una clave/correlación para evitar duplicados. No se inventa una semántica de idempotencia como requisito aprobado.

La épica exige idempotencia para pagos, estados asíncronos, resultado terminal único y trazabilidad para conciliación. Esos requisitos deben diseñarse en las historias de pagos correspondientes. No se propone aquí un endpoint de pago ni se atribuyen al onboarding estados como `exitoso`, `fallido` o `expirado`.

## 4. Trazabilidad de criterios a componentes y verificación

### Criterios de aceptación del Issue

| Criterio | Componente responsable | Verificación observable |
|---|---|---|
| **1.1** Generar `backend-nestjs/` y `frontend-react/` con `ensure_scaffolding` y verificar ambos `package.json`. | Scaffold de `crew.scaffold.ensure_scaffolding`; verificación del Architect. | Ejecutar el comando indicado en `tasks.md` y comprobar que existen las dos carpetas y sus `package.json`. No se marca como hecho en este informe. |
| **1.2** Instalar dependencias y verificar `npm run build` sin errores en cada proyecto. | Configuración de dependencias y scripts de backend y frontend; verificación del Architect. | Instalar dependencias en cada carpeta y ejecutar `npm run build` en ambas. Registrar el resultado. No se marca como hecho en este informe. |

### Requisitos funcionales de onboarding del OpenSpec

Son trazabilidad del cambio asociado, no criterios adicionales de las tareas 1.1 y 1.2.

| Requisito OpenSpec | Componente que lo resolvería | Forma de verificarlo |
|---|---|---|
| Secuencia visible y paso actual | Frontend React, respaldado por consulta de onboarding; caso de uso de consulta. | Prueba de inicio y de avance: se presenta la lista completa y el paso actual cambia al completar uno. |
| Bloqueo ante datos faltantes o inválidos | Validación de DTO en adaptador de entrada y reglas/caso de uso de onboarding. | Pruebas para campo obligatorio, celular inválido y OTP incorrecto; comprobar que no avanza y el mensaje indica qué corregir. |
| Activar la wallet únicamente al finalizar | Caso de uso y dominio; persistencia debe guardar de forma consistente onboarding y wallet. | Completar el flujo y verificar `ACTIVA`; antes de terminar, verificar `PENDIENTE_ONBOARDING` y acceso a pagos denegado. |
| Registrar inicio, pasos completados y cierre | Caso de uso y puerto de salida de eventos; adaptador de persistencia/eventos. | Verificar un evento `onboarding_started`, uno `onboarding_step_completed` por paso y `onboarding_completed` al terminar, con marcas de tiempo. |
| Verificación simulada y reproducible | Puerto de verificación y adaptador mock configurado. | Según tarea 2.2, prueba unitaria donde OTP `123456` pasa y otro código falla; confirmar que no se invoca proveedor externo. |

## 5. Supuestos y preguntas pendientes

### Supuestos que constan como propuestas, no decisiones confirmadas

- Los pasos serían `datos`, `identidad` y `verificacion`; los campos serían nombre, celular, documento y código. La fuente indica expresamente que los pasos y campos no están definidos y esta es una propuesta mínima.
- SQLite con TypeORM está propuesto, pendiente de confirmación en G1.
- El mock de identidad no debe presentarse como una integración real.
- El código OTP de prueba sería `123456`, configurable y disponible solo fuera de producción, según la tarea 2.2.
- La asignación de roles sigue siendo propuesta; PA-10 está pendiente.

### Preguntas pendientes

1. **PA-01:** ¿Cuál es la frontera y el destino de los eventos del onboarding? La propuesta sugiere registrar inicio, paso completado y cierre; falta confirmar dónde y con qué garantía se almacenan.
2. ¿El público objetivo inicial es transporte público, comercios o usuarios con smartphone? La historia indica que puede cambiar textos y ejemplos.
3. ¿Se confirma SQLite con TypeORM en G1?
4. ¿Cuáles son los campos, formatos y reglas definitivas para nombre, celular y documento?
5. ¿Cuál es el endpoint, método y esquema definitivo para enviar pasos? El material disponible solo identifica `POST /onboarding` y `GET /onboarding/:id`.
6. ¿Cuál es el formato común de errores, y qué códigos HTTP se aprobarán para validación y recursos inexistentes?
7. ¿Qué significa “biometría simulada” en la demo, si aplica, y cómo se controla?
8. ¿Cómo se evita crear onboardings duplicados ante reintentos de inicio? No está definido en el contrato recibido.
9. ¿Qué mecanismo o ruta permite a W2 comprobar que una wallet está `ACTIVA` según RN-10?

## 6. Decisiones y coordinación por rol

| Rol | Decisiones o trabajo que debe resolver |
|---|---|
| **Architect** | Cumplir y verificar las tareas 1.1 y 1.2; mantener las dependencias hexagonales; señalar como propuestas los esquemas no aprobados; coordinar PA-10 y las preguntas de interfaz. |
| **Backend** | Definir y documentar DTOs, ruta para enviar pasos, formato de errores, reglas de persistencia y consistencia entre completar onboarding y activar wallet. Resolver la semántica de reintento/idempotencia de inicio antes de implementarla. |
| **AI Engineer** | Implementar el mock reproducible descrito en la tarea **2.2** y probar código correcto e incorrecto. No conectar proveedores reales ni asumir comportamiento no acordado para KYC o biometría. |
| **QA & Security** | Verificar validaciones, orden estricto, ausencia de activación prematura, respuestas accionables y comportamiento del mock. Revisar manejo de datos personales, configuración del OTP de prueba y su exclusión de producción. Las pruebas de build del Issue corresponden a 1.2. |
| **Presenter** | Alinear la demo con el carácter simulado de KYC/OTP/biometría y con los pasos efectivamente aprobados; no presentar el mock como integración real ni atribuir KPI medidos que están fuera de alcance. |

### Idempotencia, pagos y conciliación cuando apliquen

- **Onboarding:** la idempotencia de `POST /onboarding` está pendiente; la historia no define clave, ventana de deduplicación ni resultado de reintentos.
- **Pagos:** idempotencia, estados asíncronos, confirmación terminal única, reversos y conciliación son interfaces y riesgos compartidos de la épica, pero no se implementan ni se fijan en este andamiaje.
- **Eventos de analítica:** onboarding sí requiere registrar los tres tipos de eventos descritos. Los KPI de tiempo, MAU y CAC quedan fuera de alcance; los eventos solo habilitan análisis posterior.
- **Conciliación financiera:** no es un evento ni una función de onboarding. Su contrato deberá definirse en la historia de pagos/conciliación correspondiente.

## 7. Referencia de tareas OpenSpec

- **1.1 — Architect:** generar ambos proyectos con `ensure_scaffolding` y comprobar los `package.json`.
- **1.2 — Architect:** instalar dependencias y comprobar los builds de ambos proyectos.
- **2.2 — AI Engineer 1; diseño Architect; prueba QA & Security:** implementar y probar el mock de identidad.

Este informe no marca tareas como completadas; su ejecución y validación corresponden al equipo humano.