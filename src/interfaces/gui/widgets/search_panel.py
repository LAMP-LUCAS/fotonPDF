from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, QListWidget, 
                             QListWidgetItem, QLabel, QHBoxLayout, QPushButton)
from PyQt6.QtCore import pyqtSignal, Qt
from src.domain.entities.navigation import SearchResult

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

class SearchPanel(QWidget):
    """Painel lateral de busca textual."""
    result_clicked = pyqtSignal(int, list) # page_index, highlights

    def __init__(self, search_use_case):
        super().__init__()
        self._search_use_case = search_use_case
        self._pdf_path = None
        
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
        self._pdf_path = path
        self.clear()

    def clear(self):
        self.results_list.clear()
        self.search_input.clear()
        self.status_label.setText("")

    def perform_search(self):
        if not self._pdf_path or not self.search_input.text():
            return
            
        self.results_list.clear()
        self.status_label.setText("Buscando...")
        
        try:
            results = self._search_use_case.execute(self._pdf_path, self.search_input.text())
            
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
            
            self.status_label.setText(f"{len(results)} ocorrências encontradas.")
        except Exception as e:
            self.status_label.setText(f"Erro na busca: {str(e)}")

    def _on_item_clicked(self, item):
        res = item.data(Qt.ItemDataRole.UserRole)
        if res:
            self.result_clicked.emit(res.page_index, res.highlights)
