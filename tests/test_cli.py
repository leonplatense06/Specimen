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
        assert "creado exitosamente" in result.stdout
        assert (isolated_specimen_env / "spaces" / "media").exists()

def test_cli_new_error(isolated_specimen_env):
    result = runner.invoke(app, ["new", "invalid name!", "--size", "256"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout

def test_cli_list_empty(isolated_specimen_env):
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No se encontraron specimens creados" in result.stdout

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
        assert "Metadata de media" in result.stdout
        assert "Rutas de Sistema" in result.stdout

def test_cli_info_not_found(isolated_specimen_env):
    result = runner.invoke(app, ["info", "nonexistent"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout

def test_cli_rm_cancel(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        # Simular rechazo
        result = runner.invoke(app, ["rm", "media"], input="n\n")
        assert result.exit_code == 1  # Abort lanza exit_code 1
        assert "Operación cancelada" in result.stdout
        assert (isolated_specimen_env / "spaces" / "media").exists()

def test_cli_rm_confirm(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        # Simular confirmación
        result = runner.invoke(app, ["rm", "media"], input="y\n")
        assert result.exit_code == 0
        assert "eliminado exitosamente" in result.stdout
        assert not (isolated_specimen_env / "spaces" / "media").exists()

def test_cli_rm_force(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        runner.invoke(app, ["new", "media", "--size", "256"])
        
        result = runner.invoke(app, ["rm", "media", "--force"])
        assert result.exit_code == 0
        assert "eliminado exitosamente" in result.stdout
        assert not (isolated_specimen_env / "spaces" / "media").exists()

def test_cli_clone_success(isolated_specimen_env):
    with patch("specimen.services.size_service.SizeService.get_free_space_mb", return_value=1000):
        with patch("specimen.services.size_service.SizeService.get_specimen_size_mb", return_value=50):
            runner.invoke(app, ["new", "media", "--size", "256"])
            result = runner.invoke(app, ["clone", "media", "media-clone", "--size", "300"])
            assert result.exit_code == 0
            assert "clonado exitosamente" in result.stdout
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

