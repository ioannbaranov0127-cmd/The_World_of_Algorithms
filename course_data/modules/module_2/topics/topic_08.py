# -*- coding: utf-8 -*-
"""Тема 8 модуля 2. Функции с параметрами и return."""

from __future__ import annotations

from course_data.modules.module_2.project import project_step_for_module_2
from course_data.modules.module_2.project_stage_tasks import STAGE_M2_08

TOPIC: dict = {
    'id': 'm2-t8',
    'num': 8,
    'title': 'Тема 8. Функции с параметрами и return',
    'summary': 'Передать граммы и калорийность в функцию, получить результат через return.',
    'project_step': project_step_for_module_2(8),
    'theory': {
        'intro': (
            'В теме 7 функции только выполняли команды — например, show_menu() печатала меню. '
            'Но расчёт калорий удобнее оформить иначе: передать числа в функцию и получить ответ. '
            'Параметры — это «вход», return — «выход». '
            'Так calc_portion(77, 200) вернёт калории порции — в 2.0 вызовете её для каждого '
            'ингредиента блюда, как одна строка таблицы в HTML-демо.'
        ),
        'sections': [],
        'visual_blocks': [
            {
                'title': 'Главная мысль темы',
                'body': (
                    'def calc(kcal, grams): — функция принимает два числа. '
                    'return kcal * grams / 100 — отдаёт результат. '
                    'portion = calc(52, 200) — вызов с аргументами и сохранение ответа.'
                ),
            },
        ],
        'schemes': [],
        'scheme_gallery_layout': 'stack',
        'scheme_gallery_before': [
            {
                'title': 'Параметры и return на схеме',
                'body': (
                    'На схеме видно: при вызове функции в неё «заходят» значения (граммы, калорийность), '
                    'внутри выполняется формула, а return отдаёт число обратно в основную программу. '
                    'Это связка темы 7 (def) с настоящим расчётом в калькуляторе.'
                ),
            },
        ],
        'scheme_gallery': [
            {
                'file': 'Функции_с параметрами.svg',
                'num': 1,
                'caption': 'Функция с параметрами и return',
                'sections_after': [
                    {
                        'title': 'Как читать схему',
                        'body': (
                            'Стрелки к функции — это аргументы: конкретные числа или переменные, '
                            'которые передаются в скобках при вызове.\n\n'
                            'Стрелка от return — результат вычисления возвращается туда, '
                            'откуда функцию вызвали. Его можно сохранить в переменную или сразу использовать.'
                        ),
                    },
                    {
                        'title': 'От функции без параметров к функции с данными',
                        'body': (
                            'show_menu() из темы 7 брала products «снаружи». '
                            'Для расчёта удобнее явно передать числа: сколько калорий на 100 г и сколько граммов. '
                            'Тогда функция не зависит от конкретных имён переменных снаружи — '
                            'ей достаточно двух чисел в скобках.'
                        ),
                        'code': (
                            '# Тема 7 — без параметров\n'
                            'def show_menu():\n'
                            '    print("Меню...")\n\n'
                            '# Тема 8 — с параметрами\n'
                            'def calc_portion(kcal, grams):\n'
                            '    return kcal * grams / 100'
                        ),
                    },
                    {
                        'title': 'Параметры в def',
                        'body': (
                            'В скобках после имени функции пишут параметры — имена для «входных» значений. '
                            'При вызове в эти имена попадают переданные аргументы. '
                            'Порядок важен: первый аргумент — первому параметру, второй — второму.'
                        ),
                        'code': (
                            'def calc_portion(kcal_per_100, grams):\n'
                            '    result = kcal_per_100 * grams / 100\n'
                            '    return result\n\n'
                            '# kcal_per_100 и grams — параметры (имена в def)\n'
                            '# 52 и 200 — аргументы (значения при вызове)'
                        ),
                    },
                    {
                        'title': 'Вызов с аргументами',
                        'body': (
                            'calc_portion(52, 200) — передать числа напрямую. '
                            'calc_portion(products[i][1], grams) — передать переменные из калькулятора. '
                            'Внутри функции kcal_per_100 станет 52 (или products[i][1]), grams — 200.'
                        ),
                        'code': (
                            'def calc_portion(kcal, grams):\n'
                            '    return kcal * grams / 100\n\n'
                            'print(calc_portion(52, 200))   # 104.0\n'
                            'print(calc_portion(89, 100))   # 89.0'
                        ),
                    },
                    {
                        'title': 'return — вернуть результат',
                        'body': (
                            'return число завершает функцию и отдаёт значение наружу. '
                            'После return строки в функции уже не выполняются. '
                            'Функция с return не обязана что-то печатать — она «отвечает» числом.'
                        ),
                        'code': (
                            'def double(x):\n'
                            '    return x * 2\n\n'
                            'answer = double(5)\n'
                            'print(answer)  # 10'
                        ),
                    },
                    {
                        'title': 'Сохранить ответ в переменную',
                        'body': (
                            'Часто результат функции кладут в переменную — так код читается проще. '
                            'В калькуляторе: portion = calc_portion(kcal, grams), '
                            'потом total = total + portion.'
                        ),
                        'code': (
                            'def calc_portion(kcal, grams):\n'
                            '    return kcal * grams / 100\n\n'
                            'kcal = 52\n'
                            'grams = 150\n'
                            'portion = calc_portion(kcal, grams)\n'
                            'print("Порция:", portion)  # 78.0'
                        ),
                    },
                    {
                        'title': 'calc_portion в калькуляторе',
                        'body': (
                            'После выбора продукта и ввода граммов вызываем функцию расчёта. '
                            'Калорийность берём из products[i][1], граммы — из переменной grams. '
                            'Формула в одном месте — если изменится, правите только функцию.'
                        ),
                        'code': (
                            'products = [["яблоко", 52], ["банан", 89]]\n\n'
                            'def calc_portion(kcal_per_100, grams):\n'
                            '    return kcal_per_100 * grams / 100\n\n'
                            'i = 0\n'
                            'grams = 200\n'
                            'kcal = products[i][1]\n'
                            'portion = calc_portion(kcal, grams)\n'
                            'print(products[i][0], "—", portion, "ккал")\n'
                            '# яблоко — 104.0 ккал'
                        ),
                    },
                    {
                        'title': 'return и print — не путать',
                        'body': (
                            'print() показывает текст на экране. '
                            'return отдаёт значение программе — его можно сложить, сравнить, передать дальше. '
                            'Для total нужен именно return: total += calc_portion(kcal, grams).'
                        ),
                        'code': (
                            'def bad(kcal, grams):\n'
                            '    print(kcal * grams / 100)  # только на экран\n\n'
                            'def good(kcal, grams):\n'
                            '    return kcal * grams / 100  # можно сохранить и сложить'
                        ),
                    },
                    {
                        'title': 'Версия 1.8 — Расчёт функцией',
                        'body': (
                            'Добавьте функцию расчёта порции с двумя параметрами и return. '
                            'В цикле while вместо формулы в нескольких строках вызывайте calc_portion(...). '
                            'Результат добавляйте к total. Функции show_menu из версии 1.7 сохраните.'
                        ),
                        'code': (
                            'def calc_portion(kcal_per_100, grams):\n'
                            '    return kcal_per_100 * grams / 100\n\n'
                            'total = 0\n'
                            '# в while:\n'
                            '# portion = calc_portion(products[i][1], grams)\n'
                            '# total = total + portion'
                        ),
                    },
                ],
            },
        ],
        'remember': [
            'Параметры — имена в def, аргументы — значения в скобках при вызове.',
            'return отдаёт результат; его можно сохранить: x = func(...).',
            'Порядок аргументов должен совпадать с порядком параметров.',
            'calc_portion(kcal, grams) — формула kcal * grams / 100 в одном месте.',
            'Для total нужен return, а не только print внутри функции.',
        ],
        'mistakes': [
            'Перепутать порядок: calc_portion(grams, kcal) вместо calc_portion(kcal, grams).',
            'Забыть return — функция вернёт None, total не посчитается.',
            'Писать print вместо return, когда результат нужен для total.',
            'Вызывать функцию без аргументов, хотя в def два параметра.',
            'Путать имя параметра и переменную снаружи — внутри работают параметры.',
        ],
        'tips': [
            'Сначала проверьте calc_portion(100, 100) — должно быть 100.0.',
            'Подпишите параметры понятно: kcal_per_100, grams.',
            'Вызов и print результата — хороший тест перед вставкой в while.',
            'show_menu() без параметров и calc_portion(...) с параметрами могут жить в одном файле.',
        ],
    },
    'tasks': [
        {
            'id': 430,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Что такое параметр функции?',
            'hint': 'Имя в скобках после def — «место» для входного значения.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Имя в def, которому при вызове передаётся значение'},
                {'key': 'b', 'label': 'То же самое, что return'},
                {'key': 'c', 'label': 'Список products в калькуляторе'},
            ],
            'correct': 'a',
        },
        {
            'id': 431,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Зачем нужен return в calc_portion?',
            'hint': 'Нужно получить число обратно в основную программу.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Чтобы вернуть число калорий и использовать его в total'},
                {'key': 'b', 'label': 'Чтобы начать цикл while'},
                {'key': 'c', 'label': 'Чтобы объявить список products'},
            ],
            'correct': 'a',
        },
        {
            'id': 432,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                'def double(n):\n'
                '    return n * 2\n'
                'print(double(7))\n'
                'Что выведет программа?'
            ),
            'hint': 'double(7) вернёт 14.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '14'},
                {'key': 'b', 'label': '7'},
                {'key': 'c', 'label': 'None'},
            ],
            'correct': 'a',
        },
        {
            'id': 433,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'Напишите функцию sum2(a, b), которая return a + b. '
                'Выведите результат sum2(3, 5) (одно число: 8).'
            ),
            'hint': 'def sum2(a, b): return a + b',
            'xp': 14,
            'expected': '8',
            'starter_code': '',
        },
        {
            'id': 434,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'Напишите calc_portion(kcal, grams) с return kcal * grams / 100. '
                'Выведите calc_portion(52, 200) (одно число: 104.0).'
            ),
            'hint': 'return kcal * grams / 100',
            'xp': 14,
            'expected': '104.0',
            'starter_code': '',
        },
        {
            'id': 435,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products = [["яблоко", 52], ["банан", 89]]. '
                'i = 1, grams = 100. '
                'Функция calc_portion уже есть. '
                'Сохраните portion = calc_portion(products[i][1], grams) и выведите portion (89.0).'
            ),
            'hint': 'products[1][1] — это 89',
            'xp': 14,
            'expected': '89.0',
            'starter_code': (
                'products = [["яблоко", 52], ["банан", 89]]\n\n'
                'def calc_portion(kcal, grams):\n'
                '    return kcal * grams / 100\n\n'
                'i = 1\n'
                'grams = 100\n'
            ),
        },
        {
            'id': 436,
            'kind': 'practice',
            'category': 'practice',
            'type': 'matching',
            'text': 'Сопоставьте запись и смысл.',
            'hint': 'def — параметры, вызов — аргументы, return — ответ.',
            'xp': 12,
            'left': ['def calc(kcal, grams):', 'calc(52, 200)', 'return kcal * grams / 100'],
            'right': [
                'Вызов: передать 52 и 200 в функцию',
                'Объявление: kcal и grams — параметры',
                'Отдать результат вычисления наружу',
            ],
            'correct_pairs': [1, 0, 2],
        },
        {
            'id': 437,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте функцию: calc_portion(100, 50) должна вернуть 50.0, '
                'сейчас return отсутствует.'
            ),
            'hint': 'Добавьте return перед формулой.',
            'xp': 14,
            'expected': '50.0',
            'starter_code': (
                'def calc_portion(kcal, grams):\n'
                '    kcal * grams / 100\n\n'
                'print(calc_portion(100, 50))\n'
            ),
        },
        {
            'id': 438,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'total = 0. calc_portion(kcal, grams) возвращает калории порции. '
                'Посчитайте portion = calc_portion(52, 100), добавьте к total и выведите total (52.0).'
            ),
            'hint': 'total = total + portion или total += portion',
            'xp': 14,
            'expected': '52.0',
            'starter_code': (
                'def calc_portion(kcal, grams):\n'
                '    return kcal * grams / 100\n\n'
                'total = 0\n'
            ),
        },
        STAGE_M2_08,
    ],
}
