from PyQt6.QtGui import QColor, QPalette

COLORS = {
    "Window": "#16181d",
    "WindowText": "#d8dee9",
    "Base": "#1e222a",
    "AlternateBase": "#262b35",
    "Text": "#d8dee9",
    "Button": "#1e222a",
    "ButtonText": "#d8dee9",
    "Highlight": "#77aadd",
    "HighlightedText": "#101014",
    "Mid": "#2a2f3a",
    "Dark": "#101014",
    "Shadow": "#2a2f3a",
    "ToolTipBase": "#1e222a",
    "ToolTipText": "#d8dee9",
}

QSS = """
QMainWindow, QDialog { background: #16181d; }
QLabel { color: #d8dee9; }
QLabel#lb { color: #8a94a6; }

QPushButton {
    background: #1e222a;
    border: 1px solid #2a2f3a;
    border-radius: 6px;
    padding: 6px 16px;
    color: #d8dee9;
}
QPushButton:hover { background: #262b35; border-color: #3a4150; }
QPushButton:pressed { background: #2f3542; }
QPushButton:checked { background: #77aadd; border-color: #77aadd; color: #101014; }

QMenuBar { background: #16181d; color: #8a94a6; }
QMenuBar::item { padding: 5px 10px; background: transparent; }
QMenuBar::item:selected { background: #262b35; color: #d8dee9; }
QMenu { background: #1e222a; border: 1px solid #2a2f3a; }
QMenu::item { padding: 5px 24px; }
QMenu::item:selected { background: #77aadd; color: #101014; }
QMenu::separator { height: 1px; background: #2a2f3a; margin: 4px 8px; }

QStatusBar { background: #101014; }
QStatusBar QLabel { color: #8a94a6; }
"""


def apply(app):
    app.setStyle("Fusion")
    pal = QPalette()
    for role, col in COLORS.items():
        pal.setColor(getattr(QPalette.ColorRole, role), QColor(col))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#5a6474"))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#5a6474"))
    pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#5a6474"))
    app.setPalette(pal)
    app.setStyleSheet(QSS)
