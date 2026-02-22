from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path

class ActionStack(QObject):
    """
    Gerencia a pilha de estados (caminhos de arquivo) para Undo/Redo.
    Implementa um histórico linear com truncação futura ao adicionar novo estado.
    """
    stateChanged = pyqtSignal(Path) # Emitido quando o estado (arquivo atual) muda via Undo/Redo
    stackChanged = pyqtSignal()     # Emitido para atualizar UI (habilitar/desabilitar botões)

    def __init__(self, initial_state: Path = None):
        super().__init__()
        self._stack = []
        self._cursor = -1
        
        if initial_state:
            self.reset(initial_state)

    def reset(self, initial_state: Path):
        """Reinicia a pilha com um estado inicial."""
        self._stack = [initial_state]
        self._cursor = 0
        self.stackChanged.emit()

    def push(self, state: Path):
        """
        Adiciona um novo estado à pilha, descartando qualquer histórico 'futuro' (Redo).
        """
        # Truncar o histórico se estivermos no meio dele
        if self._cursor < len(self._stack) - 1:
            self._stack = self._stack[:self._cursor + 1]
        
        self._stack.append(state)
        self._cursor = len(self._stack) - 1
        self.stackChanged.emit()

    def undo(self):
        """Volta para o estado anterior."""
        if self.can_undo:
            self._cursor -= 1
            state = self._stack[self._cursor]
            self.stateChanged.emit(state)
            self.stackChanged.emit()
            return state
        return None

    def redo(self):
        """Avança para o próximo estado (se disponível)."""
        if self.can_redo:
            self._cursor += 1
            state = self._stack[self._cursor]
            self.stateChanged.emit(state)
            self.stackChanged.emit()
            return state
        return None

    @property
    def can_undo(self) -> bool:
        return self._cursor > 0

    @property
    def can_redo(self) -> bool:
        return self._cursor < len(self._stack) - 1

    @property
    def current_state(self) -> Path:
        if 0 <= self._cursor < len(self._stack):
            return self._stack[self._cursor]
        return None
