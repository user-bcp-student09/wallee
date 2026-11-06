"""Selección del repositorio de destino y copia de output/ al terminar."""

import os
import re
import shutil
from pathlib import Path

from crew import ui
from crew.qa_sections import has_section, is_accumulating, merge_section
from crew.scaffold import BACKEND_DIR, FRONTEND_DIR

# Carpetas de participante: T52415-Samuel-Luis-Mendoza, u17721-gladys-patino-abanto, ...
PARTICIPANT_PATTERN = re.compile(r"^[A-Za-z]\d{3,}(-[A-Za-z0-9]+)+$")
SKIPPED_OUTPUT_FILES = {".checkpoint.json"}
SKIPPED_OUTPUT_DIRS = {"node_modules", "dist"}
SCAFFOLD_DIRS = {BACKEND_DIR, FRONTEND_DIR}
OWN_LAYOUT_DIRS = ("backend", "frontend")


def documents_root(start: Path | None = None) -> Path:
    """Carpeta Documents: WALLEE_DOCUMENTS_DIR, el ancestro 'Documents' de start o ~/Documents."""
    override = os.getenv("WALLEE_DOCUMENTS_DIR")
    if override:
        return Path(override).expanduser()
    for parent in (start or Path(__file__).resolve()).parents:
        if parent.name.lower() == "documents":
            return parent
    return Path.home() / "Documents"


def list_participant_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        (p for p in root.iterdir() if p.is_dir() and PARTICIPANT_PATTERN.match(p.name)),
        key=lambda p: p.name.lower(),
    )


def list_repo_dirs(parent: Path, exclude: Path | None = None) -> list[Path]:
    excluded = exclude.resolve() if exclude else None
    return sorted(
        (
            p for p in parent.iterdir()
            if p.is_dir() and not p.name.startswith(".") and p.resolve() != excluded
        ),
        key=lambda p: p.name.lower(),
    )


def _choose(title: str, options: list[Path], ask=ui.prompt) -> Path:
    ui.heading(title)
    for i, option in enumerate(options, 1):
        ui.option(i, option.name)
    while True:
        sel = ask(f"Selecciona el número (1-{len(options)}): ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(options):
            return options[int(sel) - 1]
        ui.error("Entrada inválida.")


def select_target_repo(source_repo: Path, ask=ui.prompt) -> Path:
    """Pide la carpeta del participante y luego el repositorio donde se copiará la salida."""
    override = os.getenv("WALLEE_TARGET_REPO")
    if override:
        target = Path(override).expanduser()
        if not target.is_dir():
            raise SystemExit(f"✗ WALLEE_TARGET_REPO no es una carpeta válida: {target}")
        ui.success(f"Repositorio de salida (WALLEE_TARGET_REPO): {target}")
        return target

    root = documents_root(source_repo)
    participants = list_participant_dirs(root)
    if not participants:
        raise SystemExit(
            f"✗ No se encontraron carpetas de participante en {root}. "
            "Define WALLEE_TARGET_REPO o WALLEE_DOCUMENTS_DIR."
        )

    participant = _choose(f"Carpetas en {root}:", participants, ask)
    repos = list_repo_dirs(participant, exclude=source_repo)
    if not repos:
        raise SystemExit(f"✗ No hay repositorios dentro de {participant}.")

    target = _choose(
        f"Perfecto, confirma el repositorio de salida. Listado de {participant.name}:",
        repos,
        ask,
    )
    ui.success(f"La salida se copiará en: {target}")
    return target


def has_own_layout(target_repo: Path) -> bool:
    """True si el destino ya tiene su propio backend/ o frontend/ (por ejemplo wallee-app)."""
    return any((target_repo / name).is_dir() for name in OWN_LAYOUT_DIRS)


def copy_output(output_dir: Path, target_repo: Path, qa_section: tuple[str, str] | None = None,
                replace_qa_section: bool = True) -> list[Path]:
    """Copia output/ en la raíz del repositorio destino (fusiona, sobrescribe, omite el checkpoint).

    Si el destino ya tiene backend/ o frontend/, no copia el andamiaje backend-nestjs/ y frontend-react/
    para no crear carpetas duplicadas junto a las suyas.

    Con `qa_section=(clave, título)`, los informes de QA no se sobrescriben: se agrega o actualiza solo la sección
    de ese feature. Con `replace_qa_section=False` una sección ya existente se conserva tal cual.
    """
    skipped_dirs = SCAFFOLD_DIRS if has_own_layout(target_repo) else set()
    copied: list[Path] = []
    omitted: set[str] = set()
    for src in sorted(output_dir.rglob("*")):
        rel = src.relative_to(output_dir)
        if not src.is_file() or rel.name in SKIPPED_OUTPUT_FILES or SKIPPED_OUTPUT_DIRS & set(rel.parts):
            continue
        if rel.parts[0] in skipped_dirs:
            omitted.add(rel.parts[0])
            continue
        dest = target_repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if qa_section and is_accumulating(rel):
            key, title = qa_section
            existing = dest.read_text(encoding="utf-8") if dest.is_file() else ""
            if replace_qa_section or not has_section(existing, key):
                dest.write_text(merge_section(existing, key, title, src.read_text(encoding="utf-8")),
                                encoding="utf-8")
                copied.append(rel)
            continue
        shutil.copy2(src, dest)
        copied.append(rel)
    if omitted:
        print(f"  Se omiten {', '.join(sorted(omitted))}/: {target_repo.name} ya tiene su propio backend/ o frontend/.")
    return copied
