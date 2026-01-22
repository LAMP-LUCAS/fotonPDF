from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QSize, pyqtSignal

class FloatingNavBar(QFrame):
    """Barra de navegação flutuante semi-transparente."""
    zoomIn = pyqtSignal()
    zoomOut = pyqtSignal()
    resetZoom = pyqtSignal()
    nextPage = pyqtSignal()
    prevPage = pyqtSignal()
    toggleSplit = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setObjectName("FloatingNavBar")
        self.setStyleSheet("""
            #FloatingNavBar {
                background-color: rgba(30, 30, 30, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 5px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #CCCCCC;
                font-size: 16px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
            QLabel {
                color: #858585;
                font-size: 12px;
                margin: 0 10px;
            }
        """)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(5)
        
        # Navigation
        self.btn_prev = QPushButton("◀")
        self.btn_prev.clicked.connect(self.prevPage.emit)
        
        self.page_label = QLabel("1 / 1")
        
        self.btn_next = QPushButton("▶")
        self.btn_next.clicked.connect(self.nextPage.emit)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("color: rgba(255, 255, 255, 0.1);")
        
        # Zoom
        self.btn_min = QPushButton("−")
        self.btn_min.clicked.connect(self.zoomOut.emit)
        
        self.btn_reset = QPushButton("100%")
        self.btn_reset.setStyleSheet("font-size: 11px;")
        self.btn_reset.clicked.connect(self.resetZoom.emit)
        
        self.btn_plus = QPushButton("+")
        self.btn_plus.clicked.connect(self.zoomIn.emit)
        
        # Split Button
        self.btn_split = QPushButton("◫")
        self.btn_split.setToolTip("Dividir Editor (Split)")
        self.btn_split.clicked.connect(self.toggleSplit.emit)
        
        self.layout.addWidget(self.btn_prev)
        self.layout.addWidget(self.page_label)
        self.layout.addWidget(self.btn_next)
        self.layout.addWidget(sep)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_reset)
        self.layout.addWidget(self.btn_plus)
        self.layout.addWidget(self.btn_split)
        
        self.setFixedSize(340, 40)

    def update_page(self, current, total):
        self.page_label.setText(f"{current + 1} / {total}")
