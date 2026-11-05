RULES = {"Жизнь": "B3/S23", "HighLife": "B36/S23", "Day & Night": "B3678/S34678",
         "Seeds": "B2/S", "Brain": "B3/S12345"}


def parse(rule):
    b, s = rule.split("/")
    return set(map(int, b[1:])), set(map(int, s[1:]))
