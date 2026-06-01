# -*- coding: utf-8 -*-
"""Тема 3 модуля 2. Методы списков."""

from __future__ import annotations

from course_data.modules.module_2.project import project_step_for_module_2

TOPIC: dict = {
    'id': 'm2-t3',
    'num': 3,
    'title': 'Тема 3. Методы списков (append, remove, len)',
    'summary': 'append(), remove(), len() и список введённых продуктов.',
    'project_step': project_step_for_module_2(3),
    'theory': {
        'intro': (
            'После каталога продуктов (списки в теме 2) добавляем журнал порций за день: '
            'append(), remove() и len() — чтобы приложение помнило, что пользователь уже вводил, '
            'и показывало количество записей.'
        ),
        'sections': [
            {
                'title': 'Метод append()',
                'body': 'append(элемент) добавляет значение в конец списка.',
                'code': (
                    'eaten = []\n'
                    'eaten.append("яблоко")\n'
                    'eaten.append("банан")\n'
                    'print(eaten)'
                ),
            },
            {
                'title': 'Метод remove()',
                'body': 'remove(элемент) удаляет первое вхождение значения.',
                'code': (
                    'items = ["яблоко", "банан", "яблоко"]\n'
                    'items.remove("яблоко")\n'
                    'print(items)'
                ),
            },
            {
                'title': 'Функция len()',
                'body': 'len(список) возвращает количество элементов.',
                'code': (
                    'eaten = ["яблоко", "банан", "хлеб"]\n'
                    'print("Продуктов:", len(eaten))'
                ),
            },
        ],
        'visual_blocks': [
            {
                'title': 'В проекте',
                'body': 'Пустой eaten = []. В цикле append после каждого ввода. В конце print(len(eaten)).',
            },
        ],
        'schemes': [],
        'remember': [
            'append() вызывают у списка: lst.append(x).',
            'len(lst) — число элементов.',
        ],
        'mistakes': [
            'Писать append lst вместо lst.append(x).',
            'remove() для элемента, которого нет в списке.',
        ],
        'tips': [
            'После append выведите список целиком.',
        ],
    },
    'tasks': [
        {
            'id': 72,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Что делает eaten.append("банан")?',
            'hint': 'Добавляет в конец списка.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Добавляет «банан» в конец списка eaten'},
                {'key': 'b', 'label': 'Удаляет «банан» из списка'},
                {'key': 'c', 'label': 'Считает длину списка'},
            ],
            'correct': 'a',
        },
        {
            'id': 73,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': 'lst = []. Добавьте 5 и 7 через append. Выведите len(lst).',
            'hint': 'lst.append(5); lst.append(7)',
            'xp': 14,
            'expected': '2',
            'starter_code': 'lst = []\n',
        },
        {
            'id': 74,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': 'Исправьте код: после двух append len(eaten) должен быть 2.',
            'hint': 'eaten.append("яблоко"), не append(eaten, ...).',
            'xp': 14,
            'expected': '2',
            'starter_code': (
                'eaten = []\n'
                'append(eaten, "яблоко")\n'
                'eaten.append("банан")\n'
                'print(len(eaten))\n'
            ),
        },
        {
            'id': 75,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': 'a = [1, 2, 3]\na.remove(2)\nprint(len(a))\nЧто выведет программа?',
            'hint': 'Останутся 1 и 3.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '2'},
                {'key': 'b', 'label': '3'},
                {'key': 'c', 'label': '1'},
            ],
            'correct': 'a',
        },
        {
            'id': 76,
            'kind': 'project_step',
            'category': 'project_step',
            'type': 'code',
            'text': (
                'eaten = []. Добавьте «яблоко», «банан», «хлеб» через append. '
                'Выведите «Всего продуктов: » и len(eaten).'
            ),
            'hint': 'Три append, затем print.',
            'xp': 16,
            'expected': 'Всего продуктов: 3',
            'starter_code': 'eaten = []\n# append ...\n',
        },
        {
            'id': 77,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'lst = ["a", "b", "a"]. Удалите одно «a» через remove и выведите lst.'
            ),
            'hint': 'lst.remove("a")',
            'xp': 14,
            'expected': "['b', 'a']",
            'starter_code': 'lst = ["a", "b", "a"]\n',
        },
    ],
}
