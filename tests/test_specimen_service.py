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
    
    # Verify that directories were created
    assert specimen_bin(name).exists()
    assert specimen_tmp(name).exists()
    assert specimen_home(name).exists()
    assert specimen_meta(name).exists()
    
    # Verify metadata files created
    assert specimen_config_json(name).exists()
    assert specimen_state_json(name).exists()
    assert specimen_tools_json(name).exists()
    
    # Load metadata and verify content
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
        # Requests 256 but only 100 is free
        SpecimenService.create_specimen("media", 256)

def test_create_specimen_already_exists(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        SpecimenService.create_specimen("media", 256)
        
        with pytest.raises(SpecimenAlreadyExistsError):
            SpecimenService.create_specimen("media", 128)

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_list_specimens(mock_free, isolated_specimen_env):
    # Create two specimens
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
    
    # Confirm existence
    assert specimen_dir(name).exists()
    
    SpecimenService.remove_specimen(name)
    
    # Verify that it no longer exists
    assert not specimen_dir(name).exists()

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_remove_specimen_active_fails(mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    
    # Simulate that the specimen is active
    with patch("specimen.services.runtime_service.RuntimeService.get_active_specimen", return_value=name):
        with pytest.raises(SpecimenActiveError):
            SpecimenService.remove_specimen(name)
            
    # Simulate active by its own state.json
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
    
    # Create parent
    SpecimenService.create_specimen(parent, 256)
    
    # Create a dummy file in parent's home to verify physical copy
    parent_home_file = specimen_home(parent) / "test.txt"
    parent_home_file.write_text("hello world")
    
    # Clone
    config = SpecimenService.clone_specimen(parent, child, 300)
    
    assert config.name == "media-clone"
    assert config.type == "clone"
    assert config.parent == "media"
    assert config.size_mb == 300
    assert config.persistent is False
    
    # Verify that the dummy file was physically copied to the child
    child_home_file = specimen_home(child) / "test.txt"
    assert child_home_file.exists()
    assert child_home_file.read_text() == "hello world"
    
    # Verify that the clone's state is inactive
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
    
    # Parent size is 300 MB, we try to clone with size 200 MB -> Should fail
    from specimen.exceptions import CloneSizeTooSmallError
    with pytest.raises(CloneSizeTooSmallError):
        SpecimenService.clone_specimen("parent", "child", 200)

def test_clone_specimen_insufficient_space(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        SpecimenService.create_specimen("parent", 256)
    
    # There is 100 MB free, we request 200 MB -> Raise InsufficientDiskSpaceError
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

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
@patch("specimen.services.shell_launcher.ShellLauncher.launch")
def test_enter_specimen_success(mock_launch, mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    
    mock_proc = MagicMock()
    mock_proc.pid = 12345
    mock_launch.return_value = mock_proc
    
    def mock_wait():
        state = load_json(specimen_state_json(name), SpecimenState)
        assert state.active is True
        from specimen.services.runtime_service import RuntimeService
        active_name = RuntimeService.get_active_specimen(auto_cleanup=False)
        assert active_name == name
        return 0
        
    mock_proc.wait = mock_wait
    
    SpecimenService.enter_specimen(name)
    
    state = load_json(specimen_state_json(name), SpecimenState)
    assert state.active is False
    from specimen.services.runtime_service import RuntimeService
    active_name = RuntimeService.get_active_specimen(auto_cleanup=False)
    assert active_name is None

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_enter_specimen_already_active(mock_free, isolated_specimen_env):
    SpecimenService.create_specimen("media", 256)
    SpecimenService.create_specimen("tools", 256)
    
    from specimen.models.runtime import RuntimeState
    from specimen.services.runtime_service import RuntimeService
    import os
    
    runtime_state = RuntimeState(
        active_specimen="media",
        entered_at="2026-06-05T00:00:00",
        shell_type="bash",
        session_id="session123",
        shell_pid=os.getpid()
    )
    RuntimeService.save_runtime_state(runtime_state)
    
    from specimen.exceptions import SpecimenAlreadyActiveError
    with pytest.raises(SpecimenAlreadyActiveError):
        SpecimenService.enter_specimen("tools")

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_quit_specimen_conserved(mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    
    from specimen.models.runtime import RuntimeState
    from specimen.services.runtime_service import RuntimeService
    
    state_path = specimen_state_json(name)
    state = load_json(state_path, SpecimenState)
    state.active = True
    save_json(state_path, state)
    
    runtime_state = RuntimeState(
        active_specimen=name,
        entered_at="2026-06-05T00:00:00",
        shell_type="bash",
        session_id="session123",
        shell_pid=99999,
        temp_script_path=None
    )
    RuntimeService.save_runtime_state(runtime_state)
    
    SpecimenService.quit_specimen(conserved=True)
    
    assert specimen_dir(name).exists()
    
    state = load_json(specimen_state_json(name), SpecimenState)
    assert state.active is False
    assert state.exit_mode == "conserved"
    
    active_name = RuntimeService.get_active_specimen(auto_cleanup=False)
    assert active_name is None

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_quit_specimen_destroyed(mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    
    from specimen.models.runtime import RuntimeState
    from specimen.services.runtime_service import RuntimeService
    
    state_path = specimen_state_json(name)
    state = load_json(state_path, SpecimenState)
    state.active = True
    save_json(state_path, state)
    
    runtime_state = RuntimeState(
        active_specimen=name,
        entered_at="2026-06-05T00:00:00",
        shell_type="bash",
        session_id="session123",
        shell_pid=99999,
        temp_script_path=None
    )
    RuntimeService.save_runtime_state(runtime_state)
    
    SpecimenService.quit_specimen(conserved=False)
    
    assert not specimen_dir(name).exists()
    
    active_name = RuntimeService.get_active_specimen(auto_cleanup=False)
    assert active_name is None

def test_quit_specimen_not_active(isolated_specimen_env):
    from specimen.exceptions import SpecimenError
    with pytest.raises(SpecimenError):
        SpecimenService.quit_specimen(conserved=True)

def test_build_fish_init():
    from specimen.services.shell_launcher import ShellLauncher
    launcher = ShellLauncher()
    env = {
        "PATH": "/home/user/.specimen/spaces/media/bin:/usr/bin:/bin",
        "SPEC_NAME": "media",
    }
    cmds = launcher._build_fish_init(env)
    # Verify that $PATH does not have backslash (\) escapes
    assert 'set -gx PATH "/home/user/.specimen/spaces/media/bin" $PATH' in cmds
    assert 'set -gx SPEC_NAME "media"' in cmds
    assert 'functions -c fish_prompt _original_fish_prompt' in cmds

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_set_persistence(mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    
    # By default it is not persistent
    config, _, _, _ = SpecimenService.get_specimen_info(name)
    assert config.persistent is False
    
    # Activate persistence
    SpecimenService.set_persistence(name, True)
    config, _, _, _ = SpecimenService.get_specimen_info(name)
    assert config.persistent is True
    
    # Deactivate persistence
    SpecimenService.set_persistence(name, False)
    config, _, _, _ = SpecimenService.get_specimen_info(name)
    assert config.persistent is False

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_quit_specimen_respects_persistence(mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    SpecimenService.set_persistence(name, True)
    
    from specimen.models.runtime import RuntimeState
    from specimen.services.runtime_service import RuntimeService
    
    state_path = specimen_state_json(name)
    state = load_json(state_path, SpecimenState)
    state.active = True
    save_json(state_path, state)
    
    runtime_state = RuntimeState(
        active_specimen=name,
        entered_at="2026-06-05T00:00:00",
        shell_type="bash",
        session_id="session123",
        shell_pid=99999,
        temp_script_path=None
    )
    RuntimeService.save_runtime_state(runtime_state)
    
    # Although conserved=False, since it is persistent it must be conserved
    SpecimenService.quit_specimen(conserved=False)
    
    assert specimen_dir(name).exists()
    
    state = load_json(specimen_state_json(name), SpecimenState)
    assert state.active is False
    assert state.exit_mode == "conserved"
    
    active_name = RuntimeService.get_active_specimen(auto_cleanup=False)
    assert active_name is None

@patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000)
def test_cleanup_stale_specimen_does_not_overwrite_clean_shutdown(mock_free, isolated_specimen_env):
    name = "media"
    SpecimenService.create_specimen(name, 256)
    
    # Simulate a clean shutdown with exit_mode = "conserved"
    state_path = specimen_state_json(name)
    state = load_json(state_path, SpecimenState)
    state.active = False
    state.last_exited_at = "2026-06-05T00:00:00"
    state.exit_mode = "conserved"
    save_json(state_path, state)
    
    # Invoke cleanup_stale_specimen
    from specimen.services.runtime_service import RuntimeService
    RuntimeService.cleanup_stale_specimen(name)
    
    # Verify that exit_mode is still "conserved" (not overwritten to None)
    state = load_json(state_path, SpecimenState)
    assert state.active is False
    assert state.exit_mode == "conserved"
    assert state.last_exited_at == "2026-06-05T00:00:00"



