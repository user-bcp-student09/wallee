# Tasks

El código de estas tareas vive en el repositorio de la app (`backend/` y `frontend/`). Depende de W1 (`w1-onboarding-guiado`): wallet `ACTIVA` y `GET /wallets/:id`.

## 1. Base y datos sintéticos

- [ ] 1.1 [rol: Architect] Verificar que el repositorio de la app arranca con W1 integrado y que `GET /wallets/:id` devuelve `ACTIVA` y `PENDIENTE_ONBOARDING` (dependencia RN-10); verificar con `python tools/wallee.py test backend` y una llamada a ese endpoint
- [ ] 1.2 [rol: AI Engineer 2] Definir las fixtures: directorio sintético (alias, celular y nombre), con celulares que terminan en 0, 1, 2 y 3 a 9, y saldo inicial fijo en la wallet; verificar que al arrancar la base queda cargada con esos datos

## 2. Modelo de datos

- [ ] 2.1 [rol: AI Engineer 2] Definir `Transaction` y `PaymentEvent`, agregar `balance` a `Wallet` y la migración que conserve los datos de W1; verificar que la aplicación arranca y crea las tablas sin perder wallets existentes

## 3. Mock del proveedor y reglas del dominio — W2-AC2 (D3, D4, D7)

- [ ] 3.1 [rol: AI Engineer 1; prueba: QA & Security] Implementar el mock del proveedor por último dígito del celular (0→`DECLINED`, 1→`TIMEOUT`, 2→`PENDING`, 3 a 9→`APPROVED`) y el mapeo a `exitoso`, `fallido` y `expirado`; verificar con pruebas unitarias los cuatro escenarios (W2-AC2-T1, W2-AC2-T2)
- [ ] 3.2 [rol: AI Engineer 1; prueba: QA & Security] Implementar las validaciones del dominio con DTOs: monto máximo S/ 500 configurable (RN-01), destino celular o alias (RN-04), saldo suficiente (RN-18) y wallet `ACTIVA` (RN-10), con códigos de error estables; verificar con una prueba por regla, incluidos S/ 500 permitido y S/ 500,01 bloqueado (W2-AC4-T3)

## 4. API de pagos — W2-AC1, W2-AC2, W2-AC3, W2-AC4, W2-AC6 (D5, D6, D8, D9)

- [ ] 4.1 [rol: AI Engineer 1; prueba: QA & Security] Implementar `GET /directory/:destination` que devuelve la identidad del destino; verificar con una prueba que un celular y un alias válidos devuelven su nombre y uno inválido devuelve `400 DESTINATION_INVALID` (W2-AC1-T1, W2-AC1-T2)
- [ ] 4.2 [rol: AI Engineer 1; prueba: QA & Security] Implementar `POST /payments` y `GET /payments/:id`: crea la transacción, consulta el mock y devuelve un único resultado terminal por intento; verificar con pruebas de integración que los escenarios 0, 1 y resto devuelven `fallido`, `expirado` y `exitoso` (W2-AC2-T1, W2-AC2-T2)
- [ ] 4.3 [rol: AI Engineer 1; prueba: QA & Security] Implementar `POST /payments/:id/callback` para resolver un `PENDING` sin permitir que un intento ya terminal cambie de estado; verificar con pruebas que el escenario 2 no muestra resultado terminal hasta el callback y que un segundo callback no altera el resultado (RN-06, RN-07)
- [ ] 4.4 [rol: AI Engineer 1; prueba: QA & Security] Descontar el saldo y registrar la referencia solo al aprobar, en una sola transacción, e implementar `GET /wallets/:id/payments`; verificar con pruebas que un pago exitoso aparece en el historial con su referencia y que un pago fallido o expirado no descuenta saldo ni se cobra dos veces tras un reintento (W2-AC3-T1, W2-AC3-T2, W2-AC4-T1, W2-AC4-T2)
- [ ] 4.5 [rol: AI Engineer 1; prueba: QA & Security] Registrar el evento `payment_succeeded` con marca de tiempo del servidor y referencia en cada pago exitoso; verificar con pruebas que un pago exitoso produce un solo evento y que uno fallido o expirado no produce ninguno (W2-AC6-T1, W2-AC6-T2)

## 5. Frontend — W2-AC1, W2-AC3, W2-AC4 (D10)

- [ ] 5.1 [rol: AI Engineer 2; prueba: QA & Security] Construir el formulario de pago y la pantalla de confirmación que muestra la identidad del destino y el monto antes de enviar; verificar con una prueba de componente que ambos datos se muestran y que no se envía nada hasta confirmar (W2-AC1-T2)
- [ ] 5.2 [rol: AI Engineer 2; prueba: QA & Security] Construir la pantalla de resultado: `exitoso` con la referencia; `fallido` o `expirado` con las acciones reintentar y volver; y un estado en proceso para `PENDING`; verificar con pruebas de componente para cada resultado (W2-AC2-T2, W2-AC3-T2, W2-AC4-T2)
- [ ] 5.3 [rol: AI Engineer 2; prueba: QA & Security] Mostrar los mensajes de error de la API junto al campo afectado y una vista mínima de historial con las referencias; verificar con pruebas de componente que un `422 AMOUNT_OVER_LIMIT` y un `422 INSUFFICIENT_FUNDS` muestran su mensaje y mantienen la pantalla (W2-AC4-T3)
- [ ] 5.4 [rol: AI Engineer 2; prueba: QA & Security] Mostrar el punto de entrada del pago solo con la wallet `ACTIVA`; verificar con una prueba de componente que con `PENDIENTE_ONBOARDING` no aparece

## 6. Documentación

- [ ] 6.1 [rol: Presenter] Documentar en el README de la app el contrato de la API de pagos, los escenarios del mock por último dígito y que el proveedor y los callbacks son MOCK; verificar que los comandos documentados corren tal como están escritos

## 7. Integración

- [ ] 7.1 [rol: QA & Security] Ejecutar el recorrido completo contra backend y frontend en local con los tres escenarios (exitoso, fallido y expirado, más el pendiente resuelto por callback) sin intervención manual, y registrar el resultado en `evidence.md`; verificar que W2-AC1 a W2-AC4 y W2-AC6 pasan sus pruebas T1 y T2
- [ ] 7.2 [rol: Presenter; verificación: QA & Security] Completar la matriz de trazabilidad de `challenge/docs/discovery/05-trazabilidad/01-matriz-trazabilidad.md` para W2-AC1 a W2-AC4 y W2-AC6 (test, commit, PR); verificar que ninguna fila queda sin test

## Workflow follow-up

- [rol: Product Owner] Archivar el cambio cuando el equipo revise y apruebe el PR.
- [rol: Presenter] Sincronizar la spec `low-value-payment` a las specs principales al archivar.
