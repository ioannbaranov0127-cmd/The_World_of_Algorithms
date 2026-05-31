# -*- coding: utf-8 -*-
"""Тема 8. Условные конструкции."""

from __future__ import annotations

from course_data.project import project_step_for_topic

TOPIC: dict = {
    'id': 'm1-t8',
    'num': 8,
    'title': 'Тема 8. Условные конструкции',
    'summary': 'if, elif, else и ветвление программы.',
    'project_step': project_step_for_topic(8),
    'theory': {
        'intro': (
            'Калькулятор уже умеет спрашивать продукт и граммы. Но у яблока и банана разная '
            'калорийность — нужно выбирать формулу по названию. Условия if / elif / else '
            'заставляют программу идти разными путями.'
        ),
        'sections': [
            {
                'title': 'Конструкция if',
                'body': (
                    'После if идёт условие и двоеточие. Следующие строки с отступом (обычно 4 пробела) '
                    'выполняются только если условие истинно (True).'
                ),
                'code': (
                    'product = "яблоко"\n'
                    'if product == "яблоко":\n'
                    '    kcal_per_100 = 52\n'
                    'print(kcal_per_100)'
                ),
            },
            {
                'title': 'elif и else',
                'body': (
                    'elif («иначе если») проверяет следующий вариант. else срабатывает, '
                    'когда ни одно условие не подошло. В калькуляторе так выбирают калорийность '
                    'для яблока, банана или сообщают «продукт не найден».'
                ),
                'code': (
                    'p = "банан"\n'
                    'if p == "яблоко":\n'
                    '    k = 52\n'
                    'elif p == "банан":\n'
                    '    k = 89\n'
                    'else:\n'
                    '    k = 0\n'
                    'print(k)'
                ),
            },
            {
                'title': 'Отступы — часть синтаксиса',
                'body': (
                    'В Python нет фигурных скобок для блоков. Отступ показывает, что относится к if. '
                    'Сбитый отступ — частая ошибка новичков.'
                ),
                'code': (
                    'grams = 100\n'
                    'if grams > 0:\n'
                    '    print("Порция учтена")\n'
                    'print("Готово")'
                ),
            },
            {
                'title': 'Связь с проектом',
                'body': (
                    'После ввода продукта (с .lower()) задаём kcal_per_100 через if/elif. '
                    'Затем считаем калории по уже знакомой формуле.'
                ),
                'code': (
                    'product = "банан"\n'
                    'if product == "яблоко":\n'
                    '    kcal_per_100 = 52\n'
                    'elif product == "банан":\n'
                    '    kcal_per_100 = 89\n'
                    'else:\n'
                    '    kcal_per_100 = 0\n'
                    'print(kcal_per_100)'
                ),
            },
        ],
        'visual_blocks': [
            {
                'title': 'Зачем if в калькуляторе',
                'body': 'Один и тот же код считает калории для разных продуктов — меняется только число kcal_per_100.',
            },
        ],
        'schemes': [],
        'remember': [
            'После if, elif, else обязательно двоеточие.',
            'Тело блока — строки с отступом.',
            'elif проверяется только если предыдущие условия ложны.',
        ],
        'mistakes': [
            'Забыть двоеточие после if.',
            'Писать print без отступа внутри if — он выполнится всегда.',
            'Дублировать if вместо elif — оба блока могут не сработать как ожидается.',
        ],
        'tips': [
            'Сначала проверьте один if с print внутри.',
            'Добавляйте elif по одному продукту.',
        ],
    },
    'tasks': [
        {
            'id': 42,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Когда выполняется блок else?',
            'hint': 'else — когда все if/elif ложны.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Когда ни одно условие if/elif не выполнилось'},
                {'key': 'b', 'label': 'Всегда, сразу после if'},
                {'key': 'c', 'label': 'Только если if True'},
            ],
            'correct': 'a',
        },
        {
            'id': 43,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'product = "яблоко". Если product == "яблоко", выведите 52, '
                'иначе выведите 0. Используйте if и else.'
            ),
            'hint': 'if product == "яблоко":\n    print(52)\nelse:\n    print(0)',
            'xp': 14,
            'expected': '52',
            'starter_code': 'product = "яблоко"\n',
        },
        {
            'id': 44,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте отступы: при product = "банан" программа должна вывести 89.'
            ),
            'hint': 'print(89) должен быть внутри elif с отступом.',
            'xp': 14,
            'expected': '89',
            'starter_code': (
                'product = "банан"\n'
                'if product == "яблоко":\n'
                '    print(52)\n'
                'elif product == "банан":\n'
                'print(89)\n'
            ),
        },
        {
            'id': 45,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                'x = 10\nif x > 5:\n    print("A")\nelse:\n    print("B")\n'
                'Что выведет программа?'
            ),
            'hint': '10 > 5 — True, выполнится первая ветка.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'A'},
                {'key': 'b', 'label': 'B'},
                {'key': 'c', 'label': 'A и B'},
            ],
            'correct': 'a',
        },
        {
            'id': 46,
            'kind': 'project_step',
            'category': 'project_step',
            'type': 'code',
            'text': (
                'product = "банан". Через if/elif задайте kcal_per_100: '
                'яблоко — 52, банан — 89, иначе 0. Выведите kcal_per_100.'
            ),
            'hint': 'Три ветки: if, elif, else.',
            'xp': 16,
            'expected': '89',
            'starter_code': (
                'product = "банан"\n'
                '# kcal_per_100 = ...\n# print(kcal_per_100)\n'
            ),
        },
        {
            'id': 47,
            'kind': 'quiz',
            'category': 'trainer',
            'type': 'quiz',
            'text': 'Что обязательно после строки if age >= 14:?',
            'hint': 'Блок кода с отступом.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Строки с отступом — тело условия'},
                {'key': 'b', 'label': 'Точка с запятой'},
                {'key': 'c', 'label': 'Слово then'},
            ],
            'correct': 'a',
        },
    ],
}
