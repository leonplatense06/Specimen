import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from specimen.services.specimen_service import SpecimenService
from specimen.exceptions import (
    SpecimenActiveError,
    SpecimenNotFoundError,
    SpecimenAlreadyExistsError,
    InsufficientDiskSpaceError,
)
from specimen.paths import (
    specimen_dir,
    specimen_bin,
    specimen_tmp,
    specimen_home,
    specimen_meta,
    specimen_config_json,
    specimen_state_json,
    specimen_tools_json,
)
from specimen.models import SpecimenConfig, SpecimenState, ToolsConfig
from specimen.storage.json_storage import load_json, save_json

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_create_specimen_success(mock_free, isolated_specimen_env):
    name = "media"
    size_mb = 256
    
    config = SpecimenService.create_specimen(name, size_mb)
    
    assert config.name == "media"
    assert config.type == "base"
    assert config.size_mb == 256
    assert config.parent is None
    assert config.persistent is False
    
    # Verificar que se crearon los directorios
    assert specimen_bin(name).exists()
    assert specimen_tmp(name).exists()
    assert specimen_home(name).exists()
    assert specimen_meta(name).exists()
    
    # Verificar archivos de metadatos creados
    assert specimen_config_json(name).exists()
    assert specimen_state_json(name).exists()
    assert specimen_tools_json(name).exists()
    
    # Cargar metadatos y verificar contenido
    saved_config = load_json(specimen_config_json(name), SpecimenConfig)
    assert saved_config.name == "media"
    assert saved_config.size_mb == 256
    
    saved_state = load_json(specimen_state_json(name), SpecimenState)
    assert saved_state.active is False
    assert saved_state.last_entered_at is None
    
    saved_tools = load_json(specimen_tools_json(name), ToolsConfig)
    assert len(saved_tools.tools) == 0

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=100)
def test_create_specimen_insufficient_space(mock_free, isolated_specimen_env):
    with pytest.raises(InsufficientDiskSpaceError):
        # Solicita 256 pero solo hay 100
        SpecimenService.create_specimen("media", 256)

def test_create_specimen_already_exists(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        SpecimenService.create_specimen("media", 256)
        
        with pytest.raises(SpecimenAlreadyExistsError):
            SpecimenService.create_specimen("media", 128)

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_list_specimens(mock_free, isolated_specimen_env):
    # Crear dos specimens
    SpecimenService.create_specimen("media", 256)
    SpecimenService.create_specimen("tools", 512)
    
    with patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=10):
        specs = SpecimenService.list_specimens()
        
        assert len(specs) == 2
        assert specs[0][0].name == "media"
        assert specs[0][0].size_mb == 256
        assert specs[0][2] == 10  # real size
        
        assert specs[1][0].name == "tools"
        assert specs[1][0].size_mb == 512
        assert specs[1][2] == 10

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
@patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=15)
def test_get_specimen_info(mock_size, mock_free, isolated_specimen_env):
    SpecimenService.create_specimen("media", 256)
    
    config, state, tools, real_size = SpecimenService.get_specimen_info("media")
    
    assert config.name == "media"
    assert config.size_mb == 256
    assert state.active is False
    assert len(tools.tools) == 0
    assert real_size == 15

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_remove_specimen_success(mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    
    # Confirmar existencia
    assert specimen_dir(name).exists()
    
    SpecimenService.remove_specimen(name)
    
    # Verificar que ya no existe
    assert not specimen_dir(name).exists()

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_remove_specimen_active_fails(mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    
    # Simular que el specimen está activo
    with patch("specimen.services.runtime_service.RuntimeService.get_active_specimen", return_value=name):
        with pytest.raises(SpecimenActiveError):
            SpecimenService.remove_specimen(name)
            
    # Simular activo por su propio state.json
    state_path = specimen_state_json(name)
    state = load_json(state_path, SpecimenState)
    state.active = True
    save_json(state_path, state)
    
    with pytest.raises(SpecimenActiveError):
        SpecimenService.remove_specimen(name)

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
@patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=100)
def test_clone_specimen_success(mock_size, mock_free, isolated_specimen_env):
    parent = "media"
    child = "media-clone"
    
    # Crear padre
    SpecimenService.create_specimen(parent, 256)
    
    # Crear un archivo ficticio en home del padre para verificar copia física
    parent_home_file = specimen_home(parent) / "test.txt"
    parent_home_file.write_text("hello world")
    
    # Clona
    config = SpecimenService.clone_specimen(parent, child, 300)
    
    assert config.name == "media-clone"
    assert config.type == "clone"
    assert config.parent == "media"
    assert config.size_mb == 300
    assert config.persistent is False
    
    # Verificar que el archivo ficticio se copió físicamente al hijo
    child_home_file = specimen_home(child) / "test.txt"
    assert child_home_file.exists()
    assert child_home_file.read_text() == "hello world"
    
    # Verificar que el state del clon es inactivo
    state = load_json(specimen_state_json(child), SpecimenState)
    assert state.active is False

def test_clone_specimen_parent_not_found(isolated_specimen_env):
    with pytest.raises(SpecimenNotFoundError):
        SpecimenService.clone_specimen("nonexistent", "clone", 256)

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_clone_specimen_child_already_exists(mock_free, isolated_specimen_env):
    SpecimenService.create_specimen("parent", 256)
    SpecimenService.create_specimen("child", 256)
    
    with pytest.raises(SpecimenAlreadyExistsError):
        SpecimenService.clone_specimen("parent", "child", 256)

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
@patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=300)
def test_clone_specimen_size_too_small(mock_size, mock_free, isolated_specimen_env):
    SpecimenService.create_specimen("parent", 256)
    
    # Padre mide 300 MB, intentamos clonar con size 200 MB -> Debería fallar
    from specimen.exceptions import CloneSizeTooSmallError
    with pytest.raises(CloneSizeTooSmallError):
        SpecimenService.clone_specimen("parent", "child", 200)

def test_clone_specimen_insufficient_space(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        SpecimenService.create_specimen("parent", 256)
    
    # Hay 100 MB libres, solicitamos 200 MB -> Lanzar InsufficientDiskSpaceError
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=100):
        with patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=50):
            with pytest.raises(InsufficientDiskSpaceError):
                SpecimenService.clone_specimen("parent", "child", 200)

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_get_hierarchy(mock_free, isolated_specimen_env):
    SpecimenService.create_specimen("root1", 256)
    SpecimenService.create_specimen("root2", 256)
    
    with patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=10):
        SpecimenService.clone_specimen("root1", "child1-1", 256)
        SpecimenService.clone_specimen("root1", "child1-2", 256)
        SpecimenService.clone_specimen("child1-1", "grandchild1", 256)
        
    roots, adjacency = SpecimenService.get_hierarchy()
    
    assert roots == ["root1", "root2"]
    assert adjacency["root1"] == ["child1-1", "child1-2"]
    assert adjacency["root2"] == []
    assert adjacency["child1-1"] == ["grandchild1"]
    assert adjacency["child1-2"] == []
    assert adjacency["grandchild1"] == []

