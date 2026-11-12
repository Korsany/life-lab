from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
                             QSpinBox, QVBoxLayout)

from ..core.rules import RULES


class Settings(QDialog):
    def __init__(self, parent, w, h, cell, lines, rule):
        super().__init__(parent)
        self.setWindowTitle("Настройки поля")

        self.w = QSpinBox()
        self.w.setRange(10, 300)
        self.w.setValue(w)
        self.h = QSpinBox()
        self.h.setRange(10, 300)
        self.h.setValue(h)
        self.cell = QSpinBox()
        self.cell.setRange(4, 32)
        self.cell.setValue(cell)
        self.chk = QCheckBox("Показывать сетку")
        self.chk.setChecked(lines)
        self.cb = QComboBox()
        self.cb.addItems(RULES)
        self.cb.setCurrentText(rule)

        form = QFormLayout()
        form.addRow("Ширина", self.w)
        form.addRow("Высота", self.h)
        form.addRow("Клетка", self.cell)
        form.addRow("Правило", self.cb)

        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        box.button(QDialogButtonBox.StandardButton.Ok).setText("ОК")
        box.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(self.chk)
        lay.addWidget(box)

    def get(self):
        return self.w.value(), self.h.value(), self.cell.value(), self.chk.isChecked(), self.cb.currentText()
