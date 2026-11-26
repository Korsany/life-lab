import csv
import json
from io import StringIO

from . import rules

MIN = 10
MAX = 300


def dump_json(w, h, rule, grid):
    cells = [[x, y] for y, row in enumerate(grid) for x, value in enumerate(row) if value]
    data = {"w": w, "h": h, "rule": rule, "cells": cells}
    return json.dumps(data, ensure_ascii=False, indent=1)


def load_json(text):
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        raise ValueError("Файл не является корректным JSON") from None
    if not isinstance(data, dict):
        raise ValueError("Ожидался объект JSON")
    for key in ("w", "h", "rule", "cells"):
        if key not in data:
            raise ValueError(f"Отсутствует ключ {key}")
    w, h, rule, cells = data["w"], data["h"], data["rule"], data["cells"]
    if type(w) is not int or type(h) is not int:
        raise ValueError("Ширина и высота должны быть целыми числами")
    if not (MIN <= w <= MAX and MIN <= h <= MAX):
        raise ValueError(f"Размер поля должен быть от {MIN} до {MAX}")
    if not isinstance(rule, str):
        raise ValueError("Правило должно быть строкой")
    try:
        rules.parse(rule)
    except ValueError:
        raise ValueError("Некорректное правило") from None
    if not isinstance(cells, list):
        raise ValueError("Список клеток должен быть массивом")
    grid = [[0] * w for _ in range(h)]
    for item in cells:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("Каждая клетка должна быть парой [x, y]")
        x, y = item
        if type(x) is not int or type(y) is not int:
            raise ValueError("Координаты клеток должны быть целыми числами")
        if not (0 <= x < w and 0 <= y < h):
            raise ValueError(f"Клетка ({x}, {y}) выходит за границы поля")
        grid[y][x] = 1
    return w, h, rule, grid


def dump_csv(grid):
    out = StringIO()
    wr = csv.writer(out, lineterminator="\n")
    for row in grid:
        wr.writerow("1" if value else "0" for value in row)
    return out.getvalue()


def load_csv(text):
    rows = [row for row in csv.reader(StringIO(text)) if row]
    if not rows:
        raise ValueError("Файл пуст")
    width = len(rows[0])
    if not (MIN <= width <= MAX):
        raise ValueError(f"Ширина поля должна быть от {MIN} до {MAX}")
    grid = []
    for number, values in enumerate(rows, 1):
        if len(values) != width:
            raise ValueError(f"Строка {number} имеет другую длину")
        row = []
        for value in values:
            value = value.strip()
            if value not in ("0", "1"):
                raise ValueError(f"Строка {number}: допустимы только 0 и 1")
            row.append(int(value))
        grid.append(row)
    height = len(grid)
    if not (MIN <= height <= MAX):
        raise ValueError(f"Высота поля должна быть от {MIN} до {MAX}")
    return grid
