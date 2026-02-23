"""
Minimal debug script to trace MainWindow.__init__ line-by-line.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress all network calls from litellm by not touching AI at all
os.environ["LITELLM_LOCAL_MODEL_ONLY"] = "1"

from PyQt6.QtWidgets import QApplication

def trace_init():
    print("Creating QApplication...", flush=True)
    app = QApplication(sys.argv)
    print("QApplication created.", flush=True)
    
    # Step-by-step import tracing
    print("Importing MainWindow prerequisites...", flush=True)
    
    print("  1. PyMuPDFAdapter...", flush=True)
    from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
    print("     OK", flush=True)
    
    print("  2. StageStateRepository...", flush=True)
    from src.infrastructure.repositories.sqlite_stage_repository import StageStateRepository
    print("     OK", flush=True)
    
    print("  3. Use Cases...", flush=True)
    from src.application.use_cases.search_text import SearchTextUseCase
    from src.application.use_cases.get_toc import GetTOCUseCase
    from src.application.use_cases.get_document_metadata import GetDocumentMetadataUseCase
    from src.application.use_cases.detect_text_layer import DetectTextLayerUseCase
    from src.application.use_cases.apply_ocr import ApplyOCRUseCase
    from src.application.use_cases.ocr_area_extraction import OCRAreaExtractionUseCase
    from src.application.use_cases.add_annotation import AddAnnotationUseCase
    print("     OK", flush=True)
    
    print("  4. GUI widgets...", flush=True)
    from src.interfaces.gui.widgets.activity_bar import ActivityBar
    print("     ActivityBar OK", flush=True)
    from src.interfaces.gui.widgets.sidebar import SideBar
    print("     SideBar OK", flush=True)
    from src.interfaces.gui.widgets.tab_container import TabContainer
    print("     TabContainer OK", flush=True)
    from src.interfaces.gui.widgets.bottom_panel import BottomPanel
    print("     BottomPanel OK", flush=True)
    from src.interfaces.gui.widgets.light_table_view import LightTableView
    print("     LightTableView OK", flush=True)
    
    print("  5. TopBar...", flush=True)
    from src.interfaces.gui.widgets.top_bar import TopBarWidget
    print("     TopBar OK", flush=True)
    
    print("  6. InspectorPanel...", flush=True) 
    from src.interfaces.gui.widgets.inspector_panel import InspectorPanel
    print("     InspectorPanel OK", flush=True)
    
    print("  7. Panels...", flush=True)
    from src.interfaces.gui.panels.thumbnail_panel import ThumbnailPanel
    from src.interfaces.gui.panels.toc_panel import TOCPanel
    from src.interfaces.gui.panels.search_panel import SearchPanel
    print("     Panels OK", flush=True)
    
    print("  8. CommandOrchestrator...", flush=True)
    from src.application.services.command_orchestrator import CommandOrchestrator
    print("     CommandOrchestrator OK", flush=True)
    
    print("\n=== All imports OK! Now testing MainWindow... ===", flush=True)
    from src.interfaces.gui.main_window import MainWindow
    print("MainWindow import OK. Creating instance...", flush=True)
    win = MainWindow()
    print("MainWindow instance created!", flush=True)
    
    return 0

if __name__ == "__main__":
    trace_init()
