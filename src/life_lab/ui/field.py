import random

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

from ..core.rules import RULES, parse
from .style import colors


class Field(QWidget):
    changed = pyqtSignal()
    zoomed = pyqtSignal(int)

    def __init__(self, w, h, cell):
        super().__init__()
        self.b, self.s = parse(RULES["Жизнь"])
        self.v = 1
        self.prev = None
        self.last = None
        self.setup(w, h, cell, False)

    def setup(self, w, h, cell, lines):
        self.w, self.h, self.cell, self.lines = w, h, cell, lines
        self.g = [[0] * w for _ in range(h)]
        self.prev = None
        self.setFixedSize(w * cell, h * cell)
        self.update()

    def set_cell(self, cell):
        self.cell = max(2, min(32, cell))
        self.setFixedSize(self.w * self.cell, self.h * self.cell)
        self.update()

    def set_rule(self, rule):
        self.b, self.s = parse(rule)

    def set_lines(self, on):
        self.lines = on
        self.update()

    def alive(self):
        return sum(sum(row) for row in self.g)

    def snapshot(self):
        self.prev = [row[:] for row in self.g]

    def undo(self):
        if self.prev is None:
            return False
        self.g = self.prev
        self.prev = None
        self.update()
        return True

    def paintEvent(self, e):
        c = colors()
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(c["field"]))
        if self.lines:
            p.setPen(QColor(c["grid"]))
            for x in range(self.w + 1):
                p.drawLine(x * self.cell, 0, x * self.cell, self.h * self.cell)
            for y in range(self.h + 1):
                p.drawLine(0, y * self.cell, self.w * self.cell, y * self.cell)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(c["alive"]))
        for y in range(self.h):
            for x in range(self.w):
                if self.g[y][x]:
                    p.drawRect(x * self.cell, y * self.cell, self.cell, self.cell)

    def mousePressEvent(self, e):
        self.v = 0 if e.button() == Qt.MouseButton.RightButton else 1
        self.snapshot()
        self.last = None
        self.draw(e.position())

    def mouseMoveEvent(self, e):
        if e.buttons():
            self.draw(e.position())

    def mouseReleaseEvent(self, e):
        self.last = None

    def wheelEvent(self, e):
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoomed.emit(1 if e.angleDelta().y() > 0 else -1)
            e.accept()
            return
        e.ignore()

    def draw(self, pos):
        x, y = int(pos.x()) // self.cell, int(pos.y()) // self.cell
        if not (0 <= x < self.w and 0 <= y < self.h):
            self.last = None
            return
        cells = [(x, y)]
        if self.last and self.last != (x, y):
            cells = self.line(self.last, (x, y))
        hit = False
        for cx, cy in cells:
            if self.g[cy][cx] != self.v:
                self.g[cy][cx] = self.v
                hit = True
        self.last = (x, y)
        if hit:
            self.update()
            self.changed.emit()

    def line(self, a, b):
        x0, y0 = a
        x1, y1 = b
        n = max(abs(x1 - x0), abs(y1 - y0))
        out = []
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            if 0 <= x < self.w and 0 <= y < self.h:
                out.append((x, y))
        return out

    def count(self, x, y):
        k = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if i or j:
                    k += self.g[(y + j) % self.h][(x + i) % self.w]
        return k

    def step(self):
        n = [[0] * self.w for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                rule = self.s if self.g[y][x] else self.b
                n[y][x] = 1 if self.count(x, y) in rule else 0
        self.g = n
        self.update()

    def fill(self, d=0.3):
        self.g = [[int(random.random() < d) for _ in range(self.w)] for _ in range(self.h)]
        self.update()

    def clear(self):
        self.g = [[0] * self.w for _ in range(self.h)]
        self.update()

    def place(self, cells, cx, cy):
        self.snapshot()
        pw = max(x for x, _ in cells) + 1
        ph = max(y for _, y in cells) + 1
        ox, oy = cx - pw // 2, cy - ph // 2
        for x, y in cells:
            gx, gy = ox + x, oy + y
            if 0 <= gx < self.w and 0 <= gy < self.h:
                self.g[gy][gx] = 1
        self.update()
        self.changed.emit()
