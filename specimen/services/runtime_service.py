import os
from datetime import datetime
from typing import Optional
from specimen.paths import active_json, ensure_base_dirs
from specimen.models.runtime import RuntimeState
from specimen.storage.json_storage import load_json, save_json

class RuntimeService:
    @staticmethod
    def get_runtime_state() -> RuntimeState:
        """Obtiene el estado de ejecución actual."""
        ensure_base_dirs()
        if not active_json().exists():
            return RuntimeState(None, None, None, None)
        try:
            return load_json(active_json(), RuntimeState)
        except Exception:
            # Retorna estado vacío si está corrupto o hay algún error
            return RuntimeState(None, None, None, None)

    @classmethod
    def save_runtime_state(cls, state: RuntimeState) -> None:
        """Guarda el estado de ejecución."""
        ensure_base_dirs()
        save_json(active_json(), state)

    @classmethod
    def clear_runtime_state(cls) -> None:
        """Limpia el estado de ejecución global."""
        cls.save_runtime_state(RuntimeState(None, None, None, None))

    @classmethod
    def is_process_alive(cls, pid: int) -> bool:
        """Verifica si un PID está vivo en Linux."""
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True

    @classmethod
    def get_active_specimen(cls, auto_cleanup: bool = True) -> Optional[str]:
        """
        Obtiene el nombre del specimen activo actual.
        Si hay un proceso registrado pero está muerto, realiza la limpieza automática (si auto_cleanup=True).
        """
        state = cls.get_runtime_state()
        if not state.active_specimen:
            return None
        
        if state.shell_pid is not None:
            if not cls.is_process_alive(state.shell_pid):
                if auto_cleanup:
                    cls.cleanup_stale_specimen(state.active_specimen)
                    return None
        return state.active_specimen

    @classmethod
    def cleanup_stale_specimen(cls, name: str) -> None:
        """Limpia un specimen que quedó activo pero su proceso murió."""
        from specimen.paths import specimen_state_json
        from specimen.models.state import SpecimenState
        
        state_path = specimen_state_json(name)
        if state_path.exists():
            try:
                spec_state = load_json(state_path, SpecimenState)
                spec_state.active = False
                spec_state.last_exited_at = datetime.now().isoformat()
                spec_state.exit_mode = None
                save_json(state_path, spec_state)
            except Exception:
                pass
        
        cls.clear_runtime_state()
