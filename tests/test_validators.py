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
    assert SpecimenValidator.validate_name("MEDIA") == "media"  # Normalized to lowercase
    assert SpecimenValidator.validate_name("media-test") == "media-test"
    assert SpecimenValidator.validate_name("media_test_123") == "media_test_123"

def test_validate_name_invalid_chars():
    invalid_names = [
        "media test",      # Spaces
        "media$test",      # Shell symbols
        "media/test",      # Path separators
        "media;test",
        "media&test",
        "",                # Empty
    ]
    for name in invalid_names:
        with pytest.raises(InvalidSpecimenNameError):
            SpecimenValidator.validate_name(name)

def test_validate_name_check_exists_and_not_exists(isolated_specimen_env):
    # By default does not exist
    name = "media"
    
    # Should raise NotFoundError if check_exists is True
    with pytest.raises(SpecimenNotFoundError):
        SpecimenValidator.validate_name(name, check_exists=True)
        
    # Should pass if check_not_exists is True
    assert SpecimenValidator.validate_name(name, check_not_exists=True) == "media"
    
    # Physically create the directory to simulate existence
    s_dir = specimen_dir(name)
    s_dir.mkdir(parents=True)
    
    # Now should pass if check_exists is True
    assert SpecimenValidator.validate_name(name, check_exists=True) == "media"
    
    # Should raise AlreadyExistsError if check_not_exists is True
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
