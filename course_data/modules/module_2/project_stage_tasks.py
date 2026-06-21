# -*- coding: utf-8 -*-
"""Проектные этапы модуля 2: развитие «Калькулятор калорий» после версии 1.0."""

from __future__ import annotations

from course_data.modules.module_2.project import M2_VERSION_NAMES
from course_data.modules.module_2.roadmap import (
    MODULE_2_DEMO_GOAL,
    M2_DISHES,
    M2_FRUITS_1_1,
    M2_FRUITS_1_2,
    M2_FRUITS_NESTED,
    M2_PRODUCTS_KCAL,
    ROADMAP_BY_VERSION,
    format_dict_literal,
    format_dishes_literal,
    format_nested_products,
    format_products_kcal,
    format_products_menu,
    products_names_kcals,
)

_PROJECT_HEADER = (
    '# Калькулятор калорий — main.py\n'
    '# Дополняйте код из прошлых тем. Цель модуля — калькулятор блюда как в HTML-демо.\n\n'
)

# Stepik-подобные сценарии: stdin подставляет система (auto_stdin) по каталогу из кода ученика.
_RUN_EXIT = {
    'name': 'выход без порций',
    'auto_stdin': 'exit',
    'checks': [{'check': 'no_crash'}],
    'message_timeout': 'Программа зависла на вводе. Добавьте выход через 0 (или последний пункт меню).',
}

_RUN_ONE_PORTION = {
    'name': 'одна порция и выход',
    'auto_stdin': 'one_portion',
    'checks': [
        {'check': 'no_crash'},
        {
            'check': 'has_portion_or_total',
            'message': 'После порции должно появиться число калорий или общий итог.',
        },
        {
            'check': 'output_kcal_hint',
            'message': 'Покажите результат расчёта (число или слово «ккал»).',
        },
    ],
}

_RUN_ONE_WITH_TOTAL = {
    'name': 'итог за день',
    'auto_stdin': 'one_portion',
    'checks': [
        {'check': 'no_crash'},
        {'check': 'computed_total', 'message': 'Проверьте формулу: калории × граммы / 100.'},
        {
            'check': 'output_contains_any',
            'values': ['Всего', 'всего', 'Итого', 'итого', 'ккал', 'Ккал'],
            'message': 'После цикла покажите общий итог за день.',
        },
    ],
}

_RUN_TWO_PORTIONS = {
    'name': 'две порции',
    'auto_stdin': 'two_portions',
    'checks': [
        {'check': 'no_crash'},
        {
            'check': 'computed_total_min',
            'min': 10,
            'message': 'Две порции должны дать сумму калорий больше нуля.',
        },
        {
            'check': 'journal_hint',
            'message': 'Журнал: после двух порций покажите число записей (len) или итог.',
        },
    ],
}

_RUN_MENU = {
    'name': 'меню продуктов',
    'auto_stdin': 'one_portion',
    'checks': [
        {'check': 'no_crash'},
        {
            'check': 'menu_lines_min',
            'count': 2,
            'auto_count': True,
            'message': 'Меню должно показывать продукты с номерами (1, 2, 3…).',
        },
    ],
}

_RUN_DISH_CHECKS = [
    {'check': 'no_crash'},
    {
        'check': 'dish_total',
        'message': 'Сложите калории всех ингредиентов: ккал × граммы / 100.',
    },
    {
        'check': 'dish_weight',
        'message': 'Покажите общий вес блюда в граммах.',
    },
    {
        'check': 'dish_per100',
        'message': 'Покажите калорийность на 100 г готового блюда.',
    },
    {
        'check': 'dish_ingredients_flow',
        'message': 'По каждому ингредиенту спросите граммы — как в демо-калькуляторе.',
    },
    {
        'check': 'output_contains_any',
        'values': ['ккал', 'Ккал', 'калори', 'Калори', 'блюд', 'Блюд'],
        'message': 'Покажите результат расчёта блюда.',
    },
]

_RUN_DISH_SALAD = {
    'name': 'фруктовый салат',
    'mode': 'dish',
    'dish_index': 1,
    'auto_stdin': 'dish',
    'grams_per_ingredient': 100,
    'checks': _RUN_DISH_CHECKS,
    'message_timeout': (
        'Программа долго ждёт ввод. Проверьте: выбор блюда → '
        'цикл for по ингредиентам → input() для граммов каждого.'
    ),
}

_RUN_DISH_BORSCHT = {
    'name': 'борщ',
    'mode': 'dish',
    'dish_index': 2,
    'auto_stdin': 'dish',
    'grams_per_ingredient': 100,
    'checks': _RUN_DISH_CHECKS,
    'message_timeout': (
        'Программа долго ждёт ввод. Проверьте цикл for по ингредиентам борща.'
    ),
}

_RUN_DISH_OMELET = {
    'name': 'омлет',
    'mode': 'dish',
    'dish_index': 3,
    'auto_stdin': 'dish',
    'grams_per_ingredient': 100,
    'checks': _RUN_DISH_CHECKS,
    'message_timeout': (
        'Программа долго ждёт ввод. Проверьте цикл for по ингредиентам омлета.'
    ),
}


def _stage(
    task_id: int,
    version_label: str,
    body: str,
    tz: str,
    requirements: list[str],
    expected_result: str,
    hint: str,
    starter_code: str,
    project_tests: list[dict] | None = None,
    project_runs: list[dict] | None = None,
    *,
    xp: int = 20,
    roadmap_line: str | None = None,
) -> dict:
    ver_name = M2_VERSION_NAMES.get(version_label, '')
    title = (
        f'🚀 Версия {version_label} — {ver_name}'
        if ver_name
        else f'🚀 Версия {version_label}'
    )
    return {
        'id': task_id,
        'kind': 'project_stage',
        'category': 'project_stage',
        'type': 'code',
        'text': f'{title}: {body}',
        'hint': hint,
        'xp': xp,
        'expected': (
            'Проверка автоматическая — как на Stepik. Нажмите «Проверить»: '
            'система подставит тестовый ввод. «Выполнить» — для ручной проверки.'
        ),
        'starter_code': starter_code,
        'project_spec': {
            'tz': tz,
            'requirements': requirements,
            'expected_result': expected_result,
            'roadmap_line': roadmap_line or ROADMAP_BY_VERSION.get(version_label, ''),
            'module_goal': MODULE_2_DEMO_GOAL,
        },
        'project_tests': project_tests or [],
        'project_runs': project_runs or [],
    }


_F1 = M2_FRUITS_1_1
_F2 = M2_FRUITS_1_2
_F2_NAMES, _F2_KCALS = products_names_kcals(_F2)
_F1_MENU = format_products_menu(_F1)
_F2_KCAL_TEXT = format_products_kcal(_F2)
_F_NESTED = format_nested_products(M2_FRUITS_NESTED)
_PRODUCTS_KCAL_TEXT = format_products_kcal(list(M2_PRODUCTS_KCAL.items()))
_PRODUCTS_LITERAL = format_dict_literal(M2_PRODUCTS_KCAL)
_DISHES_LITERAL = format_dishes_literal(M2_DISHES)


STAGE_M2_01 = _stage(
    310,
    '1.1',
    (
        'соберите в main.py рабочий калькулятор на продуктах фруктового салата: '
        f'{format_products_kcal(_F1)}. '
        'Приветствие, цикл while, выбор по номеру через if / elif, '
        'граммы, формула ккал × г / 100, итог total и выход через 0. '
        'Это первый шаг к HTML-демo: там та же формула для каждой строки ингредиента.'
    ),
    'Первый шаг к демo-калькулятору блюда: считаем порции фруктов по формуле из демo.',
    [
        f'Меню: {_F1_MENU}, 0 — выход',
        'Перед циклом: приветствие и total = 0',
        'В while: ввод номера и граммов, if / elif с калорийностью из списка выше',
        'Формула: граммы × ккал / 100; выход через 0 и итог после цикла',
    ],
    'Калькулятор считает порции фруктов и показывает общий итог — как формула в демo.',
    (
        'if num == 1: kcal_per_100 = 52; product = "яблоко" '
        'elif num == 2: kcal_per_100 = 89; product = "банан" '
        'elif num == 3: kcal_per_100 = 47; product = "апельсин"'
    ),
    _PROJECT_HEADER
    + 'print("Калькулятор калорий — фруктовый салат")\n'
    + f'print("{_F1_MENU}, 0 — выход")\n\n'
    + 'total = 0\n\n'
    + 'while True:\n'
    + '    num = int(input("Номер продукта: "))\n'
    + '    if num == 0:\n'
    + '        break\n'
    + '    grams = int(input("Граммы: "))\n'
    + '    # if num == 1: kcal_per_100 = 52; product = "яблоко"\n'
    + '    # elif num == 2: kcal_per_100 = 89; product = "банан"\n'
    + '    # elif num == 3: kcal_per_100 = 47; product = "апельсин"\n'
    + '    # else: continue\n'
    + '    # calories = grams * kcal_per_100 / 100\n'
    + '    # total = total + calories\n\n'
    + 'print("Всего:", total, "ккал")\n',
    project_runs=[_RUN_EXIT, _RUN_ONE_WITH_TOTAL],
)


STAGE_M2_02 = _stage(
    329,
    '1.2',
    (
        'добавьте списки products и kcal_per_100 — будущая база для рецептов в демo. '
        f'Запрограммируйте фрукты для салата: {_F2_KCAL_TEXT}. '
        'Покажите каталог на экране. Алгоритм while из версии 1.1 сохраните.'
    ),
    'Каталог продуктов в списках — заготовка под базу products_kcal из HTML-демo.',
    [
        f'products = {_F2_NAMES!r}',
        f'kcal_per_100 = {_F2_KCALS!r} — порядок совпадает с products',
        'Каталог продуктов виден на экране',
        'Цикл while, break и расчёт порции — как в 1.1',
    ],
    'Фрукты салата лежат в списках — калькулятор по-прежнему считает порции.',
    'products[i] и kcal_per_100[i] — один индекс, один продукт из каталога фруктов.',
    (
        '# Версия 1.2: каталог фруктов для салата\n'
        f'products = {_F2_NAMES!r}\n'
        f'kcal_per_100 = {_F2_KCALS!r}\n\n'
        '# print(...) — показать каталог\n'
        '# ... while, break, расчёт из 1.1 ...\n'
    ),
    project_runs=[_RUN_EXIT, _RUN_ONE_PORTION, _RUN_MENU],
)


STAGE_M2_03 = _stage(
    340,
    '1.3',
    (
        'пользователь вводит номер из меню. Переведите его в индекс списка '
        'и возьмите название и калории из products[i] и kcal_per_100[i]. '
        f'Каталог — те же фрукты: {_F2_KCAL_TEXT}. '
        'Посчитайте калории порции. Так в демо выбирают строку в таблице продуктов.'
    ),
    'Номер меню → индекс списка — как выбор продукта по строке в HTML-демо.',
    [
        f'products = {_F2_NAMES!r}, kcal_per_100 = {_F2_KCALS!r}',
        'Номер меню → индекс (num - 1)',
        'name = products[i]; kcal = kcal_per_100[i]',
        'Цикл while с break и формула порции',
    ],
    'Фрукт выбирается по номеру из списка — без длинного if / elif.',
    'i = num - 1; portion = grams * kcal_per_100[i] / 100; total += portion',
    (
        '# Версия 1.3: выбор по номеру из списка\n'
        f'products = {_F2_NAMES!r}\n'
        f'kcal_per_100 = {_F2_KCALS!r}\n\n'
        + f'print("{format_products_menu(_F2)}, 0 — выход")\n'
        + 'total = 0\n\n'
        'while True:\n'
        '    num = int(input("Номер продукта: "))\n'
        '    if num == 0:\n'
        '        break\n'
        '    grams = int(input("Граммы: "))\n'
        '    # i = num - 1\n'
        '    # name = products[i]\n'
        '    # kcal = kcal_per_100[i]\n'
        '    # portion = grams * kcal / 100\n'
        '    # total = total + portion\n\n'
        'print("Всего:", total, "ккал")\n'
    ),
    project_runs=[_RUN_EXIT, _RUN_ONE_PORTION],
)


STAGE_M2_04 = _stage(
    360,
    '1.4',
    (
        'заведите список eaten = [] — тренировка перед списком ингредиентов блюда в демo. '
        f'Каталог фруктов: {_F2_KCAL_TEXT}. '
        'После каждой порции добавляйте продукт через append. '
        'Покажите len(eaten) — сколько продуктов уже «в списке», как ингредиентов в рецепте.'
    ),
    'Список append — зачаток списка ингредиентов: в демo блюдо = несколько продуктов подряд.',
    [
        f'products = {_F2_NAMES!r}, kcal_per_100 = {_F2_KCALS!r}',
        'Пустой список eaten в начале программы',
        'eaten.append(name) после успешной порции',
        'len(eaten) показывает число записей',
        'Выбор по индексу и расчёт порции из 1.3 сохранены',
    ],
    'Журнал порций фруктов — тренировка перед списком ингредиентов блюда в версии 2.0.',
    'eaten.append(name); print("Записей:", len(eaten)) — как счётчик строк в рецепте.',
    (
        '# Версия 1.4: список «ингредиентов» за день\n'
        f'products = {_F2_NAMES!r}\n'
        f'kcal_per_100 = {_F2_KCALS!r}\n'
        'eaten = []\n\n'
        '# while True: ... после расчёта:\n'
        '# eaten.append(name)\n'
        '# print("Записей:", len(eaten))\n'
    ),
    project_runs=[_RUN_EXIT, _RUN_ONE_PORTION, _RUN_TWO_PORTIONS],
)


STAGE_M2_05 = _stage(
    373,
    '1.5',
    (
        'оформите вывод меню функцией show_menu(): цикл for по products — '
        f'номер и название каждого фрукта ({_F2_KCAL_TEXT}). '
        'Как список продуктов на экране в HTML-демо. Журнал eaten и расчёт порции сохраните.'
    ),
    'Меню циклом for — как список продуктов в HTML-демо, без копипасты print().',
    [
        'Функция show_menu() с циклом for',
        f'Видны номер и название каждого фрукта из {_F2_NAMES!r}',
        f'products = {_F2_NAMES!r}, kcal_per_100 = {_F2_KCALS!r}',
        'eaten, while и расчёт порции — как в 1.4',
    ],
    'Каталог фруктов выводится одним циклом for — заготовка под show_dishes().',
    'def show_menu(): for i in range(len(products)): print(i + 1, products[i])',
    (
        '# Версия 1.5: меню циклом for\n'
        f'products = {_F2_NAMES!r}\n'
        f'kcal_per_100 = {_F2_KCALS!r}\n'
        'eaten = []\n\n'
        'def show_menu():\n'
        '    for i in range(len(products)):\n'
        '        print(i + 1, products[i])\n'
        '    print("0 — выход")\n\n'
        '# while True:\n'
        '#     show_menu()\n'
        '#     num = int(input("Номер продукта: "))\n'
        '#     ...\n'
    ),
    project_runs=[_RUN_EXIT, _RUN_ONE_PORTION, _RUN_MENU],
)


STAGE_M2_06 = _stage(
    399,
    '1.6',
    (
        'замените два списка одним products — каждый элемент [название, калории]. '
        f'Запрограммируйте фрукты салата: {_F2_KCAL_TEXT}. '
        'В меню и расчёте: products[i][0] и products[i][1]. '
        'Компактная база — как одна строка таблицы в демо.'
    ),
    'Имя и калории в одной строке списка — удобнее для каталога фруктов.',
    [
        f'products — вложенные списки [[имя, кал], …]: {_F2_KCAL_TEXT}',
        'Обращение через products[i][0] и products[i][1]',
        'Меню через for в show_menu()',
        'eaten и while сохранены',
    ],
    'Данные продукта в одной «строчке» — проще не перепутать имя и калории.',
    'products = [["яблоко", 52], ["банан", 89], ...]; kcal = products[i][1]',
    (
        '# Версия 1.6: фрукты салата во вложенном списке\n'
        'products = [\n'
        f'{_F_NESTED}\n'
        ']\n'
        'eaten = []\n\n'
        '# for i in range(len(products)):\n'
        '#     print(i + 1, products[i][0])\n'
        '# kcal = products[i][1]\n'
    ),
    project_runs=[_RUN_EXIT, _RUN_ONE_PORTION, _RUN_MENU, _RUN_TWO_PORTIONS],
)


STAGE_M2_07 = _stage(
    419,
    '1.7',
    (
        'вынесите вывод в функции show_welcome() и show_menu() — '
        'минимум две def с вызовами из программы. '
        'show_menu() — цикл for по products. Заготовка под show_dishes() в демо. '
        f'Каталог фруктов: {_F2_KCAL_TEXT}.'
    ),
    'Вывод в функциях — готовим show_dishes() и приветствие, как в HTML-демо.',
    [
        'def show_welcome() — приветствие калькулятора',
        'def show_menu() — for по products с номерами',
        f'products — фрукты: {_F2_KCAL_TEXT}',
        'Обе функции вызываются со скобками ()',
        'Расчёт порции и products сохранены',
    ],
    'Меню и приветствие живут в функциях — шаг к show_dishes() в версии 2.0.',
    'def show_welcome(): print("Калькулятор калорий"); show_welcome(); show_menu()',
    (
        '# Версия 1.7: вывод в функциях\n'
        'products = [\n'
        f'{_F_NESTED}\n'
        ']\n'
        'eaten = []\n\n'
        'def show_welcome():\n'
        '    print("Калькулятор калорий")\n'
        '    print("Готовим базу к калькулятору блюда из демо")\n\n'
        'def show_menu():\n'
        '    for i in range(len(products)):\n'
        '        print(i + 1, products[i][0])\n'
        '    print("0 — выход")\n\n'
        'show_welcome()\n'
        '# while True: show_menu(); ...\n'
    ),
    project_runs=[_RUN_EXIT, _RUN_ONE_PORTION, _RUN_MENU],
)


STAGE_M2_08 = _stage(
    439,
    '1.8',
    (
        'сделайте функцию calc_portion(kcal_per_100, grams) с return — '
        'та же формула, что для каждой строки ингредиента в HTML-демо. '
        f'Каталог фруктов: {_F2_KCAL_TEXT}. '
        'В цикле while вызывайте её и добавляйте результат к total.'
    ),
    'calc_portion — формула демо в отдельной функции: ккал × граммы / 100.',
    [
        'def calc_portion(kcal_per_100, grams) с return',
        f'products — фрукты: {_F2_KCAL_TEXT}',
        'В while: total += calc_portion(...)',
        'show_welcome() и show_menu() из 1.7 сохранены',
    ],
    'Калории порции считает calc_portion — та же математика, что в HTML-демо.',
    'def calc_portion(kcal, grams): return kcal * grams / 100',
    (
        '# Версия 1.8: calc_portion — формула из демо\n'
        'products = [\n'
        f'{_F_NESTED}\n'
        ']\n'
        'total = 0\n\n'
        'def calc_portion(kcal_per_100, grams):\n'
        '    return kcal_per_100 * grams / 100\n\n'
        'def show_welcome():\n'
        '    print("Калькулятор калорий")\n\n'
        'def show_menu():\n'
        '    for i in range(len(products)):\n'
        '        print(i + 1, products[i][0])\n'
        '    print("0 — выход")\n\n'
        '# while: portion = calc_portion(products[i][1], grams); total += portion\n'
    ),
    project_runs=[_RUN_EXIT, _RUN_ONE_WITH_TOTAL, _RUN_TWO_PORTIONS, _RUN_MENU],
)


STAGE_M2_09 = _stage(
    459,
    '1.9',
    (
        'замените список products на словарь products_kcal — '
        f'полная база для трёх блюд (фруктовый салат, борщ, омлет): {_PRODUCTS_KCAL_TEXT}. '
        'Меню — for по словарю. В 2.0 добавим dishes с рецептами.'
    ),
    'products_kcal — словарь базы продуктов; в 2.0 добавим dishes для рецептов.',
    [
        f'products_kcal — все продукты с ккал на 100 г: {_PRODUCTS_KCAL_TEXT}',
        'Калории: products_kcal[name] и calc_portion',
        'Меню через for name in products_kcal',
        'calc_portion, total и show_menu() сохранены',
    ],
    'База продуктов в словаре — готова к dishes в версии 2.0.',
    'products_kcal = {"яблоко": 52, "банан": 89, ...}; kcal = products_kcal[name]',
    (
        '# Версия 1.9: база products_kcal (фрукты, борщ, омлет)\n'
        'products_kcal = {\n'
        f'{_PRODUCTS_LITERAL}\n'
        '}\n'
        'total = 0\n\n'
        'def calc_portion(kcal_per_100, grams):\n'
        '    return kcal_per_100 * grams / 100\n\n'
        'def show_menu():\n'
        '    n = 1\n'
        '    for name in products_kcal:\n'
        '        print(n, name)\n'
        '        n += 1\n'
        '    print("0 — выход")\n\n'
        '# while: kcal = products_kcal[name]; total += calc_portion(kcal, grams)\n'
    ),
    project_runs=[_RUN_EXIT, _RUN_ONE_WITH_TOTAL, _RUN_MENU, _RUN_TWO_PORTIONS],
)


STAGE_M2_10 = _stage(
    485,
    '2.0',
    (
        'соберите калькулятор блюда, как в HTML-демо: products_kcal, '
        'dishes (блюдо → список ингредиентов), show_dishes(), '
        'выбор блюда, цикл for по ингредиентам, input() с граммами, '
        'calc_portion() и products_kcal.get(). '
        'Запрограммируйте три блюда: фруктовый салат (яблоко, банан, апельсин, груша), '
        'борщ (говядина, свёкла, картофель, капуста, морковь, лук, масло подсолнечное), '
        'омлет (яйцо, молоко, масло сливочное) — калории из products_kcal версии 1.9. '
        'В конце — калорий в блюде, вес блюда и ккал на 100 г.'
    ),
    'Финал модуля 2 — полная копия логики HTML-демо: блюдо → ингредиенты → граммы → итог.',
    [
        f'products_kcal — база из 1.9: {_PRODUCTS_KCAL_TEXT}',
        'dishes — три рецепта: «фруктовый салат», «борщ», «омлет» (ингредиенты как в задании)',
        'show_dishes() — меню блюд; выбор по номеру',
        'for по ингредиентам: input("Граммы …") → calc_portion → сумма',
        'Итог: калорий в блюде, вес блюда, ккал на 100 г',
        'products_kcal.get(ing, 0) — безопасно',
    ],
    'Калькулятор считает любое из трёх блюд — как HTML-демо на сайте курса.',
    (
        'dishes["фруктовый салат"] → ["яблоко", "банан", ...]. '
        'for ing in ingredients: total_kcal += calc_portion(products_kcal.get(ing, 0), grams)'
    ),
    (
        '# Версия 2.0: калькулятор блюда (как в HTML-демо)\n'
        'products_kcal = {\n'
        f'{_PRODUCTS_LITERAL}\n'
        '}\n\n'
        'dishes = {\n'
        f'{_DISHES_LITERAL}\n'
        '}\n\n'
        'def calc_portion(kcal_per_100, grams):\n'
        '    return kcal_per_100 * grams / 100\n\n'
        'def show_dishes():\n'
        '    n = 1\n'
        '    for name in dishes:\n'
        '        print(n, name)\n'
        '        n += 1\n\n'
        'print("Калькулятор калорийности блюда")\n'
        'show_dishes()\n'
        'num = int(input("Номер блюда: "))\n'
        'dish_name = list(dishes.keys())[num - 1]\n'
        'ingredients = dishes.get(dish_name, [])\n'
        'total_kcal = 0\n'
        'total_weight = 0\n'
        'print("Блюдо:", dish_name)\n'
        'for ing in ingredients:\n'
        '    grams = int(input("Граммы " + ing + ": "))\n'
        '    kcal100 = products_kcal.get(ing, 0)\n'
        '    portion = calc_portion(kcal100, grams)\n'
        '    total_kcal = total_kcal + portion\n'
        '    total_weight = total_weight + grams\n'
        'print("Калорий в блюде:", total_kcal)\n'
        'print("Вес блюда:", total_weight, "г")\n'
        'if total_weight > 0:\n'
        '    per100 = total_kcal * 100 / total_weight\n'
        '    print("На 100 г:", round(per100, 1), "ккал")\n'
    ),
    project_runs=[_RUN_DISH_SALAD, _RUN_DISH_BORSCHT, _RUN_DISH_OMELET],
)
