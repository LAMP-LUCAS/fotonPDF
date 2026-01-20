from dataclasses import dataclass
from typing import List, Tuple

@dataclass(frozen=True)
class SearchResult:
    """Representa um hit textual em uma busca no PDF."""
    page_index: int
    text_snippet: str
    highlights: List[Tuple[float, float, float, float]]  # List of rectangles (x0, y0, x1, y1)

@dataclass(frozen=True)
class TOCItem:
    """Representa um item no sumário (Bookmarks) do PDF."""
    level: int
    title: str
    page_index: int
