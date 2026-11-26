from pathlib import Path

from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap

DIR = Path(__file__).resolve().parent.parent / "assets"


def img(name, color):
    p = QPixmap(str(DIR / name))
    if p.isNull():
        return p
    out = QPixmap(p.size())
    out.fill(QColor(0, 0, 0, 0))
    q = QPainter(out)
    q.drawPixmap(0, 0, p)
    q.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    q.fillRect(out.rect(), QColor(color))
    q.end()
    return out


def icon(name, color):
    return QIcon(img(name, color))
