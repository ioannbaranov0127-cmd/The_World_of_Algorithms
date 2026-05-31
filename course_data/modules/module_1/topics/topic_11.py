# -*- coding: utf-8 -*-
"""Тема 10. Цикл while и выход из цикла."""

from __future__ import annotations

from course_data.project import project_step_for_topic

TOPIC: dict = {
    'id': 'm1-t10',
    'num': 10,
    'title': 'Тема 10. Цикл while и выход из цикла',
    'summary': 'while, break и условие завершения цикла.',
    'project_step': project_step_for_topic(10),
    'theory': {
        'intro': (
            'Один раз спросить продукт — мало. За обед можно съесть несколько позиций. '
            'Цикл for повторяет блок кода заданное число раз — и калькулятор готов '
            'принимать несколько порций подряд.'
        ),
        'sections': [
            {
                'title': 'Цикл for',
                'body': (
                    'for переменная in последовательность: — тело цикла выполняется для каждого '
                    'элемента. Часто используют range(n), чтобы повторить действие n раз.'
                ),
                'code': (
                    'for i in range(3):\n'
                    '    print("Шаг", i)'
                ),
            },
            {
                'title': 'Функция range()',
                'body': (
                    'range(5) даёт числа 0, 1, 2, 3, 4 — пять итераций. '
                    'range(1, 4) — 1, 2, 3. В проекте range(3) может означать «три продукта за приём».'
                ),
                'code': (
                    'for n in range(1, 4):\n'
                    '    print("Продукт №", n)'
                ),
            },
            {
                'title': 'Накопление суммы в цикле',
                'body': (
                    'Перед циклом total = 0. На каждом шаге добавляем калории порции — '
                    'так считают общий итог за несколько продуктов.'
                ),
                'code': (
                    'total = 0\n'
                    'for _ in range(2):\n'
                    '    total = total + 100\n'
                    'print(total)'
                ),
            },
            {
                'title': 'Подготовка к вводу в цикле',
                'body': (
                    'Пока можно задавать граммы в коде, но структура уже как в финальном проекте: '
                    'цикл → ввод (позже) → расчёт → добавление к total.'
                ),
                'code': (
                    'total = 0\n'
                    'kcal_per_100 = 52\n'
                    'for _ in range(3):\n'
                    '    grams = 100\n'
                    '    total = total + grams * kcal_per_100 / 100\n'
                    'print("Итого:", total)'
                ),
            },
        ],
        'visual_blocks': [
            {
                'title': 'Зачем цикл в калькуляторе',
                'body': 'Без for пришлось бы копировать один и тот же код для каждого продукта. Цикл — один шаблон, много повторений.',
            },
        ],
        'schemes': [],
        'remember': [
            'range(n) — n итераций, счёт с 0.',
            'Тело for — строки с отступом после двоеточия.',
            'Переменная цикла можно не использовать: for _ in range(3).',
        ],
        'mistakes': [
            'Забыть отступ у строк внутри for.',
            'Думать, что range(3) даёт 1, 2, 3 — на самом деле 0, 1, 2.',
            'Не обнулять total перед циклом.',
        ],
        'tips': [
            'Сначала выведите i в цикле, чтобы увидеть, сколько раз он крутится.',
            'Считайте итерации на бумаге для range(1, 5).',
        ],
    },
    'tasks': [
        {
            'id': 54,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Сколько раз выполнится тело цикла for i in range(4):?',
            'hint': 'range(4) — числа 0, 1, 2, 3.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '4 раза'},
                {'key': 'b', 'label': '3 раза'},
                {'key': 'c', 'label': '5 раз'},
            ],
            'correct': 'a',
        },
        {
            'id': 55,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'Выведите числа 0, 1, 2 каждое с новой строки с помощью for и range(3).'
            ),
            'hint': 'for i in range(3):\n    print(i)',
            'xp': 14,
            'expected': '0\n1\n2',
            'starter_code': '# цикл for\n',
        },
        {
            'id': 56,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте цикл: программа должна три раза вывести слово «Приём» '
                '(три строки «Приём»).'
            ),
            'hint': 'print должен быть с отступом внутри for.',
            'xp': 14,
            'expected': 'Приём\nПриём\nПриём',
            'starter_code': (
                'for _ in range(3):\n'
                'print("Приём")\n'
            ),
        },
        {
            'id': 57,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                's = 0\nfor i in range(1, 4):\n    s = s + i\n'
                'Что выведет print(s)?'
            ),
            'hint': 'i принимает 1, 2, 3. s = 0+1+2+3.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '6'},
                {'key': 'b', 'label': '3'},
                {'key': 'c', 'label': '10'},
            ],
            'correct': 'a',
        },
        {
            'id': 58,
            'kind': 'project_step',
            'category': 'project_step',
            'type': 'code',
            'text': (
                'Два «продукта» по 100 г, яблоко 52 ккал/100 г. В цикле for _ in range(2) '
                'добавляйте к total калории одной порции. Выведите «Итого: » и total '
                '(ожидается 104.0).'
            ),
            'hint': 'total = 0; в цикле total += 100 * 52 / 100',
            'xp': 16,
            'expected': 'Итого: 104.0',
            'starter_code': (
                'total = 0\nkcal_per_100 = 52\n'
                '# for _ in range(2):\n#     ...\n# print("Итого:", total)\n'
            ),
        },
        {
            'id': 59,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'С помощью for и range(1, 6) выведите сумму чисел 1+2+3+4+5 одним числом 15 '
                '(накопите в переменной s).'
            ),
            'hint': 's = 0; for i in range(1, 6): s += i; print(s)',
            'xp': 14,
            'expected': '15',
            'starter_code': '# s = 0\n# цикл\n',
        },
    ],
}
