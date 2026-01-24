from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback

class SideBar(QFrame):
    """Container colapsável para os painéis de ferramentas estilo Obsidian."""
    def __init__(self, parent=None, initial_width=300):
        super().__init__(parent)
        self.setObjectName("SideBar")
        self._base_width = initial_width
        self.setFixedWidth(initial_width)
        self._is_collapsed = False
        
        # Estilo Obsidian/VS Code
        self.setStyleSheet("""
            QFrame#SideBar {
                background-color: #252526;
                border-right: 1px solid #2d2d2d;
            }
            QLabel#SideBarTitle {
                font-weight: bold;
                color: #cccccc;
                font-size: 11px;
                letter-spacing: 1px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header (Slimmer)
        self.header = QWidget()
        self.header.setFixedHeight(35)
        self.header.setStyleSheet("background-color: #252526; border-bottom: 1px solid #2d2d2d;")
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
        
        # Animation setup
        self._animation = QPropertyAnimation(self, b"minimumWidth")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.OutQuint)
        
        # Sincronizar minimumWidth com maximumWidth para o Splitter não forçar o tamanho
        self._animation_max = QPropertyAnimation(self, b"maximumWidth")
        self._animation_max.setDuration(300)
        self._animation_max.setEasingCurve(QEasingCurve.Type.OutQuint)

    def add_panel(self, widget, title):
        self.stack.addWidget(widget)

    @safe_ui_callback("Sidebar Panel Switch")
    def show_panel(self, idx, title):
        if self._is_collapsed:
            self.toggle_collapse()
        
        if idx < self.stack.count():
            self.stack.setCurrentIndex(idx)
            self.title_label.setText(title.upper())

    @safe_ui_callback("Sidebar Animation")
    def toggle_collapse(self, checked=None):
        start_val = self.width()
        end_val = 0 if not self._is_collapsed else self._base_width
        
        self._animation.setStartValue(start_val)
        self._animation.setEndValue(end_val)
        self._animation_max.setStartValue(start_val)
        self._animation_max.setEndValue(end_val)
        
        self._animation.start()
        self._animation_max.start()
        
        self._is_collapsed = not self._is_collapsed

    def set_title(self, text):
        self.title_label.setText(text.upper())
