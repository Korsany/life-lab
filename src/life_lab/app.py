import sys

from PyQt6.QtWidgets import QApplication

from .ui.window import Win


def main():
    app = QApplication(sys.argv)
    win = Win()
    win.show()
    return app.exec()
