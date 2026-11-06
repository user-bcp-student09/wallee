"""Publica lo copiado a output/: rama, commit, push y PR con un paso de preaprobación humana."""
import os
import re
import shutil
import subprocess
from pathlib import Path

from crew import ui
from crew.code_paths import feature_slug

TEMPLATES = (".github/pull_request_template.md", "pull_request_template.md", "docs/pull_request_template.md")
PREVIEW_LINES = 40
FILES_IN_BODY = 40
FALLBACK_BASES = ("main", "master")
DEFAULT_PR_REPO = "user-bcp-student17/wallee-app"
_REPO_RE = re.compile(r"^[\w.-]+/[\w.-]+$")
_GITHUB_URL_RE = re.compile(r"github\.com[:/]+([\w.-]+)/([\w.-]+?)(?:\.git)?/?$", re.IGNORECASE)


class PublishError(Exception):
    pass


def _run(program: str, repo: Path, *args: str, input: str | bytes | None = None) -> str:
    data = input.encode("utf-8") if isinstance(input, str) else input
    try:
        done = subprocess.run([program, *args], cwd=repo, input=data, capture_output=True, check=False)
    except OSError as exc:
        raise PublishError(f"no se pudo ejecutar {program}: {exc}") from exc
    if done.returncode:
        detail = done.stderr.decode("utf-8", "replace").strip()
        raise PublishError(f"{program} {' '.join(args[:2])} falló: {detail or done.returncode}")
    return done.stdout.decode("utf-8", "replace")


def git(repo: Path, *args: str, input=None) -> str:
    return _run("git", repo, *args, input=input).strip()


def gh(repo: Path, *args: str, input=None) -> str:
    return _run("gh", repo, *args, input=input).strip()


def gh_available() -> bool:
    return shutil.which("gh") is not None


def default_base(repo: Path) -> str:
    try:
        return git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").split("/", 1)[1]
    except (PublishError, IndexError):
        pass
    for name in FALLBACK_BASES:
        try:
            git(repo, "rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{name}")
            return name
        except PublishError:
            continue
    return FALLBACK_BASES[0]


def parse_github_repo(value: str) -> str | None:
    """'owner/repo' a partir de 'owner/repo' o de una URL https/ssh de GitHub; None si no se reconoce."""
    value = value.strip()
    if _REPO_RE.match(value) and "github.com" not in value:
        return value.removesuffix(".git")
    found = _GITHUB_URL_RE.search(value)
    return f"{found.group(1)}/{found.group(2)}" if found else None


def ask_pr_repo(saved: str | None, ask=ui.prompt) -> str:
    """Pide el repo donde se abrirá el PR; Enter acepta el guardado (o el predeterminado)."""
    default = saved or DEFAULT_PR_REPO
    while True:
        answer = ask(f"Repo destino del PR (owner/repo) [{default}]: ").strip()
        if not answer:
            return default
        repo = parse_github_repo(answer)
        if repo:
            return repo
        ui.error("Formato inválido. Usa owner/repo o la URL del repo en GitHub.")


def _repo_base(target: Path, repo: str, origin_repo: str | None) -> str:
    if origin_repo and origin_repo.lower() == repo.lower():
        return default_base(target)
    try:
        return gh(target, "repo", "view", repo, "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name") or default_base(target)
    except PublishError:
        return default_base(target)


def _free_branch(repo: Path, wanted: str) -> str:
    name, n = wanted, 2
    while True:
        try:
            git(repo, "rev-parse", "--verify", "--quiet", f"refs/heads/{name}")
        except PublishError:
            return name
        name, n = f"{wanted}-{n}", n + 1


def pr_template(repo: Path) -> str:
    for relative in TEMPLATES:
        path = repo / relative
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace").strip()
    return ""


def build_pr_body(feature: dict, role_labels, change: str | None, files, approved, template: str = "") -> str:
    shown = [f"- `{Path(f).as_posix()}`" for f in files[:FILES_IN_BODY]]
    if len(files) > FILES_IN_BODY:
        shown.append(f"- … y {len(files) - FILES_IN_BODY} archivos más")
    lines = [
        "## Resumen generado por Wallee",
        f"- **Feature:** {feature.get('title', '')}",
        f"- **Rol(es):** {', '.join(role_labels)}",
        f"- **Cambio OpenSpec:** {change or 'ninguno'}",
        f"- **Archivos:** {len(files)}",
        "",
        "## Revisión humana (HITL)",
        *[f"- [x] {label}: aprobado por una persona antes de guardar" for label in approved],
        "- [ ] Revisé el código generado; los criterios de aceptación y las tareas de OpenSpec no se dan por cumplidos hasta validarlos",
        "",
        "## Archivos incluidos",
        *shown,
    ]
    body = "\n".join(lines)
    return f"{template}\n\n---\n\n{body}" if template else body


def _preview(base, branch, title, body, draft, files, repo=None):
    ui.heading("Preaprobación del Pull Request")
    if repo:
        print(f"  Repo    : {repo}")
    print(f"  Destino : {base} ← {branch}")
    print(f"  Título  : {title}")
    print(f"  Tipo    : {'borrador (draft)' if draft else 'listo para revisión'}")
    print(f"  Archivos: {len(files)}")
    print("  ── Descripción ──")
    body_lines = body.splitlines()
    for line in body_lines[:PREVIEW_LINES]:
        print(f"  {line}")
    if len(body_lines) > PREVIEW_LINES:
        print(f"  … ({len(body_lines) - PREVIEW_LINES} líneas más)")


def preapprove(base, branch, title, body, files, ask=ui.prompt, repo=None) -> tuple:
    """Muestra el PR y pide la decisión. Devuelve (decisión 's'|'n', título, borrador)."""
    draft = False
    while True:
        _preview(base, branch, title, body, draft, files, repo)
        ans = ask("¿Crear el PR? [s] sí · [d] alternar borrador · [e] editar título · [n] no crear: ").strip().lower()
        if ans in ("s", "n"):
            return ans, title, draft
        if ans == "d":
            draft = not draft
        elif ans == "e":
            title = ask("Nuevo título: ").strip() or title
        else:
            ui.error("Opción inválida.")


def publish_output(target: Path, files, feature: dict, role_labels, change: str | None = None,
                   approved=(), ask=ui.prompt, pr_repo: str | None = None, on_pr_repo=None) -> str | None:
    """Commit + push de lo copiado y PR tras preaprobación. Devuelve la URL del PR o None.

    El push va a `origin`; el PR se abre en el repo que se pide aquí (pr_repo es el guardado, por defecto
    DEFAULT_PR_REPO) y se informa a on_pr_repo para guardarlo. Nunca lanza: el output ya está copiado y un
    fallo aquí solo se informa. WALLEE_PUBLISH=false lo desactiva.
    """
    if os.getenv("WALLEE_PUBLISH", "true").strip().lower() == "false":
        ui.success("Publicación omitida (WALLEE_PUBLISH=false).")
        return None
    try:
        return _publish(Path(target), [Path(f) for f in files], feature, list(role_labels), change, list(approved), ask,
                        pr_repo, on_pr_repo)
    except PublishError as exc:
        ui.error(f"No se pudo publicar: {exc}")
        print(f"  El output ya está copiado en {target}; puedes commitear y abrir el PR a mano.")
        return None


def _publish(target, files, feature, role_labels, change, approved, ask, pr_repo=None, on_pr_repo=None):
    try:
        git(target, "rev-parse", "--is-inside-work-tree")
    except PublishError:
        raise PublishError("el repositorio de destino no es un repo git") from None
    if not gh_available():
        raise PublishError("falta GitHub CLI (gh); instálalo y ejecuta `gh auth login`")
    origin_repo = parse_github_repo(git(target, "remote", "get-url", "origin"))
    current = git(target, "branch", "--show-current")
    if not current:
        raise PublishError("el repositorio de destino está en HEAD desacoplado")

    names = "\0".join(f.as_posix() for f in files).encode("utf-8")
    try:
        git(target, "add", "--pathspec-from-file=-", "--pathspec-file-nul", input=names)
    except PublishError:
        pass  # rutas ignoradas por .gitignore: se publica solo lo que sí quedó en el índice
    staged = git(target, "diff", "--cached", "--name-only", "--", *[f.as_posix() for f in files]).splitlines()
    if not staged:
        ui.success("No hay cambios nuevos que publicar: el output ya coincide con el repositorio.")
        return None

    suffix = "all" if len(role_labels) > 1 else feature_slug(role_labels[0])
    repo = ask_pr_repo(pr_repo, ask)
    if on_pr_repo:
        on_pr_repo(repo)
    base = _repo_base(target, repo, origin_repo)
    branch = current
    if current in (base, default_base(target)):
        branch = _free_branch(target, f"wallee/{suffix}-{feature_slug(feature.get('title', ''))}"[:80].rstrip("-"))
        git(target, "checkout", "-b", branch)
    title = f"[{', '.join(role_labels) if len(role_labels) < 3 else 'Wallee'}] {feature.get('title', 'feature')}"
    git(target, "commit", "-m", title, "-m", f"OpenSpec: {change or 'ninguno'}", "--", *staged)
    git(target, "push", "-u", "origin", branch)
    ui.success(f"Push realizado a origin/{branch}")

    body = build_pr_body(feature, role_labels, change, staged, approved, pr_template(target))
    decision, title, draft = preapprove(base, branch, title, body, staged, ask, repo)
    if decision == "n":
        print(f"  PR no creado. La rama origin/{branch} quedó publicada; puedes abrirlo luego con `gh pr create --repo {repo}`.")
        return None
    cross_repo = origin_repo and origin_repo.lower() != repo.lower()
    head = f"{origin_repo.split('/')[0]}:{branch}" if cross_repo else branch
    args = ["pr", "create", "--repo", repo, "--base", base, "--head", head, "--title", title, "--body-file", "-"]
    if draft:
        args.append("--draft")
    url = (gh(target, *args, input=body).splitlines() or [""])[-1]
    ui.success(f"Pull Request creado: {url}")
    return url
