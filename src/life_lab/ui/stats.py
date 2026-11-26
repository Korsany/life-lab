import csv
from io import StringIO
from math import ceil

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import (QAbstractItemView, QHeaderView, QPushButton,
                             QSizePolicy, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from .style import colors

KEEP_POINTS = 20000
KEEP_ROWS = 500
DRAW_MAX = 2000


class Plot(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pts = []
        self.setMinimumHeight(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_points(self, pts):
        self._pts = pts
        self.update()

    def paintEvent(self, _):
        c = colors()
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.fillRect(self.rect(), QColor(c["base"]))

        r = QRectF(self.rect()).adjusted(46, 12, -12, -24)
        if r.width() < 8 or r.height() < 8:
            return

        p.setPen(QPen(QColor(c["border"]), 1))
        p.drawLine(r.bottomLeft(), r.topLeft())
        p.drawLine(r.bottomLeft(), r.bottomRight())

        pts = self._pts
        top = 1
        for _, a in pts:
            if a > top:
                top = a

        p.setPen(QColor(c["muted"]))
        p.drawText(QRectF(0, r.top() - 9, r.left() - 6, 18),
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(top))
        p.drawText(QRectF(0, r.bottom() - 9, r.left() - 6, 18),
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "0")

        if not pts:
            p.drawText(r, Qt.AlignmentFlag.AlignCenter, "нет данных")
            return

        g0 = pts[0][0]
        g1 = pts[-1][0]
        span = g1 - g0
        if span <= 0:
            span = 1

        if len(pts) > DRAW_MAX:
            k = ceil(len(pts) / DRAW_MAX)
            pts = pts[::k] + pts[-1:]

        poly = QPolygonF()
        for g, a in pts:
            x = r.left() + ((g - g0) / span) * r.width() if g1 != g0 else r.center().x()
            y = r.bottom() - (a / top) * r.height()
            poly.append(QPointF(x, y))

        p.setPen(QPen(QColor(c["accent"]), 1.6))
        p.drawPolyline(poly)


class Stats(QWidget):
    export = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pts = []

        self.plot = Plot(self)
        self.table = QTableWidget(0, 2, self)
        self.table.setHorizontalHeaderLabels(["Поколение", "Живых"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)

        self.btn = QPushButton("Экспорт CSV", self)
        self.btn.clicked.connect(self.export.emit)

        lay = QVBoxLayout(self)
        lay.addWidget(self.plot, 3)
        lay.addWidget(self.table, 2)
        lay.addWidget(self.btn)

    def reset(self):
        self._pts.clear()
        self.table.setRowCount(0)
        self.plot.set_points(self._pts)

    def add(self, gen: int, alive: int):
        self._pts.append((gen, alive))
        if len(self._pts) > KEEP_POINTS:
            del self._pts[:-KEEP_POINTS]

        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, val in enumerate((gen, alive)):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, col, item)
        if self.table.rowCount() > KEEP_ROWS:
            self.table.removeRow(0)
        self.table.scrollToBottom()
        self.plot.set_points(self._pts)

    def data(self) -> str:
        out = StringIO()
        wr = csv.writer(out, delimiter=";", lineterminator="\n")
        wr.writerow(["поколение", "живых"])
        wr.writerows(self._pts)
        return out.getvalue()

    def rows(self) -> list[tuple[int, int]]:
        return list(self._pts)
