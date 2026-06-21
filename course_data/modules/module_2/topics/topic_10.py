# -*- coding: utf-8 -*-
"""Тема 10 модуля 2. Методы словарей."""

from __future__ import annotations

from course_data.modules.module_2.project import project_step_for_module_2
from course_data.modules.module_2.project_stage_tasks import STAGE_M2_10

TOPIC: dict = {
    'id': 'm2-t10',
    'num': 10,
    'title': 'Тема 10. Методы словарей',
    'summary': 'get, items и калькулятор блюда — как в демо: рецепт → граммы по ингредиентам → итог.',
    'project_step': project_step_for_module_2(10),
    'theory': {
        'intro': (
            'В версии 1.9 база продуктов — словарь products_kcal. '
            'В версии 2.0 калькулятор становится как HTML-демо: пользователь выбирает блюдо, '
            'программа показывает список ингредиентов и по каждому спрашивает граммы. '
            'Методы словаря помогают: get — безопасно взять калории продукта, '
            'dishes.get("фруктовый салат") — список ингредиентов, items() — вывести меню блюд.'
        ),
        'sections': [],
        'visual_blocks': [
            {
                'title': 'Главная мысль темы',
                'body': (
                    'Метод — команда после точки у словаря: products_kcal.get("яблоко"). '
                    'В версии 2.0 два словаря: products_kcal (продукт → ккал) '
                    'и dishes (блюдо → список ингредиентов). '
                    'Цикл for по ингредиентам — как строки таблицы в демо-калькуляторе.'
                ),
            },
        ],
        'schemes': [],
        'scheme_gallery_layout': 'stack',
        'scheme_gallery_before': [
            {
                'title': 'Таблица методов на схеме',
                'body': (
                    'На схеме — таблица, как у методов списков в теме 4. '
                    'В каждой строке: имя метода, что он делает и короткий пример для products_kcal. '
                    'Сверяйте код с таблицей: метод всегда через точку после имени словаря.'
                ),
            },
        ],
        'scheme_gallery': [
            {
                'file': 'Словари_методы.svg',
                'num': 1,
                'caption': 'Методы словаря: get, keys, items и добавление',
                'sections_after': [
                    {
                        'title': 'Как читать схему',
                        'body': (
                            'Слева — словарь products_kcal (ключ → значение). '
                            'Справа — методы и что они возвращают.\n\n'
                            '• get — «спросить» калории по имени.\n'
                            '• keys — все названия продуктов.\n'
                            '• items — пары (название, калории) для цикла for.\n'
                            '• запись [ключ] = число — добавить или изменить продукт.'
                        ),
                    },
                    {
                        'title': 'Метод или скобки []?',
                        'body': (
                            'products_kcal["яблоко"] — быстро, но если ключа нет, будет ошибка KeyError. '
                            'products_kcal.get("яблоко") — то же число, если ключ есть. '
                            'Если ключа нет — get вернёт None (или число по умолчанию, см. ниже).'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89}\n'
                            'print(products_kcal["яблоко"])   # 52\n'
                            'print(products_kcal.get("банан"))  # 89'
                        ),
                    },
                    {
                        'title': 'get(ключ) — безопасный доступ',
                        'body': (
                            'get читает значение и не «ломает» программу, если продукта нет в базе. '
                            'Без второго аргумента при отсутствии ключа вернётся None — '
                            'это значит «ничего не нашли».'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52}\n'
                            'print(products_kcal.get("яблоко"))   # 52\n'
                            'print(products_kcal.get("ананас"))   # None'
                        ),
                    },
                    {
                        'title': 'get(ключ, значение_по_умолчанию)',
                        'body': (
                            'Второй аргумент — запасной ответ, если ключа нет. '
                            'Удобно подставить 0 и потом проверить: если калории 0, '
                            'можно написать «продукт не найден».'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52}\n'
                            'kcal = products_kcal.get("ананас", 0)\n'
                            'print(kcal)  # 0\n'
                            'kcal = products_kcal.get("яблоко", 0)\n'
                            'print(kcal)  # 52'
                        ),
                    },
                    {
                        'title': 'keys() — все названия',
                        'body': (
                            'keys() возвращает все ключи словаря — названия продуктов. '
                            'Цикл for name in products_kcal уже перебирает ключи; '
                            'products_kcal.keys() делает то же явно. '
                            'Полезно, когда нужно подчеркнуть: «берём именно имена».'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89, "хлеб": 265}\n'
                            'for name in products_kcal.keys():\n'
                            '    print(name)\n'
                            '# яблоко, банан, хлеб — по одному на строку'
                        ),
                    },
                    {
                        'title': 'values() — все калорийности',
                        'body': (
                            'values() возвращает только числа — калорийность каждого продукта, без имён. '
                            'Для меню калькулятора values() редко нужен: там важны и имя, и число. '
                            'Но метод показывает: у словаря есть «левая колонка» (ключи) и «правая» (значения).'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89}\n'
                            'for kcal in products_kcal.values():\n'
                            '    print(kcal)\n'
                            '# 52, затем 89'
                        ),
                    },
                    {
                        'title': 'items() — пары для меню',
                        'body': (
                            'items() возвращает пары (ключ, значение). '
                            'В цикле for пишут две переменные сразу — так меню получается короче, '
                            'чем в теме 9, где калории брали отдельно: products_kcal[name].'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89, "хлеб": 265}\n'
                            'for name, kcal in products_kcal.items():\n'
                            '    print(name, "—", kcal, "ккал/100 г")'
                        ),
                    },
                    {
                        'title': 'show_menu() через items()',
                        'body': (
                            'В show_menu() из версии 1.9 замените цикл на items() — '
                            'сразу видны и название, и калории. '
                            'Нумерацию 1, 2, 3… можно сделать через переменную n, как в теме 9.'
                        ),
                        'code': (
                            'def show_menu():\n'
                            '    print("Меню:")\n'
                            '    n = 1\n'
                            '    for name, kcal in products_kcal.items():\n'
                            '        print(n, ".", name, "—", kcal, "ккал")\n'
                            '        n = n + 1'
                        ),
                    },
                    {
                        'title': 'Добавить продукт: словарь[ключ] = значение',
                        'body': (
                            'Новый продукт — новая пара в словаре. '
                            'Если ключ уже есть, число обновится. '
                            'Это не метод, а обычная запись — как переменной присваивают значение.'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89}\n'
                            'products_kcal["сыр"] = 350\n'
                            'print(products_kcal["сыр"])  # 350'
                        ),
                    },
                    {
                        'title': 'update() — несколько продуктов сразу',
                        'body': (
                            'update(другой_словарь) добавляет или обновляет сразу несколько пар. '
                            'Удобно, если есть маленький список новых продуктов в виде словаря.'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52}\n'
                            'products_kcal.update({"банан": 89, "хлеб": 265})\n'
                            'print(len(products_kcal))  # 3 — три продукта'
                        ),
                    },
                    {
                        'title': 'Оператор in — есть ли продукт в базе',
                        'body': (
                            'Перед products_kcal[name] можно проверить: if name in products_kcal. '
                            'in — не метод, но часто используется вместе с get. '
                            'Альтернатива: kcal = products_kcal.get(name) и проверка if kcal is None.'
                        ),
                        'code': (
                            'name = "банан"\n'
                            'if name in products_kcal:\n'
                            '    print(products_kcal[name])\n'
                            'else:\n'
                            '    print("Нет такого продукта")'
                        ),
                    },
                    {
                        'title': 'Расчёт порции с get',
                        'body': (
                            'Пользователь ввёл имя продукта. '
                            'Безопасный вариант: kcal = products_kcal.get(name). '
                            'Если kcal is None — продукт не найден, расчёт не делаем. '
                            'Или сразу: kcal = products_kcal.get(name, 0) и проверка if kcal == 0.'
                        ),
                        'code': (
                            'def calc_portion(kcal, grams):\n'
                            '    return kcal * grams / 100\n\n'
                            'name = "яблоко"\n'
                            'grams = 150\n'
                            'kcal = products_kcal.get(name)\n'
                            'if kcal is not None:\n'
                            '    print(calc_portion(kcal, grams))  # 78.0'
                        ),
                    },
                    {
                        'title': 'get и print — не путать',
                        'body': (
                            'get — метод словаря: products_kcal.get("яблоко"). '
                            'Точка обязательна. Нельзя писать get(products_kcal) или products_kcal.get["яблокo"]. '
                            'Скобки () — как у print() или append().'
                        ),
                        'code': (
                            '# Правильно:\n'
                            'products_kcal.get("яблоко")\n\n'
                            '# Ошибки:\n'
                            '# products_kcal.get["яблоко"]\n'
                            '# get("яблоко")'
                        ),
                    },
                    {
                        'title': 'Словарь dishes — рецепты блюд',
                        'body': (
                            'В демо при выборе блюда подставляется список ингредиентов. '
                            'В main.py — словарь dishes: ключ — название блюда, '
                            'значение — список продуктов из products_kcal. '
                            'В project_stage — три рецепта: фруктовый салат, борщ, омлет.'
                        ),
                        'code': (
                            'dishes = {\n'
                            '    "фруктовый салат": ["яблоко", "банан", "апельсин", "груша"],\n'
                            '    "борщ": ["говядина", "свёкла", "картофель", "капуста", "морковь", "лук", "масло подсолнечное"],\n'
                            '    "омлет": ["яйцо", "молоко", "масло сливочное"],\n'
                            '}\n'
                            'ingredients = dishes.get("фруктовый салат", [])\n'
                            'print(ingredients)  # список ингредиентов салата'
                        ),
                    },
                    {
                        'title': 'Цикл for — граммы по каждому ингредиенту',
                        'body': (
                            'После выбора блюда перебираем ингредиенты. '
                            'Для каждого — input() с граммами, как в демо, где у каждой строки свой вес. '
                            'Калории порции считает calc_portion, сумму копим в total_kcal.'
                        ),
                        'code': (
                            'total_kcal = 0\n'
                            'total_weight = 0\n'
                            'for ing in ingredients:\n'
                            '    grams = int(input("Граммы " + ing + ": "))\n'
                            '    kcal100 = products_kcal.get(ing, 0)\n'
                            '    portion = calc_portion(kcal100, grams)\n'
                            '    total_kcal = total_kcal + portion\n'
                            '    total_weight = total_weight + grams\n'
                            'print("Калорий в блюде:", total_kcal)\n'
                            'print("Вес блюда:", total_weight, "г")'
                        ),
                    },
                    {
                        'title': 'Ккал на 100 г блюда — как в демо',
                        'body': (
                            'В демо показывают итоговый вес и калорийность на 100 г готового блюда. '
                            'Формула: total_kcal × 100 / total_weight (если вес больше нуля).'
                        ),
                        'code': (
                            'if total_weight > 0:\n'
                            '    per100 = total_kcal * 100 / total_weight\n'
                            '    print("На 100 г:", round(per100, 1), "ккал")'
                        ),
                    },
                    {
                        'title': 'Версия 2.0 — Калькулятор блюда',
                        'body': (
                            'Оставьте products_kcal и calc_portion из версии 1.9. '
                            'Добавьте dishes с тремя блюдами (фруктовый салат, борщ, омлет) — '
                            'калории продуктов заданы в project_stage. '
                            'Покажите меню блюд, примите выбор, '
                            'в цикле for спросите граммы каждого ингредиента через get(). '
                            'Выведите калорий в блюде — как в HTML-демо на сайте курса.'
                        ),
                        'code': (
                            'products_kcal = {"яблоко": 52, "банан": 89, "апельсин": 47, "груша": 57}\n'
                            'dishes = {"фруктовый салат": ["яблоко", "банан", "апельсин", "груша"]}\n\n'
                            'def calc_portion(kcal, grams):\n'
                            '    return kcal * grams / 100\n\n'
                            'def show_dishes():\n'
                            '    n = 1\n'
                            '    for name in dishes:\n'
                            '        print(n, name)\n'
                            '        n += 1\n\n'
                            'show_dishes()\n'
                            'num = int(input("Номер блюда: "))\n'
                            'dish_name = list(dishes.keys())[num - 1]\n'
                            'for ing in dishes.get(dish_name, []):\n'
                            '    g = int(input("Граммы " + ing + ": "))\n'
                            '    # total_kcal += calc_portion(products_kcal.get(ing, 0), g)'
                        ),
                    },
                ],
            },
        ],
        'remember': [
            'products_kcal — база продуктов; dishes — блюдо → список ингредиентов.',
            'dishes.get("фруктовый салат") — список продуктов для блюда.',
            'get(ключ) — калории продукта без KeyError.',
            'for ing in ingredients: — ввод граммов по каждому продукту, как в демо.',
            'Сумма calc_portion по всем ингредиентам = калории блюда.',
            'Можно вывести вес блюда и ккал на 100 г — как в демо.',
        ],
        'mistakes': [
            'Считать только один ингредиент — нужен цикл for по всему списку dishes.get(...).',
            'Забыть int(input()) для граммов — input() возвращает строку.',
            'Искать калории блюда в dishes — калории лежат в products_kcal.get(ing).',
            'Путать dishes и products_kcal: в dishes — списки имён, не числа ккал.',
            'Не выводить итог блюда после цикла — пользователь должен увидеть сумму.',
        ],
        'tips': [
            'Откройте HTML-демо на сайте — логика та же, только ввод через input().',
            'Начните с одного блюда и трёх ингредиентов, потом добавьте второе блюдо.',
            'Проверьте в «Выполнить»: выбор блюда → граммы по каждой строке → итог.',
            'products_kcal.get(ing, 0) — если опечатка в названии, программа не упадёт.',
        ],
    },
    'tasks': [
        {
            'id': 470,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Что делает products_kcal.get("яблоко")?',
            'hint': 'get «спрашивает» значение по ключу.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Возвращает калорийность яблока (52), если ключ есть'},
                {'key': 'b', 'label': 'Удаляет яблоко из словаря'},
                {'key': 'c', 'label': 'Добавляет яблоко в словарь'},
            ],
            'correct': 'a',
        },
        {
            'id': 471,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Зачем нужен items() в show_menu()?',
            'hint': 'items отдаёт и имя, и калории за один проход.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'Чтобы в цикле for сразу получить название и калорийность'},
                {'key': 'b', 'label': 'Чтобы удалить все продукты из словаря'},
                {'key': 'c', 'label': 'Чтобы превратить словарь в список eaten'},
            ],
            'correct': 'a',
        },
        {
            'id': 472,
            'kind': 'quiz',
            'category': 'theory',
            'type': 'quiz',
            'text': 'Чем get("ананас", 0) лучше, чем ["ананас"], если ананаса нет в базе?',
            'hint': 'Без get программа может упасть с ошибкой.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'get вернёт 0 и программа не упадёт; [] вызовет KeyError'},
                {'key': 'b', 'label': 'get всегда возвращает 0, даже если продукт есть'},
                {'key': 'c', 'label': 'Разницы нет — это одно и то же'},
            ],
            'correct': 'a',
        },
        {
            'id': 473,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                'd = {"яблоко": 52, "банан": 89}\n'
                'print(d.get("банан"))\n'
                'print(d.get("хлеб"))\n'
                'print(d.get("хлеб", 0))\n'
                'Что выведет программа?'
            ),
            'hint': 'Нет ключа — None; с вторым аргументом — 0.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': '89\nNone\n0'},
                {'key': 'b', 'label': '89\n0\n0'},
                {'key': 'c', 'label': 'None\nNone\n0'},
            ],
            'correct': 'a',
        },
        {
            'id': 474,
            'kind': 'output_prediction',
            'category': 'trainer',
            'type': 'quiz',
            'text': (
                'd = {"яблоко": 52, "банан": 89}\n'
                'for name, kcal in d.items():\n'
                '    print(name, kcal)\n'
                'Что выведет программа?'
            ),
            'hint': 'items() даёт пары: название и число.',
            'xp': 10,
            'options': [
                {'key': 'a', 'label': 'яблоко 52\nбанан 89'},
                {'key': 'b', 'label': '52\n89'},
                {'key': 'c', 'label': 'яблоко\nбанан'},
            ],
            'correct': 'a',
        },
        {
            'id': 475,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52, "банан": 89}. '
                'Выведите products_kcal.get("яблоко") (одно число: 52).'
            ),
            'hint': 'print(products_kcal.get("яблоко"))',
            'xp': 12,
            'expected': '52',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "банан": 89}\n'
            ),
        },
        {
            'id': 476,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52}. '
                'Выведите products_kcal.get("банан", 0) — продукта нет, нужен запасной ответ (0).'
            ),
            'hint': 'get("банан", 0)',
            'xp': 12,
            'expected': '0',
            'starter_code': (
                'products_kcal = {"яблоко": 52}\n'
            ),
        },
        {
            'id': 477,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52, "банан": 89}. '
                'В цикле for name, kcal in products_kcal.items(): '
                'выведите две строки: «яблоко — 52» и «банан — 89».'
            ),
            'hint': 'print(name, "—", kcal)',
            'xp': 14,
            'expected': 'яблоко — 52\nбанан — 89',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "банан": 89}\n\n'
            ),
        },
        {
            'id': 478,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52, "банан": 89}. '
                'Добавьте продукт: products_kcal["сыр"] = 350. '
                'Выведите products_kcal.get("сыр") (350).'
            ),
            'hint': 'Сначала присвоение, потом get',
            'xp': 12,
            'expected': '350',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "банан": 89}\n'
            ),
        },
        {
            'id': 479,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52}. '
                'Добавьте через update({"банан": 89}). '
                'Выведите products_kcal.get("банан") (89).'
            ),
            'hint': 'products_kcal.update({"банан": 89})',
            'xp': 12,
            'expected': '89',
            'starter_code': (
                'products_kcal = {"яблоко": 52}\n'
            ),
        },
        {
            'id': 480,
            'kind': 'practice',
            'category': 'practice',
            'type': 'matching',
            'text': 'Сопоставьте метод и что он делает.',
            'hint': 'get — значение, keys — названия, items — пары.',
            'xp': 12,
            'left': [
                'products_kcal.get("яблоко", 0)',
                'products_kcal.keys()',
                'products_kcal.items()',
                'products_kcal["сыр"] = 350',
            ],
            'right': [
                'Все пары (название, калории) для цикла for',
                'Калории яблока или 0, если ключа нет',
                'Добавить или изменить продукт «сыр»',
                'Все названия продуктов в словаре',
            ],
            'correct_pairs': [1, 3, 0, 2],
        },
        {
            'id': 481,
            'kind': 'fix_error',
            'category': 'trainer',
            'type': 'code',
            'text': (
                'Исправьте вызов get: программа должна вывести 52. '
                'Сейчас скобки перепутаны.'
            ),
            'hint': 'get пишут с круглыми скобками: .get("яблоко")',
            'xp': 14,
            'expected': '52',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "банан": 89}\n'
                'print(products_kcal.get["яблоко"])\n'
            ),
        },
        {
            'id': 482,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52, "банан": 89}. '
                'Если "банан" in products_kcal — выведите «есть», иначе «нет». '
                'Должно вывести: есть'
            ),
            'hint': 'if "банан" in products_kcal: print("есть")',
            'xp': 12,
            'expected': 'есть',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "банан": 89}\n'
            ),
        },
        {
            'id': 483,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52}. '
                'def calc_portion(kcal, grams): return kcal * grams / 100\n'
                'name = "яблоко", grams = 100. '
                'kcal = products_kcal.get(name). '
                'Выведите calc_portion(kcal, grams) (52.0).'
            ),
            'hint': 'get(name) затем calc_portion',
            'xp': 14,
            'expected': '52.0',
            'starter_code': (
                'products_kcal = {"яблоко": 52}\n\n'
                'def calc_portion(kcal, grams):\n'
                '    return kcal * grams / 100\n\n'
                'name = "яблоко"\n'
                'grams = 100\n'
            ),
        },
        {
            'id': 484,
            'kind': 'code_input',
            'category': 'practice',
            'type': 'code',
            'text': (
                'products_kcal = {"яблоко": 52, "банан": 89, "хлеб": 265}. '
                'Выведите только названия — по одному на строку — '
                'через for name in products_kcal.keys(): (три строки: яблоко, банан, хлеб).'
            ),
            'hint': 'for name in products_kcal.keys(): print(name)',
            'xp': 12,
            'expected': 'яблоко\nбанан\nхлеб',
            'starter_code': (
                'products_kcal = {"яблоко": 52, "банан": 89, "хлеб": 265}\n'
            ),
        },
        STAGE_M2_10,
    ],
}
