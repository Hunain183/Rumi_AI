"""
Styling — Dark theme with cyan accents (matching CLI aesthetic).
"""

# Colors
DARK_BG = "#1a1a2e"
DARK_PANEL = "#16213e"
CYAN_PRIMARY = "#00d4ff"
CYAN_DARK = "#0099cc"
TEXT_PRIMARY = "#e0e0e0"
TEXT_SECONDARY = "#a0a0a0"
ACCENT_GREEN = "#00ff88"
ACCENT_RED = "#ff4757"

# Main stylesheet
STYLESHEET = f"""
    QMainWindow {{
        background-color: {DARK_BG};
        color: {TEXT_PRIMARY};
    }}
    
    QWidget {{
        background-color: {DARK_BG};
        color: {TEXT_PRIMARY};
    }}
    
    QTabWidget::pane {{
        border: 1px solid {DARK_PANEL};
        background-color: {DARK_BG};
    }}
    
    QTabBar::tab {{
        background-color: {DARK_PANEL};
        color: {TEXT_SECONDARY};
        padding: 8px 16px;
        border: none;
        border-bottom: 2px solid transparent;
    }}
    
    QTabBar::tab:selected {{
        background-color: {DARK_BG};
        color: {CYAN_PRIMARY};
        border-bottom: 2px solid {CYAN_PRIMARY};
    }}
    
    QLineEdit {{
        background-color: {DARK_PANEL};
        color: {TEXT_PRIMARY};
        border: 1px solid {CYAN_DARK};
        border-radius: 4px;
        padding: 8px;
    }}
    
    QLineEdit:focus {{
        border: 2px solid {CYAN_PRIMARY};
    }}
    
    QPushButton {{
        background-color: {CYAN_PRIMARY};
        color: #000;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    
    QPushButton:hover {{
        background-color: {CYAN_DARK};
    }}
    
    QPushButton:pressed {{
        background-color: #006699;
    }}
    
    QTextEdit, QPlainTextEdit {{
        background-color: {DARK_PANEL};
        color: {TEXT_PRIMARY};
        border: 1px solid {DARK_PANEL};
        border-radius: 4px;
    }}
    
    QScrollBar:vertical {{
        background-color: {DARK_BG};
        width: 12px;
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {DARK_PANEL};
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
        border: 1px solid {DARK_PANEL};
        border-radius: 4px;
        padding-top: 10px;
        margin-top: 10px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }}
"""


def get_chat_message_css(is_user: bool) -> str:
    """Returns CSS for styling a chat message bubble."""
    if is_user:
        return f"""
            background-color: {CYAN_PRIMARY};
            color: #000;
            border-radius: 12px 2px 12px 12px;
            padding: 10px 14px;
        """
    else:
        return f"""
            background-color: {DARK_PANEL};
            color: {TEXT_PRIMARY};
            border: 1px solid {CYAN_DARK};
            border-radius: 2px 12px 12px 12px;
            padding: 10px 14px;
        """
