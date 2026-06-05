import json
from pathlib import Path
from typing import Type, TypeVar, Any
from dacite import from_dict
from dataclasses import is_dataclass, asdict

T = TypeVar("T")

def load_json(path: Path, data_class: Type[T]) -> T:
    """Lee un archivo JSON y lo deserializa usando dacite si es un dataclass."""
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return from_dict(data_class=data_class, data=data)

def save_json(path: Path, obj: Any) -> None:
    """Guarda un objeto o dataclass en un archivo JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if is_dataclass(obj):
        data = asdict(obj)
    else:
        data = obj
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
