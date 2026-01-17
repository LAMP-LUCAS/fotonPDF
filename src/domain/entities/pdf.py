from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class PDFDocument:
    """Entidade que representa um documento PDF no domínio."""
    path: Path
    name: str
    page_count: Optional[int] = None

    @classmethod
    def from_path(cls, path: Path) -> "PDFDocument":
        return cls(
            path=path,
            name=path.name
        )
