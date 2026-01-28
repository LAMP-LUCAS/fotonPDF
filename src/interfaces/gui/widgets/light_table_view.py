from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap, QTransform
from src.interfaces.gui.widgets.nav_hub import NavHub
from src.interfaces.gui.widgets.floating_navbar import ModernNavBar

class PageItem(QGraphicsPixmapItem):
    """Representa uma página PDF individual na Mesa de Luz."""
    moved = pyqtSignal(int, float, float) # page_idx, x, y

    def __init__(self, page_index, source_path, width_pt=595, height_pt=842):
        super().__init__()
        self.page_index = page_index
        self.source_path = source_path
        self.width_pt = width_pt
        self.height_pt = height_pt
        
        # Estilo base
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Render inicial placeholder
        self.update_render(0.3)

    def _on_render_finished(self, pix):
        """Aplica o pixmap e ajusta a escala local para manter as dimensões em pontos."""
        if pix.isNull(): return
        self.setPixmap(pix)
        
        # Ajustar escala interna para que o pixmap caiba exatamente no retângulo de pontos (PT)
        # Isso garante que a posição na cena não mude e o item seja estável
        sx = self.width_pt / pix.width()
        sy = self.height_pt / pix.height()
        self.setTransform(QTransform().scale(sx, sy))

    def update_render(self, zoom):
        """Solicita uma renderização condizente com o zoom atual."""
        from src.interfaces.gui.state.render_engine import RenderEngine
        # Permitir qualidade Hi-Res até 3.0x para evitar pixelização em zooms próximos
        target_zoom = max(0.3, min(zoom, 3.0))
        
        RenderEngine.instance().request_render(
            self.source_path, self.page_index, target_zoom, 0, 
            lambda idx, pix, z, r, m, c: self._on_render_finished(pix)
        )


    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemPositionHasChanged:
            # Check if scene is valid before emitting (item may be removed during transitions)
            scene = self.scene()
            if scene and hasattr(scene, 'pageMoved'):
                pos = self.pos()
                scene.pageMoved.emit(self.page_index, pos.x(), pos.y())
        return super().itemChange(change, value)

class LightTableView(QGraphicsView):
    """Mesa de Luz: visualização de páginas como objetos físicos arrastáveis."""
    pageMoved = pyqtSignal(int, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LightTableView")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.pageMoved = self.pageMoved # Pass-through manual
        self.scene.setBackgroundBrush(QColor("#0F172A"))
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        # Zoom focado no mouse
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self.setStyleSheet("border: none; background-color: #0F172A;")
        
        # Navigation Hub
        self.nav_hub = NavHub(self)
        self.nav_hub.toolChanged.connect(self._on_hub_tool_changed)
        self.nav_hub.hide()
        
        # Modern NavBar (Universal)
        self.nav_bar = ModernNavBar(self)
        self.nav_bar.show()
        self.setup_nav_bar(self.nav_bar)
        
        self._zoom = 1.0
        self._tool_mode = "pan"
        self._panning = False
        self._last_mouse_pos = QPointF()
        
        # Timer para renderização de alta qualidade após zoom/pan
        self._quality_timer = QTimer(self)
        self._quality_timer.setSingleShot(True)
        self._quality_timer.timeout.connect(self._refresh_quality)

    def load_document(self, path, metadata):
        """Carrega os itens da cena de forma progressiva para evitar travamento da GUI."""
        self.scene.clear()
        page_count = metadata.get("page_count", 0)
        page_info = metadata.get("pages", [])
        
        spacing = 400
        cols = 3
        batch_size = 10
        
        def process_batch(current_start):
            if current_start >= page_count:
                return
                
            self.viewport().setUpdatesEnabled(False)
            end_idx = min(current_start + batch_size, page_count)
            
            for i in range(current_start, end_idx):
                w_pt, h_pt = 595, 842
                if i < len(page_info):
                    w_pt = page_info[i].get("width_pt", 595)
                    h_pt = page_info[i].get("height_pt", 842)
                    
                item = PageItem(i, str(path), width_pt=w_pt, height_pt=h_pt)
                row, col = i // cols, i % cols
                item.setPos(col * spacing, row * spacing)
                self.scene.addItem(item)
            
            self.viewport().setUpdatesEnabled(True)
            
            if end_idx < page_count:
                QTimer.singleShot(30, lambda: process_batch(end_idx))

        process_batch(0)

    def _on_hub_tool_changed(self, action):
        if action == "pan": self.set_tool_mode("pan")
        elif action == "select": self.set_tool_mode("selection")
        elif action == "zoom_in": self.zoom_in()
        elif action == "zoom_out": self.zoom_out()

    def setup_nav_bar(self, nav_bar):
        """Conecta os sinais da barra de navegação moderna."""
        nav_bar.zoomIn.connect(self.zoom_in)
        nav_bar.zoomOut.connect(self.zoom_out)
        nav_bar.resetZoom.connect(self.reset_zoom)
        nav_bar.setTool.connect(self.set_tool_mode)
        nav_bar.viewAll.connect(self.viewport_to_overview)
        
        # Connect highlight color if signal exists
        if hasattr(nav_bar, 'highlightColor'):
            nav_bar.highlightColor.connect(self._on_highlight_color_changed)
        
        # Conectar Visão de Scroll à troca de modo na MainWindow
        try:
            main_window = self.window()
            if hasattr(main_window, "_switch_view_mode_v4"):
                nav_bar.viewAll.disconnect() # Limpar conexão de overview se for voltar p/ scroll
                nav_bar.viewAll.connect(lambda: main_window._switch_view_mode_v4("scroll"))
        except: pass

    def _on_highlight_color_changed(self, color: str):
        """Handles highlight color change from navbar."""
        self._highlight_color = color


    def viewport_to_overview(self):
        """Enquadra todas as páginas na visão atual."""
        if self.scene.items():
            self.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            # Atualizar zoom interno baseado na escala atual
            self._zoom = self.transform().m11()

    def set_tool_mode(self, mode: str):
        self._tool_mode = mode
        self.nav_hub.set_tool(mode)
        if mode == "selection":
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif mode == "zoom_area":
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)
            self._zoom_area_active = True
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self._zoom_area_active = False

    def zoom_in(self): self.set_zoom(self._zoom * 1.25)
    def zoom_out(self): self.set_zoom(self._zoom / 1.25)
    def reset_zoom(self): self.set_zoom(1.0)

    def set_zoom(self, zoom: float):
        old_zoom = self._zoom
        self._zoom = max(0.05, min(zoom, 5.0))
        factor = self._zoom / old_zoom
        # Usar o mecanismo interno do QGraphicsView para manter o foco no mouse
        self.scale(factor, factor)
        
        # Programar atualização de qualidade
        self._quality_timer.start(300)

    def _refresh_quality(self):
        """Atualiza a renderização dos itens visíveis com base no zoom atual."""
        visible_rect = self.mapToScene(self.viewport().rect()).boundingRect()
        for item in self.scene.items():
            if isinstance(item, PageItem):
                # Se o item está visível no viewport, atualizar qualidade
                if item.sceneBoundingRect().intersects(visible_rect):
                    item.update_render(self._zoom)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0: self.zoom_in()
            else: self.zoom_out()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        mod = event.modifiers()
        
        if mod == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_Plus or key == Qt.Key.Key_Equal: self.zoom_in()
            elif key == Qt.Key.Key_Minus: self.zoom_out()
            elif key == Qt.Key.Key_0: self.reset_zoom()
        elif mod == Qt.KeyboardModifier.NoModifier:
            if key == Qt.Key.Key_P: self.set_tool_mode("pan")
            elif key == Qt.Key.Key_S: self.set_tool_mode("selection")
            elif key == Qt.Key.Key_Z:
                self.set_tool_mode("zoom_area")
            elif key == Qt.Key.Key_N:
                if self.nav_hub.isVisible(): self.nav_hub.hide()
                else: self.nav_hub.show()
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # Pan prioritário se:
        # 1. Botão do meio (sempre)
        # 2. Botão esquerdo E ferramenta 'Pan' ativa
        if event.button() == Qt.MouseButton.MiddleButton or \
           (self._tool_mode == "pan" and event.button() == Qt.MouseButton.LeftButton):
            self._panning = True
            self._last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        # Modo Seleção: Deixar o QGraphicsView lidar com RubberBand e movimento de itens
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.position() - self._last_mouse_pos
            self._last_mouse_pos = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._panning:
            self._panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor if self._tool_mode == "pan" else Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        
        # Zoom por Área: aplica fitInView na área selecionada pelo RubberBand
        if getattr(self, '_zoom_area_active', False) and self.rubberBandRect():
            rect = self.mapToScene(self.rubberBandRect()).boundingRect()
            if rect.width() > 10 and rect.height() > 10:
                self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
                self._zoom = self.transform().m11()
                self._quality_timer.start(300)
            # Voltar para modo Pan após o zoom
            self.set_tool_mode("pan")
            event.accept()
            return
        
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_nav_pos()

    def _update_nav_pos(self):
        # NavHub centralizado na base
        if hasattr(self, "nav_hub") and self.nav_hub.isVisible():
            self.nav_hub.move((self.width() - self.nav_hub.width()) // 2, self.height() - 80)
        
        # ModernNavBar centralizada na base
        if hasattr(self, "nav_bar"):
            self.nav_bar.move((self.width() - self.nav_bar.width()) // 2, self.height() - 60)

    def update_page(self, current, total):
        """Sincroniza o contador de páginas na barra."""
        if hasattr(self, "nav_bar"):
            self.nav_bar.update_page(current, total)
