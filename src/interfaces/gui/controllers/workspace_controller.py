from pathlib import Path
from PyQt6.QtCore import Qt

from src.infrastructure.services.logger import log_debug, log_exception, set_session_id
from src.interfaces.gui.state.render_engine import RenderEngine
from src.infrastructure.services.telemetry_service import TelemetryService

class WorkspaceController:
    """
    Controlador responsável por gerenciar o ciclo de vida da sessão de trabalho.
    Centraliza a lógica de 'Load Finished', sincronização de estado e atualizações de UI
    que antes inchavam a MainWindow.
    """

    def __init__(self, main_window):
        self.main_window = main_window

    def handle_load_finished(self, file_path: Path, metadata: dict, hints: dict, opened_doc, is_searchable: bool):
        """
        Orquestra a finalização do carregamento de um documento.
        Executa sincronização de estado, cache, render engine e atualizações de UI.
        """
        try:
            # 1. Cursor e Estado Básico
            self.main_window.setCursor(Qt.CursorShape.ArrowCursor)
            self.main_window.current_file = file_path
            
            # --- RESGATE DE METADADOS (Graceful Degradation) ---
            # Se metadados vierem vazios (falha na análise), reconstruímos o mínimo viável
            if not metadata or metadata.get("page_count", 0) == 0:
                log_debug(f"WController: Metadados corrompidos para {file_path.name}. Iniciando resgate...")
                try:
                    page_count = opened_doc.page_count if opened_doc else 0
                    metadata = {
                        "page_count": page_count,
                        "pages": [{"width_mm": 210, "height_mm": 297, "format": "A4"} for _ in range(page_count)],
                        "layers": []
                    }
                    log_debug(f"WController: Metadados resgatados (Páginas: {page_count})")
                except Exception as rescue_err:
                    log_exception(f"WController: Falha fatal no resgate de metadados: {rescue_err}")
            
            # 2. Sincronizar StateManager SEM BLOQUEIO 
            if self.main_window.state_manager:
                try:
                    if opened_doc:
                        self.main_window.state_manager.load_from_document(opened_doc, str(file_path))
                    else:
                        # Fallback seguro
                        self.main_window.state_manager.load_base_document(str(file_path))
                except Exception as e:
                    log_exception(f"WController: Erro no StateManager: {e}")
            
            # 3. Adicionar ao container de abas (Passando metadados para CACHE imediato)
            #log_debug(f"WController [DEBUG-TABS]: tabs existe? {self.main_window.tabs is not None}, tipo={type(self.main_window.tabs).__name__}, bool={bool(self.main_window.tabs) if self.main_window.tabs is not None else 'N/A'}")
            # 4. Sincronizar RenderEngine (Single-Open Architecture)
            # MOVED UP: Este passo DEVE ocorrer antes da criação da UI (Tabs) para garantir
            # que quando o Viewer pedir render, o motor já tenha o handle injetado.
            log_debug("WController [STEP 3]: Iniciando RenderEngine.set_document")
            try:
                # Passamos o opened_doc para evitar abertura concorrente
                RenderEngine.instance().set_document(file_path, pre_opened_handle=opened_doc)
            except Exception as e:
                log_exception(f"WController: Erro crítico no RenderEngine: {e}")
                try:
                    self.main_window.statusBar().showMessage("⚠️ Erro de Renderização", 5000)
                except: pass

            # 3. Adicionar ao container de abas (Passando metadados para CACHE imediato)
            if self.main_window.tabs is not None:
                try:
                    self.main_window.tabs.add_editor(file_path, metadata)
                except Exception as e:
                    log_exception(f"WController: Erro ao adicionar aba: {e}")
            else:
                log_debug("WController [SKIPPED]: tabs é None, não pode adicionar aba!")
                log_exception(f"WController: Erro crítico no RenderEngine: {e}")
                # FEEDBACK CRÍTICO: Notificar usuário que a visualização pode não funcionar
                try:
                    if not RenderEngine.instance()._current_doc_path:
                        self.main_window.statusBar().showMessage(
                            "⚠️ ATENÇÃO: Motor de renderização falhou. Visualização pode estar indisponível.", 
                            10000
                        )
                except:
                    pass
            
            # 5. Carregar na Mesa de Luz (Componente Auxiliar - Falha Graciosa)
            if self.main_window.light_table:
                log_debug("WController [STEP 4]: Iniciando LightTable.load")
                try:
                    self.main_window.light_table.load_document(file_path, metadata)
                except Exception as e:
                    log_exception(f"WController: Falha na Mesa de Luz (Ignorado): {e}")
            
            # 6. Sincronizar UI (Toolbar, Sidebar, etc) via método existente da MainWindow
                # Nota: Mantemos o _on_tab_changed na MainWindow por enquanto pois ele acopla muitos widgets,
            # mas o invocamos aqui para garantir a sequência correta.
            log_debug("WController [STEP 5]: Iniciando MainWindow._on_tab_changed")
            try:
                self.main_window._on_tab_changed(file_path)
            except Exception as e:
                log_exception(f"WController: Erro ao sincronizar abas (Recoverable): {e}")
            
            # 7. Lógica de OCR (Status Check)
            try:
                self.main_window._apply_ocr_status(file_path, is_searchable)
            except Exception as e:
                log_exception(f"WController: Erro ao verificar OCR: {e}")

            # 8. Feedback Final de UI
            try:
                self.main_window.setWindowTitle(f"fotonPDF - {file_path.name}")
                mode = hints.get("complexity", "STANDARD")
                
                if self.main_window.statusBar():
                    self.main_window.statusBar().showMessage(f"Pronto ({mode})", 3000)
                
                if hasattr(self.main_window, 'bottom_panel'):
                    self.main_window.bottom_panel.add_log(f"Opened: {file_path.name} ({mode})")
                
                self.main_window._enable_actions(True)
                self.main_window.navigation_history = [0]
                self.main_window.history_index = 0
                
                # Telemetria
                TelemetryService.log_operation("Session Loaded", file_path)
            except Exception as e:
                 log_exception(f"WController: Erro no feedback final de UI: {e}")
            
        except Exception as e:
            log_exception(f"WorkspaceController: Erro ao finalizar carregamento: {e}")
            self.main_window._on_load_error(f"Controller Error: {str(e)}")
