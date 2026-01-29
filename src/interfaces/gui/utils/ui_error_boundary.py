import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
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
    Widget base robusto que usa QStackedLayout para alternar entre
    Conteúdo Real e Placeholder/Erro de forma eficiente e sem recálculos pesados.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Usamos StackedLayout para troca limpa de estado
        from PyQt6.QtWidgets import QStackedLayout
        self.stack = QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)
        
        # Estado 0: Placeholder / Erro
        self.placeholder_widget = QWidget()
        self.placeholder_layout = QVBoxLayout(self.placeholder_widget)
        self.placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_layout.setSpacing(10)
        
        self.error_icon = QLabel("⚠️")
        self.error_icon.setStyleSheet("font-size: 24px;")
        self.error_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_icon.hide()
        
        self.placeholder_label = QLabel("Recurso indisponível")
        self.placeholder_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
        self.placeholder_label.setWordWrap(True)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.placeholder_layout.addWidget(self.error_icon)
        self.placeholder_layout.addWidget(self.placeholder_label)
        
        # Estado 1: Conteúdo (Pode ser vazio inicialmente)
        self.content_container = QWidget()
        self.content_container_layout = QVBoxLayout(self.content_container)
        self.content_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack.addWidget(self.placeholder_widget) # Index 0
        self.stack.addWidget(self.content_container)  # Index 1
        
        self.show_placeholder(True)

    def show_placeholder(self, visible=True, message=None, is_error=False):
        """ Alterna entre a stack 0 (placeholder) e 1 (conteúdo). """
        if visible:
            self.stack.setCurrentIndex(0)
            if is_error:
                self.error_icon.show()
                self.placeholder_label.setStyleSheet("color: #F87171; font-weight: bold; font-size: 11px;")
            else:
                self.error_icon.hide()
                self.placeholder_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
            
            if message:
                self.placeholder_label.setText(message)
        else:
            self.stack.setCurrentIndex(1)

    def set_content_widget(self, widget):
        """ 
        Define o widget de conteúdo real na stack 1.
        """
        # Limpar anterior
        while self.content_container_layout.count():
            item = self.content_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if widget:
            self.content_container_layout.addWidget(widget)
