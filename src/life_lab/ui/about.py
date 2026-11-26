from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from .. import __version__
from . import assets, style


class About(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setMinimumWidth(360)

        logo = QLabel()
        logo.setPixmap(assets.img("logo.png", style.colors()["accent"]).scaled(
            72, 72, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name = QLabel("Лаборатория клеточных автоматов")
        name.setStyleSheet("font-size: 16px; font-weight: bold;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ver = QLabel(f"Версия {__version__}")
        ver.setObjectName("muted")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)

        author = QLabel("Автор: Сарычев Семён")
        author.setObjectName("muted")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt = QLabel("Правила, паттерны, статистика и сохранение полей.")
        txt.setObjectName("muted")
        txt.setWordWrap(True)
        txt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        b = QPushButton("Закрыть")
        b.clicked.connect(self.accept)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(8)
        lay.addWidget(logo)
        lay.addWidget(name)
        lay.addWidget(ver)
        lay.addWidget(author)
        lay.addWidget(txt)
        lay.addSpacing(8)
        lay.addWidget(b)
