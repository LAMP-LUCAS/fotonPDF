"""
Trace MainWindow init by writing to a file for debugging.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TRACE_FILE = os.path.join(os.path.dirname(__file__), "trace_output.txt")

def trace(msg):
    with open(TRACE_FILE, "a") as f:
        f.write(msg + "\n")
        f.flush()

# Clear trace file
with open(TRACE_FILE, "w") as f:
    f.write("=== TRACE START ===\n")

try:
    trace("1. Before QApplication")
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    trace("2. QApplication created")
    
    trace("3. Importing PyMuPDFAdapter...")
    from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
    trace("3. DONE: PyMuPDFAdapter")
    
    trace("4. Importing MainWindow module...")
    from src.interfaces.gui import main_window
    trace("4. DONE: MainWindow module loaded")
    
    trace("5. Creating MainWindow instance...")
    win = main_window.MainWindow()
    trace("5. DONE: MainWindow created!")
    
    trace("=== ALL OK ===")
except Exception as e:
    trace(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    trace(traceback.format_exc())

trace("Script finished.")
