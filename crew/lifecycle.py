"""Ciclo de vida del item del backlog en el Project: Todo → In Progress (al empezar) → Done (al terminar, con confirmación)."""
import json
import os
import subprocess

import mcp_projects
from crew import ui

ICONS = {"Todo": "⚪", "In Progress": "🟡", "Done": "✅"}
_YES = ("", "s", "si", "sí", "y", "yes")
ERROR_CHARS = 200


def sync_enabled() -> bool:
    return os.getenv("WALLEE_PROJECT_SYNC", "true").strip().lower() != "false"


def status_of(item: dict) -> str:
    """Estado a mostrar: el del Project o, si no lo trae, el del issue (open/closed)."""
    return item.get("status") or ("Closed" if str(item.get("state", "")).lower() == "closed" else "Open")


def describe_item(item: dict) -> str:
    status = status_of(item)
    return f"{ICONS.get(status, '⚫' if status == 'Closed' else '🟢')} {status:<11}"


def _short(exc: Exception) -> str:
    text = " ".join(str(exc).split())
    return text if len(text) <= ERROR_CHARS else text[:ERROR_CHARS] + "…"


def _gh_graphql(query: str, **variables: str) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        args += ["-f", f"{key}={value}"]
    try:
        done = subprocess.run(args, capture_output=True, check=False)
    except OSError as exc:
        raise RuntimeError(f"no se pudo ejecutar gh: {exc}") from exc
    out = done.stdout.decode("utf-8", "replace")
    if done.returncode:
        detail = done.stderr.decode("utf-8", "replace").strip() or out.strip()
        raise RuntimeError(detail or f"gh terminó con código {done.returncode}")
    return json.loads(out)


def _gh_set(project_id: str, item_id: str, status: str) -> None:
    field = _gh_graphql(
        'query($id:ID!){ node(id:$id){ ... on ProjectV2 { field(name:"Status"){ '
        '... on ProjectV2SingleSelectField { id options{ id name } } } } } }', id=project_id,
    )["data"]["node"]["field"]
    option = next((o["id"] for o in field["options"] if o["name"] == status), None)
    if option is None:
        raise RuntimeError(f"el campo Status no tiene la opción '{status}'")
    _gh_graphql(
        "mutation($p:ID!,$i:ID!,$f:ID!,$o:String!){ updateProjectV2ItemFieldValue(input:"
        "{projectId:$p,itemId:$i,fieldId:$f,value:{singleSelectOptionId:$o}}){ projectV2Item{ id } } }",
        p=project_id, i=item_id, f=field["id"], o=option,
    )


def set_status(project_id: str, item_id: str, status: str) -> str | None:
    """Cambia el estado del item. Prueba el MCP y, si falla, la API de GitHub con gh. Devuelve None si salió bien o el error."""
    errors = []
    for name, update in (("MCP", mcp_projects.set_item_status), ("gh", _gh_set)):
        try:
            update(project_id, item_id, status)
            return None
        except Exception as exc:  # cualquier fallo de red/permisos pasa al siguiente intento
            errors.append(f"{name}: {_short(exc)}")
    return " | ".join(errors)


def _apply(project: dict, item: dict, status: str) -> bool:
    error = set_status(project["id"], item["id"], status)
    if error:
        ui.error(f"No se pudo pasar '{item.get('title', '')}' a {status} en '{project.get('title', '')}'.")
        print(f"    {error}")
        print("    Revisa que tu clave del MCP o tu cuenta de gh tengan permiso de escritura en el proyecto, "
              "o cámbialo a mano en el tablero.")
        return False
    item["status"] = status
    ui.success(f"'{item.get('title', '')}' → {status} en '{project.get('title', '')}'")
    return True


def start_item(project: dict, item: dict) -> bool:
    """Al empezar: pasa a In Progress los items que están en Todo."""
    if not sync_enabled() or not item.get("id") or status_of(item) != "Todo":
        return False
    return _apply(project, item, "In Progress")


def finish_item(project: dict, item: dict, ask=ui.prompt) -> bool:
    """Al terminar el flujo: pregunta y pasa el item a Done."""
    if not sync_enabled() or not item.get("id") or status_of(item) == "Done":
        return False
    title = item.get("title", "")
    ans = ask(f"¿Marcar '{title}' como Done en '{project.get('title', '')}'? [Enter] sí · [n] no: ").strip().lower()
    if ans not in _YES:
        print("  El item no se modificó.")
        return False
    return _apply(project, item, "Done")
