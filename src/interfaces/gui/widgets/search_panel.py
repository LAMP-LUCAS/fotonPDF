from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QListWidget, 
                             QListWidgetItem, QLabel, QHBoxLayout, QPushButton)
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from src.domain.entities.navigation import SearchResult
from src.infrastructure.services.logger import log_debug, log_exception

class SearchResultItem(QWidget):
    """Widget customizado para exibir um resultado de busca com snippet."""
    def __init__(self, result: SearchResult):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        title = QLabel(f"Página {result.page_index + 1}")
        title.setStyleSheet("font-weight: bold; color: #3498db;")
        
        snippet = QLabel(result.text_snippet)
        snippet.setWordWrap(True)
        snippet.setStyleSheet("font-size: 11px; color: #bdc3c7;")
        
        layout.addWidget(title)
        layout.addWidget(snippet)

class SearchWorker(QThread):
    """Worker para busca textual em background."""
    finished = pyqtSignal(list, int) # results, session_id
    error = pyqtSignal(str)

    def __init__(self, use_case, pdf_path, query, session_id):
        super().__init__()
        self.use_case = use_case
        self.pdf_path = pdf_path
        self.query = query
        self.session_id = session_id

    def run(self):
        try:
            results = self.use_case.execute(self.pdf_path, self.query)
            self.finished.emit(results, self.session_id)
        except Exception as e:
            log_exception(f"SearchWorker Error: {e}")
            self.error.emit(str(e))

class SearchPanel(QWidget):
    """Painel lateral de busca textual."""
    result_clicked = pyqtSignal(int, list) # page_index, highlights
    results_found = pyqtSignal(list) # list[SearchResult]

    def __init__(self, search_use_case):
        super().__init__()
        self._search_use_case = search_use_case
        self._pdf_path = None
        self._worker = None
        self._current_session = 0
        
        self.layout = QVBoxLayout(self)
        
        # Barra de Busca
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar no documento...")
        self.search_input.returnPressed.connect(self.perform_search)
        
        self.btn_search = QPushButton("🔍")
        self.btn_search.setFixedWidth(40)
        self.btn_search.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        
        self.layout.addLayout(search_layout)
        
        # Lista de Resultados
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self._on_item_clicked)
        self.layout.addWidget(self.results_list)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        self.layout.addWidget(self.status_label)

    def set_pdf(self, path):
        if self._pdf_path == path:
            return
        self._pdf_path = path
        self._current_session += 1
        self.clear()

    def clear(self):
        self.results_list.clear()
        self.search_input.clear()
        self.status_label.setText("")

    def perform_search(self):
        query = self.search_input.text().strip()
        if not self._pdf_path or not query:
            return
            
        # Cancelar worker anterior (verificação de ID na volta)
        self.results_list.clear()
        self.status_label.setText("Buscando...")
        
        self._worker = SearchWorker(self._search_use_case, self._pdf_path, query, self._current_session)
        self._worker.finished.connect(self._on_search_finished)
        self._worker.error.connect(lambda e: self.status_label.setText(f"Erro: {e}"))
        self._worker.start()

    def _on_search_finished(self, results, session_id):
        if session_id != self._current_session:
            return
            
        if not results:
            self.status_label.setText("Nenhum resultado encontrado.")
            return
            
        for res in results:
            item = QListWidgetItem(self.results_list)
            custom_widget = SearchResultItem(res)
            item.setSizeHint(custom_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, res)
            
            self.results_list.addItem(item)
            self.results_list.setItemWidget(item, custom_widget)
        
        self.results_found.emit(results)
        self.status_label.setText(f"{len(results)} ocorrências encontradas.")

    def _on_item_clicked(self, item):
        res = item.data(Qt.ItemDataRole.UserRole)
        if res:
            self.result_clicked.emit(res.page_index, res.highlights)
