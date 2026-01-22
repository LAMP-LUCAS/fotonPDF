from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class ActivityBar(QWidget):
    """Barra vertical lateral estilo VS Code com ícones."""
    clicked = pyqtSignal(int) # Emite o índice da aba selecionada

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ActivityBar")
        self.setFixedWidth(50)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.group.idClicked.connect(self.clicked.emit)
        
        self._add_action(0, "📁") # Explorer (Miniaturas)
        self._add_action(1, "🔍") # Busca
        self._add_action(2, "🔖") # Sumário
        self._add_action(3, "✍️") # Anotações
        
        self.layout.addStretch()
        self._add_action(99, "⚙️") # Configurações (Sempre ao fundo)

    def _add_action(self, idx, icon_text):
        btn = QPushButton(icon_text)
        btn.setCheckable(True)
        btn.setFixedSize(50, 50)
        btn.setStyleSheet("font-size: 20px;")
        self.group.addButton(btn, idx)
        self.layout.addWidget(btn)
        
        if idx == 0:
            btn.setChecked(True)

    def set_active(self, idx):
        btn = self.group.button(idx)
        if btn:
            btn.setChecked(True)
