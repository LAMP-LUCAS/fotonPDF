def get_main_stylesheet():
    return """
    QMainWindow {
        background-color: #1E1E1E; /* Editor Background */
        color: #D4D4D4;
    }

    QWidget {
        background-color: #1E1E1E;
        color: #D4D4D4;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Activity Bar (Icons on the left) */
    #ActivityBar {
        background-color: #333333;
        border-right: 1px solid #252526;
        min-width: 50px;
        max-width: 50px;
    }

    #ActivityBar QPushButton {
        background-color: transparent;
        border: none;
        padding: 12px;
        color: #858585;
    }

    #ActivityBar QPushButton:hover {
        color: #FFFFFF;
    }

    #ActivityBar QPushButton:checked {
        color: #FFFFFF;
        border-left: 2px solid #FFFFFF;
    }

    /* Side Bar (Collapsible Content) */
    #SideBar {
        background-color: #252526;
        border-right: 1px solid #333333;
    }

    QListWidget {
        background-color: #252526;
        border: none;
        outline: none;
    }

    QListWidget::item {
        margin: 5px 10px;
        padding: 5px;
        border-radius: 4px;
        color: #CCCCCC;
    }

    QListWidget::item:selected {
        background-color: #37373D;
        color: #FFFFFF;
    }

    /* TabWidget (Inside Sidebar) */
    QTabWidget::pane { 
        border: none;
        background-color: #252526;
    }
    QTabBar::tab {
        background: #2D2D2D;
        color: #969696;
        padding: 6px 15px;
        font-size: 11px;
        text-transform: uppercase;
    }
    QTabBar::tab:selected {
        background: #252526;
        color: #E7E7E7;
        border-bottom: 1px solid #007ACC;
    }

    /* Scrollbars (Floating style) */
    QScrollBar:vertical {
        background: transparent;
        width: 12px;
    }

    QScrollBar::handle:vertical {
        background: rgba(121, 121, 121, 0.4);
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background: rgba(121, 121, 121, 0.7);
    }

    /* Menu Bar */
    QMenuBar {
        background-color: #3C3C3C;
        color: #CCCCCC;
    }

    QMenuBar::item:selected {
        background-color: #505050;
    }

    /* Status Bar */
    QStatusBar {
        background-color: #007ACC;
        color: #FFFFFF;
    }

    /* QSplitter Handle */
    QSplitter::handle {
        background-color: #252526;
    }
    QSplitter::handle:horizontal {
        width: 1px;
    }
    """
