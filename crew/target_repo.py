"""Selección del repositorio de destino y copia de output/ al terminar."""

import os
import re
import shutil
from pathlib import Path

# Carpetas de participante: T52415-Samuel-Luis-Mendoza, u17721-gladys-patino-abanto, ...
PARTICIPANT_PATTERN = re.compile(r"^[A-Za-z]\d{3,}(-[A-Za-z0-9]+)+$")
SKIPPED_OUTPUT_FILES = {".checkpoint.json"}
SKIPPED_OUTPUT_DIRS = {"node_modules", "dist"}


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


def _choose(title: str, options: list[Path], ask=input) -> Path:
    print(f"\n{title}")
    for i, option in enumerate(options, 1):
        print(f"  {i} - {option.name}")
    while True:
        sel = ask(f"\nSelecciona el número [1-{len(options)}]: ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(options):
            return options[int(sel) - 1]
        print("  ✗ Entrada inválida.")


def select_target_repo(source_repo: Path, ask=input) -> Path:
    """Pide la carpeta del participante y luego el repositorio donde se copiará la salida."""
    override = os.getenv("WALLEE_TARGET_REPO")
    if override:
        target = Path(override).expanduser()
        if not target.is_dir():
            raise SystemExit(f"✗ WALLEE_TARGET_REPO no es una carpeta válida: {target}")
        print(f"\n[Destino] Repositorio de salida (WALLEE_TARGET_REPO): {target}")
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
        "Perfecto, confirma el repositorio de salida. Listado de "
        f"{participant.name}:",
        repos,
        ask,
    )
    print(f"\n[Destino] La salida se copiará en: {target}")
    return target


def copy_output(output_dir: Path, target_repo: Path) -> list[Path]:
    """Copia output/ en la raíz del repositorio destino (fusiona, sobrescribe, omite el checkpoint)."""
    copied: list[Path] = []
    for src in sorted(output_dir.rglob("*")):
        rel = src.relative_to(output_dir)
        if not src.is_file() or rel.name in SKIPPED_OUTPUT_FILES or SKIPPED_OUTPUT_DIRS & set(rel.parts):
            continue
        dest = target_repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(rel)
    return copied
