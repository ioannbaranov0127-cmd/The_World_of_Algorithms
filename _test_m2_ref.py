# -*- coding: utf-8 -*-
"""Проверка M2 project_stage на полных эталонных решениях."""
from course_data.loader import TASK_BY_ID
from course_data.project_stage_runner import validate_project_stage_runs

M2_REF: dict[int, str] = {}

M2_REF[310] = '''
print("Калькулятор калорий — фруктовый салат")
print("1 - яблоко, 2 - банан, 3 - апельсин, 0 — выход")
total = 0
while True:
    num = int(input("Номер продукта: "))
    if num == 0:
        break
    grams = int(input("Граммы: "))
    if num == 1:
        kcal_per_100 = 52
        product = "яблоко"
    elif num == 2:
        kcal_per_100 = 89
        product = "банан"
    elif num == 3:
        kcal_per_100 = 47
        product = "апельсин"
    else:
        continue
    calories = grams * kcal_per_100 / 100
    total = total + calories
    print("Порция:", calories, "ккал")
print("Всего:", total, "ккал")
'''

M2_REF[329] = '''
products = ['яблоко', 'банан', 'апельсин', 'груша']
kcal_per_100 = [52, 89, 47, 57]
print("Каталог:")
for i in range(len(products)):
    print(i + 1, products[i])
print("1 - яблоко, 2 - банан, 3 - апельсин, 4 - груша, 0 — выход")
total = 0
while True:
    num = int(input("Номер продукта: "))
    if num == 0:
        break
    grams = int(input("Граммы: "))
    i = num - 1
    kcal = kcal_per_100[i]
    portion = grams * kcal / 100
    total += portion
    print("Порция:", portion, "ккал")
print("Всего:", total, "ккал")
'''

M2_REF[340] = M2_REF[329]  # same logic with index

M2_REF[360] = '''
products = ['яблоко', 'банан', 'апельсин', 'груша']
kcal_per_100 = [52, 89, 47, 57]
eaten = []
print("1 - яблоко, 2 - банан, 3 - апельсин, 4 - груша, 0 — выход")
total = 0
while True:
    num = int(input("Номер продукта: "))
    if num == 0:
        break
    grams = int(input("Граммы: "))
    i = num - 1
    name = products[i]
    kcal = kcal_per_100[i]
    portion = grams * kcal / 100
    total += portion
    eaten.append(name)
    print("Порция:", portion, "ккал")
    print("Записей:", len(eaten))
print("Всего:", total, "ккал")
'''

M2_REF[373] = '''
products = ['яблоко', 'банан', 'апельсин', 'груша']
kcal_per_100 = [52, 89, 47, 57]
eaten = []

def show_menu():
    for i in range(len(products)):
        print(i + 1, products[i])
    print("0 — выход")

total = 0
while True:
    show_menu()
    num = int(input("Номер продукта: "))
    if num == 0:
        break
    grams = int(input("Граммы: "))
    i = num - 1
    name = products[i]
    kcal = kcal_per_100[i]
    portion = grams * kcal / 100
    total += portion
    eaten.append(name)
    print("Порция:", portion, "ккал")
    print("Записей:", len(eaten))
print("Всего:", total, "ккал")
'''

M2_REF[399] = '''
products = [
    ["яблоко", 52],
    ["банан", 89],
    ["апельсин", 47],
    ["груша", 57],
]
eaten = []

def show_menu():
    for i in range(len(products)):
        print(i + 1, products[i][0])
    print("0 — выход")

total = 0
while True:
    show_menu()
    num = int(input("Номер продукта: "))
    if num == 0:
        break
    grams = int(input("Граммы: "))
    i = num - 1
    name = products[i][0]
    kcal = products[i][1]
    portion = grams * kcal / 100
    total += portion
    eaten.append(name)
    print("Порция:", portion, "ккал")
    print("Записей:", len(eaten))
print("Всего:", total, "ккал")
'''

M2_REF[419] = M2_REF[399].replace(
    'def show_menu():',
    'def show_welcome():\n    print("Калькулятор калорий")\n\ndef show_menu():',
).replace(
    'total = 0\nwhile True:',
    'def show_welcome():\n    print("Калькулятор калорий")\n\nshow_welcome()\ntotal = 0\nwhile True:',
)

# fix duplicate show_welcome - rewrite cleanly
M2_REF[419] = '''
products = [
    ["яблоко", 52],
    ["банан", 89],
    ["апельсин", 47],
    ["груша", 57],
]
eaten = []

def show_welcome():
    print("Калькулятор калорий")

def show_menu():
    for i in range(len(products)):
        print(i + 1, products[i][0])
    print("0 — выход")

show_welcome()
total = 0
while True:
    show_menu()
    num = int(input("Номер продукта: "))
    if num == 0:
        break
    grams = int(input("Граммы: "))
    i = num - 1
    name = products[i][0]
    kcal = products[i][1]
    portion = grams * kcal / 100
    total += portion
    eaten.append(name)
    print("Порция:", portion, "ккал")
    print("Записей:", len(eaten))
print("Всего:", total, "ккал")
'''

M2_REF[439] = '''
products = [
    ["яблоко", 52],
    ["банан", 89],
    ["апельсин", 47],
    ["груша", 57],
]
total = 0

def calc_portion(kcal_per_100, grams):
    return kcal_per_100 * grams / 100

def show_welcome():
    print("Калькулятор калорий")

def show_menu():
    for i in range(len(products)):
        print(i + 1, products[i][0])
    print("0 — выход")

show_welcome()
while True:
    show_menu()
    num = int(input("Номер продукта: "))
    if num == 0:
        break
    grams = int(input("Граммы: "))
    i = num - 1
    kcal = products[i][1]
    portion = calc_portion(kcal, grams)
    total += portion
    print("Порция:", portion, "ккал")
print("Всего:", total, "ккал")
'''

M2_REF[459] = '''
products_kcal = {
    "яблоко": 52, "банан": 89, "апельсин": 47, "груша": 57,
    "говядина": 250, "свёкла": 43, "картофель": 77, "капуста": 27,
    "морковь": 35, "лук": 41, "масло подсолнечное": 884,
    "яйцо": 157, "молоко": 52, "масло сливочное": 748,
}
total = 0

def calc_portion(kcal_per_100, grams):
    return kcal_per_100 * grams / 100

def show_menu():
    n = 1
    for name in products_kcal:
        print(n, name)
        n += 1
    print("0 — выход")

while True:
    show_menu()
    num = int(input("Номер продукта: "))
    if num == 0:
        break
    grams = int(input("Граммы: "))
    name = list(products_kcal.keys())[num - 1]
    kcal = products_kcal[name]
    portion = calc_portion(kcal, grams)
    total += portion
    print("Порция:", portion, "ккал")
print("Всего:", total, "ккал")
'''

M2_REF[485] = TASK_BY_ID[485]['starter_code']

failures = []
for tid in sorted(M2_REF):
    task = TASK_BY_ID[tid]
    ok, fails, out, stdin = validate_project_stage_runs(M2_REF[tid], task)
    status = 'OK' if ok else 'FAIL'
    print(f'{tid}: {status}')
    if not ok:
        print('  ', fails[:3])
        failures.append((tid, fails))

print('---')
print('Passed:', len(M2_REF) - len(failures), '/', len(M2_REF))
if failures:
    raise SystemExit(1)
