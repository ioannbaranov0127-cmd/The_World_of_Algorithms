# -*- coding: utf-8 -*-
"""Тема 8. Тренажёр ввода текста и вывода на экран."""

from __future__ import annotations

from course_data.constants import DEFAULT_CODE_EDITOR_PLACEHOLDER
from course_data.project import project_step_for_topic

TOPIC: dict = {
    'id': 'm1-t8',
    'num': 8,
    'title': 'Тема 8. Тренажёр ввода текста и вывода на экран',
    'summary': 'print, input, метод lower() и выбор продукта без учёта регистра.',
    'project_step': project_step_for_topic(8),
    'theory': {
        'intro': (
            'Пользователь может набрать «Яблоко», «яблоко» или «ЯБЛОКО» — для программы '
            'это разные строки, если сравнивать напрямую. Метод .lower() переводит текст '
            'в нижний регистр, и выбор продукта в калькуляторе становится удобнее.'
        ),
        'sections': [
            {
                'title': 'Повторение: print и input',
                'body': (
                    'print() показывает меню и подсказки. input() читает ответ. '
                    'Связка «меню → ввод → ответ» — основа диалога с пользователем.'
                ),
                'code': (
                    'print("1. Яблоко")\nprint("2. Банан")\n'
                    'choice = input("Продукт: ")\nprint("Вы выбрали:", choice)'
                ),
            },
            {
                'title': 'Метод .lower()',
                'body': (
                    'У строки есть методы. .lower() возвращает копию строки в нижнем регистре. '
                    '"ЯБЛОКО".lower() → "яблоко". Сравнивайте уже приведённые строки.'
                ),
                'code': 'product = input("Продукт: ")\nproduct = product.lower()\nprint(product)',
            },
            {
                'title': 'Сравнение без регистра',
                'body': (
                    'Вместо product == "Яблоко" пишите product.lower() == "яблоко" — '
                    'тогда подойдут любые буквы одного размера.'
                ),
                'code': (
                    'p = input("Что съели? ")\n'
                    'if p.lower() == "яблоко":\n'
                    '    print("Яблоко выбрано")\n'
                    'else:\n'
                    '    print("Другой продукт")'
                ),
            },
            {
                'title': 'Меню проекта',
                'body': (
                    'Выведите список продуктов, спросите выбор, приведите к lower() — '
                    'это задел под условия if в следующей теме.'
                ),
            },
        ],
        'visual_blocks': [
            {
                'title': 'Шаг проекта',
                'body': 'Яблоко = яблоко = ЯБЛОКО — один и тот же продукт для программы после .lower().',
            },
        ],
        'schemes': [],
        'remember': [
            'input() → str; перед сравнением часто нужен .lower().',
            'Меню делают несколькими print подряд.',
        ],
        'mistakes': [
            'Сравнивать "Яблоко" и "яблоко" без lower() — условие не сработает.',
            'Писать lower вместо .lower() — это метод строки.',
        ],
        'tips': [
            'Проверьте три варианта написания в «Выполнить».',
            'Сначала выведите product.lower() через print, чтобы увидеть результат.',
        ],
    },
    'tasks': [
        {
            'id': 36,
            'kind': 'quiz',
            'category': 'trainer',
            'type': 'quiz',
            'text': 'Что выведет print("БАНАН".lower())?',
            'hint': 'lower() — все буквы маленькие.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'банан'},
                {'key': 'b', 'label': 'БАНАН'},
                {'key': 'c', 'label': 'Banana'},
            ],
            'correct': 'a',
        },
        {
            'id': 37,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'Выведите меню из трёх строк: «=== Продукты ===», «1. Яблоко», «2. Банан» '
                '(каждая с новой строки).'
            ),
            'hint': 'Три print.',
            'xp': 14,
            'expected': '=== Продукты ===\n1. Яблоко\n2. Банан',
            'starter_code': DEFAULT_CODE_EDITOR_PLACEHOLDER,
        },
        {
            'id': 38,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте сравнение: при вводе «ЯБЛОКО» (в коде задайте product = "ЯБЛОКО") '
                'программа должна вывести «Ок».'
            ),
            'hint': 'Используйте product.lower() == "яблоко".',
            'xp': 14,
            'expected': 'Ок',
            'starter_code': (
                'product = "ЯБЛОКО"\n'
                'if product == "яблоко":\n'
                '    print("Ок")\n'
            ),
        },
        {
            'id': 39,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                'product = "Банан"\nЧто выведет print(product.lower() == "банан")?'
            ),
            'hint': 'Сравнение даёт True или False.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'True'},
                {'key': 'b', 'label': 'False'},
                {'key': 'c', 'label': 'банан'},
            ],
            'correct': 'a',
        },
        {
            'id': 40,
            'kind': 'project_step',
            'category': 'project_step',
            'type': 'code',
            'text': (
                'Задайте product = input() (в коде можно product = "ЯбЛоКо" для проверки без ввода). '
                'Если product.lower() == "яблоко", выведите «Выбрано: Яблоко».'
            ),
            'hint': 'if product.lower() == "яблоко": ...',
            'xp': 16,
            'expected': 'Выбрано: Яблоко',
            'starter_code': 'product = "ЯбЛоКо"\n# if ...\n',
        },
        {
            'id': 41,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'Строка word = "Python". Выведите её в нижнем регистре одной строкой.'
            ),
            'hint': 'print(word.lower())',
            'xp': 12,
            'expected': 'python',
            'starter_code': 'word = "Python"\n',
        },
    ],
}
