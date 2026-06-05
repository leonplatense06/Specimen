class SpecimenError(Exception):
    """Base Specimen exception."""

class SpecimenNotFoundError(SpecimenError):
    """The requested specimen does not exist."""

class SpecimenAlreadyExistsError(SpecimenError):
    """A specimen with that name already exists."""

class SpecimenActiveError(SpecimenError):
    """Cannot perform operation: the specimen is currently active."""

class SpecimenAlreadyActiveError(SpecimenError):
    """A specimen is already active. Exit before entering another one."""

class InvalidSpecimenNameError(SpecimenError):
    """Specimen name contains invalid characters."""

class InsufficientDiskSpaceError(SpecimenError):
    """Insufficient disk space for the operation."""

class InvalidSizeError(SpecimenError):
    """Specified size is invalid."""

class CloneSizeTooSmallError(SpecimenError):
    """The clone's --size is smaller than the parent's actual size."""

