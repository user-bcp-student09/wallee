# Design

## Context

Ver [proposal.md](proposal.md) para el motivo y el alcance. Restricciones que dan forma al enfoque:

- Stack acordado (PA-09, aprobado en DEC-05): NestJS con TypeScript en el backend, React con Vite en el frontend y SQLite para persistir. Datos solo sintéticos.
- El código vive en el repositorio de la app (`user-bcp-student17/wallee-app`), en `backend/` y `frontend/`. Hoy el backend base solo trae `@nestjs/common`, `core` y `platform-express`, y un módulo `health`; no incluye `class-validator` ni persistencia. Las dependencias que W1 agregue (DTOs y SQLite) se reutilizan aquí.
- W2 depende de W1: usa `GET /wallets/:id` y el estado `ACTIVA` (RN-10). W1 dejó el saldo inicial a cargo de W2 (SUP-15).
- El proveedor de pagos y los callbacks son MOCK (RN-08). El último dígito del celular decide el escenario.
- Tiempo disponible: W2 debía estar en verde a las 11:45, así que el diseño se mantiene mínimo.

## Goals / Non-Goals

**Goals:**
- Un pago de bajo monto con un único resultado terminal por intento, derivado del estado del proveedor mock (RN-05, RN-06).
- Un historial con referencia de transacción y un evento `payment_succeeded` por pago exitoso.
- Un contrato de API estable sobre el que W4 agregue idempotencia y W5 clasifique fallas.
- Un mock reproducible: cada escenario se dispara solo con los datos de entrada, sin intervención manual.

**Non-Goals:**
- Idempotencia por clave y callbacks duplicados (W4), clasificación de fallas y guía de soporte (W5).
- Pago por QR de comercio (W3) y conciliación (W6).
- Autenticación del pagador; se identifica por `walletId`, igual que en W1.
- Cálculo de KPI (caída en checkout, MAU); solo se guarda el evento.

## Decisions

### D1. Ubicación del código
El backend va en `backend/src/payments/` y el frontend en `frontend/src/payments/`, en el repositorio de la app, con los nombres de carpeta que ya tiene ese repo.
- Alternativa: `backend-nestjs/` y `frontend-react/` en este repositorio, como indica el diseño de W1 (D1). Descartada porque el código de ejecución vive aparte; este repo conserva solo la gestión.
- Consecuencia: el diseño y las tareas de W1 que mencionan `backend-nestjs/` y `frontend-react/` deben alinearse con esta decisión.

### D2. Modelo de datos
| Entidad | Campos clave |
|---|---|
| `Wallet` (extiende la de W1) | `balance` (monto en soles con dos decimales), saldo inicial fijo en fixtures |
| `Transaction` | `id`, `reference`, `walletId`, `destination`, `destinationType` (`PHONE` \| `ALIAS`), `amount`, `providerStatus` (`CREADA` \| `PENDING` \| `APPROVED` \| `DECLINED` \| `TIMEOUT`), `outcome` (`exitoso` \| `fallido` \| `expirado` \| nulo mientras está en proceso), `createdAt`, `resolvedAt` |
| `PaymentEvent` | `id`, `transactionId`, `type` (`payment_succeeded`), `occurredAt` |
| `DirectoryEntry` (fixture) | `alias`, `phone`, `displayName` |

El historial es la lista de `Transaction` de la wallet. La referencia se genera al crear la transacción y es única.
- Los montos se guardan en céntimos enteros o decimal fijo para evitar errores de redondeo (PROPUESTO).

### D3. Estados y mapeo del proveedor
Ciclo: `CREADA` → `PENDING` → `APPROVED` | `DECLINED` | `TIMEOUT`. El mapeo a resultado terminal es `APPROVED`→`exitoso`, `DECLINED`→`fallido`, `TIMEOUT`→`expirado` (RN-05). `PENDING` no es terminal y no se muestra como resultado (RN-07).
- Un intento ya terminal no cambia de estado (RN-06). Una transición posterior se ignora; registrar el duplicado queda para W4.

### D4. Mock del proveedor
Una función pura decide el escenario por el último dígito del celular (RN-08): `0`→`DECLINED`, `1`→`TIMEOUT`, `2`→`PENDING`, `3` a `9`→`APPROVED`. Para un alias se usa el celular asociado en el directorio.
- Para `DECLINED`, `TIMEOUT` y `APPROVED` el resultado se resuelve en la misma solicitud, sin esperas; así la demo es determinista.
- Para `PENDING`, el pago queda en proceso hasta que llega el callback (D6).

### D5. Contrato de API (REST, JSON)
| Método y ruta | Resultado |
|---|---|
| `GET /directory/:destination` | `200` con el nombre del destino (celular o alias) para mostrarlo en la confirmación (W2-AC1); `400` `DESTINATION_INVALID`; `404` `DESTINATION_NOT_FOUND` |
| `POST /payments` | `201` con la transacción (`id`, `reference`, `outcome`, `providerStatus`, `amount`, `destination`); errores en D7 |
| `GET /payments/:id` | `200` con la transacción; `404` `PAYMENT_NOT_FOUND` |
| `GET /wallets/:id/payments` | `200` con el historial, de la más reciente a la más antigua |
| `POST /payments/:id/callback` | `200` con la transacción; recibe el estado final del proveedor mock para resolver un `PENDING` |

El cuerpo de `POST /payments` lleva `walletId`, `destination` y `amount`. El frontend consulta `GET /directory/:destination`, muestra el destino y el monto, y solo envía el pago cuando el pagador confirma.

### D6. Resolución de `PENDING`
Un pago `PENDING` queda en proceso y se resuelve con `POST /payments/:id/callback` (estado `APPROVED`, `DECLINED` o `TIMEOUT`). El frontend consulta `GET /payments/:id` hasta ver un resultado terminal. El mecanismo es PROPUESTO: las convenciones del mock dejan al Arquitecto decidir cómo se dispara el callback; esta forma permite probarlo sin esperar tiempos reales.

### D7. Validaciones y errores
Con DTOs y `class-validator` en el servidor; el cliente solo ayuda. Los errores llevan un código de motivo estable y un mensaje que indica qué corregir.
| Caso | Respuesta |
|---|---|
| Wallet no `ACTIVA` (RN-10) | `403` `WALLET_NOT_ACTIVE` |
| Celular que no empieza con 9 o sin 9 dígitos, o alias inexistente (RN-04) | `400` `DESTINATION_INVALID` |
| Monto no numérico o menor o igual a cero | `400` `VALIDATION_ERROR` con el campo |
| Monto mayor a S/ 500 (RN-01) | `422` `AMOUNT_OVER_LIMIT` |
| Saldo menor al monto (RN-18) | `422` `INSUFFICIENT_FUNDS`; no se crea transacción |
El límite de S/ 500 vive en configuración, para poder variarlo por proveedor o canal (PA-02) sin cambiar código.

### D8. Saldo y cobro sin duplicados
El saldo se descuenta únicamente cuando la transacción pasa a `APPROVED`, en la misma transacción de base de datos que fija el resultado `exitoso` y registra el evento. Un pago `fallido` o `expirado` no toca el saldo. Un reintento crea una transacción nueva; no se reutiliza la anterior.
- Alternativa: reservar el saldo al crear el pago y liberarlo si falla. Descartada por complejidad; sin concurrencia en el MVP, validar y descontar al aprobar es suficiente.
- La protección contra solicitudes repetidas con la misma clave es de W4.

### D9. Evento `payment_succeeded`
Se registra exactamente un evento por pago exitoso, con marca de tiempo del servidor y la referencia, en la misma transacción de base de datos que el descuento (D8). No hay evento para pagos fallidos o expirados.

### D10. Frontend
Un flujo en tres pantallas en `frontend/src/payments/`: formulario (destino y monto), confirmación (identidad del destino y monto) y resultado (`exitoso` con la referencia, `fallido` o `expirado` con las acciones reintentar y volver; en proceso mientras hay un `PENDING`). Los mensajes de error se toman de la respuesta de la API. Una vista mínima de historial muestra las referencias. El punto de entrada solo aparece con la wallet `ACTIVA` (el estado de W1).
- El estado `walletId` se conserva en el cliente, como en W1.

## Risks / Trade-offs

- [Etiquetas de estado y textos finales sin definir con producto] → Se usan `exitoso`, `fallido` y `expirado`; cambiar el texto solo toca la UI.
- [Mecanismo del callback PROPUESTO (D6)] → Se aísla en un endpoint; W4 y W5 lo reutilizan y pueden ajustarlo.
- [Sin idempotencia en W2] → Una solicitud repetida puede crear dos transacciones. Se mitiga con W4, que va justo después, y con la UI que deshabilita el botón durante el envío.
- [Sin autenticación] → Cualquiera con el `walletId` podría pagar. Aceptable en un MVP con datos sintéticos; se anota como pendiente posterior.
- [Saldo inicial arbitrario] → Un valor fijo en fixtures (PROPUESTO: S/ 1,000), suficiente para probar S/ 500 y un saldo insuficiente.
- [Calendario] → W2 está atrasado frente a las 11:45; se mantiene el alcance mínimo (un mock, tres pantallas).

## Open Questions

- ¿Texto final de las etiquetas de estado terminal con producto? No cambia las specs ni las tareas.
- ¿Saldo inicial exacto y datos del directorio sintético? No cambia las specs; se fijan en las fixtures.
