import subprocess
import shutil
from pathlib import Path
from specimen.exceptions import InsufficientDiskSpaceError

class SizeService:
    @staticmethod
    def get_specimen_size_mb(path: Path) -> int:
        """Obtiene el tamaño real usado por el directorio en MB con 'du -sm'."""
        if not path.exists():
            return 0
        try:
            result = subprocess.run(
                ["du", "-sm", str(path)],
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.split()[0])
        except Exception:
            # Fallback por robustez
            return 0

    @staticmethod
    def get_free_space_mb(path: Path) -> int:
        """Obtiene el espacio libre en el disco en MB."""
        target = path
        while not target.exists() and target.parent != target:
            target = target.parent
        usage = shutil.disk_usage(str(target))
        return usage.free // (1024 * 1024)

    @classmethod
    def validate_space_available(cls, target_dir: Path, required_mb: int) -> None:
        """Verifica si hay suficiente espacio libre en el disco. Si no, lanza InsufficientDiskSpaceError."""
        free_mb = cls.get_free_space_mb(target_dir)
        if free_mb < required_mb:
            raise InsufficientDiskSpaceError(
                f"Espacio insuficiente en disco: se requieren {required_mb} MB, pero solo hay {free_mb} MB libres."
            )
