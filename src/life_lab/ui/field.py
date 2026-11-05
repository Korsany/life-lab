import random

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

from ..core.rules import RULES, parse


class Field(QWidget):
    def __init__(self, w, h, cell):
        super().__init__()
        self.w, self.h, self.cell = w, h, cell
        self.g = [[0] * w for _ in range(h)]
        self.b, self.s = parse(RULES["Жизнь"])
        self.v = 1
        self.setFixedSize(w * cell, h * cell)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#101014"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#7ad"))
        for y in range(self.h):
            for x in range(self.w):
                if self.g[y][x]:
                    p.drawRect(x * self.cell, y * self.cell, self.cell, self.cell)

    def mousePressEvent(self, e):
        self.v = 0 if e.button() == Qt.MouseButton.RightButton else 1
        self.draw(e.position())

    def mouseMoveEvent(self, e):
        if e.buttons():
            self.draw(e.position())

    def draw(self, pos):
        x, y = int(pos.x()) // self.cell, int(pos.y()) // self.cell
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        if self.g[y][x] == self.v:
            return
        self.g[y][x] = self.v
        self.update()

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

    def fill(self):
        self.g = [[int(random.random() < 0.3) for _ in range(self.w)] for _ in range(self.h)]

    def clear(self):
        self.g = [[0] * self.w for _ in range(self.h)]
