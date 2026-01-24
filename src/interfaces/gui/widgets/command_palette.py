from PyQt6.QtWidgets import QDialog, QLineEdit, QListWidget, QVBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor

class CommandPalette(QDialog):
    """Paleta de Comandos flutuante (Ctrl+P) inspirada no VS Code."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setFixedSize(600, 350)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # Importante para sombra
        
        # Container Principal com Sombra
        self.container = QFrame(self)
        self.container.setGeometry(5, 5, 590, 340) # Margem para sombra
        self.container.setStyleSheet("""
            QFrame {
                background-color: #27272A; /* Surface */
                border: 1px solid #3F3F46; /* Border */
                border-radius: 8px;
            }
        """)
        
        # Sombra (Drop Shadow)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para buscar arquivos ou comandos...")
        # Estilo do Input
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #18181B; /* Panel BG */
                color: #FAFAFA;
                border: none;
                border-bottom: 1px solid #3F3F46;
                padding: 16px 20px;
                font-size: 14px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            }
            QLineEdit::placeholder { color: #52525B; }
        """)
        
        self.results_list = QListWidget()
        # Estilo da Lista
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #27272A;
                border: none;
                color: #A1A1AA;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QListWidget::item:selected {
                background-color: #3F3F46;
                color: #FFD600; /* Accent */
                border-left: 2px solid #FFD600;
            }
            QListWidget::item:hover:not(:selected) {
                background-color: #2E2E33;
                color: #FAFAFA;
            }
        """)
        
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
