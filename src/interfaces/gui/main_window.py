import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QFileDialog, QLabel, QToolBar, QStatusBar)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize
from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
from src.interfaces.gui.widgets.thumbnail_panel import ThumbnailPanel

from src.infrastructure.services.update_service import UpdateService

class MainWindow(QMainWindow):
    """Janela Principal do fotonPDF com Design Premium."""

    def __init__(self, initial_file: Path = None):
        super().__init__()
        self.setWindowTitle("fotonPDF")
        self.resize(1200, 900)
        self.current_file = None
        
        # Iniciar Verificador de Update
        self.update_service = UpdateService()
        self.update_service.check_for_updates(self._on_update_found)
        
        # Apply Premium Dark Theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QToolBar {
                background-color: #1e1e1e;
                border-bottom: 1px solid #333;
                padding: 10px;
                spacing: 15px;
            }
            QStatusBar {
                background-color: #1e1e1e;
                color: #888;
                border-top: 1px solid #333;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Root Layout
        self.root_layout = QVBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        
        # Content Layout
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(0)
        self.root_layout.addLayout(self.content_layout)
        
        # 1. Primeiro criar os widgets de conteúdo
        self.viewer = PDFViewerWidget()
        self.sidebar = ThumbnailPanel()
        
        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.viewer)
        
        # 2. Configurar conexões entre widgets
        self.sidebar.pageSelected.connect(self.on_page_selected)
        self.sidebar.orderChanged.connect(self.viewer.reorder_pages)
        self.sidebar.orderChanged.connect(self._on_pages_reordered)
        
        # 3. Agora configurar a Toolbar (que depende do viewer)
        self.toolbar = QToolBar("Ferramentas")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        self._setup_toolbar()
        
        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto")
        
        # Drag & Drop support
        self.setAcceptDrops(True)
        
        # Placeholder se nenhum arquivo aberto
        self.show_welcome_message()
        
        # Carregar arquivo se fornecido
        if initial_file:
            if initial_file.exists() and initial_file.suffix.lower() == ".pdf":
                self.open_file(initial_file)

    def show_welcome_message(self):
        if not self.viewer.has_document():
            label = QLabel("Arraste um PDF aqui para começar 🚀")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 18px; color: #666; font-family: 'Segoe UI', sans-serif;")
            self.viewer.setPlaceholder(label)

    def _setup_toolbar(self):
        """Configura a barra de ferramentas premium."""
        # --- Grupo: Arquivo ---
        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self._on_open_clicked)
        self.toolbar.addAction(open_action)
        
        self.save_action = QAction("Salvar Como...", self)
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self._on_save_clicked)
        self.toolbar.addAction(self.save_action)

        self.toolbar.addSeparator()

        # --- Grupo: Navegação ---
        zoom_in_action = QAction("Zoom +", self)
        zoom_in_action.triggered.connect(self.viewer.zoom_in)
        self.toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom -", self)
        zoom_out_action.triggered.connect(self.viewer.zoom_out)
        self.toolbar.addAction(zoom_out_action)

        fit_w_action = QAction("Ajustar Largura", self)
        fit_w_action.triggered.connect(self.viewer.fit_width)
        self.toolbar.addAction(fit_w_action)

        self.toolbar.addSeparator()

        # --- Grupo: Ferramentas ---
        self.rotate_left_action = QAction("Girar Esq.", self)
        self.rotate_left_action.setEnabled(False)
        self.rotate_left_action.triggered.connect(lambda: self._on_rotate_clicked(-90))
        self.toolbar.addAction(self.rotate_left_action)

        self.rotate_right_action = QAction("Girar Dir.", self)
        self.rotate_right_action.setEnabled(False)
        self.rotate_right_action.triggered.connect(lambda: self._on_rotate_clicked(90))
        self.toolbar.addAction(self.rotate_right_action)

        self.extract_action = QAction("Extrair", self)
        self.extract_action.setEnabled(False)
        self.extract_action.triggered.connect(self._on_extract_clicked)
        self.toolbar.addAction(self.extract_action)

        self.merge_action = QAction("Unir PDF", self)
        self.merge_action.triggered.connect(self._on_merge_clicked)
        self.toolbar.addAction(self.merge_action)

    def _on_open_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir PDF", "", "Arquivos PDF (*.pdf)")
        if file_path:
            self.open_file(Path(file_path))

    def _on_extract_clicked(self):
        selected_pages = self.sidebar.get_selected_pages()
        if not selected_pages:
            self.statusBar().showMessage("Selecione ao menos uma página na barra lateral.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Extração", "", "Arquivos PDF (*.pdf)")
        if not save_path:
            return

        try:
            from src.application.use_cases.split_pdf import SplitPDFUseCase
            from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
            
            adapter = PyMuPDFAdapter()
            use_case = SplitPDFUseCase(adapter)
            
            use_case.execute(self.current_file, selected_pages, Path(save_path))
            self.statusBar().showMessage(f"Sucesso! {len(selected_pages)} páginas extraídas.")
        except Exception as e:
            self.statusBar().showMessage(f"Erro na extração: {str(e)}")

    def _on_export_clicked(self):
        selected_pages = self.sidebar.get_selected_pages()
        if not selected_pages:
            self.statusBar().showMessage("Selecione ao menos uma página na barra lateral.")
            return

        target_dir = QFileDialog.getExistingDirectory(self, "Selecionar Pasta para Exportação")
        if not target_dir:
            return

        try:
            import fitz
            doc = fitz.open(str(self.current_file))
            for page_num in selected_pages:
                page = doc.load_page(page_num - 1)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Alta qualidade
                output_name = f"{self.current_file.stem}_page_{page_num}.png"
                pix.save(str(Path(target_dir) / output_name))
            
            doc.close()
            self.statusBar().showMessage(f"Exportação concluída em: {target_dir}")
        except Exception as e:
            self.statusBar().showMessage(f"Erro na exportação: {str(e)}")

    def _on_update_found(self, version, url):
        """Notifica o usuário sobre a nova versão."""
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Atualização Disponível")
        msg.setText(f"Uma nova versão do fotonPDF (v{version}) está disponível!")
        msg.setInformativeText("Deseja baixar a atualização agora?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            import webbrowser
            webbrowser.open(url)

    def open_file(self, file_path: Path):
        """Abre um novo arquivo PDF no visualizador e atualiza as miniaturas."""
        try:
            self.current_file = file_path
            
            # import os
            # size = os.path.getsize(str(file_path))
            # log_debug(f"MainWindow: Abrindo {file_path} ({size} bytes)")
            
            # Initialize State Manager
            from src.interfaces.gui.state.pdf_state import PDFStateManager
            self.state_manager = PDFStateManager()
            self.state_manager.load_base_document(str(file_path))
            
            doc = self.viewer.load_document(file_path)
            self.sidebar.load_thumbnails(doc)
            self.setWindowTitle(f"fotonPDF - {file_path.name}")
            self.statusBar().showMessage(f"Arquivo carregado: {file_path.name}")
            
            # Habilitar ações
            self.save_action.setEnabled(True)
            self.rotate_left_action.setEnabled(True)
            self.rotate_right_action.setEnabled(True)
            self.extract_action.setEnabled(True)
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao abrir arquivo: {str(e)}")
            print(f"Erro ao abrir PDF: {e}")

    def _on_rotate_clicked(self, degrees: int):
        """Gira as páginas selecionadas visualmente e no estado."""
        selected_pages_indices = []
        # Obter índices selecionados (0-based)
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            if item.isSelected():
                page_idx = item.data(Qt.ItemDataRole.UserRole)
                selected_pages_indices.append(i) # Use visual index for State Manager
        
        if not selected_pages_indices:
             self.statusBar().showMessage("Selecione páginas para girar.")
             return

        for idx in selected_pages_indices:
            self.state_manager.rotate_page(idx, degrees)
            # Obter nova rotação absoluta
            page_state = self.state_manager.get_page(idx)
            if page_state:
                # Atualizar visualizador
                self.viewer.refresh_page(idx, rotation=page_state.absolute_rotation)
                # Atualizar ícone (Opcional, futuro)
        
        self.statusBar().showMessage(f"Girou {len(selected_pages_indices)} páginas em {degrees}°.")

    def _on_save_clicked(self):
        if not hasattr(self, 'state_manager'):
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF Como", "", "Arquivos PDF (*.pdf)")
        if not save_path:
            return

        try:
            # Sincronizar ordem visual final antes de salvar
            # A sidebar reflete a ordem desejada
            final_order = []
            for i in range(self.sidebar.count()):
                item = self.sidebar.item(i)
                # O UserRole armazena o índice ORIGINAL do carregamento inicial
                # Mas o State Manager já está alinhado visualmente se reordenarmos?
                # Não, precisamos reordenar o StateManager baseando-se nos índices visuais
                # O jeito mais fácil é reconstruir a lista do manager baseada nos dados da sidebar?
                # O sidebar move itens. O item na posição 0 tem data=X. X é o índice original.
                # Precisamos dizer pro manager: "A página na posição 0 agora é a página original X"
                # Mas espera, se fizermos merge, os índices originais mudam.
                # Simplificação: O StateManager deve ser a fonte da verdade.
                # Quando a sidebar emite 'orderChanged', atualizamos o StateManager.
                pass

            # Como o StateManager já deve estar atualizado via 'reorder_pages' (vamos conectar isso),
            # apenas salvamos.
            self.state_manager.save(str(save_path))
            
            self.statusBar().showMessage(f"Arquivo salvo com sucesso em: {save_path}")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao salvar: {str(e)}")
            import traceback
            traceback.print_exc()

    def _on_merge_clicked(self):
        other_files, _ = QFileDialog.getOpenFileNames(self, "Selecionar PDFs para Unir", "", "Arquivos PDF (*.pdf)")
        if not other_files:
            return
            
        try:
            if not hasattr(self, 'state_manager'):
                 # Cria novo se vazio
                 from src.interfaces.gui.state.pdf_state import PDFStateManager
                 self.state_manager = PDFStateManager()
            
            for f in other_files:
                self.state_manager.append_document(str(f))
                
            # Recarregar tudo (Brute force visual refresh for safety)
            # Salvar estado atual em temp e recarregar é mais seguro visualmente por enquanto
            # Mas queremos performance.
            # Vamos apenas adicionar as páginas novas no final do viewer e sidebar.
            
            # Melhor: criar um reload_from_state() no futuro.
            # Por agora: Salvar temp e abrir (garante consistência total)
            import uuid
            unique_id = uuid.uuid4().hex[:8]
            temp_path = Path(sys.argv[0]).parent / f"temp_merge_{unique_id}.pdf"
            
            self.state_manager.save(str(temp_path))
            self.open_file(temp_path)
            
            self.statusBar().showMessage("PDFs unidos e recarregados!")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao unir: {str(e)}")

    def _on_pages_reordered(self, new_order: list[int]):
        """Sincroniza o StateManager com a nova ordem visual."""
        if hasattr(self, 'state_manager'):
            self.state_manager.reorder_pages(new_order)
            self.statusBar().showMessage("Ordem das páginas atualizada.")

    def on_page_selected(self, page_num: int):
        self.viewer.scroll_to_page(page_num)

    def keyPressEvent(self, event):
        """Atalhos de teclado senior."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_J: # Estilo Vim (Baixo)
            self.viewer.verticalScrollBar().setValue(self.viewer.verticalScrollBar().value() + 50)
        elif event.key() == Qt.Key.Key_K: # Estilo Vim (Cima)
            self.viewer.verticalScrollBar().setValue(self.viewer.verticalScrollBar().value() - 50)
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [Path(u.toLocalFile()) for u in event.mimeData().urls()]
        if files and files[0].suffix.lower() == ".pdf":
            self.open_file(files[0])
