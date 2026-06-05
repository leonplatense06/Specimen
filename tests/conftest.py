import os
import shutil
import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def isolated_specimen_env(tmp_path):
    """Fixture que aísla el entorno de Specimen para cada test usando un directorio temporal."""
    # Guardar valor original si existe
    original_val = os.environ.get("SPECIMEN_ROOT_DIR")
    
    # Apuntar a un directorio temporal único para el test
    test_root = tmp_path / ".specimen_test"
    os.environ["SPECIMEN_ROOT_DIR"] = str(test_root)
    
    yield test_root
    
    # Restaurar valor original
    if original_val is not None:
        os.environ["SPECIMEN_ROOT_DIR"] = original_val
    else:
        os.environ.pop("SPECIMEN_ROOT_DIR", None)
        
    # Limpieza del directorio temporal
    if test_root.exists():
        try:
            shutil.rmtree(test_root)
        except Exception:
            pass
