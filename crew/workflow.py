"""Orden de ejecución y activación explícita del séptimo perfil.

Los roles se cargan al usarlos (no al importar este módulo): importar los agentes tarda segundos.
"""
import os
from crew.roles import discover_roles


def _active(with_data: bool) -> tuple:
    return tuple(role for role in discover_roles() if with_data or role.KEY != "data")


def __getattr__(name):
    if name == "DATA_ROLES":
        return _active(True)
    if name == "ROLES":
        return _active(False)
    if name == "STEPS":
        return workflow_steps()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def include_data() -> bool:
    value = os.getenv("CREWAI_INCLUDE_DATA", "false").strip().lower()
    if value not in ("true", "false"):
        raise ValueError("CREWAI_INCLUDE_DATA debe ser true o false")
    return value == "true"


def workflow_steps(with_data=False, roles=None):
    return tuple((role.KEY, role.LABEL, role.agent, role.SPEC_FILE, role.EXTRACT_CODE)
                 for role in (roles or _active(with_data)))


def build_tasks(feature: dict, with_data=False, roles=None) -> dict:
    return {role.KEY: role.build_task(feature) for role in (roles or _active(with_data))}
