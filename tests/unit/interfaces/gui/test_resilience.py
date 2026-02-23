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
    
    # Inicialmente o placeholder(True) deixa o placeholder visível (Index 0)
    assert widget.stack.currentIndex() == 0
    
    # Ativar conteúdo (Index 1)
    widget.show_placeholder(False)
    assert widget.stack.currentIndex() == 1
    
    # Ativar placeholder (Index 0)
    widget.show_placeholder(True, "Erro de Teste")
    assert widget.stack.currentIndex() == 0
    assert widget.placeholder_label.text() == "Erro de Teste"

def test_resilient_widget_content_replacement(qtbot):
    """Verifica se a substituição de conteúdo limpa o layout anterior."""
    widget = ResilientWidget()
    qtbot.addWidget(widget)
    
    child1 = QWidget()
    widget.set_content_widget(child1)
    # The stack should have Placeholder (0) and child1 (1)
    assert widget.stack.count() == 2
    assert widget.stack.widget(1) == child1
    
    child2 = QWidget()
    widget.set_content_widget(child2)
    # The stack should still have 2 items, child1 is replaced
    assert widget.stack.count() == 2
    assert widget.stack.widget(1) == child2
