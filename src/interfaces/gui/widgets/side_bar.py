from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QFrame, QSizePolicy
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal
from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback
from src.infrastructure.adapters.gui_settings_adapter import GUISettingsAdapter
from PyQt6.QtCore import QTimer

class SideBarHeader(QWidget):
    """Header que detecta clique duplo para atalho inteligente."""
    doubleClicked = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

class SideBar(QFrame):
    """Container colapsável para os painéis de ferramentas estilo Obsidian."""
    def __init__(self, parent=None, initial_width=260):
        super().__init__(parent)
        self.setObjectName("SideBar")
        
        # Persistência
        self.settings = GUISettingsAdapter()
        saved_width = self.settings.get("sidebar_width", initial_width)
        saved_collapsed = self.settings.get("sidebar_collapsed", True)
        
        self._base_width = saved_width  # Largura "Padrão"
        self._last_width = saved_width  # Largura "Usuário"
        self._is_collapsed = saved_collapsed
        
        # Debounce para evitar salvar a cada pixel de resize
        self._resize_timer = QTimer()
        self._resize_timer.setInterval(1000)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._save_width_state)
        
        # Permitir redimensionamento
        self.setMinimumWidth(0)
        
        if self._is_collapsed:
            self.setFixedWidth(0)
        else:
            self.resize(saved_width, self.height())
        
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
        self.layout.addWidget(self.stack, 1) # Stretch 1 is CRITICAL for expansion
        
        # Pre-populate with 4 placeholder slots (indices 0, 1, 2, 3)
        # This ensures panel indices match ActivityBar button indices
        for _ in range(4):
            placeholder = QWidget()
            self.stack.addWidget(placeholder)
        
        # Animations
        self._animation = QPropertyAnimation(self, b"minimumWidth")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.OutQuint)
        
        self._animation_max = QPropertyAnimation(self, b"maximumWidth")
        self._animation_max.setDuration(300)
        self._animation_max.setEasingCurve(QEasingCurve.Type.OutQuint)
        
        self._animation_max.finished.connect(self._on_animation_finished)

    def add_panel(self, widget, title, idx=None):
        """Adds a panel at a specific index, replacing any placeholder."""
        from src.infrastructure.services.logger import log_debug
        log_debug(f"SideBar: Adicionando painel '{title}' no índice {idx}")
        
        if idx is not None and 0 <= idx < self.stack.count():
            # Remove placeholder and insert real widget at same index
            old = self.stack.widget(idx)
            self.stack.removeWidget(old)
            old.deleteLater()
            self.stack.insertWidget(idx, widget)
            log_debug(f"SideBar: Placeholder substituído no índice {idx} por {widget}")
            
            # Garantir que o stack reflita a mudança imediatamente se o índice for o ativo
            if self.stack.currentIndex() == idx:
                self.stack.setCurrentWidget(widget)
                widget.show() # Safe here because it has a parent now
                widget.update()
        else:
            # Fallback: append to end (legacy behavior)
            self.stack.addWidget(widget)
            log_debug(f"SideBar: Painel anexado ao final (Índice {self.stack.count()-1})")

    @safe_ui_callback("Sidebar Panel Switch")
    def show_panel(self, idx, title):
        from src.infrastructure.services.logger import log_debug
        
        if self._is_collapsed:
            log_debug("SideBar: Auto-expandindo para exibir painel")
            self.toggle_collapse()
        
        if idx < self.stack.count():
            self.stack.setCurrentIndex(idx)
            current_w = self.stack.currentWidget()
            log_debug(f"SideBar: Mostrando painel {idx} ({title}). Widget visível? {current_w.isVisible()}")
            self.title_label.setText(title.upper())
            
            # Forçar repaint
            current_w.update()

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
            self.collapse()
        else:
            self.expand()

    def collapse(self):
        """Força o fechamento da sidebar."""
        if not self._is_collapsed:
            self._last_width = self.width()
            self._animate_to(0)
            self._is_collapsed = True
            self.settings.set("sidebar_collapsed", True)

    def expand(self):
        """Força a abertura da sidebar."""
        if self._is_collapsed:
            target = self._last_width if self._last_width > 50 else self._base_width
            self._animate_to(target)
            self._is_collapsed = False
            self.settings.set("sidebar_collapsed", False)

    def _on_animation_finished(self):
        """Libera o redimensionamento após expandir."""
        if not self._is_collapsed:
            self.setMaximumWidth(16777215)
            self.setMinimumWidth(150) 

    def set_title(self, text):
        self.title_label.setText(text.upper())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Só salva se não estiver colapsado e não estiver animando (aproximado)
        if not self._is_collapsed and self.width() > 50:
            self._base_width = self.width()
            self._resize_timer.start()

    def _save_width_state(self):
        """Persiste a largura atual."""
        if self.width() > 50:
            self.settings.set("sidebar_width", self.width())
