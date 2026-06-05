from specimen.paths.specimen_paths import (
    spaces_dir,
    runtime_dir,
    temp_dir,
    logs_dir,
    active_json,
    specimen_dir,
    specimen_bin,
    specimen_tmp,
    specimen_home,
    specimen_meta,
    specimen_config,
    specimen_cache,
    specimen_logs,
    specimen_config_json,
    specimen_state_json,
    specimen_tools_json,
    ensure_base_dirs,
)
import specimen.paths.specimen_paths as _paths

def __getattr__(name: str):
    """Dynamically delegates to the paths module."""
    return getattr(_paths, name)

