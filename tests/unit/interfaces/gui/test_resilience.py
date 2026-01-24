import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback, ResilientWidget

class MockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.error_caught = False

    @safe_ui_callback("Test Method")
    def failing_method(self):
        raise ValueError("Simulated UI Error")

def test_safe_ui_callback_prevents_crash(qtbot):
    """Verifica se o decorador captura a exceção e impede o crash."""
    widget = MockWidget()
    qtbot.addWidget(widget)
    
    # Não deve subir exceção ValueError
    widget.failing_method()
    
    # Se chegamos aqui sem crash, o teste passou na captura
    assert True

def test_resilient_widget_placeholder_toggle(qtbot):
    """Verifica se o ResilientWidget alterna corretamente entre conteúdo e placeholder."""
    widget = ResilientWidget()
    qtbot.addWidget(widget)
    
    # Inicialmente não deve mostrar placeholder
    assert widget.placeholder_widget.isHidden()
    assert not widget.content_widget.isHidden()
    
    # Ativar placeholder
    widget.show_placeholder(True, "Erro de Teste")
    assert not widget.placeholder_widget.isHidden()
    assert widget.content_widget.isHidden()
    assert widget.placeholder_label.text() == "Erro de Teste"

def test_resilient_widget_content_replacement(qtbot):
    """Verifica se a substituição de conteúdo limpa o layout anterior."""
    widget = ResilientWidget()
    qtbot.addWidget(widget)
    
    child1 = QWidget()
    widget.set_content_widget(child1)
    assert widget.content_layout.count() == 1
    
    child2 = QWidget()
    widget.set_content_widget(child2)
    assert widget.content_layout.count() == 1
    # child1 deve ter sido marcado para deleção
