from PyQt6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QSpinBox,
                             QVBoxLayout)


class Settings(QDialog):
    def __init__(self, parent, w, h, cell, lines):
        super().__init__(parent)
        self.setWindowTitle("Настройки поля")

        self.w = QSpinBox()
        self.w.setRange(10, 300)
        self.w.setValue(w)
        self.h = QSpinBox()
        self.h.setRange(10, 300)
        self.h.setValue(h)
        self.cell = QSpinBox()
        self.cell.setRange(2, 32)
        self.cell.setValue(cell)
        self.chk = QCheckBox("Показывать сетку")
        self.chk.setChecked(lines)

        form = QFormLayout()
        form.addRow("Ширина", self.w)
        form.addRow("Высота", self.h)
        form.addRow("Клетка", self.cell)

        box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        box.button(QDialogButtonBox.StandardButton.Ok).setText("ОК")
        box.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)
        lay.addLayout(form)
        lay.addWidget(self.chk)
        lay.addWidget(box)
        self.setMinimumWidth(260)

    def get(self):
        return self.w.value(), self.h.value(), self.cell.value(), self.chk.isChecked()
