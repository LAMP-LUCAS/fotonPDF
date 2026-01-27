from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
from src.application.use_cases.get_document_metadata import GetDocumentMetadataUseCase
from src.application.services.document_analyzer import DocumentAnalyzer
from src.infrastructure.services.logger import log_debug, log_exception

class AsyncDocumentLoader(QThread):
    """
    Worker que abre o PDF e extrai metadados em background.
    Evita que a GUI trave durante o fitz.open() de arquivos complexos.
    """
    # path, metadata, analysis_hints, opened_doc (fitz.Document), is_searchable (bool)
    finished = pyqtSignal(Path, dict, dict, object, bool) 
    progress = pyqtSignal(str) # mensagem de status
    error = pyqtSignal(str)

    def __init__(self, pdf_path: Path, metadata_use_case, detect_ocr_use_case):
        super().__init__()
        self.pdf_path = pdf_path
        self.metadata_use_case = metadata_use_case
        self.detect_ocr_use_case = detect_ocr_use_case

    def run(self):
        import fitz
        try:
            log_debug(f"AsyncLoader: Iniciando análise de {self.pdf_path.name}...")
            self.progress.emit("Analisando estrutura do PDF...")
            
            # 1. Análise de Complexidade (Rápida)
            hints = DocumentAnalyzer.analyze(self.pdf_path)
            
            # 2. Abrir Documento (Abertura ÚNICA Centralizada)
            self.progress.emit("Abrindo documento...")
            doc = fitz.open(str(self.pdf_path))
            
            # 3. Extração de Metadados (Handle Injetado)
            self.progress.emit("Extraindo metadados e camadas...")
            metadata = self.metadata_use_case.execute(self.pdf_path, doc_handle=doc)
            metadata["hints"] = hints
            
            # 4. Detecção de OCR (Camada de texto - Handle Injetado)
            self.progress.emit("Verificando pesquisabilidade...")
            is_searchable = self.detect_ocr_use_case.execute(self.pdf_path, doc_handle=doc)
            
            self.finished.emit(self.pdf_path, metadata, hints, doc, is_searchable)
            
        except Exception as e:
            log_exception(f"AsyncLoader Error: {e}")
            self.error.emit(str(e))
