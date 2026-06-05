from dataclasses import dataclass
from typing import Optional

@dataclass
class SpecimenConfig:
    name: str
    type: str                  # "base" | "clone"
    parent: Optional[str]      # name of parent specimen, or None
    size_mb: int
    created_at: str            # ISO datetime string
    persistent: bool
