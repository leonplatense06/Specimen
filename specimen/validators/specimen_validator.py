import re
from specimen.exceptions import (
    InvalidSpecimenNameError,
    InvalidSizeError,
    SpecimenAlreadyExistsError,
    SpecimenNotFoundError,
)
from specimen.paths import specimen_dir

class SpecimenValidator:
    @staticmethod
    def validate_name(name: str, check_exists: bool = False, check_not_exists: bool = False) -> str:
        """Validates the naming rules of a specimen and optionally its existence/non-existence."""
        if not name:
            raise InvalidSpecimenNameError("Specimen name is required and cannot be empty.")
        
        # Name cannot contain spaces or special shell characters
        # Regex: ^[a-zA-Z0-9_-]+$
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise InvalidSpecimenNameError(
                f"The name '{name}' contains invalid characters. Only letters, numbers, '-' and '_' are allowed."
            )
        
        normalized_name = name.lower()
        path = specimen_dir(normalized_name)
        
        if check_not_exists and path.exists():
            raise SpecimenAlreadyExistsError(f"A specimen with the name '{normalized_name}' already exists.")
        
        if check_exists and not path.exists():
            raise SpecimenNotFoundError(f"The specimen '{normalized_name}' does not exist.")
            
        return normalized_name

    @staticmethod
    def validate_size(size_mb: int) -> int:
        """Validates that the size is a positive integer."""
        if size_mb is None:
            raise InvalidSizeError("Size is required.")
        
        # In case a float or string is passed by error in the python API invocation
        if not isinstance(size_mb, int) or size_mb <= 0:
            raise InvalidSizeError("Size must be a positive integer (in MB).")
            
        return size_mb

