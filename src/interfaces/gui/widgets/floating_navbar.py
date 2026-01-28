from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QGraphicsOpacityEffect, QMenu, QWidgetAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QPoint, QEasingCurve, QTimer
from PyQt6.QtGui import QAction, QIcon, QColor, QPalette

class ModernNavBar(QFrame):
    """
    Barra de navegação flutuante de última geração.
    - Translucidez dinâmica (0.1 ociosa / 0.7 ativa).
    - Submenus colapsáveis para Zoom e Ferramentas.
    - Design premium com animações suaves.
    """
    zoomIn = pyqtSignal()
    zoomOut = pyqtSignal()
    resetZoom = pyqtSignal()
    nextPage = pyqtSignal()
    prevPage = pyqtSignal()
    toggleSplit = pyqtSignal()
    
    # Novos sinais para funções avançadas
    fitWidth = pyqtSignal()
    fitHeight = pyqtSignal()
    fitPage = pyqtSignal()
    viewAll = pyqtSignal()
    setTool = pyqtSignal(str) # 'pan', 'selection', 'zoom_area'
    highlightColor = pyqtSignal(str)  # Emits color hex code for highlights

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ModernNavBar")
        self.setMouseTracking(True)
        
        # Efeito de opacidade para controle dinâmico
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.3) # Visível mas discreto por padrão
        self.setGraphicsEffect(self.opacity_effect)
        
        # Animação de opacidade
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.setStyleSheet("""
            #ModernNavBar {
                background-color: rgba(15, 23, 42, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 24px;
                padding: 4px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #E2E8F0;
                font-size: 14px;
                padding: 8px;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: #38BDF8;
            }
            QPushButton#main_btn {
                font-weight: bold;
                padding: 8px 12px;
            }
            QLabel {
                color: #94A3B8;
                font-size: 12px;
                margin: 0 8px;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
        """)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 12, 0)
        self.layout.setSpacing(4)
        
        self._setup_ui()
        self.setFixedSize(self.layout.sizeHint().width() + 40, 48)

    def _setup_ui(self):
        # 1. Navegação de Páginas
        self.btn_prev = QPushButton("◀") 
        self.btn_prev.setToolTip("Página Anterior (Backspace)")
        self.btn_prev.clicked.connect(self.prevPage.emit)
        
        self.page_label = QLabel("1 / 1")
        
        self.btn_next = QPushButton("▶")
        self.btn_next.setToolTip("Próxima Página (Space)")
        self.btn_next.clicked.connect(self.nextPage.emit)
        
        # 2. Separador
        sep1 = self._create_separator()
        
        # 3. Submenu de Ferramentas (Mouse)
        self.btn_tools = QPushButton("🛠") 
        self.btn_tools.setObjectName("main_btn")
        self.btn_tools.setToolTip("Ferramentas de Interação")
        self._setup_tools_menu()
        
        # 4. Submenu de Zoom
        self.btn_zoom = QPushButton("100%")
        self.btn_zoom.setObjectName("main_btn")
        self.btn_zoom.setToolTip("Opções de Zoom e Enquadramento")
        self._setup_zoom_menu()
        
        # 5. Highlight Color Palette
        self.btn_highlight = QPushButton("🖍")
        self.btn_highlight.setObjectName("main_btn")
        self.btn_highlight.setToolTip("Cor de Marcação")
        self._setup_highlight_menu()
        
        # 6. Split/Extras
        sep2 = self._create_separator()
        self.btn_split = QPushButton("◫")
        self.btn_split.setToolTip("Dividir Visualização (Split)")
        self.btn_split.clicked.connect(self.toggleSplit.emit)
        
        # Adicionar ao layout
        self.layout.addWidget(self.btn_prev)
        self.layout.addWidget(self.page_label)
        self.layout.addWidget(self.btn_next)
        self.layout.addWidget(sep1)
        self.layout.addWidget(self.btn_tools)
        self.layout.addWidget(self.btn_zoom)
        self.layout.addWidget(self.btn_highlight)
        self.layout.addWidget(sep2)
        self.layout.addWidget(self.btn_split)

    def _create_separator(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); margin: 10px 4px;")
        return sep

    def _setup_tools_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        pan_act = QAction("✋ Mover (Pan)", self)
        pan_act.triggered.connect(lambda: self.setTool.emit("pan"))
        
        sel_act = QAction("🔍 Seleção de Texto", self)
        sel_act.triggered.connect(lambda: self.setTool.emit("selection"))
        
        zarea_act = QAction("🖼 Zoom por Área", self)
        zarea_act.triggered.connect(lambda: self.setTool.emit("zoom_area"))
        
        menu.addAction(pan_act)
        menu.addAction(sel_act)
        menu.addAction(zarea_act)
        
        self.btn_tools.setMenu(menu)

    def _setup_highlight_menu(self):
        """Creates a color palette menu for highlight annotations."""
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style() + """
            QPushButton#colorBtn {
                min-width: 24px;
                min-height: 24px;
                max-width: 24px;
                max-height: 24px;
                border-radius: 12px;
                margin: 2px;
            }
        """)
        
        # Color palette with common highlight colors
        colors = [
            ("#FFEB3B", "Amarelo"),
            ("#4CAF50", "Verde"),
            ("#2196F3", "Azul"),
            ("#F44336", "Vermelho"),
            ("#E91E63", "Rosa"),
        ]
        
        # Create a widget for horizontal color buttons
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        color_layout.setContentsMargins(8, 8, 8, 8)
        color_layout.setSpacing(4)
        
        for hex_color, name in colors:
            btn = QPushButton()
            btn.setObjectName("colorBtn")
            btn.setToolTip(name)
            btn.setStyleSheet(f"background-color: {hex_color}; border: 2px solid rgba(255,255,255,0.3);")
            btn.clicked.connect(lambda checked, c=hex_color: self._on_color_selected(c, menu))
            color_layout.addWidget(btn)
        
        color_action = QWidgetAction(self)
        color_action.setDefaultWidget(color_widget)
        menu.addAction(color_action)
        
        self.btn_highlight.setMenu(menu)
        self._current_highlight_color = "#FFEB3B"  # Default: yellow
    
    def _on_color_selected(self, color: str, menu: QMenu):
        """Handles color selection and updates the highlight button."""
        self._current_highlight_color = color
        # Update button to show selected color
        self.btn_highlight.setStyleSheet(f"background-color: {color}; border-radius: 18px;")
        self.highlightColor.emit(color)
        menu.close()

    def _setup_zoom_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._menu_style())
        
        z_in = QAction("➕ Zoom In (+)", self)
        z_in.triggered.connect(self.zoomIn.emit)
        
        z_out = QAction("➖ Zoom Out (-)", self)
        z_out.triggered.connect(self.zoomOut.emit)
        
        z_100 = QAction("🎯 Tamanho Real (100%)", self)
        z_100.triggered.connect(self.resetZoom.emit)
        
        menu.addSeparator()
        
        fit_w = QAction("↔ Ajustar Largura", self)
        fit_w.triggered.connect(self.fitWidth.emit)
        
        fit_h = QAction("↕ Ajustar Altura", self)
        fit_h.triggered.connect(self.fitHeight.emit)
        
        fit_p = QAction("📄 Ver Página Inteira", self)
        fit_p.triggered.connect(self.fitPage.emit)
        
        menu.addSeparator()
        
        view_all = QAction("🔲 Visão Geral (Mesa)", self)
        view_all.triggered.connect(self.viewAll.emit)
        
        menu.addAction(z_in)
        menu.addAction(z_out)
        menu.addAction(z_100)
        menu.addSeparator()
        menu.addAction(fit_w)
        menu.addAction(fit_h)
        menu.addAction(fit_p)
        menu.addSeparator()
        menu.addAction(view_all)
        
        self.btn_zoom.setMenu(menu)

    def _menu_style(self):
        return """
            QMenu {
                background-color: #0F172A;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                color: #E2E8F0;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #1E293B;
                color: #38BDF8;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(255, 255, 255, 0.05);
                margin: 4px 8px;
            }
        """

    def enterEvent(self, event):
        """Ativa a barra ao passar o mouse."""
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(self.opacity_effect.opacity())
        self.opacity_anim.setEndValue(0.9) # Menos transparente quando ativo
        self.opacity_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Esconde a barra ao sair o mouse."""
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(self.opacity_effect.opacity())
        self.opacity_anim.setEndValue(0.3) # Mais visível mesmo ociosa
        self.opacity_anim.start()
        super().leaveEvent(event)

    def update_page(self, current, total):
        self.page_label.setText(f"{current + 1} / {total}")
        self.setFixedSize(self.layout.sizeHint().width() + 40, 48)

# Mapeamento para retrocompatibilidade se necessário
FloatingNavBar = ModernNavBar
