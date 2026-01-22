def get_main_stylesheet():
    return """
    QMainWindow {
        background-color: #1E1E1E;
        color: #D4D4D4;
    }

    QWidget {
        background-color: #1E1E1E;
        color: #D4D4D4;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }

    /* Activity Bar */
    #ActivityBar {
        background-color: #333333;
        border-right: 1px solid #252526;
    }

    #ActivityBar QPushButton {
        background-color: transparent;
        border: none;
        padding: 12px;
        color: #858585;
    }

    #ActivityBar QPushButton:hover {
        color: #FFFFFF;
        background-color: #3c3c3c;
    }

    #ActivityBar QPushButton:checked {
        color: #FFFFFF;
        border-left: 2px solid #FFFFFF;
    }

    /* Side Bars (Left & Right) */
    #SideBar {
        background-color: #252526;
        border-right: 1px solid #1e1e1e;
        border-left: 1px solid #1e1e1e;
    }

    /* Tabs Container */
    QTabWidget::pane { 
        border: none;
        background-color: #1e1e1e;
    }

    QTabBar {
        background-color: #252526;
    }

    QTabBar::tab {
        background: #2d2d2d;
        color: #969696;
        padding: 8px 20px;
        font-size: 11px;
        border-right: 1px solid #1e1e1e;
        min-width: 120px;
    }

    QTabBar::tab:selected {
        background: #1e1e1e;
        color: #ffffff;
        border-top: 1px solid #007acc;
    }

    QTabBar::tab:hover:not(:selected) {
        background: #323232;
    }

    /* Bottom Panel */
    BottomPanel {
        background-color: #1e1e1e;
        border-top: 1px solid #333;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        background: #1e1e1e;
        width: 14px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background: #37373d;
        min-height: 20px;
        margin: 2px;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical:hover {
        background: #4f4f56;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    /* Menu Bar */
    QMenuBar {
        background-color: #3c3c3c;
        color: #cccccc;
        border-bottom: 1px solid #252526;
    }

    QMenuBar::item:selected {
        background-color: #505050;
    }

    /* Status Bar (VS Code Blue) */
    QStatusBar {
        background-color: #007acc;
        color: #ffffff;
    }
    
    QStatusBar QLabel {
        background: transparent;
        color: white;
    }

    /* Splitter */
    QSplitter::handle {
        background-color: #1a1a1a;
    }
    
    QSplitter::handle:horizontal {
        width: 1px;
    }
    
    QSplitter::handle:vertical {
        height: 1px;
    }
    """
