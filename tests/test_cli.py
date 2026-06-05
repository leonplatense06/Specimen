import os
import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from specimen.cli import app
from specimen.paths import specimen_dir

runner = CliRunner()

def test_cli_new_success(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        result = runner.invoke(app, ["new", "media", "--size", "256"])
        assert result.exit_code == 0
        assert "created successfully" in result.stdout
        assert (isolated_specimen_env / "spaces" / "media").exists()

def test_cli_new_error(isolated_specimen_env):
    result = runner.invoke(app, ["new", "invalid name!", "--size", "256"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout

def test_cli_list_empty(isolated_specimen_env):
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No specimens found" in result.stdout

def test_cli_list_populated(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "media" in result.stdout
        assert "base" in result.stdout
        assert "256" in result.stdout

def test_cli_info_success(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        result = runner.invoke(app, ["info", "media"])
        assert result.exit_code == 0
        assert "Metadata for media" in result.stdout
        assert "System Paths" in result.stdout

def test_cli_info_not_found(isolated_specimen_env):
    result = runner.invoke(app, ["info", "nonexistent"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout

def test_cli_rm_cancel(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        # Simulate rejection
        result = runner.invoke(app, ["rm", "media"], input="n\n")
        assert result.exit_code == 1  # Abort raises exit_code 1
        assert "Operation cancelled" in result.stdout
        assert (isolated_specimen_env / "spaces" / "media").exists()

def test_cli_rm_confirm(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        # Simulate confirmation
        result = runner.invoke(app, ["rm", "media"], input="y\n")
        assert result.exit_code == 0
        assert "deleted successfully" in result.stdout
        assert not (isolated_specimen_env / "spaces" / "media").exists()

def test_cli_rm_force(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        result = runner.invoke(app, ["rm", "media", "--force"])
        assert result.exit_code == 0
        assert "deleted successfully" in result.stdout
        assert not (isolated_specimen_env / "spaces" / "media").exists()

def test_cli_clone_success(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        with patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=50):
            runner.invoke(app, ["new", "media", "--size", "256"])
            result = runner.invoke(app, ["clone", "media", "media-clone", "--size", "300"])
            assert result.exit_code == 0
            assert "cloned successfully" in result.stdout
            assert (isolated_specimen_env / "spaces" / "media-clone").exists()

def test_cli_clone_size_too_small(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        with patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=200):
            runner.invoke(app, ["new", "media", "--size", "256"])
            result = runner.invoke(app, ["clone", "media", "media-clone", "--size", "100"])
            assert result.exit_code == 1
            assert "Error:" in result.stdout

def test_cli_tree(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        with patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=10):
            runner.invoke(app, ["new", "root", "--size", "256"])
            runner.invoke(app, ["clone", "root", "child", "--size", "256"])
            
            result = runner.invoke(app, ["tree"])
            assert result.exit_code == 0
            assert "Specimens" in result.stdout
            assert "root" in result.stdout
            assert "child" in result.stdout

def test_cli_enter_success(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        # Mock enter_specimen so that it does not open a real shell in test
        with patch("specimen.services.specimen_service.SpecimenService.enter_specimen") as mock_enter:
            result = runner.invoke(app, ["enter", "media"])
            assert result.exit_code == 0
            assert "Entering specimen" in result.stdout
            mock_enter.assert_called_once_with("media")

def test_cli_quit_success(isolated_specimen_env):
    # Mock quit_specimen
    with patch("specimen.services.specimen_service.SpecimenService.quit_specimen") as mock_quit:
        result = runner.invoke(app, ["quit", "-c"])
        assert result.exit_code == 0
        assert "deactivated and conserved" in result.stdout
        mock_quit.assert_called_once_with(True)
        
    with patch("specimen.services.specimen_service.SpecimenService.quit_specimen") as mock_quit:
        result = runner.invoke(app, ["quit"])
        assert result.exit_code == 0
        assert "deactivated and destroyed" in result.stdout
        mock_quit.assert_called_once_with(False)

def test_cli_quit_prompts_and_cancels(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        from specimen.models.runtime import RuntimeState
        from specimen.services.runtime_service import RuntimeService
        runtime_state = RuntimeState(
            active_specimen="media",
            entered_at="2026-06-05T00:00:00",
            shell_type="bash",
            session_id="session123",
            shell_pid=os.getpid(),
            temp_script_path=None
        )
        RuntimeService.save_runtime_state(runtime_state)
        
        with patch("specimen.services.specimen_service.SpecimenService.quit_specimen") as mock_quit:
            result = runner.invoke(app, ["quit"], input="n\n")
            assert result.exit_code == 1
            assert "Operation cancelled" in result.stdout
            mock_quit.assert_not_called()

def test_cli_quit_prompts_and_confirms(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        from specimen.models.runtime import RuntimeState
        from specimen.services.runtime_service import RuntimeService
        runtime_state = RuntimeState(
            active_specimen="media",
            entered_at="2026-06-05T00:00:00",
            shell_type="bash",
            session_id="session123",
            shell_pid=os.getpid(),
            temp_script_path=None
        )
        RuntimeService.save_runtime_state(runtime_state)
        
        with patch("specimen.services.specimen_service.SpecimenService.quit_specimen") as mock_quit:
            result = runner.invoke(app, ["quit"], input="y\n")
            assert result.exit_code == 0
            assert "deactivated and destroyed" in result.stdout
            mock_quit.assert_called_once_with(False)

def test_cli_quit_no_prompt_for_persistent(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        runner.invoke(app, ["persist", "media"])
        
        from specimen.models.runtime import RuntimeState
        from specimen.services.runtime_service import RuntimeService
        runtime_state = RuntimeState(
            active_specimen="media",
            entered_at="2026-06-05T00:00:00",
            shell_type="bash",
            session_id="session123",
            shell_pid=os.getpid(),
            temp_script_path=None
        )
        RuntimeService.save_runtime_state(runtime_state)
        
        with patch("specimen.services.specimen_service.SpecimenService.quit_specimen") as mock_quit:
            result = runner.invoke(app, ["quit"])
            assert result.exit_code == 0
            assert "deactivated and conserved" in result.stdout
            mock_quit.assert_called_once_with(False)

def test_cli_persist_command(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        result = runner.invoke(app, ["persist", "media"])
        assert result.exit_code == 0
        assert "is now persistent" in result.stdout
        
        result = runner.invoke(app, ["persist", "media", "--unset"])
        assert result.exit_code == 0
        assert "is now non-persistent" in result.stdout

def test_cli_unpersist_command(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        runner.invoke(app, ["persist", "media"])
        
        result = runner.invoke(app, ["unpersist", "media"])
        assert result.exit_code == 0
        assert "is now non-persistent" in result.stdout

