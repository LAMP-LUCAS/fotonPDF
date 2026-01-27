from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QTabBar
from PyQt6.QtCore import Qt, pyqtSignal
from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback
from src.interfaces.gui.widgets.editor_group import EditorGroup

class TabContainer(QTabWidget):
    """
    Container de abas estilo VS Code.
    Gerencia múltiplos documentos, cada um em seu próprio EditorGroup.
    """
    fileChanged = pyqtSignal(object) # Emitido quando a aba ativa muda

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        self.currentChanged.connect(self._on_current_changed)
        
        self.setStyleSheet("""
            QTabWidget::pane { border: none; background: #1e1e1e; }
            QTabBar::tab {
                background: #2d2d2d;
                color: #858585;
                padding: 8px 15px;
                border-right: 1px solid #1e1e1e;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #1e1e1e;
                color: #ffffff;
                border-top: 1px solid #007acc;
            }
            QTabBar::tab:hover {
                background: #323232;
            }
        """)

    @safe_ui_callback("Open Tab")
    def add_editor(self, file_path, metadata):
        """Adiciona um novo documento em uma nova aba."""
        from src.infrastructure.services.logger import log_debug
        
        # Verificar se já está aberto (opcional, para evitar duplicatas nas abas)
        for i in range(self.count()):
            group = self.widget(i)
            if group.current_file == file_path:
                self.setCurrentIndex(i)
                # Se metadata do group estiver vazio mas o novo não, recarregar
                if metadata.get("page_count", 0) > 0 and (not group.metadata or group.metadata.get("page_count", 0) == 0):
                    log_debug(f"TabContainer: Recarregando documento na aba existente (metadata anterior inválido)")
                    group.load_document(file_path, metadata)
                return group

        log_debug(f"TabContainer: Criando nova aba para {file_path.name}")
        group = EditorGroup()
        group.load_document(file_path, metadata)
        
        idx = self.addTab(group, file_path.name)
        self.setCurrentIndex(idx)
        return group

    @safe_ui_callback("Close Tab")
    def _on_tab_close_requested(self, index):
        widget = self.widget(index)
        if widget:
            widget.deleteLater()
        self.removeTab(index)

    def _on_current_changed(self, index):
        if index >= 0:
            group = self.widget(index)
            self.fileChanged.emit(group.current_file)

    def current_editor(self) -> EditorGroup:
        """Retorna o EditorGroup da aba atual."""
        return self.currentWidget()
