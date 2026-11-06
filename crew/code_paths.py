"""Decide dónde se guarda cada archivo de código que emite el AI Engineer (NestJS + React)."""
import re
import unicodedata
from pathlib import PurePosixPath

from crew.scaffold import BACKEND_DIR, FRONTEND_DIR

FILENAME_PATTERN = r"[a-zA-Z0-9_.\-/]+\.(?:tsx|ts|html|css|sql|json|md)(?![a-zA-Z0-9_])"

_FRONT_EVIDENCE = re.compile(
    r"""['"](?:react(?:-dom|-router-dom)?(?:/[\w-]+)?|vitest|@testing-library/[\w-]+)['"]|import\.meta\.env"""
)
_BACK_EVIDENCE = re.compile(r"@nestjs/|typeorm|class-validator")
_BACK_NAME = re.compile(r"\.(?:controller|module|entity|dto|guard|pipe|filter|strategy|repository|spec|e2e-spec)\.ts$")
_JSX = re.compile(r"</?[A-Za-z][^>\n]*>|<>|</>")
_DECLARATION = re.compile(
    r"export\s+(?:default\s+)?(?:abstract\s+)?(?:class|interface|enum|type|function|const)\s+(\w+)"
)
_BACK_SUFFIXES = ("Controller", "Service", "Module", "Guard", "Pipe", "Filter", "Interceptor",
                  "Strategy", "Repository", "Entity", "Dto")
_FRONT_ROOT_FILES = {"main.tsx", "App.tsx", "index.css", "setupTests.ts"}


def feature_slug(title: str) -> str:
    folded = unicodedata.normalize("NFKD", str(title or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", folded.lower()).strip("-") or "feature"


def _kebab(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "-", name).lower()


def detect_side(name: str, code: str) -> str:
    """Devuelve 'backend' o 'frontend' según extensión, nombre e imports del código."""
    if name.lower().endswith((".tsx", ".css", ".html")):
        return "frontend"
    if _FRONT_EVIDENCE.search(code):
        return "frontend"
    if _BACK_EVIDENCE.search(code) or _BACK_NAME.search(name):
        return "backend"
    return "frontend"


def guess_filename(code: str) -> str | None:
    """Deduce un nombre cuando el bloque no lo declara."""
    upper = code.upper()
    if "CREATE TABLE" in upper:
        return "schema.sql"
    if "INSERT INTO" in upper:
        return "seed.sql"
    found = _DECLARATION.search(code)
    if not found:
        return None
    name = found.group(1)
    if detect_side("", code) == "backend":
        for suffix in _BACK_SUFFIXES:
            if name.endswith(suffix) and len(name) > len(suffix):
                return f"{_kebab(name[:-len(suffix)])}.{suffix.lower()}.ts"
        return f"{_kebab(name)}.ts"
    return f"{name}.tsx" if _JSX.search(code) else f"{name}.ts"


def _pick_folder(folders: tuple, raw: str) -> str:
    """Carpeta declarada que mejor describe el archivo: por nombre, por tipo de prueba o la primera."""
    low = raw.lower()
    for folder in folders:
        if folder.lower() in low:
            return folder
    if re.search(r"test|spec", low):
        for folder in folders:
            if "test" in folder.lower():
                return folder
    return folders[0]


def resolve_destination(target: str, code: str, slug: str, folders: tuple | None = None) -> str | None:
    """Ruta relativa a output/ para el archivo, o None si no es segura o no se reconoce.

    Con `folders` (las carpetas de salida que declara el prompt del rol), el resultado siempre cae
    dentro de ellas: lo que ya apunta a una carpeta declarada se conserva y el resto se reubica.
    """
    raw = str(target or "").strip().replace("\\", "/")
    while raw.startswith("./"):
        raw = raw[2:]
    if raw.startswith("output/"):
        raw = raw[len("output/"):]
    parts = PurePosixPath(raw).parts
    if not parts or raw.startswith("/") or ".." in parts or any(":" in part for part in parts):
        return None
    if not folders:
        return _legacy_destination(raw, parts, code, slug)
    if parts[0] in folders:
        return raw if len(parts) > 1 else None
    dest = _legacy_destination(raw, parts, code, slug)
    if dest is None or PurePosixPath(dest).parts[0] in folders:
        return dest
    return f"{_pick_folder(folders, raw)}/{dest}"


def _legacy_destination(raw: str, parts: tuple, code: str, slug: str) -> str | None:
    name = parts[-1]
    ext = name.rsplit(".", 1)[-1].lower()
    if ext == "md":
        return None  # los .md solo se guardan dentro de una carpeta declarada por el rol
    if ext == "sql":
        return f"db/{name}"
    if parts[0] in (BACKEND_DIR, FRONTEND_DIR):
        return raw if len(parts) > 1 else None
    if ext == "json":
        return None  # package.json y tsconfig solo se aceptan con la ruta del proyecto explícita

    side = detect_side(name, code)
    root = BACKEND_DIR if side == "backend" else FRONTEND_DIR
    if len(parts) > 1:
        return f"{root}/{raw}" if parts[0] in ("src", "test") else f"{root}/src/{raw}"

    if name == "index.html":
        return f"{FRONTEND_DIR}/index.html"
    if side == "backend":
        if name.endswith(".e2e-spec.ts"):
            return f"{root}/test/{name}"
        if name in ("main.ts", "app.module.ts"):
            return f"{root}/src/{name}"
        if name.endswith(".dto.ts"):
            return f"{root}/src/{slug}/dto/{name}"
        if name.endswith(".entity.ts"):
            return f"{root}/src/{slug}/entities/{name}"
        return f"{root}/src/{slug}/{name}"
    if name in _FRONT_ROOT_FILES:
        return f"{root}/src/{name}"
    return f"{root}/src/{slug}/{name}"
