import shutil
from datetime import datetime
from typing import List, Tuple, Optional
from specimen.exceptions import (
    SpecimenActiveError,
    SpecimenNotFoundError,
    CloneSizeTooSmallError,
)
from specimen.models import SpecimenConfig, SpecimenState, ToolsConfig
from specimen.paths import (
    spaces_dir,
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
from specimen.storage.json_storage import load_json, save_json
from specimen.validators.specimen_validator import SpecimenValidator
from specimen.services.size_service import SizeService
from specimen.services.runtime_service import RuntimeService

class SpecimenService:
    @staticmethod
    def create_specimen(name: str, size_mb: int) -> SpecimenConfig:
        """Crea un nuevo specimen base con la estructura de directorios y metadata inicial."""
        # 1. Validar nombre y que no exista
        normalized_name = SpecimenValidator.validate_name(name, check_not_exists=True)
        # 2. Validar tamaño (entero positivo)
        validated_size = SpecimenValidator.validate_size(size_mb)
        
        # 3. Asegurar que existan los directorios base del sistema
        ensure_base_dirs()
        
        # 4. Verificar espacio libre en disco
        SizeService.validate_space_available(spaces_dir(), validated_size)
        
        # 5. Crear la estructura de directorios
        s_dir = specimen_dir(normalized_name)
        specimen_bin(normalized_name).mkdir(parents=True, exist_ok=True)
        specimen_tmp(normalized_name).mkdir(parents=True, exist_ok=True)
        specimen_home(normalized_name).mkdir(parents=True, exist_ok=True)
        specimen_config(normalized_name).mkdir(parents=True, exist_ok=True)
        specimen_cache(normalized_name).mkdir(parents=True, exist_ok=True)
        specimen_logs(normalized_name).mkdir(parents=True, exist_ok=True)
        specimen_meta(normalized_name).mkdir(parents=True, exist_ok=True)
        
        # 6. Crear metadata inicial
        now_str = datetime.now().isoformat()
        config = SpecimenConfig(
            name=normalized_name,
            type="base",
            parent=None,
            size_mb=validated_size,
            created_at=now_str,
            persistent=False
        )
        state = SpecimenState(
            active=False,
            last_entered_at=None,
            last_exited_at=None,
            exit_mode=None
        )
        tools = ToolsConfig(tools=[])
        
        save_json(specimen_config_json(normalized_name), config)
        save_json(specimen_state_json(normalized_name), state)
        save_json(specimen_tools_json(normalized_name), tools)
        
        return config

    @staticmethod
    def list_specimens() -> List[Tuple[SpecimenConfig, SpecimenState, int]]:
        """Lista todos los specimens existentes con su config, estado y tamaño real en MB."""
        ensure_base_dirs()
        result = []
        if not spaces_dir().exists():
            return result
            
        for path in spaces_dir().iterdir():
            if path.is_dir():
                name = path.name
                config_path = specimen_config_json(name)
                state_path = specimen_state_json(name)
                if config_path.exists() and state_path.exists():
                    try:
                        config = load_json(config_path, SpecimenConfig)
                        state = load_json(state_path, SpecimenState)
                        real_size = SizeService.get_specimen_size_mb(path)
                        result.append((config, state, real_size))
                    except Exception:
                        pass
        result.sort(key=lambda x: x[0].name)
        return result

    @staticmethod
    def get_specimen_info(name: str) -> Tuple[SpecimenConfig, SpecimenState, ToolsConfig, int]:
        """Obtiene la información detallada de un specimen."""
        normalized_name = SpecimenValidator.validate_name(name, check_exists=True)
        s_dir = specimen_dir(normalized_name)
        
        config = load_json(specimen_config_json(normalized_name), SpecimenConfig)
        state = load_json(specimen_state_json(normalized_name), SpecimenState)
        tools = load_json(specimen_tools_json(normalized_name), ToolsConfig)
        real_size = SizeService.get_specimen_size_mb(s_dir)
        
        return config, state, tools, real_size

    @staticmethod
    def remove_specimen(name: str) -> None:
        """Borra un specimen del disco. Si está activo, lanza SpecimenActiveError."""
        normalized_name = SpecimenValidator.validate_name(name, check_exists=True)
        
        # 1. Verificar si está activo en runtime
        active_specimen = RuntimeService.get_active_specimen()
        if active_specimen == normalized_name:
            raise SpecimenActiveError(f"No se puede eliminar el specimen '{normalized_name}' porque está activo.")
            
        # 2. Verificar si está marcado como activo en su state.json
        state_path = specimen_state_json(normalized_name)
        is_active = False
        if state_path.exists():
            try:
                state = load_json(state_path, SpecimenState)
                is_active = state.active
            except Exception:
                pass
        
        if is_active:
            raise SpecimenActiveError(f"No se puede eliminar el specimen '{normalized_name}' porque está marcado como activo.")
                
        # 3. Eliminar la carpeta completa
        s_dir = specimen_dir(normalized_name)
        shutil.rmtree(s_dir)

    @staticmethod
    def clone_specimen(parent_name: str, child_name: str, size_mb: int) -> SpecimenConfig:
        """Clona un specimen existente en uno nuevo e independiente."""
        normalized_parent = SpecimenValidator.validate_name(parent_name, check_exists=True)
        normalized_child = SpecimenValidator.validate_name(child_name, check_not_exists=True)
        validated_size = SpecimenValidator.validate_size(size_mb)
        
        parent_dir = specimen_dir(normalized_parent)
        parent_real_size = SizeService.get_specimen_size_mb(parent_dir)
        
        if validated_size < parent_real_size:
            raise CloneSizeTooSmallError(
                f"El tamaño del clon ({validated_size} MB) no puede ser menor "
                f"al tamaño real actual del padre ({parent_real_size} MB)."
            )
            
        SizeService.validate_space_available(spaces_dir(), validated_size)
        
        child_dir = specimen_dir(normalized_child)
        shutil.copytree(parent_dir, child_dir)
        
        now_str = datetime.now().isoformat()
        config = SpecimenConfig(
            name=normalized_child,
            type="clone",
            parent=normalized_parent,
            size_mb=validated_size,
            created_at=now_str,
            persistent=False
        )
        save_json(specimen_config_json(normalized_child), config)
        
        state = SpecimenState(
            active=False,
            last_entered_at=None,
            last_exited_at=None,
            exit_mode=None
        )
        save_json(specimen_state_json(normalized_child), state)
        
        return config

    @staticmethod
    def get_hierarchy() -> Tuple[List[str], dict]:
        """
        Retorna la lista de specimens raíz (sin padre) y un diccionario
        que mapea cada nombre de specimen a la lista de sus hijos.
        """
        ensure_base_dirs()
        roots = []
        adjacency = {}
        
        if not spaces_dir().exists():
            return roots, adjacency
            
        all_specs = {}
        for path in spaces_dir().iterdir():
            if path.is_dir():
                name = path.name
                config_path = specimen_config_json(name)
                if config_path.exists():
                    try:
                        config = load_json(config_path, SpecimenConfig)
                        all_specs[config.name] = config
                    except Exception:
                        pass
                        
        for name in all_specs:
            adjacency[name] = []
            
        for name, config in all_specs.items():
            if config.parent and config.parent in all_specs:
                adjacency[config.parent].append(name)
            else:
                roots.append(name)
                
        roots.sort()
        for parent in adjacency:
            adjacency[parent].sort()
            
        return roots, adjacency
