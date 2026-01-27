from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap, QTransform
from src.interfaces.gui.widgets.nav_hub import NavHub

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
        # Limitar o zoom para evitar sobrecarga (Mesa de Luz costuma ser visão geral)
        target_zoom = max(0.3, min(zoom, 1.5))
        
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

    def set_tool_mode(self, mode: str):
        self._tool_mode = mode
        self.nav_hub.set_tool(mode)
        if mode == "selection":
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.OpenHandCursor)

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
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "nav_hub"):
            self.nav_hub.move((self.width() - self.nav_hub.width()) // 2, self.height() - 80)
