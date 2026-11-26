import sqlite3
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog, QHBoxLayout,
                             QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QScrollArea, QSlider, QSpinBox,
                             QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
                             QTextBrowser, QVBoxLayout, QWidget)

from ..core import io
from ..core.db import DB
from ..core.patterns import PATTERNS
from ..core.patterns import size as psize
from ..core.rules import DESC, RULES, describe, valid
from . import assets, style
from .about import About
from .field import Field
from .settings import Settings
from .stats import Stats

CUSTOM = "Своё..."


class Win(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаборатория клеточных автоматов")
        self.setMinimumSize(900, 600)
        self.resize(1100, 720)
        self.f = Field(50, 34, 12)
        self.gen = 0
        self.rule = RULES["Жизнь"]
        self.path = None
        self.dirty = False
        self.db = DB()
        dark = self.db.get_setting("theme", "dark") != "light"
        style.apply(QApplication.instance(), dark)
        self.setWindowIcon(assets.icon("logo.png", style.colors()["accent"]))
        self.t = QTimer(self)
        self.t.setInterval(100)
        self.t.timeout.connect(self.tick)

        self.panel()
        self.menu()
        self.main()
        self.upd()
        self.upd_rules()
        self.refresh_db()

    def panel(self):
        self.b_start = self.btn("Старт", self.run, True)
        self.b_step = self.btn("Шаг", self.tick)
        self.b_reset = self.btn("Сброс", self.clear)
        self.b_rand = self.btn("Случайно", self.fill)

        self.sp = QSpinBox()
        self.sp.setRange(1, 60)
        self.sp.setValue(10)
        self.sp.setFixedWidth(56)
        self.sp.setToolTip("Скорость, поколений в секунду")
        self.sp.valueChanged.connect(lambda v: self.t.setInterval(1000 // v))

        self.cb = QComboBox()
        self.cb.addItems(list(RULES) + [CUSTOM])
        self.cb.setMinimumWidth(110)
        self.cb.currentTextChanged.connect(self.pick_rule)

        self.dn = QSlider(Qt.Orientation.Horizontal)
        self.dn.setRange(0, 100)
        self.dn.setValue(30)
        self.dn.setFixedWidth(90)
        self.dn.setToolTip("Плотность случайного заполнения")
        self.dl = QLabel("30%")
        self.dl.setFixedWidth(36)

        def _dn(v):
            self.dl.setText(f"{v}%")

        self.dn.valueChanged.connect(_dn)

        self.b_out = QPushButton("-")
        self.b_out.setToolTip("Уменьшить масштаб")
        self.b_out.clicked.connect(lambda: self.zoom(-2))
        self.b_in = QPushButton("+")
        self.b_in.setToolTip("Увеличить масштаб")
        self.b_in.clicked.connect(lambda: self.zoom(2))
        self.b_theme = QPushButton()
        self.b_theme.setToolTip("Сменить тему")
        self.b_theme.setFixedSize(32, 32)
        self.b_theme.setIconSize(QSize(18, 18))
        self.b_theme.clicked.connect(self.toggle_theme)
        self.theme_icon()

        for b in (self.b_out, self.b_in):
            b.setFixedSize(32, 32)

        lb = QLabel("Скорость")

        top = QHBoxLayout()
        top.setSpacing(6)
        top.addWidget(self.b_start)
        top.addWidget(self.b_step)
        top.addWidget(self.b_reset)
        top.addWidget(self.b_rand)
        top.addStretch()
        top.addWidget(lb)
        top.addWidget(self.sp)
        top.addWidget(self.cb)
        top.addWidget(QLabel("Плотность"))
        top.addWidget(self.dn)
        top.addWidget(self.dl)
        top.addWidget(self.b_out)
        top.addWidget(self.b_in)
        top.addWidget(self.b_theme)
        self.top = top

    def btn(self, text, slot, check=False):
        b = QPushButton(text)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setCheckable(check)
        if check:
            b.toggled.connect(slot)
        else:
            b.clicked.connect(slot)
        return b

    def menu(self):
        m = self.menuBar()

        f = m.addMenu("Файл")
        self.a("Новое поле...", self.new_field, "Ctrl+N", f)
        self.a("Открыть...", self.open, "Ctrl+O", f)
        self.a("Сохранить", self.save, "Ctrl+S", f)
        self.a("Сохранить как...", self.save_as, "Ctrl+Shift+S", f)
        f.addSeparator()
        self.a("Экспорт PNG...", self.png, None, f)
        f.addSeparator()
        self.a("Выход", self.close, "Ctrl+Q", f)

        p = m.addMenu("Правка")
        self.a("Отменить", self.undo, "Ctrl+Z", p)
        self.grid_act = self.a("Показывать сетку", None, "Ctrl+G", p, True)
        self.grid_act.toggled.connect(self.f.set_lines)
        p.addSeparator()
        self.a("Очистить поле", self.clear, "Ctrl+R", p)
        self.a("Заполнить случайно", self.fill, "Ctrl+F", p)
        sub = p.addMenu("Вставить фигуру")
        for name in PATTERNS:
            act = QAction(name, self)
            act.triggered.connect(lambda on=False, n=name: self.place(n))
            sub.addAction(act)

        s = m.addMenu("Симуляция")
        self.a("Старт/Пауза", self.b_start.toggle, "Ctrl+Space", s)
        self.a("Шаг", self.tick, "F10", s)
        s.addSeparator()
        self.a("Сброс", self.clear, None, s)
        self.a("Случайно", self.fill, None, s)

        h = m.addMenu("Справка")
        self.a("Правила", lambda: self.tabs.setCurrentIndex(0), "F1", h)
        self.a_theme = self.a("Темная тема", None, "Ctrl+T", h, True)
        self.a_theme.blockSignals(True)
        self.a_theme.setChecked(style.is_dark())
        self.a_theme.blockSignals(False)
        self.a_theme.toggled.connect(self.set_theme)
        h.addSeparator()
        self.a("О программе", self.about, None, h)

    def a(self, text, slot, key, menu, check=False):
        act = QAction(text, self)
        if slot is not None:
            act.triggered.connect(slot)
        if key:
            act.setShortcut(key)
        act.setCheckable(check)
        menu.addAction(act)
        return act

    def main(self):
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.f)
        self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left = QWidget()
        lay = QVBoxLayout(left)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.scroll)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.tab_rules(), "Правила")
        self.tabs.addTab(self.tab_patterns(), "Паттерны")
        self.tabs.addTab(self.tab_saved(), "Сохранённые")
        self.tabs.addTab(self.tab_stats(), "Статистика")

        self.split = QSplitter(Qt.Orientation.Horizontal)
        self.split.addWidget(left)
        self.split.addWidget(self.tabs)
        self.split.setStretchFactor(0, 3)
        self.split.setStretchFactor(1, 2)
        self.split.setSizes([590, 330])

        lay = QVBoxLayout()
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(8)
        lay.addLayout(self.top)
        lay.addWidget(self.split)

        w = QWidget()
        w.setLayout(lay)
        self.setCentralWidget(w)

        self.sl = QLabel()
        self.rl = QLabel()
        self.statusBar().addWidget(self.sl)
        self.statusBar().addPermanentWidget(self.rl)

        self.f.changed.connect(self.mark)
        self.f.zoomed.connect(self.zoom)

    def tab_rules(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.rb = QTextBrowser()
        self.rb.setOpenExternalLinks(False)
        self.rle = QLineEdit()
        self.rle.setPlaceholderText("B3/S23")
        self.rle.returnPressed.connect(self.custom_rule)
        b = QPushButton("Применить")
        b.clicked.connect(self.custom_rule)
        row = QHBoxLayout()
        row.addWidget(self.rle)
        row.addWidget(b)
        lay.addWidget(self.rb, 1)
        lay.addLayout(row)
        return w

    def tab_patterns(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.pt = QTableWidget(0, 2)
        self.pt.setHorizontalHeaderLabels(["Фигура", "Размер"])
        self.pt.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pt.verticalHeader().setVisible(False)
        self.pt.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pt.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.pt.setAlternatingRowColors(True)
        for name, cells in PATTERNS.items():
            i = self.pt.rowCount()
            self.pt.insertRow(i)
            self.pt.setItem(i, 0, QTableWidgetItem(name))
            pw, ph = psize(cells)
            self.pt.setItem(i, 1, QTableWidgetItem(f"{pw}x{ph}"))
        self.pt.cellDoubleClicked.connect(lambda r, c: self.place_cur())
        b = QPushButton("Вставить в центр")
        b.clicked.connect(self.place_cur)
        lay.addWidget(self.pt, 1)
        lay.addWidget(b)
        return w

    def tab_saved(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.sv = QTableWidget(0, 4)
        self.sv.setHorizontalHeaderLabels(["Название", "Поле", "Правило", "Дата"])
        self.sv.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sv.verticalHeader().setVisible(False)
        self.sv.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sv.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.sv.setAlternatingRowColors(True)
        self.sv.cellDoubleClicked.connect(lambda r, c: self.db_load())
        row = QHBoxLayout()
        for text, slot in (("Сохранить", self.db_save), ("Загрузить", self.db_load),
                           ("Удалить", self.db_del)):
            b = QPushButton(text)
            b.clicked.connect(slot)
            row.addWidget(b)
        lay.addWidget(self.sv, 1)
        lay.addLayout(row)
        return w

    def tab_stats(self):
        self.st = Stats()
        self.st.export.connect(self.export_stats)
        return self.st

    def pick_rule(self, text):
        if text == CUSTOM:
            self.tabs.setCurrentIndex(0)
            self.rle.setFocus()
            self.rle.selectAll()
            return
        self.set_rule(RULES[text], text)

    def custom_rule(self):
        code = self.rle.text().strip().upper()
        if not valid(code):
            QMessageBox.warning(self, "Ошибка", "Некорректное правило")
            return
        self.set_rule(code)

    def set_rule(self, code, name=None):
        self.rule = code
        self.f.set_rule(code)
        self.rl.setText(describe(code))
        if name is None:
            name = self.rule_name(code)
        self.cb.blockSignals(True)
        if name:
            self.cb.setCurrentText(name)
        else:
            self.cb.setCurrentText(CUSTOM)
            self.rle.setText(code)
        self.cb.blockSignals(False)

    def rule_name(self, code):
        for name, value in RULES.items():
            if value == code:
                return name
        return None

    def upd_rules(self):
        c = style.colors()
        html = [f"<p style='color:{c['muted']}'>Текущее правило: <b>{self.rule}</b>. "
                f"{describe(self.rule)}.</p>"]
        for name, code in RULES.items():
            html.append(f"<h3>{name} <span style='color:{c['accent']}'>{code}</span></h3>")
            html.append(f"<p>{DESC[name]}</p>")
        html.append("<h3>Своё правило</h3>")
        html.append("<p>Запись B/S: сколько соседей нужно мёртвой клетке для рождения "
                    "и живой для выживания. Цифры от 0 до 8, например B3/S23.</p>")
        self.rb.setHtml("".join(html))

    def run(self, on):
        if on:
            self.t.start()
        else:
            self.t.stop()
        self.b_start.setText("Пауза" if on else "Старт")

    def tick(self):
        self.gen += 1
        self.f.step()
        self.st.add(self.gen, self.f.alive())
        self.upd()

    def clear(self):
        if not self.ask():
            return
        self.f.snapshot()
        self.f.clear()
        self.gen = 0
        self.st.reset()
        self.dirty = True
        self.upd()

    def fill(self):
        self.f.snapshot()
        self.f.fill(self.dn.value() / 100)
        self.gen = 0
        self.st.reset()
        self.dirty = True
        self.upd()

    def undo(self):
        if self.f.undo():
            self.dirty = True
            self.upd()

    def mark(self):
        self.dirty = True

    def zoom(self, d):
        self.f.set_cell(self.f.cell + d)

    def place(self, name):
        self.f.place(PATTERNS[name], self.f.w // 2, self.f.h // 2)
        self.dirty = True
        self.upd()

    def place_cur(self):
        row = self.pt.currentRow()
        if row < 0:
            return
        self.place(self.pt.item(row, 0).text())

    def new_field(self):
        if not self.ask():
            return
        d = Settings(self, self.f.w, self.f.h, self.f.cell, self.grid_act.isChecked())
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        w, h, cell, lines = d.get()
        self.f.setup(w, h, cell, lines)
        self.f.set_rule(self.rule)
        self.grid_act.setChecked(lines)
        self.gen = 0
        self.st.reset()
        self.path = None
        self.dirty = False
        self.upd()

    def open(self):
        if not self.ask():
            return
        name, _ = QFileDialog.getOpenFileName(
            self, "Открыть поле", "", "Поля (*.json *.csv);;JSON (*.json);;CSV (*.csv)")
        if not name:
            return
        p = Path(name)
        try:
            text = p.read_text(encoding="utf-8")
            if p.suffix.lower() == ".csv":
                grid = io.load_csv(text)
                w, h, rule = len(grid[0]), len(grid), self.rule
            else:
                w, h, rule, grid = io.load_json(text)
        except (OSError, ValueError):
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить файл")
            return
        self.f.setup(w, h, self.f.cell, self.grid_act.isChecked())
        self.f.g = [row[:] for row in grid]
        self.f.update()
        self.set_rule(rule)
        self.gen = 0
        self.st.reset()
        self.path = p
        self.dirty = False
        self.upd()

    def save(self):
        if self.path is None:
            self.save_as()
            return
        if self.write(self.path):
            self.dirty = False

    def save_as(self):
        name, flt = QFileDialog.getSaveFileName(
            self, "Сохранить поле", "поле.json", "JSON (*.json);;CSV (*.csv)")
        if not name:
            return
        p = Path(name)
        if not p.suffix:
            p = p.with_suffix(".csv" if "CSV" in flt else ".json")
        if self.write(p):
            self.path = p
            self.dirty = False

    def write(self, p):
        try:
            if p.suffix.lower() == ".csv":
                text = io.dump_csv(self.f.g)
            else:
                text = io.dump_json(self.f.w, self.f.h, self.rule, self.f.g)
            p.write_text(text, encoding="utf-8")
            return True
        except OSError:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить файл")
            return False

    def png(self):
        name, _ = QFileDialog.getSaveFileName(self, "Экспорт PNG", "поле.png", "PNG (*.png)")
        if not name:
            return
        p = Path(name)
        if p.suffix.lower() != ".png":
            p = p.with_suffix(".png")
        if not self.f.grab().save(str(p)):
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить картинку")

    def refresh_db(self):
        try:
            rows = self.db.all()
        except sqlite3.Error:
            QMessageBox.warning(self, "Ошибка", "Ошибка базы данных")
            return
        self.sv.setRowCount(0)
        for r in rows:
            i = self.sv.rowCount()
            self.sv.insertRow(i)
            item = QTableWidgetItem(r["name"])
            item.setData(Qt.ItemDataRole.UserRole, r["id"])
            self.sv.setItem(i, 0, item)
            self.sv.setItem(i, 1, QTableWidgetItem(f"{r['w']}x{r['h']}"))
            self.sv.setItem(i, 2, QTableWidgetItem(r["rule"]))
            self.sv.setItem(i, 3, QTableWidgetItem(r["date"]))

    def cur_id(self):
        row = self.sv.currentRow()
        if row < 0:
            return None
        return self.sv.item(row, 0).data(Qt.ItemDataRole.UserRole)

    def db_save(self):
        default = self.path.stem if self.path else f"Поле {self.sv.rowCount() + 1}"
        name, ok = QInputDialog.getText(self, "Сохранить в базу", "Название:", text=default)
        if not ok or not name.strip():
            return
        try:
            self.db.save(name.strip(), self.f.w, self.f.h, self.rule, self.f.g)
        except sqlite3.Error:
            QMessageBox.warning(self, "Ошибка", "Ошибка базы данных")
            return
        self.refresh_db()

    def db_load(self):
        id = self.cur_id()
        if id is None or not self.ask():
            return
        try:
            cfg = self.db.get(id)
        except sqlite3.Error:
            QMessageBox.warning(self, "Ошибка", "Ошибка базы данных")
            return
        if cfg is None:
            return
        self.f.setup(cfg["w"], cfg["h"], self.f.cell, self.grid_act.isChecked())
        self.f.g = [row[:] for row in cfg["grid"]]
        self.f.update()
        self.set_rule(cfg["rule"])
        self.gen = 0
        self.st.reset()
        self.path = None
        self.dirty = False
        self.upd()

    def db_del(self):
        id = self.cur_id()
        if id is None:
            return
        r = QMessageBox.question(self, "Удалить", "Удалить конфигурацию?")
        if r != QMessageBox.StandardButton.Yes:
            return
        try:
            self.db.delete(id)
        except sqlite3.Error:
            QMessageBox.warning(self, "Ошибка", "Ошибка базы данных")
            return
        self.refresh_db()

    def export_stats(self):
        name, _ = QFileDialog.getSaveFileName(
            self, "Экспорт статистики", "статистика.csv", "CSV (*.csv)")
        if not name:
            return
        p = Path(name)
        if p.suffix.lower() != ".csv":
            p = p.with_suffix(".csv")
        try:
            p.write_text(self.st.data(), encoding="utf-8-sig")
        except OSError:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить файл")

    def theme_icon(self):
        name = "sun.png" if style.is_dark() else "moon.png"
        self.b_theme.setIcon(assets.icon(name, style.colors()["text"]))

    def toggle_theme(self):
        self.set_theme(not style.is_dark())

    def set_theme(self, dark):
        style.apply(QApplication.instance(), dark)
        try:
            self.db.set_setting("theme", "dark" if dark else "light")
        except sqlite3.Error:
            pass
        self.a_theme.blockSignals(True)
        self.a_theme.setChecked(dark)
        self.a_theme.blockSignals(False)
        self.f.update()
        self.st.plot.update()
        self.upd_rules()
        self.theme_icon()
        self.setWindowIcon(assets.icon("logo.png", style.colors()["accent"]))

    def ask(self):
        if not self.dirty:
            return True
        r = QMessageBox.question(self, "Несохранённые изменения", "Поле изменено. Продолжить?")
        return r == QMessageBox.StandardButton.Yes

    def upd(self):
        self.sl.setText(f"поколение: {self.gen}   живых: {self.f.alive()}")

    def about(self):
        About(self).exec()

    def closeEvent(self, e):
        if self.ask():
            self.db.close()
            e.accept()
        else:
            e.ignore()
