from PyQt6.QtGui import QColor, QPalette

GREEN = "#4caf50"
GREEN_LIGHT = "#2e7d32"

DARK = {
    "win": "#16181d",
    "base": "#1e222a",
    "alt": "#262b35",
    "text": "#d8dee9",
    "muted": "#8a94a6",
    "border": "#2a2f3a",
    "accent": GREEN,
    "accent_text": "#101014",
    "alive": GREEN,
    "field": "#101014",
    "grid": "#20242c",
}

LIGHT = {
    "win": "#f5f6f8",
    "base": "#ffffff",
    "alt": "#eef1f5",
    "text": "#1b1f27",
    "muted": "#5c6675",
    "border": "#d3d9e2",
    "accent": GREEN_LIGHT,
    "accent_text": "#ffffff",
    "alive": GREEN_LIGHT,
    "field": "#ffffff",
    "grid": "#e1e6ee",
}

_cur = DARK


def colors():
    return dict(_cur)


def is_dark():
    return _cur is DARK


def _css(c):
    return f"""
QMainWindow, QDialog {{
    background: {c["win"]};
    color: {c["text"]};
}}
QWidget {{
    color: {c["text"]};
    font-size: 13px;
}}
QLabel {{
    color: {c["text"]};
    background: transparent;
}}
QLabel#muted, QLabel#lb {{
    color: {c["muted"]};
}}
QPushButton {{
    background: {c["base"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    padding: 5px 10px;
}}
QPushButton:hover {{
    background: {c["alt"]};
}}
QPushButton:checked {{
    background: {c["accent"]};
    color: {c["accent_text"]};
    border-color: {c["accent"]};
}}
QLineEdit, QSpinBox, QComboBox {{
    background: {c["base"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    border-radius: 4px;
    padding: 4px 6px;
    min-height: 22px;
}}
QSlider::groove:horizontal {{
    border: 1px solid {c["border"]};
    height: 6px;
    background: {c["alt"]};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {c["accent"]};
    border: none;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {c["accent"]};
    border-radius: 3px;
}}
QMenuBar, QStatusBar {{
    background: {c["win"]};
    color: {c["text"]};
}}
QMenu {{
    background: {c["base"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
}}
QMenu::item:selected {{
    background: {c["accent"]};
    color: {c["accent_text"]};
}}
QTabWidget::pane {{
    background: {c["base"]};
    border: 1px solid {c["border"]};
}}
QTabBar::tab {{
    background: {c["alt"]};
    color: {c["muted"]};
    border: 1px solid {c["border"]};
    padding: 6px 10px;
}}
QTabBar::tab:selected {{
    background: {c["base"]};
    color: {c["accent"]};
}}
QTableWidget, QTextBrowser {{
    background: {c["base"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    gridline-color: {c["border"]};
}}
QHeaderView::section {{
    background: {c["alt"]};
    color: {c["text"]};
    border: 1px solid {c["border"]};
    padding: 4px;
}}
QSplitter::handle {{
    background: {c["border"]};
}}
"""


def _palette(c):
    pal = QPalette()
    roles = {
        QPalette.ColorRole.Window: c["win"],
        QPalette.ColorRole.WindowText: c["text"],
        QPalette.ColorRole.Base: c["base"],
        QPalette.ColorRole.AlternateBase: c["alt"],
        QPalette.ColorRole.Text: c["text"],
        QPalette.ColorRole.Button: c["base"],
        QPalette.ColorRole.ButtonText: c["text"],
        QPalette.ColorRole.Highlight: c["accent"],
        QPalette.ColorRole.HighlightedText: c["accent_text"],
        QPalette.ColorRole.Mid: c["border"],
        QPalette.ColorRole.Dark: c["field"],
        QPalette.ColorRole.Shadow: c["border"],
        QPalette.ColorRole.ToolTipBase: c["base"],
        QPalette.ColorRole.ToolTipText: c["text"],
        QPalette.ColorRole.PlaceholderText: c["muted"],
    }
    for role, col in roles.items():
        pal.setColor(role, QColor(col))
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
    ):
        pal.setColor(QPalette.ColorGroup.Disabled, role, QColor(c["muted"]))
    return pal


def apply(app, dark=True):
    global _cur
    _cur = DARK if dark else LIGHT
    app.setStyle("Fusion")
    app.setPalette(_palette(_cur))
    app.setStyleSheet(_css(_cur))
