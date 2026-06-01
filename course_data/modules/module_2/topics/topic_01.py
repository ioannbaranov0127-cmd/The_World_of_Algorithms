# -*- coding: utf-8 -*-
"""Тема 1 модуля 2. Повторение ключевых конструкций."""

from __future__ import annotations

from course_data.modules.module_2.project import project_step_for_module_2

TOPIC: dict = {
    'id': 'm2-t1',
    'num': 1,
    'title': 'Тема 1. Повторение ключевых конструкций',
    'summary': 'print, input, переменные, формулы, if и циклы for/while в проекте.',
    'project_step': project_step_for_module_2(1),
    'theory': {
        'intro': (
            'Вы сделали версию 1.0 — калькулятор считает порции в цикле while. Модуль 2 — развитие '
            'готового продукта: сначала повторим скелет (print, input, if, while), затем добавим базу '
            'продуктов в списках и журнал съеденного.'
        ),
        'sections': [
            {
                'title': 'Вывод и ввод',
                'body': (
                    'print() показывает текст и числа. input() читает строку с клавиатуры — часто сразу '
                    'преобразуют в int() или float(). Так пользователь вводит продукт и граммы.'
                ),
                'code': (
                    'print("Калькулятор калорий")\n'
                    'product = input("Продукт: ")\n'
                    'grams = int(input("Граммы: "))\n'
                    'print(product, grams)'
                ),
            },
            {
                'title': 'Переменные и формула',
                'body': (
                    'В переменных храним граммы, калорийность и результат. Формула та же: '
                    'калории = граммы × kcal_на_100 ÷ 100.'
                ),
                'code': (
                    'grams = 150\nkcal_per_100 = 52\n'
                    'calories = grams * kcal_per_100 / 100\nprint(calories)'
                ),
            },
            {
                'title': 'Условия if',
                'body': (
                    'if / elif / else выбирают калорийность по продукту или дают совет '
                    '«Мало / Нормально / Много» по итоговым калориям.'
                ),
                'code': (
                    'total = 450\n'
                    'if total < 400:\n'
                    '    print("Мало")\n'
                    'elif total <= 700:\n'
                    '    print("Нормально")\n'
                    'else:\n'
                    '    print("Много")'
                ),
            },
            {
                'title': 'Циклы for и while',
                'body': (
                    'for с range() повторяет ввод нескольких продуктов. while держит главное меню, '
                    'пока пользователь не выберет «выход».'
                ),
                'code': (
                    'for i in range(3):\n'
                    '    print("Приём", i + 1)\n'
                    'n = 0\nwhile n < 3:\n'
                    '    n = n + 1\n'
                    '    print(n)'
                ),
            },
        ],
        'visual_blocks': [
            {
                'title': 'Практика модуля',
                'body': 'Разберите свой код проекта: где ввод, расчёт, условия и цикл.',
            },
        ],
        'schemes': [],
        'remember': [
            'Порядок в программе: ввод → расчёт → вывод → (опционально) условие.',
            'for — когда известно число повторений; while — пока условие истинно.',
        ],
        'mistakes': [
            'Путать = (присваивание) и == (сравнение) в if.',
            'Забыть int() после input() для граммов.',
        ],
        'tips': [
            'Перед новой темой прогоните старый код через «Выполнить».',
            'Комментируйте блоки: # ввод, # расчёт, # условие.',
        ],
    },
    'tasks': [
        {
            'id': 60,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Какая конструкция удобнее для главного меню «пока не выход»?',
            'hint': 'Цикл с условием в начале каждой итерации.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'while'},
                {'key': 'b', 'label': 'for'},
                {'key': 'c', 'label': 'print'},
            ],
            'correct': 'a',
        },
        {
            'id': 61,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': 'grams = 100\nkcal = 52\nprint(grams * kcal / 100)\nЧто выведет программа?',
            'hint': '100 * 52 / 100 = 52.0',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '52.0'},
                {'key': 'b', 'label': '152'},
                {'key': 'c', 'label': '5200'},
            ],
            'correct': 'a',
        },
        {
            'id': 62,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': 'Выведите две строки: «Калькулятор калорий» и «Готов к работе».',
            'hint': 'Два print подряд.',
            'xp': 12,
            'expected': 'Калькулятор калорий\nГотов к работе',
            'starter_code': '# print(...)\n',
        },
        {
            'id': 63,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте: при product = "Яблоко" программа должна вывести «Ок», '
                'сейчас сравнение без lower() не срабатывает.'
            ),
            'hint': 'if product.lower() == "яблоко":',
            'xp': 14,
            'expected': 'Ок',
            'starter_code': (
                'product = "Яблоко"\n'
                'if product == "яблоко":\n'
                '    print("Ок")\n'
            ),
        },
        {
            'id': 64,
            'kind': 'project_step',
            'category': 'project_step',
            'type': 'code',
            'text': (
                'Шаг проекта: grams = 120, kcal_per_100 = 52 — посчитайте calories '
                'и выведите «Калории: » и значение.'
            ),
            'hint': 'calories = grams * kcal_per_100 / 100',
            'xp': 16,
            'expected': 'Калории: 62.4',
            'starter_code': (
                'grams = 120\nkcal_per_100 = 52\n'
                '# calories = ...\n# print(...)\n'
            ),
        },
        {
            'id': 65,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Сколько раз выполнится тело for i in range(2):?',
            'hint': 'range(2) → 0 и 1.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '2 раза'},
                {'key': 'b', 'label': '3 раза'},
                {'key': 'c', 'label': '1 раз'},
            ],
            'correct': 'a',
        },
    ],
}
