from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal
from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback

class SideBarHeader(QWidget):
    """Header que detecta clique duplo para atalho inteligente."""
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

class SideBar(QFrame):
    """Container colapsável para os painéis de ferramentas estilo Obsidian."""
    def __init__(self, parent=None, initial_width=300):
        super().__init__(parent)
        self.setObjectName("SideBar")
        
        self._base_width = initial_width  # Largura "Padrão"
        self._last_width = initial_width  # Largura "Usuário" (para restore)
        self._is_collapsed = False
        
        # Permitir redimensionamento
        self.setMinimumWidth(0)
        self.resize(initial_width, self.height())
        
        # Estilo Obsidian/VS Code
        self.setStyleSheet("""
            QFrame#SideBar {
                background-color: #252526;
                border-right: 1px solid #2d2d2d;
            }
            QLabel#SideBarTitle {
                font-weight: bold;
                color: #71717A;
                font-size: 11px;
                letter-spacing: 1px;
                text-transform: uppercase;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header (Smart)
        self.header = SideBarHeader()
        self.header.setFixedHeight(35)
        self.header.setStyleSheet("background-color: #252526; border-bottom: 1px solid #2d2d2d;")
        self.header.doubleClicked.connect(self._on_smart_resize)
        
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(15, 0, 10, 0)
        
        self.title_label = QLabel("EXPLORER")
        self.title_label.setObjectName("SideBarTitle")
        
        h_layout.addWidget(self.title_label)
        h_layout.addStretch()
        
        self.layout.addWidget(self.header)
        
        # Stacked Widget for Panels
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        # Animations
        self._animation = QPropertyAnimation(self, b"minimumWidth")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.OutQuint)
        
        self._animation_max = QPropertyAnimation(self, b"maximumWidth")
        self._animation_max.setDuration(300)
        self._animation_max.setEasingCurve(QEasingCurve.Type.OutQuint)
        
        self._animation_max.finished.connect(self._on_animation_finished)

    def add_panel(self, widget, title):
        self.stack.addWidget(widget)

    @safe_ui_callback("Sidebar Panel Switch")
    def show_panel(self, idx, title):
        if self._is_collapsed:
            self.toggle_collapse()
        
        if idx < self.stack.count():
            self.stack.setCurrentIndex(idx)
            self.title_label.setText(title.upper())

    def _on_smart_resize(self):
        """
        Lógica 'Smart Shortcut':
        - Se estiver fora do padrão -> Anima para padrão.
        - Se estiver no padrão -> Colapsa.
        """
        if self._is_collapsed:
            return
            
        current_width = self.width()
        standard = self._base_width
        tolerance = 10
        
        if abs(current_width - standard) > tolerance:
            # Caso 1: Fora do padrão -> Redefinir para padrão
            self._animate_to(standard)
            self.setMaximumWidth(16777215) # Garante que nao trava
        else:
            # Caso 2: Já no padrão -> Colapsar
            self.toggle_collapse()

    def _animate_to(self, target_width):
        """Helper para animar largura."""
        self._animation.setStartValue(self.width())
        self._animation.setEndValue(target_width)
        self._animation_max.setStartValue(self.width())
        self._animation_max.setEndValue(target_width)
        self._animation.start()
        self._animation_max.start()

    @safe_ui_callback("Sidebar Animation")
    def toggle_collapse(self, checked=None):
        if not self._is_collapsed:
            # Colapsando
            self._last_width = self.width()
            self._animate_to(0)
        else:
            # Expandindo
            # Se a última largura for 0 (erro), usa base
            target = self._last_width if self._last_width > 50 else self._base_width
            self._animate_to(target)
            
        self._is_collapsed = not self._is_collapsed

    def _on_animation_finished(self):
        """Libera o redimensionamento após expandir."""
        if not self._is_collapsed:
            self.setMaximumWidth(16777215)
            self.setMinimumWidth(150) 

    def set_title(self, text):
        self.title_label.setText(text.upper())
