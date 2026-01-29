"""Painel de Notas e Anotações do Usuário."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton, QHBoxLayout, QTextEdit
from PyQt6.QtCore import pyqtSignal, Qt
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget
from src.infrastructure.services.logger import log_debug

class AnnotationsPanel(ResilientWidget):
    """Painel lateral resiliente para anotações do usuário."""
    annotationClicked = pyqtSignal(int, str, str)  # page_index, annotation_id, pdf_path

    def __init__(self, use_case):
        super().__init__()
        self._use_case = use_case
        self._pdf_path = None
        self._annotations = []  # list[{id, page_index, text, ...}]
        
        # Widget de lista de anotações
        self.list = QListWidget()
        self.list.setStyleSheet("background: transparent; border: none;")
        self.list.itemClicked.connect(self._on_item_clicked)
        # Context Menu para deletar
        self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._show_context_menu)
        
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
        # Sempre recarrega para garantir sincronia (pode ter sido editado externamente)
        self._pdf_path = path
        self.load_annotations()

    def load_annotations(self):
        """Carrega anotações do repositório."""
        if not self._pdf_path:
            self.show_placeholder(True, "Nenhum documento carregado")
            return
        
        try:
            self._annotations = self._use_case.get_annotations(str(self._pdf_path))
            self.list.clear()
            
            if not self._annotations:
                self.show_placeholder(True, "Nenhuma nota neste documento.\nClique em '+ Nova Nota' para começar.")
            else:
                self.show_placeholder(False)
                for ann in self._annotations:
                    self._add_annotation_item(ann)
        except Exception as e:
            log_debug(f"AnnotationsPanel: Erro ao carregar: {e}")
            self.show_placeholder(True, f"Erro ao carregar notas: {e}")

    def _add_annotation_item(self, annotation: dict):
        """Adiciona um item de anotação à lista."""
        page_idx = annotation.get('page_index', 0)
        text = annotation.get('text', '')
        
        item = QListWidgetItem(f"📝 Pág. {page_idx + 1}: {text[:30]}...")
        item.setData(Qt.ItemDataRole.UserRole, annotation)
        item.setToolTip(text)
        self.list.addItem(item)

    def _on_item_clicked(self, item):
        """Navega para a página da anotação selecionada."""
        ann = item.data(Qt.ItemDataRole.UserRole)
        if ann:
            # page_index pode vir como string do JSON, converter
            p_idx = int(ann.get('page_index', 0))
            self.annotationClicked.emit(p_idx, ann.get('id', ''), str(self._pdf_path))

    def _on_add_clicked(self):
        """Abre dialog para criar nova anotação."""
        if not self._pdf_path: return
        
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Nova Nota", "Conteúdo da anotação:")
        
        if ok and text:
            # Tenta acessar o viewer via main window para obter página atual
            current_page = 0
            try:
                mw = self.window()
                if hasattr(mw, 'state_manager') and mw.state_manager:
                    visual_idx = mw.viewer.get_current_page_index()
                    v_page = mw.state_manager.get_page(visual_idx)
                    if v_page:
                        current_page = v_page.source_page_index
                        # IMPORTANTE: A nota deve ser associada ao path de ORIGEM da página
                        self._pdf_path = v_page.source_doc.name
            except Exception as e:
                log_debug(f"AnnotationsPanel: Falha ao resolver pág física: {e}")
            
            new_ann = self._use_case.add_annotation(str(self._pdf_path), current_page, text)
            self._annotations.append(new_ann)
            
            self.show_placeholder(False)
            self._add_annotation_item(new_ann)

    def _show_context_menu(self, pos):
        """Menu de contexto para deletar notas."""
        item = self.list.itemAt(pos)
        if not item: return
        
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        delete_action = menu.addAction("❌ Excluir Nota")
        
        action = menu.exec(self.list.mapToGlobal(pos))
        if action == delete_action:
            ann = item.data(Qt.ItemDataRole.UserRole)
            self._use_case.remove_annotation(str(self._pdf_path), ann['id'])
            # Remove da lista e da memória
            row = self.list.row(item)
            self.list.takeItem(row)
            self._annotations = [a for a in self._annotations if a['id'] != ann['id']]
            
            if not self._annotations:
                self.show_placeholder(True, "Nenhuma nota neste documento.")

    def add_annotation(self, page_index: int, text: str):
        """API pública para adicionar uma anotação programaticamente (Externo)."""
        if not self._pdf_path:
            # Tenta pegar do parent se não estiver setado (fallback)
            mw = self.window()
            if hasattr(mw, 'current_file') and mw.current_file:
                self._pdf_path = mw.current_file
            else:
                log_debug("AnnotationsPanel: Tentativa de adicionar nota sem PDF carregado.")
                return

        try:
            new_ann = self._use_case.add_annotation(str(self._pdf_path), page_index, text)
            self._annotations.append(new_ann)
            self.show_placeholder(False)
            self._add_annotation_item(new_ann)
        except Exception as e:
            log_debug(f"AnnotationsPanel: Erro ao adicionar nota programática: {e}")
