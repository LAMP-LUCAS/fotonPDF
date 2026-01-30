from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QStackedWidget
from PyQt6.QtCore import Qt
from src.infrastructure.services.logger import log_exception

def safe_ui_callback(title="Component Error"):
    """
    Decorador para funções de UI que captura exceções e evita crashes do loop principal.
    Identifica automaticamente se é um método (com self) ou função estática/closure.
    """
    def decorator(func):
        import functools
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Tentar identificar 'self' (primeiro argumento se for um QWidget/QObject)
            self_obj = None
            if args and hasattr(args[0], 'parentWidget'):
                self_obj = args[0]
                
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Resilience Boundary [{title}]: {str(e)}"
                log_exception(error_msg)
                
                # Procura por uma MainWindow ou BottomPanel acessível para logar na UI
                main_win = None
                curr = self_obj
                while curr:
                    if hasattr(curr, "window") and curr.window():
                        main_win = curr.window()
                        break
                    curr = curr.parentWidget() if hasattr(curr, "parentWidget") else None
                
                if main_win and hasattr(main_win, "bottom_panel"):
                    main_win.bottom_panel.add_log(f"⚠️ {title}: {str(e)}", color="red")
                elif self_obj and hasattr(self_obj, "statusBar") and self_obj.statusBar():
                    self_obj.statusBar().showMessage(f"⚠️ {title}: {str(e)}")
                    
        return wrapper
    return decorator

class ResilientWidget(QWidget):
    """
    Widget base robusto que alterna entre Conteúdo Real e Placeholder
    usando QStackedWidget para máxima estabilidade de gerenciamento de janelas.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        from src.infrastructure.services.logger import log_debug
        log_debug(f"ResilientWidget [{type(self).__name__}]: __init__ (Parent: {parent})")
        
        # Layout principal que contém o stack
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Stack para alternar entre estados
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        # 1. Placeholder Widget (Index 0)
        self.placeholder_widget = QWidget()
        p_layout = QVBoxLayout(self.placeholder_widget)
        p_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.error_icon = QLabel("⚠️")
        self.error_icon.setStyleSheet("font-size: 24px;")
        self.error_icon.hide()
        
        self.placeholder_label = QLabel("Recurso indisponível")
        self.placeholder_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self.placeholder_label.setWordWrap(True)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        p_layout.addWidget(self.error_icon)
        p_layout.addWidget(self.placeholder_label)
        
        self.stack.addWidget(self.placeholder_widget)
        
        # 2. Content Widget Slot (Index 1) - Inicialmente um dummy
        self._content_widget = QWidget()
        self.stack.addWidget(self._content_widget)
        
        self.show_placeholder(True)

    def show_placeholder(self, visible=True, message=None, is_error=False):
        """ Alterna visibilidade entre placeholder e conteúdo através do stack. """
        if visible:
            self.stack.setCurrentIndex(0)
            if is_error:
                self.error_icon.show()
                self.placeholder_label.setStyleSheet("color: #F87171; font-weight: bold;")
            else:
                self.error_icon.hide()
                self.placeholder_label.setStyleSheet("color: #94A3B8;")
            
            if message:
                self.placeholder_label.setText(message)
        else:
            # FORCE VISIBILITY: Usar setCurrentWidget é mais seguro que Index
            if self._content_widget:
                self.stack.setCurrentWidget(self._content_widget)
                self._content_widget.setVisible(True)
                self._content_widget.raise_()
                self._content_widget.updateGeometry()
            else:
                 self.stack.setCurrentIndex(1)

        from src.infrastructure.services.logger import log_debug
        log_debug(f"ResilientWidget [{type(self).__name__}]: show_placeholder={visible}")
        
        # Trigger layout update
        self.stack.updateGeometry()
        self.update()

    def set_content_widget(self, widget):
        """ Define o widget real, substituindo o dummy no index 1. """
        if not widget: return
        
        from src.infrastructure.services.logger import log_debug
        log_debug(f"ResilientWidget [{type(self).__name__}]: set_content_widget({type(widget).__name__})")
        
        # Remover widget antigo do slot 1
        old = self.stack.widget(1)
        if old:
            self.stack.removeWidget(old)
            if old != widget:
                old.deleteLater()
        
        # Injetar novo
        self._content_widget = widget
        self.stack.insertWidget(1, widget)
        
        # Manter políticas de expansão
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Forçar atualização de visibilidade
        self.stack.updateGeometry()

    def showEvent(self, event):
        super().showEvent(event)
        self.stack.updateGeometry()
