import sys
from PyQt6.QtWidgets import QApplication
from src.interfaces.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("fotonPDF")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
