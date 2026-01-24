from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from src.infrastructure.services.resource_service import ResourceService

class TopBarWidget(QFrame):
    """
    Barra Superior Profissional (v4) com Busca Universal e Toggles de Layout.
    Modular e independente para fácil manutenção e plugins.
    """
    searchTriggered = pyqtSignal(str)
    toggleRequested = pyqtSignal(str) # 'left', 'right', 'bottom', 'activity'
    viewModeChanged = pyqtSignal(str) # 'scroll', 'table'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.setFixedHeight(48)
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(12, 0, 12, 0)
        self.main_layout.setSpacing(10)

        # --- SEÇÃO ESQUERDA: View Switcher ---
        self.left_section = QWidget()
        self.left_layout = QHBoxLayout(self.left_section)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(4)

        self.btn_scroll = self._create_nav_btn("📄 Scroll", "scroll", True)
        self.btn_table = self._create_nav_btn("🗂️ Mesa", "table", False)
        
        self.left_layout.addWidget(self.btn_scroll)
        self.left_layout.addWidget(self.btn_table)
        self.main_layout.addWidget(self.left_section)

        # --- SEÇÃO CENTRAL: Busca Universal ---
        self.center_section = QWidget()
        self.center_layout = QHBoxLayout(self.center_section)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.search_container = QFrame()
        self.search_container.setObjectName("SearchContainer")
        self.search_container.setFixedWidth(400)
        self.search_container.setFixedHeight(30)
        
        search_inner_layout = QHBoxLayout(self.search_container)
        search_inner_layout.setContentsMargins(10, 0, 10, 0)
        
        icon_label = QLabel("🔍")
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("Pesquisar documento ou comandos (Ctrl+P)")
        self.search_input.returnPressed.connect(self._on_search_enter)
        
        search_inner_layout.addWidget(icon_label)
        search_inner_layout.addWidget(self.search_input)
        
        self.center_layout.addWidget(self.search_container)
        self.main_layout.addWidget(self.center_section, stretch=1)

        # --- SEÇÃO DIREITA: Toggles ---
        self.right_section = QWidget()
        self.right_layout = QHBoxLayout(self.right_section)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(6)

        self.btn_side_l = self._create_toggle_btn("▥", "sidebar_left", "Alternar SideBar Esquerda")
        self.btn_bottom = self._create_toggle_btn("▲", "bottom_panel", "Alternar Painel Inferior")
        self.btn_side_r = self._create_toggle_btn("▤", "sidebar_right", "Alternar SideBar Direita")
        
        self.aec_tag = QLabel("● AEC-COPILOT")
        self.aec_tag.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 10px; margin-left: 10px;")

        self.right_layout.addWidget(self.btn_side_l)
        self.right_layout.addWidget(self.btn_bottom)
        self.right_layout.addWidget(self.btn_side_r)
        self.right_layout.addWidget(self.aec_tag)
        
        self.main_layout.addWidget(self.right_section)

    def _create_nav_btn(self, text, mode, active):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self._on_mode_clicked(mode))
        btn.setStyleSheet("""
            QPushButton { 
                background: #0F172A; border: 1px solid #334155; 
                padding: 4px 12px; border-radius: 6px; font-size: 11px; 
            }
            QPushButton:checked { background: #334155; color: white; border-color: #475569; }
        """)
        return btn

    def _create_toggle_btn(self, icon, target, tooltip):
        btn = QPushButton(icon)
        btn.setObjectName("ToggleBtn")
        btn.setProperty("active", True)
        btn.setToolTip(tooltip)
        btn.setFixedSize(28, 28)
        btn.clicked.connect(lambda: self._on_toggle_clicked(target, btn))
        return btn

    def _on_mode_clicked(self, mode):
        self.btn_scroll.setChecked(mode == "scroll")
        self.btn_table.setChecked(mode == "table")
        self.viewModeChanged.emit(mode)

    def _on_toggle_clicked(self, target, btn):
        # Toggle property visual
        is_active = btn.property("active")
        btn.setProperty("active", not is_active)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        self.toggleRequested.emit(target)

    def _on_search_enter(self):
        text = self.search_input.text()
        if text:
            self.searchTriggered.emit(text)

    def set_search_text(self, text):
        self.search_input.setText(text)
        self.search_input.setFocus()
