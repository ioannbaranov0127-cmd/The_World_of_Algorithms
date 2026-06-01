# -*- coding: utf-8 -*-
"""Тема 2 модуля 2. Работа со списками."""

from __future__ import annotations

from course_data.modules.module_2.project import project_step_for_module_2

TOPIC: dict = {
    'id': 'm2-t2',
    'num': 2,
    'title': 'Тема 2. Работа со списками',
    'summary': 'Создание list, индексация и хранение продуктов с калорийностью.',
    'project_step': project_step_for_module_2(2),
    'theory': {
        'intro': (
            'После версии 1.0 в калькуляторе мало продуктов и каждый if — отдельная ветка. '
            'Улучшение модуля 2: список (list) как каталог — названия и калорийность на 100 г в двух '
            'связанных списках, доступ по индексу.'
        ),
        'sections': [
            {
                'title': 'Что такое список',
                'body': (
                    'Список — упорядоченная коллекция в квадратных скобках. Элементы перечисляют через запятую.'
                ),
                'code': 'products = ["яблоко", "банан", "хлеб"]\nprint(products)',
            },
            {
                'title': 'Индексация с нуля',
                'body': (
                    'Первый элемент — индекс 0, второй — 1. Индекс -1 — последний элемент.'
                ),
                'code': (
                    'names = ["яблоко", "банан"]\n'
                    'kcal = [52, 89]\n'
                    'print(names[0], kcal[0])'
                ),
            },
            {
                'title': 'Два списка в проекте',
                'body': (
                    'Один список — названия, другой — калорийность при том же индексе.'
                ),
                'code': (
                    'products = ["яблоко", "банан", "молоко"]\n'
                    'kcal_per_100 = [52, 89, 60]\n'
                    'i = 1\nprint(products[i], kcal_per_100[i])'
                ),
            },
        ],
        'visual_blocks': [
            {
                'title': 'Связь индексов',
                'body': 'products[i] и kcal_per_100[i] описывают один и тот же продукт.',
            },
        ],
        'schemes': [],
        'remember': [
            'Индексация с 0.',
            'Списки создают через [ ] и элементы через запятую.',
        ],
        'mistakes': [
            'Обращаться к products[3] в списке из трёх элементов — ошибка.',
        ],
        'tips': [
            'Выведите len(products) и products[-1].',
        ],
    },
    'tasks': [
        {
            'id': 66,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Как получить первый элемент списка items = ["a", "b", "c"]?',
            'hint': 'Первый — индекс 0.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'items[0]'},
                {'key': 'b', 'label': 'items[1]'},
                {'key': 'c', 'label': 'items.first()'},
            ],
            'correct': 'a',
        },
        {
            'id': 67,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': 'Создайте fruits = ["яблоко", "банан"] и выведите второй элемент.',
            'hint': 'print(fruits[1])',
            'xp': 14,
            'expected': 'банан',
            'starter_code': '# fruits = [...]\n',
        },
        {
            'id': 68,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': 'kcal = [52, 89, 60]\nprint(kcal[2])\nЧто выведет программа?',
            'hint': 'Индекс 2 — третий элемент.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '60'},
                {'key': 'b', 'label': '52'},
                {'key': 'c', 'label': '89'},
            ],
            'correct': 'a',
        },
        {
            'id': 69,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': 'Исправьте индекс: должен вывестись «яблоко», сейчас выводится «банан».',
            'hint': 'Первый элемент — индекс 0.',
            'xp': 14,
            'expected': 'яблоко',
            'starter_code': (
                'products = ["яблоко", "банан"]\n'
                'print(products[1])\n'
            ),
        },
        {
            'id': 70,
            'kind': 'project_step',
            'category': 'project_step',
            'type': 'code',
            'text': (
                'products = ["яблоко", "банан"], kcal_per_100 = [52, 89]. '
                'Выведите яблоко и его kcal через пробел (52).'
            ),
            'hint': 'print(products[0], kcal_per_100[0])',
            'xp': 16,
            'expected': 'яблоко 52',
            'starter_code': '# products = ...\n# print(...)\n',
        },
        {
            'id': 71,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': 'nums = [10, 20, 30]. Выведите сумму первого и последнего элемента.',
            'hint': 'nums[0] + nums[-1]',
            'xp': 14,
            'expected': '40',
            'starter_code': 'nums = [10, 20, 30]\n',
        },
    ],
}
