# -*- coding: utf-8 -*-
"""Тема 5. Команда input()."""

from __future__ import annotations

from course_data.project import project_step_for_topic

TOPIC: dict = {
    'id': 'm1-t5',
    'num': 5,
    'title': 'Тема 5. Команда input()',
    'summary': 'input(), получение данных от пользователя, преобразование типов.',
    'project_step': project_step_for_topic(5),
    'theory': {
        'intro': (
            'До сих пор все числа мы писали в коде сами. В настоящей программе пользователь '
            'вводит граммы и название продукта. Команда input() ждёт строку с клавиатуры — '
            'и калькулятор калорий становится интерактивным.'
        ),
        'sections': [
            {
                'title': 'Как работает input()',
                'body': (
                    'input() останавливает программу и читает одну строку текста. Результат — '
                    'всегда строка (str), даже если пользователь набрал цифры.'
                ),
                'code': 'name = input("Ваше имя: ")\nprint("Привет,", name)',
            },
            {
                'title': 'Строка и число — разные типы',
                'body': (
                    '"100" + "50" склеит строки в "10050". Чтобы сложить числа, нужно преобразование. '
                    'int("100") даёт число 100.'
                ),
                'code': 'text = "150"\ngrams = int(text)\nprint(grams + 50)',
            },
            {
                'title': 'int(input()) и float(input())',
                'body': (
                    'Частый приём: сразу читать число — grams = int(input()). '
                    'Для дробных порций (например 125.5 г) используйте float(input()).'
                ),
                'code': (
                    '# В тренажёре: сначала «Выполнить», введите число в консоли\n'
                    'grams = int(input("Граммы: "))\nprint(grams * 2)'
                ),
            },
            {
                'title': 'Ввод в проекте',
                'body': (
                    'Следующий шаг калькулятора: спросить, сколько грамм съели. '
                    'Пока продукт можно задать в коде, а граммы — через input().'
                ),
                'code': (
                    'print("Калькулятор калорий")\n'
                    'grams = int(input("Сколько грамм? "))\nprint("Вы ввели:", grams)'
                ),
            },
        ],
        'visual_blocks': [
            {
                'title': 'Подсказка для тренажёра',
                'body': 'Если в задании есть input(), нажмите «Выполнить» и введите данные в консоли. Затем «Проверить».',
            },
        ],
        'schemes': [],
        'remember': [
            'input() возвращает строку.',
            'int() и float() переводят текст в число.',
            'Без преобразования "5" + "3" не даст 8.',
        ],
        'mistakes': [
            'Писать grams = input() и сразу grams + 10 — ошибка типов.',
            'Забыть подсказку внутри input("...") — пользователю непонятно, что вводить.',
        ],
        'tips': [
            'Сначала отработайте преобразование на готовой строке: int("200").',
            'Проверяйте ввод короткими print сразу после input().',
        ],
    },
    'tasks': [
        {
            'id': 30,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Что вернёт input() после ввода числа 250?',
            'hint': 'input() не возвращает int — только str.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Строку "250"'},
                {'key': 'b', 'label': 'Число 250'},
                {'key': 'c', 'label': 'Ничего, только печатает на экран'},
            ],
            'correct': 'a',
        },
        {
            'id': 31,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': 'Сохраните в переменную name строку «Аня» и выведите: Привет, Аня!',
            'hint': 'name = "Аня"\nprint("Привет,", name + "!")',
            'xp': 12,
            'expected': 'Привет, Аня!',
            'starter_code': '# имя пользователя\n',
        },
        {
            'id': 32,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'В переменной text лежит строка "180". Преобразуйте её в int, '
                'сохраните в grams и выведите grams.'
            ),
            'hint': 'grams = int(text)',
            'xp': 14,
            'expected': '180',
            'starter_code': 'text = "180"\n',
        },
        {
            'id': 33,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте ошибку: программа должна вывести сумму 100 + 50, '
                'а не склеить строки.'
            ),
            'hint': 'Нужен int() для a и b.',
            'xp': 14,
            'expected': '150',
            'starter_code': 'a = "100"\nb = "50"\nprint(a + b)\n',
        },
        {
            'id': 34,
            'kind': 'project_step',
            'category': 'project_step',
            'type': 'code',
            'text': (
                'Выведите «Сколько грамм вы съели?», затем прочитайте число через input(), '
                'преобразуйте в int и выведите «Граммы: » и значение. '
                'При проверке сначала «Выполнить» и введите 120.'
            ),
            'hint': 'print(...)\ngrams = int(input())\nprint("Граммы:", grams)',
            'xp': 16,
            'expected': 'Граммы: 120',
            'starter_code': (
                'print("Сколько грамм вы съели?")\n'
                '# grams = int(input())\n# print(...)\n'
            ),
        },
        {
            'id': 35,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Какой тип у переменной x после x = float("52.5")?',
            'hint': 'float() создаёт дробное число.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'float'},
                {'key': 'b', 'label': 'str'},
                {'key': 'c', 'label': 'int'},
            ],
            'correct': 'a',
        },
    ],
}
