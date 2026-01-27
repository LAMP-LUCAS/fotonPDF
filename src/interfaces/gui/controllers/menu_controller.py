"""
MenuController - Controlador de Menus para fotonPDF
Centraliza a criação e gerenciamento de ações de menu, desacoplando da MainWindow.

Arquitetura: Interfaces/GUI/Controllers (Camada de Interface)
Padrão: Controller Pattern - Orquestra ações sem conhecer detalhes de implementação.
"""
from pathlib import Path
from typing import Callable, Dict, Optional

from PyQt6.QtWidgets import QMenu, QMenuBar
from PyQt6.QtGui import QAction, QKeySequence

from src.infrastructure.services.logger import log_debug


class MenuController:
    """
    Controlador responsável por criar e gerenciar todas as ações de menu.
    
    Este controlador segue o padrão de inversão de dependência:
    - Recebe referência à MainWindow para executar ações
    - Não importa nem conhece detalhes de widgets específicos
    - Todas as ações são delegadas via callbacks
    """

    def __init__(self, main_window):
        """
        Inicializa o controlador de menus.
        
        Args:
            main_window: Referência à janela principal para acesso a componentes.
        """
        self.main_window = main_window
        self._actions: Dict[str, QAction] = {}
        self._menus: Dict[str, QMenu] = {}

    def setup_app_menu(self) -> QMenu:
        """
        Cria e configura o menu popup principal da aplicação.
        
        Returns:
            QMenu configurado com todos os submenus e ações.
        """
        log_debug("MenuController: Iniciando setup do menu principal")
        
        app_menu = QMenu(self.main_window)
        app_menu.setObjectName("AppMenu")
        self._apply_menu_style(app_menu)
        
        # Criar submenus
        self._menus["file"] = self._create_file_menu(app_menu)
        self._menus["edit"] = self._create_edit_menu(app_menu)
        self._menus["view"] = self._create_view_menu(app_menu)
        self._menus["tools"] = self._create_tools_menu(app_menu)
        self._menus["config"] = self._create_config_menu(app_menu)
        
        log_debug("MenuController: Menu principal configurado com sucesso")
        return app_menu

    def _create_file_menu(self, parent: QMenu) -> QMenu:
        """Cria o submenu Arquivo."""
        menu = parent.addMenu("📂 Arquivo")
        
        # Abrir
        open_action = QAction("Abrir...", self.main_window)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._action_open)
        menu.addAction(open_action)
        self._actions["open"] = open_action
        
        # Salvar
        save_action = QAction("Salvar", self.main_window)
        save_action.setShortcut("Ctrl+S")
        save_action.setEnabled(False)
        save_action.triggered.connect(self._action_save)
        menu.addAction(save_action)
        self._actions["save"] = save_action
        
        # Salvar Como
        save_as_action = QAction("Salvar Como...", self.main_window)
        save_as_action.setEnabled(False)
        save_as_action.triggered.connect(self._action_save_as)
        menu.addAction(save_as_action)
        self._actions["save_as"] = save_as_action
        
        menu.addSeparator()
        
        # Unir PDFs
        merge_action = QAction("Unir PDFs...", self.main_window)
        merge_action.triggered.connect(self._action_merge)
        menu.addAction(merge_action)
        self._actions["merge"] = merge_action
        
        # Extrair Páginas
        extract_action = QAction("Extrair Páginas...", self.main_window)
        extract_action.setEnabled(False)
        extract_action.triggered.connect(self._action_extract)
        menu.addAction(extract_action)
        self._actions["extract"] = extract_action
        
        # Submenu Exportar
        export_menu = menu.addMenu("Exportar")
        export_menu.addAction("PNG High-DPI").triggered.connect(lambda: self._action_export("png"))
        export_menu.addAction("SVG").triggered.connect(lambda: self._action_export("svg"))
        export_menu.addAction("Markdown").triggered.connect(lambda: self._action_export("md"))
        
        return menu

    def _create_edit_menu(self, parent: QMenu) -> QMenu:
        """Cria o submenu Editar."""
        menu = parent.addMenu("✏️ Editar")
        
        # Rotação
        rotate_left = QAction("Girar -90°", self.main_window)
        rotate_left.setEnabled(False)
        rotate_left.triggered.connect(lambda: self._action_rotate(-90))
        menu.addAction(rotate_left)
        self._actions["rotate_left"] = rotate_left
        
        rotate_right = QAction("Girar +90°", self.main_window)
        rotate_right.setEnabled(False)
        rotate_right.triggered.connect(lambda: self._action_rotate(90))
        menu.addAction(rotate_right)
        self._actions["rotate_right"] = rotate_right
        
        menu.addSeparator()
        
        # Realçar
        highlight = QAction("Modo Realçar", self.main_window)
        highlight.setCheckable(True)
        highlight.triggered.connect(self._action_highlight_toggle)
        menu.addAction(highlight)
        self._actions["highlight"] = highlight
        
        return menu

    def _create_view_menu(self, parent: QMenu) -> QMenu:
        """Cria o submenu Ver."""
        menu = parent.addMenu("👁️ Ver")
        
        # Zoom submenu
        zoom_menu = menu.addMenu("Zoom")
        zoom_menu.addAction("Aumentar").triggered.connect(self._action_zoom_in)
        zoom_menu.addAction("Diminuir").triggered.connect(self._action_zoom_out)
        zoom_menu.addAction("100%").triggered.connect(self._action_zoom_reset)
        
        menu.addSeparator()
        
        # Navegação
        back_action = QAction("⬅ Voltar", self.main_window)
        back_action.setShortcut(QKeySequence.StandardKey.Back)
        back_action.setEnabled(False)
        back_action.triggered.connect(self._action_back)
        menu.addAction(back_action)
        self._actions["back"] = back_action
        
        forward_action = QAction("➡ Avançar", self.main_window)
        forward_action.setShortcut(QKeySequence.StandardKey.Forward)
        forward_action.setEnabled(False)
        forward_action.triggered.connect(self._action_forward)
        menu.addAction(forward_action)
        self._actions["forward"] = forward_action
        
        menu.addSeparator()
        
        # Layout
        layout_action = QAction("Lado a Lado", self.main_window)
        layout_action.setCheckable(True)
        layout_action.triggered.connect(self._action_layout_toggle)
        menu.addAction(layout_action)
        self._actions["layout_side_by_side"] = layout_action
        
        split_action = QAction("Dividir Editor", self.main_window)
        split_action.setShortcut("Ctrl+\\")
        split_action.triggered.connect(self._action_split)
        menu.addAction(split_action)
        self._actions["split"] = split_action
        
        # Modos de leitura
        reading_menu = menu.addMenu("Modo Leitura")
        reading_menu.addAction("Padrão").triggered.connect(lambda: self._action_reading_mode("default"))
        reading_menu.addAction("Sépia").triggered.connect(lambda: self._action_reading_mode("sepia"))
        reading_menu.addAction("Noturno").triggered.connect(lambda: self._action_reading_mode("dark"))
        
        return menu

    def _create_tools_menu(self, parent: QMenu) -> QMenu:
        """Cria o submenu Ferramentas."""
        menu = parent.addMenu("🛠️ Ferramentas")
        
        pan_action = QAction("✋ Mão (Pan)", self.main_window)
        pan_action.triggered.connect(lambda: self._action_tool_mode("pan"))
        menu.addAction(pan_action)
        
        select_action = QAction("🖱️ Seleção", self.main_window)
        select_action.triggered.connect(lambda: self._action_tool_mode("selection"))
        menu.addAction(select_action)
        
        menu.addSeparator()
        
        ocr_area = QAction("🧠 OCR por Área", self.main_window)
        ocr_area.setCheckable(True)
        ocr_area.setEnabled(False)
        ocr_area.triggered.connect(self._action_ocr_area_toggle)
        menu.addAction(ocr_area)
        self._actions["ocr_area"] = ocr_area
        
        return menu

    def _create_config_menu(self, parent: QMenu) -> QMenu:
        """Cria o submenu Configurações."""
        menu = parent.addMenu("⚙️ Configurações")
        
        menu.addAction("🤖 Assistente de IA...").triggered.connect(self._action_ai_settings)
        menu.addAction("🛠️ Inicialização & Diagnóstico...").triggered.connect(self._action_startup_config)
        
        return menu

    def _apply_menu_style(self, menu: QMenu):
        """Aplica o estilo visual padrão ao menu."""
        menu.setStyleSheet("""
            QMenu {
                background-color: #27272A;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                padding: 8px 0;
            }
            QMenu::item {
                padding: 8px 24px;
                color: #E2E8F0;
            }
            QMenu::item:selected {
                background-color: #3F3F46;
                color: #FFD600;
            }
            QMenu::separator {
                height: 1px;
                background: #3F3F46;
                margin: 4px 12px;
            }
        """)

    def enable_document_actions(self, enabled: bool = True):
        """Habilita/desabilita ações que requerem documento aberto."""
        document_actions = ["save", "save_as", "extract", "rotate_left", "rotate_right", 
                           "back", "forward", "ocr_area"]
        for action_name in document_actions:
            if action_name in self._actions:
                self._actions[action_name].setEnabled(enabled)

    def get_action(self, name: str) -> Optional[QAction]:
        """Retorna uma ação pelo nome."""
        return self._actions.get(name)

    # ============================
    # ACTION HANDLERS (Delegação)
    # ============================
    # Estes métodos delegam para a MainWindow mantendo a compatibilidade.
    # Em uma refatoração futura, a lógica pode ser movida para cá.

    def _action_open(self):
        if hasattr(self.main_window, '_on_open_clicked'):
            self.main_window._on_open_clicked()

    def _action_save(self):
        if hasattr(self.main_window, '_on_save_clicked'):
            self.main_window._on_save_clicked()

    def _action_save_as(self):
        if hasattr(self.main_window, '_on_save_as_clicked'):
            self.main_window._on_save_as_clicked()

    def _action_merge(self):
        if hasattr(self.main_window, '_on_merge_clicked'):
            self.main_window._on_merge_clicked()

    def _action_extract(self):
        if hasattr(self.main_window, '_on_extract_clicked'):
            self.main_window._on_extract_clicked()

    def _action_export(self, format: str):
        if format == "png" and hasattr(self.main_window, '_on_export_image_clicked'):
            self.main_window._on_export_image_clicked("png")
        elif format == "svg" and hasattr(self.main_window, '_on_export_svg_clicked'):
            self.main_window._on_export_svg_clicked()
        elif format == "md" and hasattr(self.main_window, '_on_export_md_clicked'):
            self.main_window._on_export_md_clicked()

    def _action_rotate(self, degrees: int):
        if hasattr(self.main_window, '_on_rotate_clicked'):
            self.main_window._on_rotate_clicked(degrees)

    def _action_highlight_toggle(self):
        if hasattr(self.main_window, '_on_highlight_toggled'):
            self.main_window._on_highlight_toggled()

    def _action_zoom_in(self):
        if self.main_window.viewer:
            self.main_window.viewer.zoom_in()

    def _action_zoom_out(self):
        if self.main_window.viewer:
            self.main_window.viewer.zoom_out()

    def _action_zoom_reset(self):
        if self.main_window.viewer:
            self.main_window.viewer.real_size()

    def _action_back(self):
        if hasattr(self.main_window, '_on_back_clicked'):
            self.main_window._on_back_clicked()

    def _action_forward(self):
        if hasattr(self.main_window, '_on_forward_clicked'):
            self.main_window._on_forward_clicked()

    def _action_layout_toggle(self):
        if hasattr(self.main_window, '_on_layout_toggled'):
            self.main_window._on_layout_toggled()

    def _action_split(self):
        if hasattr(self.main_window, '_on_split_clicked'):
            self.main_window._on_split_clicked()

    def _action_reading_mode(self, mode: str):
        if self.main_window.viewer:
            self.main_window.viewer.set_reading_mode(mode)

    def _action_tool_mode(self, mode: str):
        if self.main_window.viewer:
            self.main_window.viewer.set_tool_mode(mode)

    def _action_ocr_area_toggle(self):
        if hasattr(self.main_window, '_on_ocr_area_toggled'):
            self.main_window._on_ocr_area_toggled()

    def _action_ai_settings(self):
        if hasattr(self.main_window, '_on_ai_settings_clicked'):
            self.main_window._on_ai_settings_clicked()

    def _action_startup_config(self):
        if hasattr(self.main_window, '_on_startup_config_clicked'):
            self.main_window._on_startup_config_clicked()
