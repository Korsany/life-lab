from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QSpinBox, QVBoxLayout, QWidget)

from ..core.rules import RULES, parse
from .field import Field


class Win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаборатория клеточных автоматов")
        self.f = Field(60, 40, 12)
        self.gen = 0
        self.t = QTimer(self)
        self.t.setInterval(100)
        self.t.timeout.connect(self.tick)

        self.start = QPushButton("Старт")
        self.start.setCheckable(True)
        self.start.toggled.connect(self.run)
        step = QPushButton("Шаг")
        step.clicked.connect(self.tick)
        reset = QPushButton("Сброс")
        reset.clicked.connect(self.clear)
        rand = QPushButton("Случайно")
        rand.clicked.connect(self.fill)
        speed = QSpinBox()
        speed.setRange(1, 60)
        speed.setValue(10)
        speed.valueChanged.connect(lambda v: self.t.setInterval(1000 // v))
        rule = QComboBox()
        rule.addItems(RULES)
        rule.currentTextChanged.connect(self.set_rule)
        self.info = QLabel()
        self.statusBar().addWidget(self.info)

        top = QHBoxLayout()
        top.addWidget(self.start)
        top.addWidget(step)
        top.addWidget(reset)
        top.addWidget(rand)
        top.addWidget(QLabel("Скорость"))
        top.addWidget(speed)
        top.addWidget(rule)

        lay = QVBoxLayout()
        lay.addLayout(top)
        lay.addWidget(self.f)

        w = QWidget()
        w.setLayout(lay)
        self.setCentralWidget(w)
        self.upd()

    def run(self, on):
        self.start.setText("Пауза" if on else "Старт")
        if on:
            self.t.start()
        else:
            self.t.stop()

    def tick(self):
        self.gen += 1
        self.f.step()
        self.upd()

    def clear(self):
        self.gen = 0
        self.f.clear()
        self.upd()

    def fill(self):
        self.gen = 0
        self.f.fill()
        self.upd()

    def set_rule(self, r):
        self.f.b, self.f.s = parse(RULES[r])

    def upd(self):
        alive = sum(sum(row) for row in self.f.g)
        self.info.setText(f"поколение: {self.gen}   живых: {alive}")
