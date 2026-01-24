from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class ActivityBar(QWidget):
    """Barra vertical lateral estilo VS Code com estética Neon-AEC Premium."""
    clicked = pyqtSignal(int) # Emite o índice da aba selecionada

    # Mapeamento de ícones (UTF-8 com melhor renderização)
    ICONS = {
        0: ("📂", "Explorer"),       # Miniaturas
        1: ("🔎", "Buscar"),          # Busca
        2: ("🗂️", "Sumário"),         # TOC
        3: ("🖍️", "Anotações"),       # Highlights
        99: ("⚙️", "Configurações"),  # Settings
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ActivityBar")
        self.setFixedWidth(48)
        
        # Estilo Premium VS Code Dark+
        self.setStyleSheet("""
            QWidget#ActivityBar {
                background-color: #252526;
                border-right: 1px solid #1e1e1e;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #858585;
                font-size: 18px;
                padding: 10px;
                margin: 2px 4px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2a2d2e;
                color: #ffffff;
            }
            QPushButton:checked {
                color: #ffffff;
                background-color: #37373d;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 8, 0, 8)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Logo da Marca ---
        from src.infrastructure.services.resource_service import ResourceService
        self.logo_label = QLabel()
        logo_path = ResourceService.get_logo_svg() # ou ico convertido
        if logo_path.exists():
            # Nota: Carregar SVG no Qt requer QtSvg, por simplicidade usamos texto/glow se não houver
            from PyQt6.QtGui import QPixmap
            # Pixmap placeholder para demo se fitz renderizar png do logo
            self.logo_label.setText("🔥") 
            self.logo_label.setStyleSheet("font-size: 24px; margin-bottom: 5px; color: #FFC107;")
        
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._add_separator()
        self.layout.addWidget(self.logo_label)
        
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.group.idClicked.connect(self.clicked.emit)
        
        # Botões principais
        for idx in [0, 1, 2, 3]:
            self._add_action(idx)
        
        self.layout.addStretch()
        
        # Botão de configurações (sempre ao fundo)
        self._add_action(99)

    def _add_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #2D3748; max-height: 1px; margin: 0 10px;")
        self.layout.addWidget(line)

    def _add_action(self, idx):
        icon, tooltip = self.ICONS.get(idx, ("❓", "Desconhecido"))
        btn = QPushButton(icon)
        btn.setCheckable(True)
        btn.setFixedSize(40, 40)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.group.addButton(btn, idx)
        self.layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        if idx == 0:
            btn.setChecked(True)

    def set_active(self, idx):
        btn = self.group.button(idx)
        if btn:
            btn.setChecked(True)
