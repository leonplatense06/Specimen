import os
from pathlib import Path

def get_specimen_root() -> Path:
    """Retorna la raíz del directorio de Specimen, permitiendo sobrescribirla por entorno."""
    if "SPECIMEN_ROOT_DIR" in os.environ:
        return Path(os.environ["SPECIMEN_ROOT_DIR"])
    if "SPEC_USER_HOME" in os.environ:
        return Path(os.environ["SPEC_USER_HOME"]) / ".specimen"
    return Path.home() / ".specimen"

def spaces_dir() -> Path:
    return get_specimen_root() / "spaces"

def runtime_dir() -> Path:
    return get_specimen_root() / "runtime"

def temp_dir() -> Path:
    return get_specimen_root() / "temp"

def logs_dir() -> Path:
    return get_specimen_root() / "logs"

def active_json() -> Path:
    return runtime_dir() / "active.json"

# Definimos __getattr__ para evaluación dinámica de constantes de módulo (retrocompatibilidad)
def __getattr__(name: str) -> Path:
    if name == "SPECIMEN_ROOT":
        return get_specimen_root()
    elif name == "SPACES_DIR":
        return spaces_dir()
    elif name == "RUNTIME_DIR":
        return runtime_dir()
    elif name == "TEMP_DIR":
        return temp_dir()
    elif name == "LOGS_DIR":
        return logs_dir()
    elif name == "ACTIVE_JSON":
        return active_json()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

def specimen_dir(name: str) -> Path:
    return spaces_dir() / name.lower()

def specimen_bin(name: str) -> Path:
    return specimen_dir(name) / "bin"

def specimen_tmp(name: str) -> Path:
    return specimen_dir(name) / "tmp"

def specimen_home(name: str) -> Path:
    return specimen_dir(name) / "home"

def specimen_meta(name: str) -> Path:
    return specimen_dir(name) / "meta"

def specimen_config(name: str) -> Path:
    return specimen_dir(name) / "config"

def specimen_cache(name: str) -> Path:
    return specimen_dir(name) / "cache"

def specimen_logs(name: str) -> Path:
    return specimen_dir(name) / "logs"

def specimen_config_json(name: str) -> Path:
    return specimen_meta(name) / "config.json"

def specimen_state_json(name: str) -> Path:
    return specimen_meta(name) / "state.json"

def specimen_tools_json(name: str) -> Path:
    return specimen_meta(name) / "tools.json"

def ensure_base_dirs() -> None:
    """Asegura que existan los directorios base globales del sistema Specimen."""
    spaces_dir().mkdir(parents=True, exist_ok=True)
    runtime_dir().mkdir(parents=True, exist_ok=True)
    temp_dir().mkdir(parents=True, exist_ok=True)
    logs_dir().mkdir(parents=True, exist_ok=True)
