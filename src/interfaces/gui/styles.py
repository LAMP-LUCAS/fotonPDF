def get_main_stylesheet():
    return """
    QMainWindow {
        background-color: #0F172A;
        color: #F8FAFC;
    }

    QWidget {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Toolbar Styling */
    QToolBar {
        background-color: #1E293B;
        border-bottom: 2px solid #334155;
        padding: 5px;
        spacing: 10px;
    }

    QToolBar QToolButton {
        background-color: transparent;
        color: #F8FAFC;
        border-radius: 6px;
        padding: 6px 10px;
        font-weight: 500;
    }

    QToolBar QToolButton:hover {
        background-color: #334155;
        color: #FFC107;
    }

    QToolBar::separator {
        background-color: #334155;
        width: 1px;
        margin: 5px;
    }

    /* Sidebar (Thumbnail Panel) */
    QListWidget {
        background-color: #1E293B;
        border-right: 1px solid #334155;
        outline: none;
    }

    QListWidget::item {
        margin: 10px;
        border-radius: 8px;
        background-color: #334155;
    }

    QListWidget::item:selected {
        background-color: #FFC107;
        color: #0F172A;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        background: #0F172A;
        width: 10px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background: #334155;
        min-height: 20px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical:hover {
        background: #FFC107;
    }

    /* Status Bar */
    QStatusBar {
        background-color: #1E293B;
        color: #94A3B8;
        border-top: 1px solid #334155;
    }

    /* Buttons in Dialogs */
    QPushButton {
        background-color: #FFC107;
        color: #0F172A;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #FFD54F;
    }

    QPushButton:disabled {
        background-color: #334155;
        color: #64748B;
    }
    /* Glow Effect for Active/Checked Actions */
    QToolBar QToolButton:checked {
        background-color: #334155;
        border-bottom: 2px solid #FFC107;
        color: #FFC107;
    }

    /* TabWidget Styling */
    QTabWidget::pane { 
        border: none;
        background-color: #1E293B;
    }
    QTabBar::tab {
        background: #0F172A;
        color: #94A3B8;
        padding: 8px 20px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background: #1E293B;
        color: #FFC107;
        font-weight: bold;
    }

    /* Animation-like transitions for buttons */
    QToolButton {
        transition: background-color 0.3s ease;
    }
    """
