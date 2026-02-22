from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QTextEdit
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback

class BottomPanelHeader(QWidget):
    """Header que detecta clique duplo para atalho inteligente."""
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

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
        self.header = BottomPanelHeader()
        self.header.doubleClicked.connect(self._on_smart_toggle)
        self.header.setFixedHeight(30)
        self.header.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #333;")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 0, 10, 0)
        
        # Título da Barra (Vira o resumo quando colapsado)
        self.title_label = QLabel("INFORMATION BAR")
        self.title_label.setStyleSheet("color: #71717A; font-weight: bold; font-size: 11px; letter-spacing: 1px; background-color: transparent;")
        
        # Último Log (Visível apenas quando colapsado)
        self.summary_log = QLabel("")
        self.summary_log.setStyleSheet("color: #E2E8F0; font-family: 'Consolas', monospace; font-size: 11px; margin-left: 10px; background-color: transparent;")
        self.summary_log.show() # Inicialmente colapsado
        
        # Engineering Telemetry (MM)
        self.telemetry = QLabel("W: 0.0mm | H: 0.0mm | X: 0.0mm | Y: 0.0mm")
        self.telemetry.setStyleSheet("color: #FFC107; font-family: 'JetBrains Mono'; font-size: 10px; background-color: transparent;")
        
        self.btn_toggle = QPushButton("⌃")
        self.btn_toggle.setObjectName("ToggleBtn") # Usa estilo novo
        self.btn_toggle.clicked.connect(self.toggle_expand)
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.summary_log)
        header_layout.addStretch()
        header_layout.addWidget(self.telemetry)
        header_layout.addWidget(self.btn_toggle)
        
        # Área de Conteúdo (Stack)
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #252525;")
        self.content_stack.hide() # Inicialmente colapsado
        
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
            
        # Adiciona ao log completo
        self.log_view.append(f'<span style="color: {color};">> {message}</span>')
        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())
        
        # Atualiza o resumo
        clean_msg = message.replace("<br>", " ").strip()
        self.summary_log.setText(f">> {clean_msg}")
        # Se for erro, mudar cor do resumo
        text_color = color if color else "#E2E8F0"
        self.summary_log.setStyleSheet(f"color: {text_color}; font-family: 'Consolas', monospace; font-size: 11px; margin-left: 10px; background-color: transparent;")

    def update_telemetry(self, w_mm, h_mm, x_mm, y_mm):
        """Atualiza milímetros em tempo real. Se x ou y forem -1, indica apenas tamanho da página."""
        if x_mm == -1 or y_mm == -1:
            self.telemetry.setText(f"PAGE: {w_mm:.1f}x{h_mm:.1f}mm")
            self.telemetry.setStyleSheet("color: #94A3B8; font-family: 'JetBrains Mono'; font-size: 10px; background-color: transparent;")
        else:
            self.telemetry.setText(f"SEL: {w_mm:.1f}x{h_mm:.1f}mm | X: {x_mm:.1f} Y: {y_mm:.1f}")
            self.telemetry.setStyleSheet("color: #FFC107; font-family: 'JetBrains Mono'; font-size: 10px; background-color: transparent;")

    @safe_ui_callback("Bottom Panel Animation")
    def toggle_expand(self, checked=None):
        """Toggle com animação suave e lógica de resumo."""
        self._is_expanded = not self._is_expanded
        
        target_height = self._expanded_height if self._is_expanded else 30
        
        # Controle de visibilidade do resumo
        if self._is_expanded:
            self.summary_log.hide()
            self.content_stack.show()
        else:
            # Só mostra o resumo após animação ou imediatamente?
            # Imediatamente para feedback instantâneo ao fechar
            self.summary_log.show()
            
        self.animation = QPropertyAnimation(self, b"minimumHeight")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(target_height)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        # Ao terminar de colapsar, esconder o stack
        if not self._is_expanded:
            self.animation.finished.connect(self.content_stack.hide)
        else:
            self.content_stack.show()
            self.animation.finished.connect(lambda: None) # Remove conexões anteriores
            
        self.animation.start()
        
        self.btn_toggle.setText("⌄" if self._is_expanded else "⌃")

    def _on_smart_toggle(self):
        """
        Lógica 'Smart Shortcut' para o painel inferior.
        - Se estiver colapsado ou fora do padrão -> Expande para 200px.
        - Se estiver expandido no padrão -> Colapsa.
        """
        current_height = self.height()
        standard = self._expanded_height
        tolerance = 10
        
        # Se estiver muito próximo do padrão e expandido => Colapsar
        if self._is_expanded and abs(current_height - standard) < tolerance:
            self.toggle_expand()
        else:
            # Caso contrário (colapsado ou tamanho customizado) => Expandir para padrão
            if not self._is_expanded:
                self.toggle_expand()
            else:
                # Se já estiver expandido mas com tamanho customizado, redefinir para padrão
                self.animation.setStartValue(current_height)
                self.animation.setEndValue(standard)
                self.animation.start()
