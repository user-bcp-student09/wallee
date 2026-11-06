"""Trabajos de red en segundo plano: se lanzan al inicio y se recogen cuando hacen falta."""
import threading


class Prefetch:
    def __init__(self):
        self._jobs = {}

    def start(self, key, fn, *args) -> None:
        job = {"done": threading.Event()}

        def work():
            try:
                job["value"] = fn(*args)
            except BaseException as exc:  # se relanza en get(), donde antes habría fallado la llamada directa
                job["error"] = exc
            finally:
                job["done"].set()

        self._jobs[key] = job
        threading.Thread(target=work, name=f"prefetch-{key}", daemon=True).start()

    def get(self, key, fn, *args):
        """Resultado del trabajo `key`; si no se lanzó, ejecuta fn(*args) en el momento."""
        job = self._jobs.pop(key, None)
        if job is None:
            return fn(*args)
        job["done"].wait()
        if "error" in job:
            raise job["error"]
        return job["value"]
