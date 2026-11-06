"""Salida de consola con color (rich) y degradación a texto plano."""

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich import box
    _console = Console()
except ImportError:  # sin rich: texto plano
    _console = None

_BANNER = (
    "██╗    ██╗ █████╗ ██╗     ██╗     ███████╗███████╗",
    "██║    ██║██╔══██╗██║     ██║     ██╔════╝██╔════╝",
    "██║ █╗ ██║███████║██║     ██║     █████╗  █████╗  ",
    "██║███╗██║██╔══██║██║     ██║     ██╔══╝  ██╔══╝  ",
    "╚███╔███╔╝██║  ██║███████╗███████╗███████╗███████╗",
    " ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝",
)
_GRADIENT = ("#00d4ff", "#00b4ff", "#4f8cff", "#8a6cff", "#b44fff", "#e040fb")
TAGLINE = "Wallee App  ·  Billetera digital para Perú  ·  BCP AI Lab"


def banner() -> None:
    if _console is None:
        print("\n" + "\n".join(_BANNER) + f"\n{TAGLINE}\n")
        return
    art = Text(justify="center")
    for line, color in zip(_BANNER, _GRADIENT):
        art.append(line + "\n", style=f"bold {color}")
    art.append(TAGLINE, style="italic bright_white")
    _console.print()
    _console.print(
        Align.center(Panel(art, box=box.DOUBLE, border_style="#4f8cff", padding=(1, 4), expand=False))
    )
    _console.print()


def heading(text: str) -> None:
    if _console is None:
        print(f"\n{text}")
    else:
        _console.print(f"\n[bold bright_cyan]❯ {text}[/]")


def option(number: int, label: str) -> None:
    if _console is None:
        print(f"  {number} - {label}")
    else:
        _console.print(f"  [bold magenta]{number}[/] [dim]-[/] [bright_white]{label}[/]")


def success(text: str) -> None:
    if _console is None:
        print(f"\n✔ {text}")
    else:
        _console.print(f"\n[bold green]✔[/] {text}")


def error(text: str) -> None:
    if _console is None:
        print(f"  ✗ {text}")
    else:
        _console.print(f"  [bold red]✗ {text}[/]")


def prompt(text: str) -> str:
    if _console is None:
        return input(f"\n{text}")
    return _console.input(f"\n[bold yellow]?[/] [bold]{text}[/]")
