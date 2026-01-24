import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from src.interfaces.gui.main_window import MainWindow
from src.infrastructure.mock.fake_data import FakeDataGenerator
from src.interfaces.gui.styles import get_main_stylesheet
from src.interfaces.gui.utils.snapshot_util import UISnapshotUtil
from PyQt6.QtCore import QTimer

class DevelopmentMainWindow(MainWindow):
    """Subclasse da MainWindow para rodar em modo de desenvolvimento com mocks."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("fotonPDF - [MODE: DEVELOPMENT MOCKUP]")
        self.setStyleSheet(get_main_stylesheet()) # Forçar o estilo do projeto
        self._load_mocks()
        
        # Agendar snapshot após processar eventos da UI
        QTimer.singleShot(2000, self._auto_snapshot)

    def _auto_snapshot(self):
        """Tira uma foto automática para registro visual."""
        UISnapshotUtil.capture(self, "mockup_full_view")

    def _load_mocks(self):
        """Popula a UI com dados falsos e exporta para o web concept."""
        from src.interfaces.gui.widgets.infinite_canvas import InfiniteCanvasView
        
        # Exporta mocks para JSON (facilita o pipeline Web-First)
        mock_json_path = Path("docs/visuals/mock_data.json")
        FakeDataGenerator.export_to_json(str(mock_json_path))
        
        # Substitui a área central por um Infinite Canvas para demonstração
        self.canvas_mock = InfiniteCanvasView()
        self.editor_group = self.current_editor_group
        if self.editor_group:
            self.editor_group.layout.addWidget(self.canvas_mock)
            if hasattr(self.editor_group, 'splitter'):
                self.editor_group.splitter.hide() # Esconde o viewer real para o mockup
            
        self.statusBar().showMessage(f"Mockup Mode: Dados exportados para {mock_json_path.name}", 5000)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("fotonPDF-Dev")
    
    window = DevelopmentMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
