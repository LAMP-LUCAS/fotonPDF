import os
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import QWidget
from src.infrastructure.services.logger import log_debug

class UISnapshotUtil:
    """Utilitário para capturar e salvar screenshots da interface (DRY)."""
    
    @staticmethod
    def capture(widget: QWidget, name: str):
        """Captura o widget e salva em docs/visuals/captures com timestamp."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            capture_dir = Path("docs/visuals/captures")
            capture_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{name}_{timestamp}.png"
            file_path = capture_dir / filename
            
            # Captura o widget (incluindo filhos)
            pixmap = widget.grab()
            if pixmap.save(str(file_path)):
                log_debug(f"📸 Snapshot salvo: {file_path}")
                return file_path
            else:
                log_debug(f"❌ Falha ao salvar snapshot: {file_path}")
        except Exception as e:
            log_debug(f"⚠️ Erro ao capturar interface: {e}")
        return None
