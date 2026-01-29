from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                             QCheckBox, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget
from src.infrastructure.services.logger import log_error, log_debug

class InspectorPanel(ResilientWidget):
    """
    Painel Inteligente AEC (Sidebar Direita).
    Exibe metadados de engenharia, formatos de folha e controle de camadas (Layers).
    """
    layerVisibilityChanged = pyqtSignal(int, bool) # layer_id, visible

    def __init__(self):
        super().__init__()
        self._ui_initialized = False
        # Não chamamos _setup_ui aqui para garantir Lazy Loading
        self.show_placeholder(True, "Selecione um documento para inspecionar")

    def _initialize_ui_lazy(self):
        """ Inicializa a UI real apenas quando necessário. """
        if self._ui_initialized:
            return
        
        try:
            self._setup_ui()
            self._ui_initialized = True
        except Exception as e:
            log_error(f"Erro ao inicializar UI do Inspector: {e}")
            self.show_placeholder(True, f"Erro ao carregar painel: {e}", is_error=True)

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
        
        # Estilo otimizado no container (uma única vez para todos os filhos)
        self.layers_container.setStyleSheet("""
            QCheckBox { color: #E2E8F0; font-size: 11px; }
            QCheckBox::indicator { width: 14px; height: 14px; }
        """)
        
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
        # Typography: CAPS, Bold, 10px, Letter-Spacing: 1px
        lbl_title.setStyleSheet("""
            color: #71717A; 
            font-weight: bold; 
            font-size: 10px; 
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        """)
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
        log_debug("Inspector: update_metadata iniciado...")
        
        # Proteção: Se metadata for vazio/None, apenas ocultar
        if not metadata:
            log_debug("Inspector: Metadata vazio, exibindo placeholder.")
            self.show_placeholder(True, "Sem metadados disponíveis")
            return
        
        try:
            # Lazy Loading: Garante que a UI esteja criada
            log_debug("Inspector: Verificando lazy init...")
            self._initialize_ui_lazy()
            if not self._ui_initialized: 
                log_debug("Inspector: UI não inicializada, abortando update.")
                return

            self.show_placeholder(False)
            
            # Simplesmente pegamos a primeira página para o formato principal
            log_debug("Inspector: Processando dimensões...")
            if metadata.get("pages"):
                page = metadata["pages"][0]
                self.lbl_format.setText(page.get("format", "---"))
                self.lbl_dims.setText(f"{int(page.get('width_mm', 0))} x {int(page.get('height_mm', 0))}")
            
            # Atualizar Camadas (DEFERRED LOADING para evitar travamento da UI)
            log_debug("Inspector: Limpando camadas...")
            self._clear_layers()
            
            log_debug("Inspector: Lendo lista de camadas do metadata...")
            layers = metadata.get("layers", [])
            
            log_debug(f"Inspector: Calculando len(layers)...")
            count = len(layers)
            log_debug(f"Inspector: Agendando atualização de {count} camadas...")
        
            # Usar QTimer para deferir a criação da lista de camadas (Render Break)
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self._deferred_layer_update(layers))
            
        except Exception as e:
            log_error(f"Inspector: Erro crítico em update_metadata: {e}")
            self.show_placeholder(True, f"Erro: {e}", is_error=True)

    def _deferred_layer_update(self, layers):
        """Atualiza a lista de camadas sem bloquear a thread principal."""
        try:
            self.layers_container.setUpdatesEnabled(False)
            
            # Limite de segurança para evitar UI Freeze (max 100 camadas na lista simples)
            MAX_LAYERS = 100
            for i, layer in enumerate(layers):
                if i >= MAX_LAYERS:
                    log_debug("Inspector: Limite de camadas atingido. Ignorando as demais.")
                    break
                self._add_layer_item(layer)
                
            self.layers_container.setUpdatesEnabled(True)
            log_debug("Inspector: Deferred update concluído.")
        except Exception as e:
            log_error(f"Inspector: Erro no deferred update: {e}")

    def _clear_layers(self):
        while self.layers_list_layout.count():
            item = self.layers_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _add_layer_item(self, layer):
        cb = QCheckBox(layer["name"])
        cb.setChecked(layer["visible"])
        # Estilo agora é herdado do container pai (layers_container)
        cb.toggled.connect(lambda checked, lid=layer["id"]: self.layerVisibilityChanged.emit(lid, checked))
        self.layers_list_layout.addWidget(cb)
