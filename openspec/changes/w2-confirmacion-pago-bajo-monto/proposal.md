# Proposal

## Why

El pagador que transfiere montos pequeños abandona el checkout cuando no sabe si el pago se realizó o qué hacer si falló. W2 es el segundo eslabón del flujo end-to-end: con una wallet `ACTIVA` (W1) el pagador debe poder pagar a un celular o alias y recibir un único resultado terminal claro. W4 (idempotencia) y W5 (fallas y reversos) se construyen sobre este flujo. Debe quedar en verde a las 11:45 del Sprint 1; el plan de sprints ya está retrasado respecto de esa hora.

## What Changes

- Pantalla de confirmación que muestra la identidad del destino y el monto antes de enviar el pago (W2-AC1).
- Pago a un celular (9 dígitos, empieza con 9) o a un alias del directorio sintético, con validación de monto máximo (S/ 500), saldo y destino antes de enviar (RN-01, RN-04, RN-18).
- Un único resultado terminal por intento: `exitoso`, `fallido` o `expirado`, derivado del proveedor mock según el último dígito del celular; `PENDING` no se muestra como resultado final hasta el callback (W2-AC2, RN-05 a RN-08).
- Referencia de transacción persistida en el historial cuando el pago es exitoso (W2-AC3).
- Siguiente acción clara (reintentar o volver) ante un pago fallido o expirado, sin crear cobros duplicados (W2-AC4).
- Emisión del evento `payment_succeeded` en los pagos exitosos (W2-AC6, parcial).
- Solo una wallet `ACTIVA` puede acceder al pago (RN-10, usa `GET /wallets/:id` de W1).
- El proveedor de pagos y los callbacks se simulan con un mock controlable; no se presentan como integración real.

Fuera de alcance de este cambio:
- W2-AC5 (caída en checkout de 30% a 8%) y el cálculo de MAU de W2-AC6: son KPI de negocio que no se miden hoy (RN-17). Solo se emite el evento `payment_succeeded` que luego los habilita.
- Idempotencia de solicitudes y callbacks duplicados (W4) y guía de fallas y reversos (W5). W2 solo evita el cobro duplicado dentro de un mismo intento.
- Integración real con proveedores, QR de comercio (W3) y conciliación (W6).

## Capabilities

### New Capabilities
- `low-value-payment`: pago de bajo monto a un celular o alias, validaciones previas, resultado terminal único, referencia en el historial, siguiente acción ante fallas y evento de pago exitoso.

### Modified Capabilities
<!-- `wallet-onboarding` (W1) se consume sin cambiar sus requisitos. -->

## Impact

- **Repositorio de la app (`user-bcp-student17/wallee-app`)**: backend NestJS en `backend/` (módulo de pagos, mock de proveedor, historial, evento) y frontend React en `frontend/` (pantalla de pago, confirmación, resultado y siguiente acción). Este repositorio de gestión conserva solo OpenSpec, discovery y agentes.
- **Dependencia de W1**: requiere `GET /wallets/:id` y wallet `ACTIVA` (RN-10). Debe existir un saldo inicial sintético, definido en fixtures (SUP-15).
- **Dependencias del resto del plan**: W4 agrega idempotencia sobre estos pagos y W5 clasifica las fallas.
- **Referencias**: [W2 en el discovery](../../../challenge/docs/discovery/02-producto/historias/W2-pago-contacto.md), [historia original](../../../challenge/user-stories/payer-low-value-payment-confirmation.sp.md), [reglas](../../../challenge/docs/discovery/04-reglas-y-contratos/01-reglas-de-negocio.md) (RN-01, RN-04 a RN-08, RN-10 a RN-12, RN-17, RN-18), [estados](../../../challenge/docs/discovery/04-reglas-y-contratos/02-estados-y-transiciones.md) y [convenciones del mock](../../../challenge/docs/discovery/04-reglas-y-contratos/03-convenciones-mock.md).
- **Decisiones ya aprobadas por el PO**: PA-02 (S/ 500 por transacción, SUP-01) y PA-08 (no se ejecuta con saldo menor al monto, SUP-15), DEC-05.
- **Pendiente con producto**: el texto final de las etiquetas de estado terminal (supuesto: exitoso, fallido, expirado); no cambia el comportamiento.
