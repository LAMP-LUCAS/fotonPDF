from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QLabel, QHBoxLayout, QCheckBox, QWidget)
from PyQt6.QtCore import Qt
from src.infrastructure.services.settings_service import SettingsService

class StartupConfigDialog(QDialog):
    """
    Janela de configuração de inicialização (estilo MSConfig/Task Manager).
    Permite ao usuário desativar subsistemas para diagnosticar problemas de performance ou travamentos.
    """
    
    # Feature Flags definitions: Key -> (Description, Default)
    FEATURES = {
        "startup_load_ai": ("Carregar Núcleo de IA (Background)", True),
        "startup_load_sidebar": ("Carregar Paineis Laterais", True),
        "startup_load_thumbnails": ("Carregar Miniaturas", True),
        "startup_load_toc": ("Carregar Sumário (TOC)", True),
        "startup_load_search": ("Carregar Painel de Busca", True),
        "startup_scan_pdf": ("Análise Profunda de PDF ao Abrir", True),
        "startup_async_loader": ("Carregamento Assíncrono", True),
        "startup_telemetry": ("Telemetria e Logs Detalhados", True),
        "startup_hardware_accel": ("Aceleração de Hardware (OpenGL)", False), # Default False para evitar black screen
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração de Inicialização (Modo de Diagnóstico)")
        self.resize(600, 400)
        self.settings = SettingsService.instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        info_label = QLabel("Desative recursos abaixo para identificar gargalos ou falhas na abertura de PDFs.\n"
                            "Isso permite isolar o problema desativando componentes não essenciais.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Tabela de Features
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Recurso", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Popular Tabela
        self.table.setRowCount(len(self.FEATURES))
        for i, (key, (desc, default)) in enumerate(self.FEATURES.items()):
            # Descrição
            item_desc = QTableWidgetItem(desc)
            item_desc.setFlags(item_desc.flags() ^ Qt.ItemFlag.ItemIsEditable) # Read-only
            self.table.setItem(i, 0, item_desc)
            
            # Checkbox
            checkbox_container = QWidget()
            cb_layout = QHBoxLayout(checkbox_container)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            cb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            checkbox = QCheckBox()
            # Carregar valor salvo ou default
            current_val = self.settings.get_bool(key, default)
            checkbox.setChecked(current_val)
            checkbox.setProperty("settings_key", key)
            
            cb_layout.addWidget(checkbox)
            self.table.setCellWidget(i, 1, checkbox_container)

        # Botões
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Salvar e Reiniciar") # Em um app real, pediria restart. Aqui salvamos.
        btn_save.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def save_settings(self):
        """Persiste as configurações da tabela."""
        for i in range(self.table.rowCount()):
            widget_container = self.table.cellWidget(i, 1)
            checkbox = widget_container.findChild(QCheckBox)
            key = checkbox.property("settings_key")
            self.settings.set(key, checkbox.isChecked())
