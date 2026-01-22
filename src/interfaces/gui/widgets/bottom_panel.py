from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QTextEdit
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect

class BottomPanel(QWidget):
    """
    Painel inferior estilo VS Code para Notificações e Logs.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30) # Inicia colapsado/barra
        self._expanded_height = 200
        self._is_expanded = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Barra de Cabeçalho (Botões de Toggle)
        self.header = QWidget()
        self.header.setFixedHeight(30)
        self.header.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #333;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 0, 10, 0)
        
        self.title_label = QLabel("NOTIFICATIONS")
        self.title_label.setStyleSheet("color: #858585; font-size: 11px; font-weight: bold;")
        
        self.btn_toggle = QPushButton("⌄")
        self.btn_toggle.setStyleSheet("background: transparent; border: none; color: #858585; font-size: 14px;")
        self.btn_toggle.clicked.connect(self.toggle_expand)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_toggle)
        
        # Área de Conteúdo (Stack)
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #252525;")
        
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #1e1e1e; color: #cccccc; border: none; font-family: 'Consolas', monospace;")
        self.content_stack.addWidget(self.log_view)
        
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.content_stack)
        
        self.add_log("fotonPDF ready. System initialized.")

    def add_log(self, message):
        self.log_view.append(f"> {message}")

    def toggle_expand(self):
        self._is_expanded = not self._is_expanded
        
        start_height = self.height()
        end_height = self._expanded_height if self._is_expanded else 30
        
        self.animation = QPropertyAnimation(self, b"minimumHeight")
        self.animation.setDuration(300)
        self.animation.setStartValue(start_height)
        self.animation.setEndValue(end_height)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.animation2 = QPropertyAnimation(self, b"maximumHeight")
        self.animation2.setDuration(300)
        self.animation2.setStartValue(start_height)
        self.animation2.setEndValue(end_height)
        self.animation2.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        self.animation.start()
        self.animation2.start()
        
        self.btn_toggle.setText("⌄" if self._is_expanded else "⌃")
