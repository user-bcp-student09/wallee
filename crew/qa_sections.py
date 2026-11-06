"""Documentos de QA acumulativos: una sección por feature dentro de cada archivo compartido."""

from datetime import datetime
from pathlib import Path
import re

QA_REPORT = Path("specs") / "qa_security_report.md"
QA_DOC_FOLDERS = ("test", "security")


def is_accumulating(rel: Path) -> bool:
    """Informes de QA que crecen con cada feature (los tests de código no se fusionan)."""
    rel = Path(rel)
    return rel == QA_REPORT or (rel.suffix.lower() == ".md" and len(rel.parts) > 1 and rel.parts[0] in QA_DOC_FOLDERS)


def reset_qa_documents(output_dir: Path) -> None:
    """Quita de output/ los documentos QA de ejecuciones anteriores: el repo destino ya conserva su acumulado."""
    output_dir = Path(output_dir)
    for folder in QA_DOC_FOLDERS:
        for path in (output_dir / folder).glob("**/*.md"):
            path.unlink()
    (output_dir / QA_REPORT).unlink(missing_ok=True)


def _markers(key: str) -> tuple[str, str]:
    return f"<!-- wallee-qa:begin {key} -->", f"<!-- wallee-qa:end {key} -->"


def _section_pattern(key: str) -> re.Pattern:
    begin, end = _markers(key)
    return re.compile(re.escape(begin) + r".*?" + re.escape(end), re.DOTALL)


def has_section(existing: str, key: str) -> bool:
    return bool(_section_pattern(key).search(existing))


def render_section(key: str, title: str, body: str) -> str:
    begin, end = _markers(key)
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    return f"{begin}\n## {title}\n\n_Actualizado: {stamp}_\n\n{body.strip()}\n{end}"


def merge_section(existing: str, key: str, title: str, body: str) -> str:
    """Reemplaza solo la sección de `key`; si no existe la agrega al final y conserva todo lo demás."""
    section = render_section(key, title, body)
    pattern = _section_pattern(key)
    if pattern.search(existing):
        return pattern.sub(lambda _: section, existing, count=1)
    base = existing.rstrip()
    return f"{base}\n\n{section}\n" if base else f"{section}\n"
