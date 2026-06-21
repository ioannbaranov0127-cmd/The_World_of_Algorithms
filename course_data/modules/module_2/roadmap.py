# -*- coding: utf-8 -*-
"""Общая линия модуля 2: от версии 1.1 до калькулятора блюда как в HTML-демo."""

from __future__ import annotations

MODULE_2_DEMO_GOAL = (
    'К концу модуля main.py работает как HTML-демо на сайте: '
    'выбор блюда → список ингредиентов → граммы по каждому → калории блюда.'
)

ROADMAP_BY_VERSION: dict[str, str] = {
    '1.1': 'Учимся считать одну порцию и суммировать — формула из демo.',
    '1.2': 'Собираем каталог продуктов — это будущая база для рецептов.',
    '1.3': 'Выбираем продукт по номеру — как строка в таблице демo.',
    '1.4': 'Список append — зачаток списка ингредиентов блюда.',
    '1.5': 'Меню циклом for — как список продуктов на экране.',
    '1.6': 'Имя и калории в одной строке — удобнее для базы.',
    '1.7': 'Вывод в функциях — готовим show_dishes() и приветствие.',
    '1.8': 'calc_portion — та же формула, что в демo для каждой строки.',
    '1.9': 'products_kcal — словарь базы; в 2.0 добавим dishes.',
    '2.0': 'Финал: dishes + цикл по ингредиентам — полная копия логики демo.',
}

# --- Продукты по этапам (ккал на 100 г) ---

# Версии 1.1–1.5: простой фруктовый салат — знакомые продукты, лёгкий старт.
M2_FRUITS_1_1: list[tuple[str, int]] = [
    ('яблоко', 52),
    ('банан', 89),
    ('апельсин', 47),
]

M2_FRUITS_1_2: list[tuple[str, int]] = M2_FRUITS_1_1 + [
    ('груша', 57),
]

# Версии 1.6–1.8: те же фрукты во вложенном списке.
M2_FRUITS_NESTED: list[tuple[str, int]] = M2_FRUITS_1_2

# Версия 1.9–2.0: полная база для трёх простых блюд.
M2_PRODUCTS_KCAL: dict[str, int] = {
    # фруктовый салат
    'яблоко': 52,
    'банан': 89,
    'апельсин': 47,
    'груша': 57,
    # борщ
    'говядина': 250,
    'свёкла': 43,
    'картофель': 77,
    'капуста': 27,
    'морковь': 35,
    'лук': 41,
    'масло подсолнечное': 884,
    # омлет
    'яйцо': 157,
    'молоко': 52,
    'масло сливочное': 748,
}

M2_DISHES: dict[str, list[str]] = {
    'фруктовый салат': ['яблоко', 'банан', 'апельсин', 'груша'],
    'борщ': [
        'говядина',
        'свёкла',
        'картофель',
        'капуста',
        'морковь',
        'лук',
        'масло подсолнечное',
    ],
    'омлет': ['яйцо', 'молоко', 'масло сливочное'],
}


def format_products_kcal(products: list[tuple[str, int]]) -> str:
    """«яблоко (52 ккал), банан (89 ккал), …»"""
    return ', '.join(f'{name} ({kcal} ккал)' for name, kcal in products)


def format_products_menu(products: list[tuple[str, int]]) -> str:
    """«1 — яблоко (52), 2 — банан (89), …»"""
    return ', '.join(f'{i + 1} — {name} ({kcal})' for i, (name, kcal) in enumerate(products))


def products_names_kcals(products: list[tuple[str, int]]) -> tuple[list[str], list[int]]:
    names = [name for name, _ in products]
    kcals = [kcal for _, kcal in products]
    return names, kcals


def format_dict_literal(products: dict[str, int], indent: str = '    ') -> str:
    lines = [f'{indent}"{name}": {kcal},' for name, kcal in products.items()]
    return '\n'.join(lines)


def format_nested_products(products: list[tuple[str, int]], indent: str = '    ') -> str:
    lines = [f'{indent}["{name}", {kcal}],' for name, kcal in products]
    return '\n'.join(lines)


def format_dishes_literal(dishes: dict[str, list[str]], indent: str = '    ') -> str:
    lines = []
    for dish, ings in dishes.items():
        ing_str = ', '.join(f'"{x}"' for x in ings)
        lines.append(f'{indent}"{dish}": [{ing_str}],')
    return '\n'.join(lines)
