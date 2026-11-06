"""Última selección del usuario (rol, cambio OpenSpec, repo destino y proyecto): se reconfirma en vez de preguntarla."""
import json
from pathlib import Path

from crew import ui

STATE_NAME = ".wallee-state.json"
USE, CHANGE = "use", "change"
KEYS = ("role", "role_label", "openspec_change", "target_repo", "project", "pr_repo")
_USE = ("", "s", "si", "sí", "y", "yes")
_CHANGE = ("c", "n", "no")


def load_state(path: Path) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {k: data[k] for k in KEYS if k in data} if isinstance(data, dict) else {}


def save_state(path: Path, state: dict) -> None:
    try:
        clean = {k: state[k] for k in KEYS if k in state}
        Path(path).write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"  ⚠ No se pudo guardar la selección: {exc}")


def has_selection(state: dict) -> bool:
    return bool(state.get("role"))


def describe(state: dict) -> list:
    change = state.get("openspec_change") if "openspec_change" in state else None
    return [
        f"Rol: {state.get('role_label') or state.get('role')}",
        f"Cambio OpenSpec: {change or 'ninguno'}",
        f"Repo destino: {state.get('target_repo') or '(se preguntará)'}",
        f"Proyecto: {(state.get('project') or {}).get('title') or '(se preguntará)'}",
    ]


def confirm_saved(state: dict, ask=ui.prompt) -> str:
    """Muestra la selección guardada. Devuelve USE (reutilizarla) o CHANGE (volver a elegir todo)."""
    ui.heading("Selección guardada de la última ejecución")
    for line in describe(state):
        print(f"  · {line}")
    while True:
        ans = ask("[Enter] continuar con esta selección · [c] cambiarla: ").strip().lower()
        if ans in _USE:
            return USE
        if ans in _CHANGE:
            return CHANGE
        ui.error("Opción inválida.")


def find_project(projects: list, saved: dict | None) -> dict | None:
    saved = saved or {}
    return next((p for p in projects if saved.get("id") and p.get("id") == saved["id"]), None)
