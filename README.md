# CrewAI para equipos

Los agentes parten con instrucciones básicas. Sigue [Mejora tu agente](MEJORA_TU_AGENTE.md) para completar el ejercicio y consultar resultados desde el portal.

Base de trabajo del Lab 4, S1. Lee una funcionalidad del backlog mediante MCP Projects
y genera una solución para Wallee con NestJS (backend) y React (frontend) con seis agentes de CrewAI.
Cada agente tiene su definición y la tarea en un archivo propio.

## Editar tu agente

Los agentes son básicos: un objetivo breve, una responsabilidad por rol y una salida concreta.
Usa un requisito pequeño, por ejemplo crear una tarea con título.
Ajusta ese ejemplo al requisito del backlog de tu equipo.
El Product Owner fija alcance y criterios; AI Engineer 1 implementa el dominio y el backend NestJS;
AI Engineer 2 el frontend React y el agente de excepciones; QA & Security prueba y revisa riesgos;
Presenter prepara la evidencia y el pitch. Los prompts conservan los formatos
que necesita el flujo para guardar código y revisar resultados.

Cada participante edita el archivo de su rol:

- `agents/product_owner.py`
- `agents/architect.py`
- `agents/ai_engineer_1.py`
- `agents/ai_engineer_2.py`
- `agents/qa_security.py`
- `agents/presenter.py`

El orden es `product_owner → architect → ai_engineer_1 → ai_engineer_2 → qa_security → presenter`.
La aprobación humana se conserva entre etapas.

## Elegir rol y cambio OpenSpec

Al iniciar, `main.py` pregunta **«Selecciona el rol que desea ejecutar»**. La lista sale de los archivos de `agents/`
(más la opción **Todos**, que corre el flujo completo).
Con un solo rol se reutiliza el contexto de los demás (checkpoint o informes ya generados en `output/`).
Después pregunta el cambio de `openspec/changes/` (lo que muestra `openspec list`); su propuesta, specs, diseño y las
tareas con `[rol: ...]` de ese rol se agregan al prompt. Para omitir las preguntas: `WALLEE_ROLE` (clave del rol o `all`)
y `WALLEE_OPENSPEC_CHANGE` (nombre del cambio o `none`).

Las carpetas de `output/` de cada rol se editan en su prompt (`INSTRUCTIONS`) con estas líneas:

```text
Carpetas de salida en /output: test, security
Carpeta del informe en /output: specs
```

Por defecto: `qa_security` → `test` y `security`; `ai_engineer_1` y `ai_engineer_2` → `backend-nestjs` y `frontend-react`;
`product_owner`, `architect` y `presenter` → `specs`. Los `.md` solo se guardan si su ruta empieza con
una carpeta declarada (por ejemplo `// security/security-review.md`).

## Push y Pull Request con preaprobación

Al terminar, tras copiar `output/` al repo destino, `crew/publish.py`:

1. crea una rama `wallee/<rol>-<feature>` (si el repo está en su rama principal; si ya estás en otra, la reutiliza),
   hace commit solo de los archivos copiados y `git push -u origin <rama>`;
2. muestra la **preaprobación**: destino, título, descripción y archivos. Opciones: `s` crear · `d` alternar borrador ·
   `e` editar título · `n` no crear (la rama ya queda publicada);
3. con `s` abre el PR con `gh pr create`. Si el repo tiene `pull_request_template.md`, se conserva y el resumen
   generado (feature, rol, cambio OpenSpec, pasos aprobados, archivos) se agrega debajo.

Requiere `gh` autenticado (`gh auth login`) y un remoto `origin`. Si algo falla, el `output/` ya está copiado y solo se
informa el error. `WALLEE_PUBLISH=false` omite todo este paso.
Consulta [TEAM.md](TEAM.md) para crear el repo de tu equipo y repartir los archivos.

## Preparar el entorno

Requiere Python 3.11 a 3.13, Git y acceso a GitHub Copilot.
Usa Python 3.12 durante el taller y ejecuta los comandos en Bash. En Windows, abre Git Bash.

```bash
python -m venv .venv
if [ -f .venv/Scripts/activate ]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi
python -m pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
```

Si en macOS o Linux tu instalación se llama `python3.12`, úsala para crear el entorno. Una vez activado, ejecuta `python`.

Instala [Copilot CLI](https://github.com/features/copilot/cli), abre `copilot` y ejecuta `/login`.
El SDK usa esa sesión con `COPILOT_USE_LOGGED_IN_USER=true`.
El modelo predeterminado es `gpt-6-luna` con esfuerzo `high`. Cada llamada consume uso del plan de Copilot.
Puedes descargar su runtime antes del taller con `python -m copilot download-runtime`.

## Conectar el backlog

Configura `.env` con el owner y repo del producto de tu equipo, `PROJECTS_MCP_URL`
y `PROJECTS_MCP_API_KEY`. Estos valores apuntan al servicio MCP del taller.
El repo del producto contiene el backlog; este repo contiene el código del Crew.

Si usas el MCP local del Lab 4, levántalo en otra terminal desde
`support/mcp-local` con el script `start-mcp.sh`.
Ese servicio requiere la imagen `localhost/mcp-github-project-manager:latest`, preparada por el instructor, y Podman o Docker. Si no tienes esa imagen, solicita al instructor un endpoint MCP del taller.
En macOS o Linux:

```sh
cd support/mcp-local
gh auth refresh -s project
bash start-mcp.sh --owner TU_OWNER --repo TU_PRODUCTO
```

Mantén esa terminal Bash abierta y ejecuta `python main.py` en otra terminal desde la raíz del repo. La URL de S1 es `http://localhost:8081`.

## Ejecutar el Crew

Desde la raíz de este repo, con el entorno virtual activado:

```sh
python main.py
```

Al iniciar, `main.py` pide el repositorio de destino: primero lista las carpetas de participante
dentro de `Documents` (por ejemplo `T52415-Samuel-Luis-Mendoza`) y después los repositorios de la
carpeta elegida. Cuando todos los pasos quedan aprobados, copia el contenido de `output/` en la raíz
de ese repositorio (sin `.checkpoint.json` ni `node_modules`). Para saltar la selección, define
`WALLEE_TARGET_REPO` con la ruta del repositorio; `WALLEE_DOCUMENTS_DIR` cambia la carpeta raíz.

Selecciona el proyecto y la funcionalidad. Cada paso ejecuta un mini-Crew de un agente.
En la aprobación humana puedes usar `s` para aprobar, `r` para reintentar con feedback,
o `n` para rechazar y detener el flujo. El checkpoint permite retomar los pasos aprobados.

Los artefactos se guardan en `output/`:

- `specs/product_owner_report.md`: alcance y criterios de aceptación.
- `specs/architect_report.md`: solución, módulos y contrato de API.
- `specs/ai_engineer_1_report.md` y `specs/ai_engineer_2_report.md`: implementaciones de backend y de frontend/agente.
- `specs/qa_security_report.md`: casos, tests, comandos y hallazgos de seguridad. Los resultados quedan pendientes de ejecución humana.
- `specs/presenter_report.md`: evidencia y guion del pitch.
- `backend-nestjs/` y `frontend-react/`: código extraído y configuración de arranque.
- `.checkpoint.json`: estado local de la ejecución.

## Probar la solución generada

Con Node.js 18.19 o superior y npm, abre una terminal en `output/backend-nestjs`:

```sh
npm install
npm test
npm run start:dev
```

Abre otra terminal en `output/frontend-react`:

```sh
npm install
npm test
npm run dev
```

La API se inicia en `http://localhost:3000` y React (Vite) en `http://localhost:5173`.
Los AI Engineers deben emitir `app.module.ts` y `App.tsx`; si faltan, el proyecto no arranca.
Revisa los comandos adicionales del informe de pruebas y registra sus resultados reales.

## Verificar cambios en los agentes

```sh
python tools/verify.py
```

Los checks recorren los seis roles, verifican artefactos, contexto y reanudación.
Sustituyen las llamadas al modelo y a MCP para ejecutarse sin credenciales.
La ejecución real de Copilot y MCP requiere el entorno del taller.

Consulta [SOURCE.md](SOURCE.md) para ver el origen de esta copia.
