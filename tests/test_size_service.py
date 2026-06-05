import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from specimen.services.size_service import SizeService
from specimen.exceptions import InsufficientDiskSpaceError

def test_get_specimen_size_mb_not_exists():
    path = Path("/nonexistent/path")
    assert SizeService.get_specimen_size_mb(path) == 0

@patch("subprocess.run")
def test_get_specimen_size_mb_success(mock_run):
    # Simular output de "du -sm path" -> "128\tpath\n"
    mock_proc = MagicMock()
    mock_proc.stdout = "128\t/some/path\n"
    mock_run.return_value = mock_proc

    path = Path("/some/path")
    # Asegurar que el path existe para que corra el subprocess
    with patch.object(Path, "exists", return_value=True):
        size = SizeService.get_specimen_size_mb(path)
        assert size == 128
        mock_run.assert_called_once_with(["du", "-sm", str(path)], capture_output=True, text=True, check=True)

@patch("subprocess.run")
def test_get_specimen_size_mb_failure(mock_run):
    # Simular error en subprocess.run
    mock_run.side_effect = Exception("du command failed")
    
    path = Path("/some/path")
    with patch.object(Path, "exists", return_value=True):
        size = SizeService.get_specimen_size_mb(path)
        assert size == 0

@patch("shutil.disk_usage")
def test_get_free_space_mb(mock_disk_usage):
    # Simular usage.free
    mock_usage = MagicMock()
    mock_usage.free = 500 * 1024 * 1024  # 500 MB en bytes
    mock_disk_usage.return_value = mock_usage
    
    free_space = SizeService.get_free_space_mb(Path("/some/path"))
    assert free_space == 500

@patch("shutil.disk_usage")
def test_validate_space_available_success(mock_disk_usage):
    mock_usage = MagicMock()
    mock_usage.free = 500 * 1024 * 1024  # 500 MB
    mock_disk_usage.return_value = mock_usage
    
    # 256 MB solicitados, hay 500 MB -> Debería pasar sin excepción
    SizeService.validate_space_available(Path("/some/path"), 256)

@patch("shutil.disk_usage")
def test_validate_space_available_insufficient(mock_disk_usage):
    mock_usage = MagicMock()
    mock_usage.free = 100 * 1024 * 1024  # 100 MB
    mock_disk_usage.return_value = mock_usage
    
    # 256 MB solicitados, hay 100 MB -> Lanzar InsufficientDiskSpaceError
    with pytest.raises(InsufficientDiskSpaceError):
        SizeService.validate_space_available(Path("/some/path"), 256)
