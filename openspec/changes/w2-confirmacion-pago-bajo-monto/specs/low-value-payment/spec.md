# Spec Delta

## Purpose

Define el comportamiento observable del pago de bajo monto a un celular o alias: confirmación previa, validaciones, resultado terminal único, referencia en el historial, siguiente acción ante fallas y evento de pago exitoso, para que el pagador confíe en si el pago se realizó o no.

## ADDED Requirements

### Requirement: Confirmación previa con destino y monto
El sistema SHALL mostrar al pagador la identidad del destino y el monto antes de la confirmación final del pago.

#### Scenario: Pantalla de confirmación
- **WHEN** el pagador ingresa un destino y un monto válidos y avanza a la confirmación
- **THEN** el sistema muestra la identidad del destino y el monto, y no envía el pago hasta que el pagador confirme

### Requirement: Validaciones antes del envío
El sistema SHALL rechazar, antes de enviar el pago al proveedor, un monto mayor a S/ 500, un destino inválido y un monto mayor al saldo, e SHALL indicar qué corregir.

#### Scenario: Monto en el límite
- **WHEN** el pagador confirma un pago de exactamente S/ 500 con saldo suficiente
- **THEN** el sistema permite el pago

#### Scenario: Monto sobre el límite
- **WHEN** el pagador ingresa un monto mayor a S/ 500
- **THEN** el sistema bloquea el envío y muestra un mensaje con el monto máximo permitido

#### Scenario: Destino inválido
- **WHEN** el pagador ingresa un celular que no tiene 9 dígitos o no empieza con 9, o un alias que no existe en el directorio
- **THEN** el sistema bloquea el envío y muestra un mensaje con el formato esperado

#### Scenario: Saldo insuficiente
- **WHEN** el pagador confirma un pago con monto mayor al saldo de su wallet
- **THEN** el sistema no ejecuta el pago, no crea transacción y muestra un mensaje de saldo insuficiente

### Requirement: Pago solo con wallet activa
El sistema SHALL permitir el acceso al pago de bajo monto únicamente a una wallet en estado `ACTIVA`.

#### Scenario: Wallet pendiente de onboarding
- **WHEN** un usuario cuya wallet está en `PENDIENTE_ONBOARDING` intenta iniciar un pago
- **THEN** el sistema rechaza el pago y le indica que debe completar el onboarding

### Requirement: Resultado terminal único por intento
El sistema SHALL entregar al pagador un único resultado terminal por intento de pago (`exitoso`, `fallido` o `expirado`), derivado del estado del proveedor mock, y SHALL NOT mostrar un estado no terminal como resultado final.

#### Scenario: Pago aprobado
- **WHEN** el proveedor mock responde `APPROVED` (último dígito del celular entre 3 y 9)
- **THEN** el sistema muestra el resultado `exitoso`

#### Scenario: Pago rechazado
- **WHEN** el proveedor mock responde `DECLINED` (último dígito 0)
- **THEN** el sistema muestra el resultado `fallido`

#### Scenario: Pago sin respuesta
- **WHEN** el proveedor mock responde `TIMEOUT` (último dígito 1)
- **THEN** el sistema muestra el resultado `expirado`

#### Scenario: Pago pendiente
- **WHEN** el proveedor mock responde `PENDING` (último dígito 2)
- **THEN** el sistema muestra el pago como en proceso, no lo presenta como resultado final y espera el callback

#### Scenario: Un solo resultado
- **WHEN** un intento ya tiene un resultado terminal
- **THEN** el sistema conserva ese único resultado y no lo reemplaza por otro

### Requirement: Referencia de transacción en el historial
El sistema SHALL mostrar una referencia de transacción en un pago exitoso y SHALL persistirla en el historial del pagador.

#### Scenario: Pago exitoso
- **WHEN** un pago termina como `exitoso`
- **THEN** el sistema muestra una referencia de transacción y la consulta del historial incluye esa transacción con la misma referencia

### Requirement: Siguiente acción ante fallo o expiración
El sistema SHALL ofrecer una siguiente acción clara (reintentar o volver) cuando un pago termina como `fallido` o `expirado`, y SHALL NOT crear cobros duplicados.

#### Scenario: Pago fallido o expirado
- **WHEN** un pago termina como `fallido` o `expirado`
- **THEN** el sistema ofrece reintentar o volver, y el saldo del pagador no se descuenta por ese intento

#### Scenario: Reintento tras un fallo
- **WHEN** el pagador reintenta tras un pago `fallido` o `expirado`
- **THEN** el sistema trata el reintento como un nuevo intento y el saldo se descuenta como máximo una vez si termina `exitoso`

### Requirement: Evento de pago exitoso
El sistema SHALL emitir el evento `payment_succeeded`, con marca de tiempo del servidor y la referencia de transacción, por cada pago exitoso.

#### Scenario: Evento en un pago exitoso
- **WHEN** un pago termina como `exitoso`
- **THEN** el sistema registra exactamente un evento `payment_succeeded` para ese pago

#### Scenario: Sin evento en un pago no exitoso
- **WHEN** un pago termina como `fallido` o `expirado`
- **THEN** el sistema no registra el evento `payment_succeeded`
