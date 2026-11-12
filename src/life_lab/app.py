import sys

from PyQt6.QtWidgets import QApplication

from .ui.style import apply
from .ui.window import Win


def main():
    app = QApplication(sys.argv)
    apply(app)
    win = Win()
    win.show()
    return app.exec()
