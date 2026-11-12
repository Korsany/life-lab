from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget)

from ..core.rules import RULES, parse
from .field import Field
from .settings import Settings


class Win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаборатория клеточных автоматов")
        self.f = Field(60, 40, 12)
        self.gen = 0
        self.t = QTimer(self)
        self.t.setInterval(100)
        self.t.timeout.connect(self.tick)

        self.btn = QPushButton("Старт")
        self.btn.setCheckable(True)
        self.btn.toggled.connect(self.run)
        step = QPushButton("Шаг")
        step.clicked.connect(self.tick)
        reset = QPushButton("Сброс")
        reset.clicked.connect(self.clear)
        rand = QPushButton("Случайно")
        rand.clicked.connect(self.fill)
        speed = QSpinBox()
        speed.setRange(1, 60)
        speed.setValue(10)
        speed.setFixedWidth(70)
        speed.valueChanged.connect(lambda v: self.t.setInterval(1000 // v))
        self.cb = QComboBox()
        self.cb.addItems(RULES)
        self.cb.setMinimumWidth(130)
        self.cb.currentTextChanged.connect(self.set_rule)
        self.lbl = QLabel()
        self.statusBar().addWidget(self.lbl)

        for b in (self.btn, step, reset, rand):
            b.setCursor(Qt.CursorShape.PointingHandCursor)

        lb = QLabel("Скорость")
        lb.setObjectName("lb")

        top = QHBoxLayout()
        top.setSpacing(6)
        top.addWidget(self.btn)
        top.addWidget(step)
        top.addWidget(reset)
        top.addWidget(rand)
        top.addStretch()
        top.addWidget(lb)
        top.addWidget(speed)
        top.addWidget(self.cb)

        lay = QVBoxLayout()
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(10)
        lay.addLayout(top)
        lay.addWidget(self.f)

        w = QWidget()
        w.setLayout(lay)
        self.setCentralWidget(w)
        self.upd()
        self.menu()

    def menu(self):
        m = self.menuBar()
        f = m.addMenu("Файл")
        f.addAction(self.act("Новое поле...", self.new_field, "Ctrl+N"))
        f.addSeparator()
        f.addAction(self.act("Выход", self.close, "Ctrl+Q"))
        s = m.addMenu("Симуляция")
        s.addAction(self.act("Старт/Пауза", self.btn.toggle, "Ctrl+Space"))
        s.addAction(self.act("Шаг", self.tick, "F10"))
        s.addAction(self.act("Сброс", self.clear, "Ctrl+R"))
        s.addAction(self.act("Случайно", self.fill, "Ctrl+F"))
        h = m.addMenu("Справка")
        h.addAction(self.act("О программе", self.about))

    def act(self, text, slot, key=None):
        a = QAction(text, self)
        a.triggered.connect(slot)
        if key:
            a.setShortcut(key)
        return a

    def new_field(self):
        d = Settings(self, self.f.w, self.f.h, self.f.cell, self.f.lines, self.cb.currentText())
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        w, h, cell, lines, rule = d.get()
        self.f.setup(w, h, cell, lines)
        self.cb.setCurrentText(rule)
        self.gen = 0
        self.upd()
        self.adjustSize()

    def about(self):
        QMessageBox.about(self, "О программе", "Лаборатория клеточных автоматов\nPyQt6")

    def run(self, on):
        self.btn.setText("Пауза" if on else "Старт")
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
        n = sum(sum(row) for row in self.f.g)
        self.lbl.setText(f"поколение: {self.gen}   живых: {n}")
