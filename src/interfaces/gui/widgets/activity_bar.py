from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QSize

class ActivityBar(QWidget):
    """Barra vertical lateral estilo VS Code com estética Neon-AEC Premium."""
    clicked = pyqtSignal(int) # Emite o índice da aba selecionada

    # Mapeamento de ícones (Nomenclatura genérica e universal)
    ICONS = {
        0: ("📂", "Páginas"),          # Miniaturas / Navegador de Páginas
        1: ("🔎", "Pesquisar"),         # Busca Textual
        2: ("📚", "Índice"),            # TOC / Sumário
        3: ("🖊️", "Notas"),             # Anotações do Usuário
        99: ("⚙️", "Ajustes"),          # Configurações
    }


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ActivityBar")
        self.setFixedWidth(48) # Matches concept.html
        
        # Estilo alinhado com concept.html
        self.setStyleSheet("""
            QWidget#ActivityBar {
                background-color: #18181a;
                border-right: 1px solid #2b2b2b;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #8e918f;
                font-size: 20px;
                padding: 0px;
                margin: 0px;
                border-radius: 6px;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #2d2d2e;
            }
            QPushButton:checked {
                color: #ffffff;
                border-left: 2px solid #FFC107;
                border-radius: 0px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 12, 0, 12) # Matches concept padding
        self.layout.setSpacing(12) # Matches concept gap
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Logo da Marca ---
        from src.infrastructure.services.resource_service import ResourceService
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_path = ResourceService.get_logo_ico()
        if logo_path.exists():
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.logo_label.setPixmap(scaled)
            else:
                self.logo_label.setText("🔥")
        else:
            self.logo_label.setText("🔥")

        self.layout.addWidget(self.logo_label)
        self._add_separator()
        
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
        line.setStyleSheet("background-color: #2b2b2b; max-height: 1px; margin: 5px 8px;")
        self.layout.addWidget(line)

    def _add_action(self, idx):
        icon, tooltip = self.ICONS.get(idx, ("❓", "Desconhecido"))
        btn = QPushButton(icon)
        btn.setCheckable(True)
        btn.setFixedSize(32, 32) # Matches concept.html .activity-icon
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
