import psutil
import os
import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTabWidget, QApplication, QPushButton, QFrame, QProgressBar)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from src.infrastructure.services.settings_service import SettingsService
from src.infrastructure.services.update_service import UpdateService
from src.interfaces.gui.widgets.ai_settings_panel import AISettingsWidget

class HealthMonitor(QFrame):
    """Monitor de saúde do sistema em tempo real."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #0F172A; border-radius: 10px; padding: 15px;")
        layout = QVBoxLayout(self)
        
        self.lbl_cpu = QLabel("CPU: 0%")
        self.lbl_cpu.setStyleSheet("color: #FFC107; font-weight: bold; font-family: 'JetBrains Mono';")
        self.progress_cpu = QProgressBar()
        self.progress_cpu.setFixedHeight(8)
        self.progress_cpu.setStyleSheet("QProgressBar { background: #1E293B; border: none; } QProgressBar::chunk { background: #FFC107; }")
        
        self.lbl_ram = QLabel("RAM: 0MB")
        self.lbl_ram.setStyleSheet("color: #4ADE80; font-weight: bold; font-family: 'JetBrains Mono';")
        self.progress_ram = QProgressBar()
        self.progress_ram.setFixedHeight(8)
        self.progress_ram.setStyleSheet("QProgressBar { background: #1E293B; border: none; } QProgressBar::chunk { background: #4ADE80; }")
        
        layout.addWidget(self.lbl_cpu)
        layout.addWidget(self.progress_cpu)
        layout.addSpacing(10)
        layout.addWidget(self.lbl_ram)
        layout.addWidget(self.progress_ram)
        
        # Timer para atualizar
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_stats)
        self.timer.start(2000)

    def _update_stats(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 # MB
        
        self.lbl_cpu.setText(f"CPU LOAD: {cpu_usage}%")
        self.progress_cpu.setValue(int(cpu_usage))
        
        self.lbl_ram.setText(f"APP MEMORY: {ram_usage:.1f} MB")
        # Considerar 500MB como 100% para o gráfico relativo do app
        self.progress_ram.setValue(min(100, int((ram_usage/500)*100)))

class ControlCenterWidget(QWidget):
    """
    Dashboard Central de Gestão do fotonPDF.
    Acesso profissional a telemetria, atualizações e configurações.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border-top: 1px solid #334155; top: -1px; }
            QTabBar::tab { background: #1E293B; color: #94A3B8; padding: 10px 20px; font-weight: bold; }
            QTabBar::tab:selected { background: #0F172A; color: #FFC107; border-bottom: 2px solid #FFC107; }
        """)
        
        # --- TAB 1: DASHBOARD ---
        self.dashboard_tab = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_tab)
        dash_layout.setContentsMargins(20, 20, 20, 20)
        dash_layout.setSpacing(15)
        
        title = QLabel("SYSTEM HEALTH & STATUS")
        title.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 14px;")
        dash_layout.addWidget(title)
        
        self.health = HealthMonitor()
        dash_layout.addWidget(self.health)
        
        # Info básica
        info_frame = QFrame()
        info_frame.setStyleSheet("background: #1E293B; border-radius: 8px; padding: 10px;")
        info_layout = QVBoxLayout(info_frame)
        
        from src import __version__
        info_layout.addWidget(QLabel(f"Build Version: {__version__} (RC)"))
        info_layout.addWidget(QLabel(f"Process ID: {os.getpid()}"))
        info_layout.addWidget(QLabel(f"UI Engine: PyQt6 (v4 Neon-Gold)"))
        
        dash_layout.addWidget(info_frame)
        dash_layout.addStretch()
        
        # --- TAB 2: INTELIGÊNCIA ---
        self.ai_settings = AISettingsWidget()
        
        # --- TAB 3: ATUALIZAÇÕES ---
        self.update_tab = QWidget()
        upd_layout = QVBoxLayout(self.update_tab)
        upd_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_upd_status = QLabel("Nenhuma atualização disponível.")
        self.btn_check_upd = QPushButton("Verificar Atualizações")
        self.btn_check_upd.setStyleSheet("""
            QPushButton { background: #FFC107; color: #0F172A; padding: 12px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #E2E8F0; }
        """)
        self.btn_check_upd.clicked.connect(self._check_updates)
        
        upd_layout.addWidget(self.lbl_upd_status)
        upd_layout.addSpacing(20)
        upd_layout.addWidget(self.btn_check_upd)

        self.tabs.addTab(self.dashboard_tab, "DASHBOARD")
        self.tabs.addTab(self.ai_settings, "IA CONFIG")
        self.tabs.addTab(self.update_tab, "SISTEMA")
        
        layout.addWidget(self.tabs)

    def _check_updates(self):
        self.lbl_upd_status.setText("Buscando no servidor GitHub...")
        self.svc = UpdateService()
        self.svc.check_for_updates(
            callback_success=lambda v, url: self.lbl_upd_status.setText(f"🚀 VERSÃO {v} DISPONÍVEL!"),
            callback_error=lambda e: self.lbl_upd_status.setText(f"❌ Erro: {e}")
        )
