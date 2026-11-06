"""Descubre los roles de agents/, lee sus carpetas de salida desde su prompt y pide cuál ejecutar."""
import importlib
import os
import pkgutil
import re

import agents
from crew import ui

ALL = "all"
ALL_LABEL = "Todos"
CANONICAL_ORDER = ("product_owner", "architect", "data", "ai_engineer_1", "ai_engineer_2", "qa_security", "presenter")
REQUIRED = ("KEY", "LABEL", "SPEC_FILE", "EXTRACT_CODE", "INSTRUCTIONS", "agent", "build_task")

# Líneas que el equipo edita en el prompt (INSTRUCTIONS) de cada rol.
OUTPUT_FOLDERS_LINE = re.compile(r"^\W*Carpetas de salida en /output:[ \t]*(.+)$", re.IGNORECASE | re.MULTILINE)
REPORT_FOLDER_LINE = re.compile(r"^\W*Carpeta del informe en /output:[ \t]*(.+)$", re.IGNORECASE | re.MULTILINE)
DEFAULT_REPORT_FOLDER = "specs"
_FOLDER = re.compile(r"^[A-Za-z0-9][\w.-]*$")


def discover_roles() -> tuple:
    """Módulos de agents/ que cumplen el contrato de rol, en el orden del flujo."""
    found = {}
    for info in pkgutil.iter_modules(agents.__path__):
        module = importlib.import_module(f"agents.{info.name}")
        if all(hasattr(module, name) for name in REQUIRED):
            found[module.KEY] = module
    known = [found[key] for key in CANONICAL_ORDER if key in found]
    extra = [found[key] for key in sorted(found) if key not in CANONICAL_ORDER]
    return tuple(known + extra)


def _folders(text: str) -> tuple:
    names = []
    for token in re.split(r"[,;\s]+", text):
        token = token.strip("`'\".*/")
        if _FOLDER.match(token) and token not in names:
            names.append(token)
    return tuple(names)


def output_folders(role) -> tuple | None:
    """Carpetas de /output declaradas en el prompt del rol; None si no declara ninguna."""
    found = OUTPUT_FOLDERS_LINE.search(role.INSTRUCTIONS)
    return (_folders(found.group(1)) or None) if found else None


def report_folder(role) -> str:
    found = REPORT_FOLDER_LINE.search(role.INSTRUCTIONS)
    names = _folders(found.group(1)) if found else ()
    return names[0] if names else DEFAULT_REPORT_FOLDER


def union_folders(roles) -> set:
    return {folder for role in roles for folder in (output_folders(role) or ())}


def choose_roles(all_roles, with_data: bool, ask=ui.prompt) -> tuple:
    """Pregunta qué rol ejecutar. Devuelve (roles_a_ejecutar, es_todos). WALLEE_ROLE omite la pregunta."""
    every = tuple(role for role in all_roles if with_data or role.KEY != "data")
    override = os.getenv("WALLEE_ROLE", "").strip().lower()
    if override:
        if override in (ALL, ALL_LABEL.lower()):
            return every, True
        for role in all_roles:
            if override in (role.KEY.lower(), role.LABEL.lower()):
                return (role,), False
        raise SystemExit(f"✗ WALLEE_ROLE '{override}' no existe. Usa all o uno de: "
                         + ", ".join(role.KEY for role in all_roles))

    ui.heading("Selecciona el rol que desea ejecutar.")
    for i, role in enumerate(all_roles, 1):
        folders = ", ".join(output_folders(role) or ()) or "sin carpetas declaradas"
        optional = " (opcional, activo en Todos con CREWAI_INCLUDE_DATA=true)" if role.KEY == "data" else ""
        ui.option(i, f"{role.LABEL} → /output: {folders}{optional}")
    ui.option(len(all_roles) + 1, f"{ALL_LABEL} ({' → '.join(role.LABEL for role in every)})")
    while True:
        sel = ask(f"Selecciona el número (1-{len(all_roles) + 1}): ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(all_roles):
            return (all_roles[int(sel) - 1],), False
        if sel.isdigit() and int(sel) == len(all_roles) + 1:
            return every, True
        ui.error("Entrada inválida.")
