"""Styling for the RUMI desktop HUD interface."""

# HUD palette
HUD_BG = "#040b13"
HUD_GRID = "#0a1f33"
PANEL_BG = "#071523"
PANEL_ALT = "#0a1b2f"
CYAN_PRIMARY = "#44f0ff"
CYAN_DARK = "#149bb4"
TEXT_PRIMARY = "#d7f7ff"
TEXT_SECONDARY = "#7eb6c4"
ACCENT_GREEN = "#62ff9f"
ACCENT_RED = "#ff4f7a"

# Main stylesheet
STYLESHEET = f"""
    QMainWindow {{
        background-color: {HUD_BG};
        color: {TEXT_PRIMARY};
    }}
    
    QWidget {{
        background-color: transparent;
        color: {TEXT_PRIMARY};
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
    }}

    #rootPanel {{
        background-color: {HUD_BG};
        border: 1px solid {HUD_GRID};
    }}

    #leftPanel, #rightPanel {{
        background-color: {PANEL_BG};
        border: 1px solid {CYAN_DARK};
        border-radius: 12px;
    }}

    #hudTitle {{
        color: {CYAN_PRIMARY};
        letter-spacing: 2px;
        font-weight: 700;
        font-size: 22px;
    }}

    #hudSubtitle {{
        color: {TEXT_SECONDARY};
        font-size: 11px;
    }}
    
    QTabWidget::pane {{
        border: 1px solid {CYAN_DARK};
        border-radius: 8px;
        top: -1px;
        background-color: {PANEL_ALT};
    }}
    
    QTabBar::tab {{
        background-color: {PANEL_BG};
        color: {TEXT_SECONDARY};
        padding: 8px 14px;
        border: 1px solid {CYAN_DARK};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 4px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {PANEL_ALT};
        color: {CYAN_PRIMARY};
        border-color: {CYAN_PRIMARY};
    }}
    
    QLineEdit {{
        background-color: {PANEL_ALT};
        color: {TEXT_PRIMARY};
        border: 1px solid {CYAN_DARK};
        border-radius: 8px;
        padding: 8px 10px;
    }}
    
    QLineEdit:focus, QTextEdit:focus {{
        border: 2px solid {CYAN_PRIMARY};
    }}
    
    QPushButton {{
        background-color: transparent;
        color: {CYAN_PRIMARY};
        border: 1px solid {CYAN_PRIMARY};
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        text-transform: uppercase;
    }}
    
    QPushButton:hover {{
        background-color: rgba(68, 240, 255, 0.15);
    }}
    
    QPushButton:pressed {{
        background-color: rgba(68, 240, 255, 0.25);
    }}
    
    QTextEdit, QPlainTextEdit {{
        background-color: {PANEL_ALT};
        color: {TEXT_PRIMARY};
        border: 1px solid {CYAN_DARK};
        border-radius: 8px;
        selection-background-color: rgba(68, 240, 255, 0.35);
    }}
    
    QScrollBar:vertical {{
        background-color: {HUD_BG};
        width: 12px;
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {CYAN_DARK};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {CYAN_DARK};
    }}
    
    QLabel {{
        color: {TEXT_PRIMARY};
    }}
    
    QGroupBox {{
        color: {TEXT_PRIMARY};
        border: 1px solid {CYAN_DARK};
        border-radius: 8px;
        padding-top: 10px;
        margin-top: 10px;
        background-color: {PANEL_ALT};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }}

    QStatusBar {{
        background-color: {PANEL_BG};
        color: {TEXT_SECONDARY};
        border-top: 1px solid {CYAN_DARK};
    }}
"""


def get_chat_message_css(is_user: bool) -> str:
    """Returns CSS for styling a chat message bubble."""
    if is_user:
        return f"""
            background-color: rgba(68, 240, 255, 0.2);
            color: {CYAN_PRIMARY};
            border: 1px solid {CYAN_PRIMARY};
            border-radius: 12px 2px 12px 12px;
            padding: 10px 14px;
        """
    else:
        return f"""
            background-color: {PANEL_ALT};
            color: {TEXT_PRIMARY};
            border: 1px solid {CYAN_DARK};
            border-radius: 2px 12px 12px 12px;
            padding: 10px 14px;
        """
