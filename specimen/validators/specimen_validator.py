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
        """Valida las reglas de nombrado de un specimen y opcionalmente su existencia/inexistencia."""
        if not name:
            raise InvalidSpecimenNameError("El nombre del specimen es obligatorio y no puede estar vacío.")
        
        # El nombre no puede contener espacios ni caracteres especiales de shell
        # Regex: ^[a-zA-Z0-9_-]+$
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise InvalidSpecimenNameError(
                f"El nombre '{name}' contiene caracteres inválidos. Solo se permiten letras, números, '-' y '_'."
            )
        
        normalized_name = name.lower()
        path = specimen_dir(normalized_name)
        
        if check_not_exists and path.exists():
            raise SpecimenAlreadyExistsError(f"Ya existe un specimen con el nombre '{normalized_name}'.")
        
        if check_exists and not path.exists():
            raise SpecimenNotFoundError(f"El specimen '{normalized_name}' no existe.")
            
        return normalized_name

    @staticmethod
    def validate_size(size_mb: int) -> int:
        """Valida que el tamaño sea un entero positivo."""
        if size_mb is None:
            raise InvalidSizeError("El tamaño es obligatorio.")
        
        # En caso de que se pase un float o string por error en la invocación de la API de python
        if not isinstance(size_mb, int) or size_mb <= 0:
            raise InvalidSizeError("El tamaño debe ser un número entero positivo (en MB).")
            
        return size_mb
