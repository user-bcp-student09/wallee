# Tasks

## 1. Andamiaje del proyecto

- [ ] 1.1 [rol: Architect] Generar `backend-nestjs/` y `frontend-react/` en la raíz con `python -c "from pathlib import Path; from crew.scaffold import ensure_scaffolding; ensure_scaffolding(Path('.'))"` y verificar que existen ambos `package.json`
- [ ] 1.2 [rol: Architect] Instalar dependencias en ambos proyectos y verificar que `npm run build` termina sin errores en cada uno

## 2. Modelo de datos y mock de identidad (D4, D7)

- [ ] 2.1 [rol: AI Engineer 2] Definir las entidades `Onboarding`, `Wallet` y `OnboardingEvent` con SQLite y verificar que la aplicación arranca y crea las tablas
- [ ] 2.2 [rol: AI Engineer 1; diseño: Architect; prueba: QA & Security] Implementar el mock de identidad (KYC acepta formato válido; OTP `123456`; valor fijo en configuración y solo fuera de producción) y verificar con una prueba unitaria que el código correcto pasa y uno distinto falla (cubre el requisito de verificación simulada)

## 3. Pasos y validación — W1-AC1, W1-AC2 (D2, D3, D5, D6)

- [ ] 3.1 [rol: AI Engineer 1; prueba: QA & Security] Implementar `POST /onboarding` y `GET /onboarding/:id` devolviendo los tres pasos con su estado y el paso actual (W1-AC1-T1) y verificar con una prueba que el inicio lista los pasos con `datos` como actual (W1-AC1-T2)
- [ ] 3.2 [rol: AI Engineer 1; prueba: QA & Security] Implementar `PUT /onboarding/:id/steps/:stepKey` con validación por DTO: nombre obligatorio, celular de 9 dígitos que empieza con 9, documento de 8 dígitos, código obligatorio (W1-AC2-T1); verificar con pruebas que cada dato faltante o inválido devuelve `400 VALIDATION_ERROR` con el campo a corregir y no avanza el paso (W1-AC2-T2)
- [ ] 3.3 [rol: AI Engineer 1; prueba: QA & Security] Rechazar pasos fuera de orden con `409 STEP_OUT_OF_ORDER` y verificar con una prueba que enviar `verificacion` antes de `datos` no cambia el progreso

## 4. Activación de la wallet — W1-AC3 (D4, D5)

- [ ] 4.1 [rol: AI Engineer 1; prueba: QA & Security] Al completar el último paso, marcar el onboarding `COMPLETADO` y la wallet `ACTIVA` en una sola transacción, e implementar `GET /wallets/:id` (W1-AC3-T1); verificar con una prueba que tras los tres pasos la wallet es `ACTIVA` (W1-AC3-T2)
- [ ] 4.2 [rol: AI Engineer 1; prueba: QA & Security] Verificar con una prueba que con un paso pendiente la wallet sigue en `PENDIENTE_ONBOARDING` y que `GET /wallets/:id` lo refleja, para que W2 pueda bloquear el pago (W1-AC3-T3)

## 5. Eventos del onboarding — W1-AC4 (D8)

- [ ] 5.1 [rol: AI Engineer 1; prueba: QA & Security; decisión PA-01: Product Owner] Registrar `onboarding_started`, `onboarding_step_completed` (con el paso) y `onboarding_completed` con marca de tiempo del servidor (W1-AC4-T1); verificar con una prueba que un recorrido completo produce un evento de inicio, tres de paso y uno de cierre, en ese orden (W1-AC4-T2)

## 6. Frontend y documentación (D9)

- [ ] 6.1 [rol: AI Engineer 2; prueba: QA & Security] Construir el asistente de pasos en React con indicador de todos los pasos y del actual, y formularios por paso; verificar con una prueba de componente que el indicador marca el paso actual y los completados
- [ ] 6.2 [rol: AI Engineer 2; prueba: QA & Security] Mostrar los mensajes de error que devuelve la API junto al campo afectado y bloquear el avance; verificar con una prueba de componente que un `400` muestra el mensaje y mantiene el paso
- [ ] 6.3 [rol: AI Engineer 2; prueba: QA & Security] Mostrar el punto de entrada de pagos al activarse la wallet; verificar con una prueba de componente que aparece solo con la wallet `ACTIVA`
- [ ] 6.4 [rol: Presenter] Documentar en el README cómo ejecutar backend y frontend, el contrato de la API y que KYC y OTP son MOCK con su código de prueba; verificar que los comandos documentados corren tal como están escritos

## 7. Integración

- [ ] 7.1 [rol: QA & Security] Ejecutar el recorrido completo contra backend y frontend en local (alta con datos de prueba hasta wallet `ACTIVA`) y verificar que se completa sin intervención manual
- [ ] 7.2 [rol: Presenter; verificación: QA & Security] Completar la matriz de trazabilidad de `challenge/docs/discovery/05-trazabilidad/01-matriz-trazabilidad.md` para W1-AC1 a W1-AC4 (test, commit, PR) y verificar que ninguna fila queda sin test

## Workflow follow-up

- [rol: Product Owner] Archivar el cambio cuando el equipo revise y apruebe el PR.
- [rol: Presenter] Sincronizar la spec `wallet-onboarding` a las specs principales al archivar.
