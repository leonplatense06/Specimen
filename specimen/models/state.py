from dataclasses import dataclass
from typing import Optional

@dataclass
class SpecimenState:
    active: bool
    last_entered_at: Optional[str]
    last_exited_at: Optional[str]
    exit_mode: Optional[str]   # "destroyed" | "conserved" | None
