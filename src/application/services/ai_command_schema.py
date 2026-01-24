from pydantic import BaseModel, Field
from typing import Optional

class CommandSchema(BaseModel):
    """Esquema de comando AEC para tradução via IA (Instructor)."""
    action: str = Field(description="A ação a ser executada: 'rotate', 'zoom', 'hide_layer', 'show_layer', 'open'")
    parameter: Optional[str] = Field(description="O valor do parâmetro (ex: '90', 'in', 'eletrica', 'A0')")
    explanation: str = Field(description="Uma breve explicação amigável do que a IA entendeu")
