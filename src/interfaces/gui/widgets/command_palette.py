from PyQt6.QtWidgets import QDialog, QLineEdit, QListWidget, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QPoint

class CommandPalette(QDialog):
    """Paleta de Comandos flutuante (Ctrl+P) inspirada no VS Code."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setFixedSize(600, 350)
        
        # Estilo Premium (VS Code Quick Open)
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
                border: 1px solid #454545;
                border-radius: 8px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: none;
                padding: 14px 16px;
                font-size: 14px;
                border-bottom: 1px solid #454545;
                border-radius: 0;
            }
            QLineEdit::placeholder {
                color: #858585;
            }
            QListWidget {
                background-color: #252526;
                border: none;
                color: #cccccc;
                outline: none;
                padding: 4px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QListWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QListWidget::item:hover:not(:selected) {
                background-color: #2a2d2e;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para buscar arquivos ou comandos...")
        
        self.results_list = QListWidget()
        
        layout.addWidget(self.search_input)
        layout.addWidget(self.results_list)
        
        # Mock de comandos e arquivos
        self.items = [
            "📄 Planta_Baixa_A0.pdf",
            "📄 Memorial_Descritivo.pdf",
            "⚙️ Configurações: Alternar Tema",
            "🔄 Girar Página (90° Horário)",
            "➕ Mesclar Documentos...",
            "🔍 Buscar Texto...",
            "📂 Abrir Pasta de Projetos"
        ]
        
        self.search_input.textChanged.connect(self._filter_items)
        self._filter_items("")

    def _filter_items(self, text):
        self.results_list.clear()
        for item in self.items:
            if text.lower() in item.lower():
                self.results_list.addItem(item)
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def show_centered(self):
        """Calcula posição central relativa à janela mãe."""
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.center().x() - self.width() // 2
            y = parent_geo.top() + 80 # Ligeiramente acima do centro visual
            self.move(x, y)
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()
