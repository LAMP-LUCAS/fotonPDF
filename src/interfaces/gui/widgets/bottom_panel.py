from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QTextEdit
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback

class BottomPanel(QWidget):
    """
    Painel inferior estilo VS Code para Notificações e Logs.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(30)  # Apenas altura mínima
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
        self.title_label.setStyleSheet("color: #94A3B8; font-size: 10px; font-weight: bold;")
        
        # Engineering Telemetry (MM)
        self.telemetry = QLabel("W: 0.0mm | H: 0.0mm | X: 0.0mm | Y: 0.0mm")
        self.telemetry.setStyleSheet("color: #FFC107; font-family: 'JetBrains Mono'; font-size: 10px;")
        
        self.btn_toggle = QPushButton("⌄")
        self.btn_toggle.setStyleSheet("background: transparent; border: none; color: #858585; font-size: 14px;")
        self.btn_toggle.clicked.connect(self.toggle_expand)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.telemetry)
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

    @safe_ui_callback("Logging")
    def add_log(self, message, msg_type="info", color=None):
        if not color:
            color = "#94A3B8" if msg_type == "info" else "#f44747"
            if "⚠️" in message: color = "#cca700"
            
        self.log_view.append(f'<span style="color: {color};">> {message}</span>')
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())

    def update_telemetry(self, w_mm, h_mm, x_mm, y_mm):
        """Atualiza milímetros em tempo real."""
        self.telemetry.setText(f"W: {w_mm}mm | H: {h_mm}mm | X: {x_mm}mm | Y: {y_mm}mm")

    @safe_ui_callback("Bottom Panel Animation")
    def toggle_expand(self, checked=None):
        """Toggle com animação suave."""
        self._is_expanded = not self._is_expanded
        
        # Apenas anima a altura, sem restringir depois
        target_height = self._expanded_height if self._is_expanded else 30
        
        self.animation = QPropertyAnimation(self, b"minimumHeight")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(target_height)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self.animation.start()
        
        # Atualiza texto do botão (se existir na MainWindow)
        self.btn_toggle.setText("⌄" if self._is_expanded else "⌃")
