def get_main_stylesheet():
    """
    Folha de estilos central do fotonPDF.
    Define o DNA Visual: Solar Gold (#FFC107) sobre Deep Space (#0F172A).
    Utiliza conceitos de Glassmorphism e Glow para uma interface Profissional Premium.
    """
    return """
    /* --- Globais --- */
    QMainWindow {
        background-color: #0F172A;
    }

    QWidget {
        background-color: #0F172A;
        color: #E2E8F0;
        font-family: 'Inter', 'Segoe UI', sans-serif;
        font-size: 12px;
    }

    /* --- Activity Bar (VS Code Pattern) --- */
    #ActivityBar {
        background-color: #18191D;
        border-right: 1px solid #2D3748;
    }

    #ActivityBar QPushButton {
        background-color: transparent;
        border: none;
        padding: 10px;
        color: #94A3B8;
        font-size: 18px;
    }

    #ActivityBar QPushButton:hover {
        color: #FFC107;
        background-color: rgba(255, 193, 7, 0.05);
    }

    #ActivityBar QPushButton:checked {
        color: #FFC107;
        border-left: 2px solid #FFC107;
        background-color: rgba(255, 193, 7, 0.1);
    }

    /* --- Top Custom Toolbar --- */
    #TopBar {
        background-color: #1E293B;
        border-bottom: 1px solid #334155;
    }

    #SearchContainer {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 6px;
        color: #94A3B8;
    }

    #SearchContainer:focus-within {
        border: 1px solid #FFC107;
    }

    #SearchInput {
        background-color: transparent;
        border: none;
        color: #F8FAFC;
        padding: 4px;
        font-size: 11px;
    }

    /* --- Sidebars & Splitters --- */
    #SideBar {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
        border-left: 1px solid #1E293B;
    }

    QSplitter::handle {
        background-color: #1E293B;
    }

    QSplitter::handle:hover {
        background-color: #FFC107;
    }

    /* --- Tabs Container --- */
    QTabWidget::pane {
        border: none;
        background-color: #09090B;
    }

    QTabBar::tab {
        background-color: #1E293B;
        color: #8E918F;
        padding: 8px 16px;
        border-right: 1px solid #0F172A;
        font-size: 11px;
    }

    QTabBar::tab:selected {
        background-color: #09090B;
        color: #FFFFFF;
        border-top: 2px solid #FFC107;
    }

    /* --- Scrollbars (Thin Neon Style) --- */
    QScrollBar:vertical {
        background: transparent;
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

    /* --- Status Bar --- */
    QStatusBar {
        background-color: #FFC107;
        color: #0F172A;
        font-weight: bold;
        text-transform: uppercase;
        font-size: 10px;
    }

    /* --- Buttons and Controls --- */
    QPushButton {
        border-radius: 4px;
        padding: 5px 12px;
    }

    #ToggleBtn {
        background: transparent;
        color: #94A3B8;
        font-size: 14px;
    }

    #ToggleBtn:hover {
        color: #FFFFFF;
        background: rgba(255, 255, 255, 0.05);
    }
    
    #ToggleBtn[active="true"] {
        color: #FFC107;
        background: rgba(255, 193, 7, 0.05);
    }

    /* --- Placeholders / Resilience --- */
    QLabel#Placeholder {
        color: #475569;
        font-style: italic;
    }
    """
