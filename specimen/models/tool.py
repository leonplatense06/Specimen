from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ToolRecord:
    name: str
    filename: str
    installed_at: str
    source: Optional[str] = None
    version: Optional[str] = None

@dataclass
class ToolsConfig:
    tools: List[ToolRecord] = field(default_factory=list)
