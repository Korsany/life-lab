RULES = {
    "Жизнь": "B3/S23",
    "HighLife": "B36/S23",
    "Day & Night": "B3678/S34678",
    "Seeds": "B2/S",
    "Brain": "B3/S12345",
    "Replicator": "B1357/S1357",
    "Жизнь без смерти": "B3/S012345678",
}

DESC = {
    "Жизнь": "Клетка рождается при 3 соседях, выживает при 2 или 3. Классические правила Конвея.",
    "HighLife": "Клетка рождается при 3 или 6 соседях, выживает при 2 или 3. Похожа на Жизнь, но даёт другие фигуры.",
    "Day & Night": "Клетка рождается при 3, 6, 7 или 8 соседях, выживает при 3, 4, 6, 7 или 8. Симметрична относительно инверсии.",
    "Seeds": "Мёртвая клетка рождается ровно при 2 соседях. Живые клетки всегда погибают.",
    "Brain": "Клетка рождается при 3 соседях, выживает при 1, 2, 3, 4 или 5. Напоминает активность мозга.",
    "Replicator": "Клетка рождается и выживает при 1, 3, 5 или 7 соседях. Каждая фигура копирует себя.",
    "Жизнь без смерти": "Клетка рождается при 3 соседях, а живые клетки не погибают никогда. Поле только заполняется.",
}


def parse(rule):
    if not isinstance(rule, str):
        raise ValueError("Некорректное правило")
    parts = rule.split("/")
    if len(parts) != 2:
        raise ValueError("Некорректное правило")
    b, s = parts
    if not b or not s or b[0] not in "Bb" or s[0] not in "Ss":
        raise ValueError("Некорректное правило")
    b, s = b[1:], s[1:]
    if any(c not in "012345678" for c in b + s):
        raise ValueError("Некорректное правило")
    return {int(c) for c in b}, {int(c) for c in s}


def valid(rule):
    try:
        parse(rule)
    except ValueError:
        return False
    return True


def describe(rule):
    b, s = parse(rule)
    birth = ", ".join(str(n) for n in sorted(b)) or "нет"
    survive = ", ".join(str(n) for n in sorted(s)) or "нет"
    return f"рождение: {birth}; выживание: {survive}"
