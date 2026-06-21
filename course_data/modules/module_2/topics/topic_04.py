# -*- coding: utf-8 -*-
"""Тема 4 модуля 2. Методы списков."""

from __future__ import annotations

from course_data.modules.module_2.project import project_step_for_module_2
from course_data.modules.module_2.project_stage_tasks import STAGE_M2_04

TOPIC: dict = {
    'id': 'm2-t4',
    'num': 4,
    'title': 'Тема 4. Методы списков (append, remove)',
    'summary': 'append(), len() — список как зачаток ингредиентов блюда в демо.',
    'project_step': project_step_for_module_2(4),
    'theory': {
        'intro': (
            'В версии 1.4 список eaten — тренировка перед рецептами в демо. '
            'В HTML-демо у блюда есть список ингредиентов; в 2.0 он задаётся словарём dishes. '
            'Сейчас eaten.append(name) после каждой порции — учимся собирать список продуктов в одном месте. '
            'Методы append(), remove() и len() помогают добавлять, убирать и считать записи.'
        ),
        'sections': [
            {
                'title': 'Зачем калькулятору журнал eaten',
                'body': (
                    'Список products — это каталог: что можно выбрать. '
                    'Список eaten — это дневник: что пользователь уже съел в этом сеансе. '
                    'После каждой порции мы дописываем название в eaten — так видно историю за день.'
                ),
            },
        ],
        'visual_blocks': [
            {
                'title': 'Главная мысль темы',
                'body': (
                    'append() — добавить в конец, remove() — убрать элемент, len() — сколько элементов в списке.'
                ),
            },
        ],
        'schemes': [],
        'scheme_gallery_layout': 'stack',
        'scheme_gallery_before': [
            {
                'title': 'Перед схемой',
                'body': (
                    'На схеме ниже — как методы списка меняют его содержимое. '
                    'append дописывает элемент в конец, remove убирает первое совпадение, '
                    'len показывает длину списка. Запомните: метод вызывают у списка через точку — eaten.append(x).'
                ),
            },
        ],
        'scheme_gallery': [
            {
                'file': 'Методы_списков_1.svg',
                'num': 1,
                'caption': 'Методы append, remove и функция len для списка',
                'sections_after': [
                    {
                        'title': 'Как читать схему',
                        'body': (
                            'Список — как ряд ячеек. append() ставит новый элемент после последнего. '
                            'remove(значение) ищет это значение и удаляет первое совпадение. '
                            'len(список) не меняет список — только возвращает число элементов.'
                        ),
                    },
                    {
                        'title': 'Пустой список в начале',
                        'body': (
                            'Журнал начинаем с пустого списка: eaten = []. '
                            'Квадратные скобки без элементов — «пока ничего не записано». '
                            'Такой список удобно постепенно наполнять в цикле while.'
                        ),
                        'code': 'eaten = []\nprint(eaten)  # []\nprint(len(eaten))  # 0',
                    },
                    {
                        'title': 'Метод append() — добавить в конец',
                        'body': (
                            'append(элемент) дописывает значение в конец списка. '
                            'После расчёта порции логично вызвать eaten.append(products[i]) — '
                            'в журнал попадёт название продукта. Можно append и число калорий, если так задумано в проекте.'
                        ),
                        'code': (
                            'eaten = []\n'
                            'eaten.append("яблоко")\n'
                            'eaten.append("банан")\n'
                            'print(eaten)  # ["яблоко", "банан"]'
                        ),
                    },
                    {
                        'title': 'Функция len() — сколько элементов',
                        'body': (
                            'len(eaten) возвращает количество записей. '
                            'Это не метод списка, а отдельная функция: len пишут перед скобкой. '
                            'Удобно показать пользователю: «Записей в журнале: 3».'
                        ),
                        'code': (
                            'eaten = ["яблоко", "банан", "хлеб"]\n'
                            'print("Записей:", len(eaten))  # 3'
                        ),
                    },
                    {
                        'title': 'Метод remove() — удалить элемент',
                        'body': (
                            'remove(элемент) удаляет первое вхождение значения в списке. '
                            'Если пользователь ошибся и ввёл лишнюю порцию, можно eaten.remove("банан"). '
                            'Важно: remove ищет точное совпение — регистр и пробелы должны совпадать.'
                        ),
                        'code': (
                            'eaten = ["яблоко", "банан", "яблоко"]\n'
                            'eaten.remove("яблоко")\n'
                            'print(eaten)  # ["банан", "яблоко"] — удалили первое «яблоко»'
                        ),
                    },
                    {
                        'title': 'append и remove — разные задачи',
                        'body': (
                            'append всегда добавляет в конец — список растёт. '
                            'remove убирает уже существующий элемент — список уменьшается. '
                            'Не путайте: append(eaten, "x") — ошибка; правильно eaten.append("x").'
                        ),
                        'code': (
                            '# Правильно:\n'
                            'eaten.append("молоко")\n\n'
                            '# Неправильно:\n'
                            '# append(eaten, "молоко")'
                        ),
                    },
                    {
                        'title': 'Журнал eaten в цикле while',
                        'body': (
                            'Типичный фрагмент версии 1.4 внутри тела while: '
                            'посчитали порцию → eaten.append(название) → print("Записей:", len(eaten)). '
                            'Каталог products не меняется — меняется только eaten.'
                        ),
                        'code': (
                            'eaten = []\n'
                            'while True:\n'
                            '    # ... расчёт порции ...\n'
                            '    eaten.append("яблоко")  # пример\n'
                            '    print("Записей:", len(eaten))\n'
                            '    break  # в проекте — выход по команде пользователя'
                        ),
                    },
                    {
                        'title': 'Ошибки с remove',
                        'body': (
                            'Если элемента нет в списке, remove вызовет ошибку. '
                            'Перед remove можно проверить: if "банан" in eaten: eaten.remove("банан"). '
                            'На первом этапе достаточно знать: remove работает только с тем, что уже есть в списке.'
                        ),
                    },
                    {
                        'title': 'Что изменится в project_stage',
                        'body': (
                            'После сдачи project_stage в main.py появятся eaten = [], append после порции '
                            'и вывод len(eaten). Расчёт по индексам из версии 1.3 сохраните. '
                            'Проверьте: две порции подряд → len(eaten) должен стать 2.'
                        ),
                    },
                ],
            },
        ],
        'remember': [
            'append(), remove() — методы списка: список.метод(...).',
            'len(список) — функция, не метод.',
            'eaten = [] — пустой журнал в начале программы или до цикла.',
            'append добавляет в конец; remove удаляет первое совпадение.',
            'products — каталог, eaten — что уже ввели за сеанс.',
        ],
        'mistakes': [
            'Писать append(eaten, "x") вместо eaten.append("x").',
            'Забыть eaten = [] — append к несуществующему списку нельзя.',
            'remove("продукт"), которого нет в eaten — ошибка программы.',
            'Путать len(eaten) и eaten[len(eaten)] — второе уже обращение по индексу.',
            'Удалять из products вместо eaten — каталог должен оставаться полным.',
        ],
        'tips': [
            'После каждого append выведите print(eaten) — так видно, как растёт журнал.',
            'Подпишите в комментарии: # каталог и # журнал — не перепутаете списки.',
            'Сначала отработайте append и len на маленьком примере вне while.',
            'Если remove пугает — в project_stage можно обойтись без него, append и len обязательны.',
        ],
    },
    'tasks': [
        {
            'id': 350,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Что делает eaten.append("банан")?',
            'hint': 'append дописывает элемент в конец списка.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Добавляет «банан» в конец списка eaten'},
                {'key': 'b', 'label': 'Удаляет «банан» из списка'},
                {'key': 'c', 'label': 'Считает, сколько элементов в списке'},
            ],
            'correct': 'a',
        },
        {
            'id': 351,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Чем len(eaten) отличается от eaten.append("x")?',
            'hint': 'len только считает, append меняет список.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'len возвращает число элементов, append добавляет элемент'},
                {'key': 'b', 'label': 'Это одно и то же'},
                {'key': 'c', 'label': 'len удаляет последний элемент'},
            ],
            'correct': 'a',
        },
        {
            'id': 352,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                'lst = []\n'
                'lst.append(10)\n'
                'lst.append(20)\n'
                'print(len(lst))\n'
                'Что выведет программа?'
            ),
            'hint': 'Два append — два элемента.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '2'},
                {'key': 'b', 'label': '20'},
                {'key': 'c', 'label': '0'},
            ],
            'correct': 'a',
        },
        {
            'id': 353,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'eaten = []. Добавьте «яблоко» и «банан» через append. '
                'Выведите список eaten одной строкой (как print(eaten)).'
            ),
            'hint': 'eaten.append("яблоко"); eaten.append("банан"); print(eaten)',
            'xp': 14,
            'expected': "['яблоко', 'банан']",
            'starter_code': 'eaten = []\n',
        },
        {
            'id': 354,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте код: после append в eaten должно быть два элемента, '
                'сейчас len(eaten) выводит 1.'
            ),
            'hint': 'Метод вызывают у списка: eaten.append("банан").',
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
            'id': 355,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'eaten = ["яблоко", "банан", "хлеб"]. '
                'Выведите одну строку: Записей: 3'
            ),
            'hint': 'print("Записей:", len(eaten))',
            'xp': 14,
            'expected': 'Записей: 3',
            'starter_code': 'eaten = ["яблоко", "банан", "хлеб"]\n',
        },
        {
            'id': 356,
            'kind': 'practice',
            'category': 'practice',
            'type': 'matching',
            'text': 'Сопоставь команду и её действие.',
            'hint': 'append — в конец, remove — удалить, len — длина.',
            'xp': 12,
            'left': ['eaten.append("x")', 'len(eaten)', 'eaten.remove("x")'],
            'right': [
                'Удалить первое «x» из списка',
                'Добавить «x» в конец списка',
                'Узнать количество элементов',
            ],
            'correct_pairs': [1, 2, 0],
        },
        {
            'id': 357,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                'items = ["a", "b", "c"]\n'
                'items.remove("b")\n'
                'print(len(items))\n'
                'Что выведет программа?'
            ),
            'hint': 'После remove останутся "a" и "c".',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '2'},
                {'key': 'b', 'label': '3'},
                {'key': 'c', 'label': '1'},
            ],
            'correct': 'a',
        },
        {
            'id': 358,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'eaten = ["яблоко", "банан", "яблоко"]. '
                'Удалите одно «яблоко» через remove и выведите eaten.'
            ),
            'hint': 'eaten.remove("яблоко")',
            'xp': 14,
            'expected': "['банан', 'яблоко']",
            'starter_code': 'eaten = ["яблоко", "банан", "яблоко"]\n',
        },
        {
            'id': 359,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'Симуляция журнала: eaten = []. '
                'Добавьте три продукта «молоко», «сыр», «йогурт» через append. '
                'Выведите «Записей: 3».'
            ),
            'hint': 'Три append, затем print("Записей:", len(eaten))',
            'xp': 14,
            'expected': 'Записей: 3',
            'starter_code': 'eaten = []\n',
        },
        STAGE_M2_04,
    ],
}
