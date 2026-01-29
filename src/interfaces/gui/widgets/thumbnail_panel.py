from PyQt6.QtWidgets import (QListWidget, QListWidgetItem, QAbstractItemView, 
                             QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy)
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtCore import QSize, pyqtSignal, Qt, QTimer
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget
from src.infrastructure.services.logger import log_debug, log_exception

class ThumbnailItemWidget(QWidget):
    """Widget customizado para exibir miniatura, número da página e preview de texto."""
    def __init__(self, page_num):
        super().__init__()
        # Layout principal vertical
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)
        
        # 1. Container da Imagem (Centralizado)
        self.img_label = QLabel()
        # Tamanho um pouco menor para caber em sidebars estreitas
        self.img_label.setFixedSize(110, 150)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setStyleSheet("""
            background-color: #27272A;
            border: 1px solid #3F3F46;
            border-radius: 4px;
            color: #71717A;
            font-size: 20px;
        """)
        self.img_label.setText("⌛") 
        
        # 2. Informações (Número e Preview)
        self.info_container = QWidget()
        info_layout = QVBoxLayout(self.info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        self.num_label = QLabel(f"PÁGINA {page_num}")
        self.num_label.setStyleSheet("color: #FFD600; font-weight: bold; font-size: 10px; letter-spacing: 1px;")
        
        self.text_preview = QLabel("Processando texto...")
        self.text_preview.setStyleSheet("color: #A1A1AA; font-size: 10px; line-height: 12px;")
        self.text_preview.setWordWrap(True)
        self.text_preview.setMaximumHeight(34)
        
        info_layout.addWidget(self.num_label)
        info_layout.addWidget(self.text_preview)
        
        self.main_layout.addWidget(self.img_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.info_container)
        
        # Suporte para cliques passarem para o QListWidget
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def set_pixmap(self, pixmap):
        if not pixmap or pixmap.isNull():
            self.img_label.setText("📄")
            return
        
        scaled = pixmap.scaled(110, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.img_label.setPixmap(scaled)
        self.img_label.setText("")
        # Borda amarela discreta para indicar carregado
        self.img_label.setStyleSheet("background-color: white; border: 1px solid rgba(255, 214, 0, 0.5); border-radius: 4px;")

    def set_text(self, text):
        if not text:
            self.text_preview.setText("(Sem camada de texto)")
            return
        clean_text = text.strip().replace("\n", " ")
        snippet = clean_text[:70] + "..." if len(clean_text) > 70 else clean_text
        self.text_preview.setText(snippet)

class ThumbnailPanel(ResilientWidget):
    """Painel lateral em coluna única com degradação graciosa."""
    pageSelected = pyqtSignal(int)
    orderChanged = pyqtSignal(list)

    def __init__(self, adapter=None):
        super().__init__()
        self._adapter = adapter
        self._current_session = 0
        
        self.list = QListWidget()
        # Fluxo Vertical é melhor para Sidebars
        self.list.setFlow(QListWidget.Flow.TopToBottom)
        self.list.setWrapping(False)
        self.list.setSpacing(4)
        try:
            self.list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        except AttributeError:
            self.list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        
        # Estilo premium alinhado ao tema AEC-Dark
        self.list.setStyleSheet("""
            QListWidget {
                background-color: #18181B;
                border: none;
                outline: none;
                padding-top: 10px;
            }
            QListWidget::item {
                background-color: #1F1F23;
                border: 1px solid #27272A;
                border-radius: 8px;
                margin: 6px 12px;
            }
            QListWidget::item:selected {
                background-color: #27272A;
                border: 1px solid #FFD600;
            }
            QListWidget::item:hover {
                border: 1px solid #3F3F46;
            }
        """)
        self.list.itemClicked.connect(self._on_item_clicked)
        
        self.set_content_widget(self.list)
        self.show_placeholder(True, "Aguardando documento...")

    def set_adapter(self, adapter):
        self._adapter = adapter

    def load_thumbnails(self, identities: list):
        self._current_session += 1
        log_debug(f"ThumbnailPanel [S{self._current_session}]: Carga de {len(identities)} páginas.")
        
        # Limpeza segura
        self.list.clear() 
        
        if not identities:
            self.show_placeholder(True, "Documento vazio.")
            return

        # CRITICAL FIX: Garantir que o widget de lista seja o ativo na stack
        self.show_placeholder(False)
        
        # Iniciar carga assíncrona com atraso maior para deixar a UI respirar
        QTimer.singleShot(100, lambda: self._append_batch(identities, self._current_session, 0))

    def _append_batch(self, identities, session_id, start_idx):
        if session_id != self._current_session: return
        
        batch_size = 5 # Reduzido de 15 para 5 para evitar GUI Freeze
        total = len(identities)
        end_idx = min(start_idx + batch_size, total)
        
        from src.interfaces.gui.state.render_engine import RenderEngine
        engine = RenderEngine.instance()
        
        self.list.setUpdatesEnabled(False)
        
        for i in range(start_idx, end_idx):
            path, original_idx = identities[i]
            
            # Criar Item (NÃO passar a lista no construtor para evitar inserção duplicada)
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, original_idx)
            
            # Widget Customizado
            widget = ThumbnailItemWidget(i + 1)
            # Definir tamanho fixo para o item para ajudar o QListWidget no cálculo de scroll
            item.setSizeHint(QSize(130, 220))
            
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)
            
            # Renderização (Async)
            try:
                engine.request_render(
                    path, original_idx, 0.2, 0, 
                    lambda p_idx, pix, z, r, m, c, w=widget, sid=session_id: self._on_thumb_ready(w, pix, sid)
                )
            except: pass
            
            # Texto (Async)
            if self._adapter:
                QTimer.singleShot(10 * (i - start_idx), lambda p=path, idx=original_idx, w=widget, sid=session_id: 
                                  self._fetch_text_snippet(p, idx, w, sid))

        self.list.setUpdatesEnabled(True)
        # Forçar processamento de eventos da UI para evitar travamento visual
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        if end_idx < total:
            # Intervalo aumentado para 150ms para dar chance à UI de responder
            QTimer.singleShot(150, lambda: self._append_batch(identities, session_id, end_idx))

    def _on_thumb_ready(self, widget, pixmap, session_id):
        if session_id == self._current_session:
            widget.set_pixmap(pixmap)

    def _fetch_text_snippet(self, path, page_idx, widget, session_id):
        if session_id != self._current_session: return
        try:
            text = self._adapter.get_text(path, page_idx)
            widget.set_text(text)
        except:
            widget.set_text("(Erro ao ler texto)")

    def _on_item_clicked(self, item):
        row = self.list.row(item)
        self.pageSelected.emit(row)

    def set_selected_page(self, index: int):
        if 0 <= index < self.list.count():
            item = self.list.item(index)
            self.list.setCurrentItem(item)
            item.setSelected(True)
            self.list.scrollToItem(item)
