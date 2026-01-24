from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                             QCheckBox, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget

class InspectorPanel(ResilientWidget):
    """
    Painel Inteligente AEC (Sidebar Direita).
    Exibe metadados de engenharia, formatos de folha e controle de camadas (Layers).
    """
    layerVisibilityChanged = pyqtSignal(int, bool) # layer_id, visible

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        # Container principal com scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(20)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- SEÇÃO 1: PROPRIEDADES AEC ---
        self.prop_group = self._create_group("DIMENSÕES E FORMATO")
        
        self.container_format, self.lbl_format = self._create_info_item("Formato", "---")
        self.container_dims, self.lbl_dims = self._create_info_item("Dimensões (mm)", "---")
        self.container_scale, self.lbl_scale = self._create_info_item("Escala Detectada", "N/A")
        
        self.prop_group.layout().addWidget(self.container_format)
        self.prop_group.layout().addWidget(self.container_dims)
        self.prop_group.layout().addWidget(self.container_scale)
        self.content_layout.addWidget(self.prop_group)

        # --- SEÇÃO 2: CAMADAS (OCG) ---
        self.layers_group = self._create_group("CAMADAS TÉCNICAS")
        self.layers_container = QWidget()
        self.layers_list_layout = QVBoxLayout(self.layers_container)
        self.layers_list_layout.setContentsMargins(0, 0, 0, 0)
        self.layers_list_layout.setSpacing(8)
        
        self.layers_group.layout().addWidget(self.layers_container)
        self.content_layout.addWidget(self.layers_group)

        self.scroll.setWidget(self.content)
        self.set_content_widget(self.scroll)
        self.show_placeholder(True, "Selecione um documento para inspecionar")

    def _create_group(self, title):
        group = QFrame()
        group.setStyleSheet("background: #1E293B; border-radius: 8px;")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 10px; margin-bottom: 8px;")
        layout.addWidget(lbl_title)
        return group

    def _create_info_item(self, label, value):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(f"{label}:")
        lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        val = QLabel(value)
        val.setStyleSheet("color: white; font-weight: 500; font-size: 11px;")
        val.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(lbl)
        layout.addStretch()
        layout.addWidget(val)
        return container, val

    def update_metadata(self, metadata: dict):
        """Atualiza a UI com dados reais do documento."""
        self.show_placeholder(False)
        
        # Simplesmente pegamos a primeira página para o formato principal
        if metadata.get("pages"):
            page = metadata["pages"][0]
            self.lbl_format.setText(page["format"])
            self.lbl_dims.setText(f"{int(page['width_mm'])} x {int(page['height_mm'])}")
        
        # Atualizar Camadas
        self._clear_layers()
        for layer in metadata.get("layers", []):
            self._add_layer_item(layer)

    def _clear_layers(self):
        while self.layers_list_layout.count():
            item = self.layers_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_layer_item(self, layer):
        cb = QCheckBox(layer["name"])
        cb.setChecked(layer["visible"])
        cb.setStyleSheet("QCheckBox { color: #E2E8F0; font-size: 11px; } QCheckBox::indicator { width: 14px; height: 14px; }")
        cb.toggled.connect(lambda checked, lid=layer["id"]: self.layerVisibilityChanged.emit(lid, checked))
        self.layers_list_layout.addWidget(cb)
