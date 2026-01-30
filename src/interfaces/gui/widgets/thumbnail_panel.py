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
        # Permitir que encolha se a sidebar for muito estreita, mas manter proporção
        self.img_label.setMinimumSize(40, 60)
        self.img_label.setMaximumSize(120, 160)
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.img_label.setStyleSheet("""
            background-color: #27272A;
            border: 1px solid #3F3F46;
            border-radius: 4px;
            color: #71717A;
            font-size: 16px;
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
    
    def showEvent(self, event):
        super().showEvent(event)
        # log_debug(f"ThumbnailItemWidget P{self.num_label.text()} shown.")

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

    def __init__(self, adapter=None, parent=None):
        super().__init__(parent)
        self._adapter = adapter
        self._current_session = 0
        
        self.list = QListWidget()
        
        # PIVOT FINAL: ListMode é o único que suporta largura variável sem esconder itens
        self.list.setViewMode(QListWidget.ViewMode.ListMode)
        self.list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list.setSpacing(4)
        self.list.setWordWrap(True)
        # Permite que os itens sejam menores que o ideal sem sumir
        self.list.setUniformItemSizes(False) 
        
        try:
            self.list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        except AttributeError:
            self.list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.list.setMovement(QListWidget.Movement.Static)
        
        # Estilo premium alinhado ao tema AEC-Dark
        self.list.setStyleSheet("""
            QListWidget {
                background-color: #111113;
                border: none;
                outline: none;
                padding: 0px;
                min-width: 150px;
            }
            QListWidget::item {
                background-color: #1F1F23;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                margin: 4px 8px;
            }
            QListWidget::item:selected {
                background-color: #27272A;
                border: 1px solid #FFD600;
            }
        """)
        self.list.itemClicked.connect(self._on_item_clicked)
        
        # [ARCH] Direct Layout Bypass
        # O ThumbnailPanel bypassa a arquitetura de QStackedWidget do ResilientWidget (Pai)
        # pois o aninhamento triplo de stacks (SideBar -> Resilient -> Stack) causa
        # problemas siliciosos de visibilidade/geometria.
        
        # 1. Limpar layout base (remover stack padrão)
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().hide()
                child.widget().setParent(None) # Orphan instead of delete
                
        # 2. Adicionar lista diretamente ao layout raiz
        self.main_layout.addWidget(self.list)
        self.list.show()

    def show_placeholder(self, visible=True, message=None, is_error=False):
        # Override: Placeholder desativado devido ao bypass de layout.
        pass

    def set_adapter(self, adapter):
        self._adapter = adapter

    def load_thumbnails(self, identities: list):
        """
        Popula a lista com miniaturas baseadas nas identidades das páginas.
        Deduplica para evitar processamento pesado e flickering.
        """
        # Evitar recarga se as identidades forem as mesmas (Deduplicação rápida)
        # BUGFIX: Se a largura for muito pequena, permitimos recarregar quando a barra expandir
        is_narrow = self.width() < 100
        if hasattr(self, "_last_identities") and self._last_identities == identities and not is_narrow:
            from src.infrastructure.services.logger import log_debug
            log_debug("ThumbnailPanel: Ignorando carga redundante")
            return
            
        self._last_identities = identities
        self._current_session += 1
        
        # Limpeza segura
        self.list.clear() 
        
        if not identities:
            # Sem stack, não podemos mostrar placeholder, mas limpamos a lista
            return

        # Indicar que o conteúdo está vindo
        self.list.update()
        
        # RESTAURANDO LOGICA REAL
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(200, lambda: self._append_batch(identities, self._current_session, 0))

    def _append_batch(self, identities, session_id, start_idx):
        if session_id != self._current_session: 
            log_debug(f"ThumbnailPanel: Ignorando batch de sessão antiga (S{session_id} != S{self._current_session})")
            return
        
        batch_size = 8 # Equilíbrio entre velocidade e responsividade
        total = len(identities)
        end_idx = min(start_idx + batch_size, total)
        
        log_debug(f"ThumbnailPanel [S{session_id}]: Processando batch {start_idx} até {end_idx} de {total}")
        
        from src.interfaces.gui.state.render_engine import RenderEngine
        engine = RenderEngine.instance()
        
        # Desativar updates temporariamente melhora a performance de inserção
        self.list.setUpdatesEnabled(False)
        
        for i in range(start_idx, end_idx):
            path, original_idx = identities[i]
            
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, original_idx)
            item.setSizeHint(QSize(130, 220))
            
            widget = ThumbnailItemWidget(i + 1)
            self.list.addItem(item)
            self.list.setItemWidget(item, widget)
            widget.show() # Essencial para que apareça dentro do QListWidget em alguns sistemas
            
            # Renderização Background
            try:
                engine.request_render(
                    path, original_idx, 0.2, 0, 
                    lambda p_idx, pix, z, r, m, c, w=widget, sid=session_id: self._on_thumb_ready(w, pix, sid)
                )
            except: pass
            
            # Texto Background
            if self._adapter:
                QTimer.singleShot(5, lambda p=path, idx=original_idx, w=widget, sid=session_id: 
                                  self._fetch_text_snippet(p, idx, w, sid))

        self.list.setUpdatesEnabled(True)
        self.list.update() # Forçar repaint
        
        if end_idx < total:
            # Manter intervalo de 150ms para garantir fluidicidade da UI
            QTimer.singleShot(150, lambda: self._append_batch(identities, session_id, end_idx))
        else:
            log_debug(f"ThumbnailPanel [S{session_id}]: Carga de {total} itens completa e visível.")
            self.list.doItemsLayout() # FORCE FEED
            self.list.viewport().update()

    def _on_thumb_ready(self, widget, pixmap, session_id):
        if session_id == self._current_session:
            log_debug(f"ThumbnailPanel: Miniatura pronta ({pixmap.width()}x{pixmap.height()}) para S{session_id}")
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
