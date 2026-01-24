import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from src.infrastructure.services.logger import log_exception

def safe_ui_callback(title="Component Error"):
    """
    Decorador para funções de UI que captura exceções e evita crashes do loop principal.
    Notifica via logger e pode ser estendido para emitir sinais.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                error_msg = f"Resilience Boundary [{title}]: {str(e)}"
                log_exception(error_msg)
                
                # Procura por uma MainWindow ou BottomPanel acessível para logar na UI
                main_win = None
                curr = self
                while curr:
                    if hasattr(curr, "window") and curr.window():
                        main_win = curr.window()
                        break
                    curr = curr.parentWidget() if hasattr(curr, "parentWidget") else None
                
                if main_win and hasattr(main_win, "bottom_panel"):
                    main_win.bottom_panel.add_log(f"⚠️ {title}: {str(e)}")
                elif hasattr(self, "statusBar") and self.statusBar():
                    self.statusBar().showMessage(f"⚠️ {title}: {str(e)}")
                    
        return wrapper
    return decorator

class ResilientWidget(QWidget):
    """
    Widget base que mostra um estado de 'Vazio/Erro' em caso de falha crítica
    ou se nenhum conteúdo estiver carregado.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container para o conteúdo real
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container para o placeholder / Erro
        self.placeholder_widget = QWidget()
        self.placeholder_layout = QVBoxLayout(self.placeholder_widget)
        self.placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_layout.setSpacing(10)
        
        self.error_icon = QLabel("⚠️")
        self.error_icon.setStyleSheet("font-size: 24px;")
        self.error_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_icon.hide() # Oculto por padrão
        
        self.placeholder_label = QLabel("Recurso indisponível")
        self.placeholder_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self.placeholder_label.setWordWrap(True)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.placeholder_layout.addWidget(self.error_icon)
        self.placeholder_layout.addWidget(self.placeholder_label)
        
        self.main_layout.addWidget(self.content_widget)
        self.main_layout.addWidget(self.placeholder_widget)
        
        self.show_placeholder(False)

    def show_placeholder(self, visible=True, message=None, is_error=False):
        """ Mostra o estado de placeholder ou erro. """
        self.content_widget.setVisible(not visible)
        self.placeholder_widget.setVisible(visible)
        
        if is_error:
            self.error_icon.show()
            self.placeholder_label.setStyleSheet("color: #F87171; font-weight: bold; font-size: 11px;")
        else:
            self.error_icon.hide()
            self.placeholder_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
            
        if message:
            self.placeholder_label.setText(message)

    def set_content_widget(self, widget):
        import os
        from datetime import datetime
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QCoreApplication, QTimer
        
        def _trace(msg):
            try:
                log_path = os.path.join(os.environ.get('TEMP', '.'), 'fotonpdf_startup.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    f.write(f"[{ts}] set_content_widget: {msg}\n")
            except:
                pass
        
        _trace("START")
        
        # Clear previous content safely
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        # Defer adding the new widget to the next event loop iteration
        # This prevents blocking during complex layout calculations
        def _add_async():
            try:
                _trace("async: calling addWidget")
                self.content_layout.addWidget(widget)
                _trace("async: addWidget success")
            except Exception as e:
                _trace(f"async: FATAL ERROR: {e}")
        
        QTimer.singleShot(0, _add_async)
        _trace("scheduled async addWidget")
        _trace("COMPLETE")
