from dataclasses import dataclass
from typing import Optional

@dataclass
class RuntimeState:
    active_specimen: Optional[str]
    entered_at: Optional[str]
    shell_type: Optional[str]
    session_id: Optional[str]
    shell_pid: Optional[int] = None
    temp_script_path: Optional[str] = None
