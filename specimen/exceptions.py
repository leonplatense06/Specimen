class SpecimenError(Exception):
    """Error base de Specimen."""

class SpecimenNotFoundError(SpecimenError):
    """El specimen solicitado no existe."""

class SpecimenAlreadyExistsError(SpecimenError):
    """Ya existe un specimen con ese nombre."""

class SpecimenActiveError(SpecimenError):
    """No se puede realizar la operación: el specimen está activo."""

class SpecimenAlreadyActiveError(SpecimenError):
    """Ya hay un specimen activo. Salir antes de entrar a otro."""

class InvalidSpecimenNameError(SpecimenError):
    """El nombre del specimen contiene caracteres inválidos."""

class InsufficientDiskSpaceError(SpecimenError):
    """No hay suficiente espacio en disco para la operación."""

class InvalidSizeError(SpecimenError):
    """El tamaño especificado es inválido."""

class CloneSizeTooSmallError(SpecimenError):
    """El --size del clon es menor al tamaño real del padre."""
