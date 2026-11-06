# Trabajar en equipo

## Crear el repositorio del equipo

El líder crea el repositorio en su cuenta personal desde esta plantilla:

```sh
gh repo create crewai --template NTTData-Academy/crewai --public --clone
```

Agrega a tus compañeros como colaboradores con permiso de escritura en el repo del equipo.
Los demás integrantes clonan ese mismo repo:

```sh
gh repo clone <CAPTAIN>/crewai
cd crewai
```

## Repartir los archivos

Anota un responsable por archivo. Cada persona edita su propio agente. Consulta la tabla de responsabilidades, entregables y puntos de partida en [Mejora tu agente](MEJORA_TU_AGENTE.md#de-dónde-partir-según-tu-rol).

- `agents/product_owner.py`: responsable pendiente. Prioriza, fija el alcance y mantiene los criterios de aceptación.
- `agents/architect.py`: responsable pendiente. Define la solución y el contrato de API.
- `agents/ai_engineer_1.py`: responsable pendiente. Implementa el dominio y el backend (NestJS).
- `agents/ai_engineer_2.py`: responsable pendiente. Implementa el frontend (React) y el agente de excepciones.
- `agents/qa_security.py`: responsable pendiente. Diseña las pruebas y sus comandos, y revisa riesgos de seguridad.
- `agents/presenter.py`: responsable pendiente. Controla tiempos, evidencia y pitch.

## Registrar responsables para el dashboard

Copia `team.example.json` a `team.json`, reemplaza los seis valores por usuarios reales de GitHub distintos y publica ese archivo en `main`. El dashboard lee `roles` para asociar cada agente con su responsable. Los nombres de ejemplo no son participantes.

## Entregar un cambio

1. Acuerden un requerimiento y sus criterios de aceptación.
2. Crea tu rama, por ejemplo `git switch -c agents/ai-engineer-1`.
3. Edita las instrucciones de tu agente en su archivo. Coordina los cambios de contratos con el arquitecto.
4. Ejecuta `python tools/verify.py`.
5. Publica tu rama y abre un PR hacia `main` del repo del líder. No envíes el PR al template de la organización.
6. Pide a un compañero que revise el cambio antes de integrarlo.

Una persona ejecuta el pipeline integrado desde `main`. El equipo participa en las aprobaciones
humanas y aporta feedback en cada etapa. Cada integrante conserva su propia `.env`, autenticación
y entorno virtual. No compartan checkpoints entre ejecuciones de distintas computadoras.

Los agentes generan texto y archivos. El agente de QA & Security propone tests y comandos;
una persona los ejecuta y adjunta la salida real al PR. Un informe del modelo no demuestra que las pruebas pasaron.
