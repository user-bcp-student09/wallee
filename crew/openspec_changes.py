"""Gestión de cambios con OpenSpec: lista los cambios activos, pide cuál usar y lo entrega como contexto por rol."""
import os
import re
from dataclasses import dataclass
from pathlib import Path

from crew import ui

NONE_LABEL = "Sin cambio OpenSpec"
SECTION_CHARS = 6000
DESIGN_CHARS = 3000
_TASK = re.compile(r"^\s*-\s*\[([ xX])\]\s*(.*)$")
_TASK_ID = re.compile(r"^(\d+(?:\.\d+)+)\b")
_ROLE_TAG = re.compile(r"\[rol:\s*([^\]]+)\]", re.IGNORECASE)


@dataclass(frozen=True)
class Change:
    name: str
    path: Path
    done: int
    total: int


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def _task_lines(change_path: Path) -> list:
    try:
        text = (change_path / "tasks.md").read_text(encoding="utf-8")
    except OSError:
        return []
    return [m for m in (_TASK.match(line) for line in text.splitlines()) if m]


def list_changes(base: Path) -> list:
    """Cambios activos de openspec/changes (sin archive), igual que `openspec list`."""
    changes_dir = Path(base) / "openspec" / "changes"
    if not changes_dir.is_dir():
        return []
    result = []
    for path in sorted(changes_dir.iterdir()):
        if not path.is_dir() or path.name == "archive" or path.name.startswith("."):
            continue
        tasks = _task_lines(path)
        result.append(Change(path.name, path, sum(m.group(1) in "xX" for m in tasks), len(tasks)))
    return result


def find_change(base: Path, name: str | None) -> Change | None:
    return next((change for change in list_changes(base) if change.name == name), None)


def select_change(base: Path, ask=ui.prompt) -> Change | None:
    """Pide el cambio OpenSpec de trabajo. WALLEE_OPENSPEC_CHANGE (nombre o none) omite la pregunta."""
    changes = list_changes(base)
    override = os.getenv("WALLEE_OPENSPEC_CHANGE", "").strip()
    if override:
        if override.lower() in ("none", "ninguno"):
            return None
        for change in changes:
            if change.name == override:
                return change
        raise SystemExit(f"✗ WALLEE_OPENSPEC_CHANGE '{override}' no existe en openspec/changes.")
    if not changes:
        ui.error("No hay cambios activos en openspec/changes; se continúa sin OpenSpec.")
        return None

    ui.heading("Selecciona el cambio OpenSpec de trabajo (equivale a `openspec list`).")
    for i, change in enumerate(changes, 1):
        ui.option(i, f"{change.name}  {change.done}/{change.total} tasks")
    ui.option(len(changes) + 1, NONE_LABEL)
    while True:
        sel = ask(f"Selecciona el número (1-{len(changes) + 1}): ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(changes):
            return changes[int(sel) - 1]
        if sel.isdigit() and int(sel) == len(changes) + 1:
            return None
        ui.error("Entrada inválida.")


def _read(path: Path, limit: int) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    return text if len(text) <= limit else text[:limit] + "\n...(truncado)"


def role_tasks(change: Change, aliases) -> list:
    """Tareas de tasks.md cuyo `[rol: ...]` menciona al rol, como (id, hecha, texto)."""
    wanted = [_norm(alias) for alias in aliases if alias]
    found = []
    for m in _task_lines(change.path):
        tag = _ROLE_TAG.search(m.group(2))
        if not tag:
            continue
        tag_text = f" {_norm(tag.group(1))} "
        if any(f" {alias} " in tag_text for alias in wanted):
            identifier = _TASK_ID.match(m.group(2))
            found.append((identifier.group(1) if identifier else "", m.group(1) in "xX", m.group(2)))
    return found


def change_context(change: Change | None, role) -> str:
    """Bloque para la tarea del rol: propuesta, specs, diseño y las tareas que le corresponden."""
    if change is None:
        return ""
    parts = [f"\n\n---\n## Cambio OpenSpec activo: {change.name} ({change.done}/{change.total} tasks)\n"
             f"La gestión de cambios se hace en openspec/changes/{change.name}/. "
             "Respeta su alcance y marca como PENDIENTE lo que no cubra."]
    for label, path, limit in (("proposal.md", change.path / "proposal.md", SECTION_CHARS),
                               ("design.md", change.path / "design.md", DESIGN_CHARS)):
        text = _read(path, limit)
        if text:
            parts.append(f"### {label}\n{text}")
    for spec in sorted((change.path / "specs").rglob("spec.md")) if (change.path / "specs").is_dir() else []:
        text = _read(spec, SECTION_CHARS)
        if text:
            parts.append(f"### specs/{spec.parent.name}/spec.md\n{text}")
    tasks = role_tasks(change, (role.LABEL, role.KEY, role.KEY.replace("_", " ")))
    if tasks:
        lines = [f"- [{'x' if done else ' '}] {text}" for _, done, text in tasks]
        parts.append(f"### Tareas de {role.LABEL} en tasks.md\n" + "\n".join(lines)
                     + "\nCita el ID de la tarea (por ejemplo 2.2) que cubre cada entrega; "
                       "no marques tareas como hechas: eso lo valida el humano.")
    return "\n\n".join(parts)
