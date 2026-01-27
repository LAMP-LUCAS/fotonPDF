"""Painel de Notas e Anotações do Usuário."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton, QHBoxLayout, QTextEdit
from PyQt6.QtCore import pyqtSignal, Qt
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget
from src.infrastructure.services.logger import log_debug


class AnnotationsPanel(ResilientWidget):
    """Painel lateral resiliente para anotações do usuário."""
    annotationClicked = pyqtSignal(int, str)  # page_index, annotation_id

    def __init__(self):
        super().__init__()
        self._pdf_path = None
        self._annotations = []  # list[{page, text, id}]
        
        # Widget de lista de anotações
        self.list = QListWidget()
        self.list.setStyleSheet("background: transparent; border: none;")
        self.list.itemClicked.connect(self._on_item_clicked)
        
        # Botão de adicionar nota
        self.btn_add = QPushButton("+ Nova Nota")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3c;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4c;
            }
        """)
        self.btn_add.clicked.connect(self._on_add_clicked)
        
        # Layout interno
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.list)
        
        self.set_content_widget(container)
        self.show_placeholder(True, "Nenhum documento carregado")

    def set_pdf(self, path):
        """Define o PDF ativo e carrega anotações salvas."""
        if self._pdf_path == path:
            return
        self._pdf_path = path
        self.load_annotations()

    def load_annotations(self):
        """Carrega anotações do storage local (placeholder para futura implementação)."""
        if not self._pdf_path:
            self.show_placeholder(True, "Nenhum documento carregado")
            return
        
        # TODO: Implementar persistência real das anotações
        # Por enquanto, mostra placeholder de "sem notas"
        self.list.clear()
        self._annotations = []
        
        if not self._annotations:
            self.show_placeholder(True, "Nenhuma nota neste documento.\nClique em '+ Nova Nota' para começar.")
        else:
            self.show_placeholder(False)
            for ann in self._annotations:
                self._add_annotation_item(ann)

    def _add_annotation_item(self, annotation: dict):
        """Adiciona um item de anotação à lista."""
        item = QListWidgetItem(f"📝 Pág. {annotation['page'] + 1}")
        item.setData(Qt.ItemDataRole.UserRole, annotation)
        item.setToolTip(annotation['text'][:100])
        self.list.addItem(item)

    def _on_item_clicked(self, item):
        """Navega para a página da anotação selecionada."""
        ann = item.data(Qt.ItemDataRole.UserRole)
        if ann:
            self.annotationClicked.emit(ann['page'], ann['id'])

    def _on_add_clicked(self):
        """Abre dialog para criar nova anotação (placeholder)."""
        log_debug("AnnotationsPanel: Criar nova nota (não implementado)")
        # TODO: Abrir dialog de criação de nota
        pass

    def add_annotation(self, page_index: int, text: str):
        """API pública para adicionar uma anotação programaticamente."""
        import uuid
        ann = {
            'id': str(uuid.uuid4()),
            'page': page_index,
            'text': text
        }
        self._annotations.append(ann)
        self._add_annotation_item(ann)
        self.show_placeholder(False)
