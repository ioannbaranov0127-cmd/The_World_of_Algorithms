# -*- coding: utf-8 -*-
"""Тема 9 модуля 2. Словари."""

from __future__ import annotations

from course_data.modules.module_2.project import project_step_for_module_2
from course_data.modules.module_2.project_stage_tasks import STAGE_M2_09

TOPIC: dict = {
    'id': 'm2-t9',
    'num': 9,
    'title': 'Тема 9. Словари',
    'summary': 'База продуктов как словарь: название — ключ, калорийность — значение.',
    'project_step': project_step_for_module_2(9),
    'theory': {
        'intro': (
            'В версии 1.6–1.8 продукты фруктового салата хранились во вложенном списке. '
            'В версии 1.9 переносим базу в products_kcal — как таблица продуктов в HTML-демо. '
            'Ключ (название) сразу даёт калорийность: products_kcal["яблоко"] → 52. '
            'В теме 10 добавите dishes — рецепты: фруктовый салат, борщ, омлет.'
        ),
        'sections': [],
        'visual_blocks': [
            {
                'title': 'Главная мысль темы',
                'body': (
                    'Словарь — это пары «ключ → значение». '
                    'products_kcal = {"яблоко": 52, "банан": 89} — '
                    'ключ "яблоко" хранит 52, ключ "банан" — 89.'
                ),
            },
        ],
        'schemes': [],
        'scheme_gallery_layout': 'stack',
        'scheme_gallery_before': [
            {
                'title': 'Словарь на схеме',
                'body': (
                    'На схеме — как выглядит словарь в памяти: слева ключи (названия продуктов), '
                    'справа значения (калорийность). Стрелка показывает связь: '
                    'по ключу "яблоко" программа находит число 52. '
                    'Не нужен номер в списке — достаточно точного имени в кавычках.'
                ),
            },
        ],
        'scheme_gallery': [
            {
                'file': 'Словарь_1.svg',
                'num': 1,
                'caption': 'Словарь: ключ → значение',
                'sections_after': [
                    {
                        'title': 'Как читать схему',
                        'body': (
                            'Каждая строка словаря — пара ключ и значение.\n\n'
                            '• Ключ — обычно строка с названием ("яблоко", "банан").\n'
                            '• Значение — то, что хранится под этим ключом (число калорий).\n\n'
                            'Запись products_kcal["яблоко"] читается так: '
                            '«в словаре products_kcal найди ключ "яблоко" и отдай его значение».'
                        ),
                    },
                    {
                        'title': 'Зачем словарь после вложенного списка',
                        'body': (
                            'Вложенный список хорош, когда продукт выбирают по номеру меню: products[i][1]. '
                            'Но если уже знаете имя — "банан" — искать индекс неудобно. '
                            'В словаре имя и есть «адрес» данных.'
                        ),
                        'code': (
                            '# Было (версия 1.6):\n'
                            'products = [["яблоко", 52], ["банан", 89]]\n'
                            'kcal = products[1][1]  # нужен индекс\n\n'
                            '# Стало (версия 1.9):\n'
                            'products_kcal = {"яблоко": 52, "банан": 89}\n'
                            'kcal = products_kcal["банан"]  # сразу по имени'
                        ),
                    },
                    {
                        'title': 'Запись словаря в коде',
                        'body': (
                            'Словарь пишут в фигурных скобках {}. '
                            'Внутри пары ключ: значение через двоеточие, пары разделяют запятой. '
                            'Ключ-строка — всегда в кавычках.'
                        ),
                        'code': (
                            'products_kcal = {\n'
                            '    "яблоко": 52,\n'
                            '    "банан": 89,\n'
                            '    "хлеб": 265,\n'
                            '}\n'
                            'print(products_kcal)'
                        ),
                    },
                    {
                        'title': 'Доступ по ключу',
                        'body': (
                            'Как у списка products[i], у словаря — products_kcal[ключ]. '
                            'Внутри скобок не число-индекс, а ключ (обычно строка в кавычках). '
                            'Если ключа нет — Python выдаст ошибку KeyError.'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89}\n'
                            'print(products_kcal["яблоко"])  # 52\n'
                            'print(products_kcal["банан"])  # 89'
                        ),
                    },
                    {
                        'title': 'Ключ в переменной',
                        'body': (
                            'Ключ может лежать в переменной — тогда кавычки пишут только при создании словаря, '
                            'а при обращении используют имя переменной.'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89}\n'
                            'name = "банан"\n'
                            'print(products_kcal[name])  # 89\n'
                            '# то же, что products_kcal["банан"]'
                        ),
                    },
                    {
                        'title': 'Список и словарь — не путать',
                        'body': (
                            'Список — элементы по номерам 0, 1, 2…\n'
                            'Словарь — данные по ключам (именам).\n\n'
                            'Квадратные скобки одинаковые, смысл разный: '
                            '[0] — первый элемент списка, ["яблоко"] — значение по ключу.'
                        ),
                        'code': (
                            'lst = ["яблоко", "банан"]\n'
                            'dct = {"яблоко": 52, "банан": 89}\n\n'
                            'print(lst[0])           # яблоко\n'
                            'print(dct["яблоко"])    # 52'
                        ),
                    },
                    {
                        'title': 'Перебор словаря в цикле for',
                        'body': (
                            'for key in products_kcal: — цикл идёт по ключам (названиям продуктов). '
                            'Чтобы вывести и калории, обращайтесь products_kcal[key] внутри цикла. '
                            'Так удобно строить меню без range(len(...)).'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89, "хлеб": 265}\n'
                            'for name in products_kcal:\n'
                            '    kcal = products_kcal[name]\n'
                            '    print(name, "—", kcal, "ккал/100 г")'
                        ),
                    },
                    {
                        'title': 'Меню из словаря',
                        'body': (
                            'Можно нумеровать продукты через enumerate, если пользователю нужны номера 1, 2, 3… '
                            'Список ключей даёт sorted(products_kcal) или list(products_kcal) — '
                            'для учебного калькулятора достаточно простого for.'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89, "хлеб": 265}\n'
                            'print("Меню:")\n'
                            'n = 1\n'
                            'for name in products_kcal:\n'
                            '    print(n, ".", name, "—", products_kcal[name], "ккал")\n'
                            '    n = n + 1'
                        ),
                    },
                    {
                        'title': 'calc_portion и словарь',
                        'body': (
                            'Функция calc_portion из темы 8 не меняется — ей нужны два числа. '
                            'Калорийность берём из словаря: kcal = products_kcal[name], '
                            'потом portion = calc_portion(kcal, grams).'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89}\n\n'
                            'def calc_portion(kcal, grams):\n'
                            '    return kcal * grams / 100\n\n'
                            'name = "яблоко"\n'
                            'grams = 200\n'
                            'kcal = products_kcal[name]\n'
                            'portion = calc_portion(kcal, grams)\n'
                            'print(name, "—", portion, "ккал")  # 104.0'
                        ),
                    },
                    {
                        'title': 'Журнал eaten — что не меняется',
                        'body': (
                            'eaten по-прежнему список названий: eaten.append("яблоко"). '
                            'Меняется только база products_kcal. '
                            'В журнал кладите ключ (имя), не число калорий.'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89}\n'
                            'eaten = []\n'
                            'name = "яблоко"\n'
                            'eaten.append(name)\n'
                            'print(eaten)  # ["яблоко"]'
                        ),
                    },
                    {
                        'title': 'Версия 1.9 — База products_kcal',
                        'body': (
                            'Замените вложенный список products на словарь products_kcal. '
                            'В show_menu() перебирайте ключи словаря. '
                            'В расчёте: kcal = products_kcal[name] и calc_portion(kcal, grams). '
                            'Функции и while True из версий 1.7–1.8 сохраните.'
                        ),
                        'code': (
                            'products_kcal = {\n'
                            '    "яблоко": 52,\n'
                            '    "банан": 89,\n'
                            '    "хлеб": 265,\n'
                            '}\n\n'
                            'def calc_portion(kcal, grams):\n'
                            '    return kcal * grams / 100\n\n'
                            '# kcal = products_kcal[name]\n'
                            '# portion = calc_portion(kcal, grams)'
                        ),
                    },
                ],
            },
        ],
        'remember': [
            'Словарь — пары ключ: значение в фигурных скобках {}.',
            'products_kcal["яблоко"] — значение по ключу "яблоко".',
            'Ключ-строка в словаре пишут в кавычках.',
            'for name in products_kcal: — перебор ключей (названий).',
            'calc_portion получает число из products_kcal[name], не весь словарь.',
        ],
        'mistakes': [
            'Путать список [] и словарь {} — разные типы данных.',
            'Забыть кавычки у ключа: {яблоко: 52} вместо {"яблоко": 52}.',
            'Писать products_kcal(…) со скобками как у функции — нужны квадратные скобки [].',
            'Обращаться products_kcal[0] — у словаря нет индекса 0, только ключи.',
            'Искать продукт с опечаткой в ключе — KeyError, если имени нет в словаре.',
        ],
        'tips': [
            'Назовите словарь понятно: products_kcal, kcal_by_name.',
            'Проверьте доступ: print(products_kcal["яблоко"]) сразу после создания словаря.',
            'В меню сначала выведите один ключ в цикле for, потом добавьте калории.',
            'Методы словарей (get, keys) — в теме 10; здесь достаточно [] и for.',
        ],
    },
    'tasks': [
        {
            'id': 450,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Что такое ключ в словаре products_kcal = {"яблоко": 52}?',
            'hint': 'Ключ — «метка», по которой находят значение.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Строка "яблоко" — по ней ищут калорийность'},
                {'key': 'b', 'label': 'Число 52 — оно хранится в словаре'},
                {'key': 'c', 'label': 'Номер 0 — первый элемент как в списке'},
            ],
            'correct': 'a',
        },
        {
            'id': 451,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Как получить калорийность банана из словаря d = {"банан": 89}?',
            'hint': 'Квадратные скобки и ключ в кавычках.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'd["банан"]'},
                {'key': 'b', 'label': 'd(банан)'},
                {'key': 'c', 'label': 'd[1]'},
            ],
            'correct': 'a',
        },
        {
            'id': 452,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                'products_kcal = {"яблоко": 52, "банан": 89}\n'
                'print(products_kcal["банан"])\n'
                'Что выведет программа?'
            ),
            'hint': 'Ключ "банан" связан с числом 89.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '89'},
                {'key': 'b', 'label': 'банан'},
                {'key': 'c', 'label': '52'},
            ],
            'correct': 'a',
        },
        {
            'id': 453,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'Создайте словарь d = {"яблоко": 52, "банан": 89}. '
                'Выведите значение по ключу "яблоко" (одно число: 52).'
            ),
            'hint': 'print(d["яблоко"])',
            'xp': 14,
            'expected': '52',
            'starter_code': '',
        },
        {
            'id': 454,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52, "хлеб": 265}. '
                'name = "хлеб". Выведите products_kcal[name] (одно число: 265).'
            ),
            'hint': 'Ключ лежит в переменной name',
            'xp': 14,
            'expected': '265',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "хлеб": 265}\n'
                'name = "хлеб"\n'
            ),
        },
        {
            'id': 455,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52, "банан": 89}. '
                'def calc_portion(kcal, grams): return kcal * grams / 100\n'
                'Посчитайте calc_portion(products_kcal["яблоко"], 100) и выведите (52.0).'
            ),
            'hint': 'calc_portion(products_kcal["яблоко"], 100)',
            'xp': 14,
            'expected': '52.0',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "банан": 89}\n\n'
                'def calc_portion(kcal, grams):\n'
                '    return kcal * grams / 100\n'
            ),
        },
        {
            'id': 456,
            'kind': 'practice',
            'category': 'practice',
            'type': 'matching',
            'text': 'Сопоставьте запись и смысл.',
            'hint': '{} — словарь, [] с ключом — доступ, for — перебор ключей.',
            'xp': 12,
            'left': ['{"яблоко": 52}', 'products_kcal["яблоко"]', 'for name in products_kcal:'],
            'right': [
                'Получить калорийность по ключу "яблоко"',
                'Словарь с одной парой ключ → значение',
                'Перебрать все названия продуктов в словаре',
            ],
            'correct_pairs': [1, 0, 2],
        },
        {
            'id': 457,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте словарь: ключ-строка должен быть в кавычках. '
                'Программа должна вывести 89.'
            ),
            'hint': 'Ключ: "банан": 89',
            'xp': 14,
            'expected': '89',
            'starter_code': (
                'products_kcal = {банан: 89}\n'
                'print(products_kcal["банан"])\n'
            ),
        },
        {
            'id': 458,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52, "банан": 89}. '
                'В цикле for name in products_kcal: выведите две строки — '
                'сначала "яблоко — 52", затем "банан — 89" (каждая пара name и products_kcal[name] на своей строке).'
            ),
            'hint': 'print(name, "—", products_kcal[name]) внутри for',
            'xp': 14,
            'expected': 'яблоко — 52\nбанан — 89',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "банан": 89}\n\n'
            ),
        },
        STAGE_M2_09,
    ],
}
