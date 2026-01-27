from PyQt6.QtWidgets import QFrame, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QIcon

class NavHub(QFrame):
    """
    Navigation Hub (SteeringWheel): HUD flutuante para ferramentas de navegação.
    Design inspirado em software BIM/CAD para acesso ultra-rápido.
    """
    toolChanged = pyqtSignal(str) # 'pan', 'select', 'zoom_in', 'zoom_out', 'fit_width', 'fit_page'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavHub")
        self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setStyleSheet("""
            #NavHub {
                background-color: rgba(15, 23, 42, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 30px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #94A3B8;
                font-size: 18px;
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: #F8FAFC;
            }
            QPushButton:checked {
                background-color: #3B82F6;
                color: white;
            }
            QLabel {
                color: #475569;
                font-size: 10px;
                font-weight: bold;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(10)
        
        # Ferramentas
        self.btn_pan = self._create_btn("🖐️", "Mover (P)", "pan", checkable=True)
        self.btn_select = self._create_btn("🎯", "Selecionar (S)", "select", checkable=True)
        
        # Separator
        self.layout.addWidget(self._create_sep())
        
        self.btn_zoom_in = self._create_btn("🔍+", "Zoom In (Ctrl +)", "zoom_in")
        self.btn_zoom_out = self._create_btn("🔍-", "Zoom Out (Ctrl -)", "zoom_out")
        
        # Separator
        self.layout.addWidget(self._create_sep())
        
        self.btn_fit_w = self._create_btn("↔️", "Largura (Ctrl 1)", "fit_width")
        self.btn_fit_p = self._create_btn("📄", "Página (Ctrl 2)", "fit_page")
        
        # Iniciar no modo Pan por padrão
        self.btn_pan.setChecked(True)
        
        self.setFixedSize(360, 60)
        self.hide() # Inicia oculto

    def _create_btn(self, icon, tooltip, action, checkable=False):
        btn = QPushButton(icon)
        btn.setToolTip(tooltip)
        if checkable:
            btn.setCheckable(True)
            # Garantir que apenas um do grupo checkable esteja ativo
            btn.clicked.connect(lambda: self._handle_toggle(action))
        else:
            btn.clicked.connect(lambda: self.toolChanged.emit(action))
        
        self.layout.addWidget(btn)
        return btn

    def _create_sep(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); margin: 10px 0;")
        return sep

    def _handle_toggle(self, action):
        if action == "pan":
            self.btn_select.setChecked(False)
            self.btn_pan.setChecked(True)
        elif action == "select":
            self.btn_pan.setChecked(False)
            self.btn_select.setChecked(True)
        self.toolChanged.emit(action)

    def set_tool(self, tool_name):
        """Atualiza o estado visual baseado em atalhos externos."""
        if tool_name == "pan":
            self.btn_pan.setChecked(True)
            self.btn_select.setChecked(False)
        elif tool_name == "select":
            self.btn_select.setChecked(True)
            self.btn_pan.setChecked(False)

    def show_animated(self):
        self.show()
        # Animação simples de fade-in/slide up? Omitido por brevidade e robustez inicial.
