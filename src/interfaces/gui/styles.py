def get_main_stylesheet():
    """
    Folha de estilos central do fotonPDF.
    Tema: Dark Industrial Tech (AEC-Dark)
    Conceito: Sobriedade de IDE + Urgência Visual de Obra.
    """
    return """
    /* --- VARIÁVEIS (Conceituais - aplicadas diretamente) ---
       BG Canvas: #0F0F11
       BG Panels: #18181B
       Surface:   #27272A
       Accent:    #FFD600 (Safety Yellow)
       Text:      #FAFAFA
       Border:    #3F3F46
    */

    /* --- GLOBALS --- */
    QMainWindow {
        background-color: #0F0F11;
    }

    QWidget {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 13px;
        color: #FAFAFA;
    }

    /* --- PAINÉIS LATERAIS --- */
    #SideBar, #InspectorPanel {
        background-color: #18181B;
        border-right: 1px solid #3F3F46;
        border-left: 1px solid #3F3F46;
    }
    
    QSplitter::handle {
        background-color: #0F0F11;
    }
    QSplitter::handle:hover {
        background-color: #FFD600;
    }

    /* --- TOP BAR & BOTÕES --- */
    #TopBar {
        background-color: #0F0F11;
        border-bottom: 1px solid #3F3F46;
    }

    QPushButton {
        background-color: #27272A;
        border: 1px solid #3F3F46;
        border-radius: 6px;
        padding: 6px 12px;
        color: #FAFAFA;
        font-weight: 500;
    }

    QPushButton:hover {
        background-color: #3F3F46;
        border-color: #52525B;
    }

    QPushButton:checked, QPushButton[active="true"] {
        background-color: #2E2E33;
        border: 1px solid #FFD600;
        color: #FFD600;
    }

    /* --- ACTIVITY BAR --- */
    #ActivityBar {
        background-color: #18181B;
        border-right: 1px solid #3F3F46;
    }
    #ActivityBar QPushButton {
        border: none;
        background: transparent;
        color: #71717A;
        border-radius: 0;
    }
    #ActivityBar QPushButton:hover {
        color: #FAFAFA;
        background: #27272A;
    }
    #ActivityBar QPushButton:checked {
        color: #FFD600;
        border-left: 2px solid #FFD600;
    }

    /* --- PESQUISA --- */
    #SearchContainer {
        background-color: #27272A;
        border: 1px solid #3F3F46;
        border-radius: 8px;
    }
    #SearchContainer:focus-within {
        border: 1px solid #FFD600;
        background-color: #27272A;
    }
    #SearchInput {
        background: transparent;
        border: none;
        color: #FAFAFA;
        font-size: 13px;
    }

    /* --- SCROLLBARS (Minimalista) --- */
    QScrollBar:vertical {
        background: #18181B;
        width: 8px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #3F3F46;
        min-height: 30px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #52525B;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    
    QSplitter::handle {
        background-color: #0F0F11;
        /* create a pseudo-border/highlight for visibility */
        border: 1px solid #27272A; 
        margin: 1px;
    }
    QSplitter::handle:hover {
        background-color: #FFD600;
        border-color: #FFD600;
    }

    /* --- STATUS BAR --- */
    QStatusBar {
        background-color: #FFD600;
        color: #18181B;
        font-weight: bold;
        font-size: 11px;
        border-top: 1px solid #CCAA00;
    }
    QStatusBar QLabel {
        color: #18181B; /* Contraste preto no amarelo */
    }

    /* --- TABS --- */
    QTabWidget::pane {
        border: none;
        background: #0F0F11;
        border-top: 1px solid #3F3F46;
    }
    QTabBar::tab {
        background: #18181B;
        color: #A1A1AA;
        padding: 8px 16px;
        border-right: 1px solid #27272A;
        font-size: 12px;
    }
    QTabBar::tab:selected {
        background: #0F0F11;
        color: #FFD600;
        border-top: 2px solid #FFD600;
    }

    /* --- Buttons and Controls --- */
    QPushButton {
        border-radius: 4px;
        padding: 5px 12px;
    }

    /* Reset padding for icon-only buttons to prevent clipping */
    #ToggleBtn {
        background: transparent;
        color: #94A3B8;
        font-size: 16px; /* Aumentado para melhor visibilidade */
        padding: 0px;    /* Zero padding for centered icon */
        border: none;    /* Remove default border */
    }

    #ToggleBtn:hover {
        color: #FFFFFF;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    #ToggleBtn[active="true"] {
        color: #FFD600;
        background: rgba(255, 214, 0, 0.1);
    }
    QLabel#Placeholder {
        color: #52525B;
        font-style: italic;
    }
    """
