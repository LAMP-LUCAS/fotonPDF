from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty

class SideBar(QFrame):
    """Container colapsável para os painéis de ferramentas (Miniaturas, Busca, etc)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SideBar")
        self.setFixedWidth(300)
        self._is_collapsed = False
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        self.header = QWidget()
        self.header.setFixedHeight(35)
        h_layout = QVBoxLayout(self.header)
        h_layout.setContentsMargins(15, 0, 0, 0)
        self.title_label = QLabel("EXPLORER")
        self.title_label.setStyleSheet("font-weight: bold; color: #BBBBBB; font-size: 11px;")
        h_layout.addWidget(self.title_label)
        
        self.layout.addWidget(self.header)
        
        # Stacked Widget for Panels
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)
        
        # Animation
        self._width_animation = QPropertyAnimation(self, b"minimumWidth")
        self._width_animation.setDuration(200)
        self._width_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def add_panel(self, widget, title):
        self.stack.addWidget(widget)

    def show_panel(self, idx, title):
        if self._is_collapsed:
            self.toggle_collapse()
        
        self.stack.setCurrentIndex(idx)
        self.title_label.setText(title.upper())

    def toggle_collapse(self):
        start_val = self.width()
        end_val = 0 if not self._is_collapsed else 300
        
        self._width_animation.setStartValue(start_val)
        self._width_animation.setEndValue(end_val)
        self._width_animation.start()
        
        self._is_collapsed = not self._is_collapsed

    @pyqtProperty(int)
    def width_val(self):
        return self.width()

    @width_val.setter
    def width_val(self, val):
        self.setFixedWidth(val)
