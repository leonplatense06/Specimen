import pytest
from specimen.validators.specimen_validator import SpecimenValidator
from specimen.exceptions import (
    InvalidSpecimenNameError,
    InvalidSizeError,
    SpecimenAlreadyExistsError,
    SpecimenNotFoundError,
)
from specimen.paths import specimen_dir

def test_validate_name_success():
    assert SpecimenValidator.validate_name("media") == "media"
    assert SpecimenValidator.validate_name("MEDIA") == "media"  # Normalizado a lowercase
    assert SpecimenValidator.validate_name("media-test") == "media-test"
    assert SpecimenValidator.validate_name("media_test_123") == "media_test_123"

def test_validate_name_invalid_chars():
    invalid_names = [
        "media test",      # Espacios
        "media$test",      # Símbolos de shell
        "media/test",      # Separadores de ruta
        "media;test",
        "media&test",
        "",                # Vacío
    ]
    for name in invalid_names:
        with pytest.raises(InvalidSpecimenNameError):
            SpecimenValidator.validate_name(name)

def test_validate_name_check_exists_and_not_exists(isolated_specimen_env):
    # Por defecto no existe
    name = "media"
    
    # Debería lanzar NotFoundError si check_exists es True
    with pytest.raises(SpecimenNotFoundError):
        SpecimenValidator.validate_name(name, check_exists=True)
        
    # Debería pasar si check_not_exists es True
    assert SpecimenValidator.validate_name(name, check_not_exists=True) == "media"
    
    # Creamos físicamente el directorio para simular existencia
    s_dir = specimen_dir(name)
    s_dir.mkdir(parents=True)
    
    # Ahora debería pasar si check_exists es True
    assert SpecimenValidator.validate_name(name, check_exists=True) == "media"
    
    # Debería lanzar AlreadyExistsError si check_not_exists es True
    with pytest.raises(SpecimenAlreadyExistsError):
        SpecimenValidator.validate_name(name, check_not_exists=True)

def test_validate_size_success():
    assert SpecimenValidator.validate_size(1) == 1
    assert SpecimenValidator.validate_size(1000) == 1000

def test_validate_size_invalid():
    invalid_sizes = [0, -5, None, "100", 10.5]
    for size in invalid_sizes:
        with pytest.raises(InvalidSizeError):
            SpecimenValidator.validate_size(size)
