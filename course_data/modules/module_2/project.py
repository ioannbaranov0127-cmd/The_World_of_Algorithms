# -*- coding: utf-8 -*-
"""Шаги проекта для тем модуля 2 — путь к калькулятору блюда как в HTML-демо."""

from __future__ import annotations

from course_data.project import PROJECT_NAME

# Говорящие названия: что умеет программа после темы (номер версии — как раньше).
M2_VERSION_NAMES: dict[str, str] = {
    '1.1': 'Старт: формула и цикл',
    '1.2': 'Каталог в списках',
    '1.3': 'Выбор по номеру меню',
    '1.4': 'Список ингредиентов',
    '1.5': 'Меню циклом for',
    '1.6': 'Имя и калории вместе',
    '1.7': 'Вывод в функциях',
    '1.8': 'Функция calc_portion',
    '1.9': 'База products_kcal',
    '2.0': 'Блюдо как в демо',
}

MODULE_2_PROJECT: dict[int, dict] = {
    1: {
        'version': '1.1',
        'name': M2_VERSION_NAMES['1.1'],
        'goal': 'Восстановить рабочий цикл: меню, порция, формула ккал × г / 100, итог.',
        'milestone': 'Одна и несколько порций подряд — основа формулы из демо.',
        'feature': M2_VERSION_NAMES['1.1'],
    },
    2: {
        'version': '1.2',
        'name': M2_VERSION_NAMES['1.2'],
        'goal': 'Хранить продукты в двух списках — будущая база для рецептов блюд.',
        'milestone': 'Каталог из 3+ продуктов (фруктовый салат: яблоко 52, банан 89, апельсин 47…).',
        'feature': M2_VERSION_NAMES['1.2'],
    },
    3: {
        'version': '1.3',
        'name': M2_VERSION_NAMES['1.3'],
        'goal': 'Выбирать продукт по номеру меню — как строка в таблице демо.',
        'milestone': 'products[i] и kcal_per_100[i] — один индекс, один продукт.',
        'feature': M2_VERSION_NAMES['1.3'],
    },
    4: {
        'version': '1.4',
        'name': M2_VERSION_NAMES['1.4'],
        'goal': 'Вести список append — тренировка перед списком ингредиентов блюда.',
        'milestone': 'eaten.append(name) и len() — «сколько продуктов уже в списке».',
        'feature': M2_VERSION_NAMES['1.4'],
    },
    5: {
        'version': '1.5',
        'name': M2_VERSION_NAMES['1.5'],
        'goal': 'Показывать каталог одним циклом for — без копипасты print.',
        'milestone': 'Меню с номерами — как список продуктов в демо.',
        'feature': M2_VERSION_NAMES['1.5'],
    },
    6: {
        'version': '1.6',
        'name': M2_VERSION_NAMES['1.6'],
        'goal': 'Хранить [название, калории] в одной строке списка.',
        'milestone': 'products[i][0] и [1] — компактная база продуктов.',
        'feature': M2_VERSION_NAMES['1.6'],
    },
    7: {
        'version': '1.7',
        'name': M2_VERSION_NAMES['1.7'],
        'goal': 'Оформить show_menu() и приветствие функциями — заготовка под show_dishes().',
        'milestone': 'Минимум две def с вызовами из main.',
        'feature': M2_VERSION_NAMES['1.7'],
    },
    8: {
        'version': '1.8',
        'name': M2_VERSION_NAMES['1.8'],
        'goal': 'Вынести формулу демо в calc_portion(kcal, grams) с return.',
        'milestone': 'Та же математика, что для каждой строки ингредиента в демо.',
        'feature': M2_VERSION_NAMES['1.8'],
    },
    9: {
        'version': '1.9',
        'name': M2_VERSION_NAMES['1.9'],
        'goal': 'Перенести базу в products_kcal — словарь «продукт → ккал на 100 г».',
        'milestone': 'База products_kcal для фруктов, борща и омлета; в теме 10 — dishes.',
        'feature': M2_VERSION_NAMES['1.9'],
    },
    10: {
        'version': '2.0',
        'name': M2_VERSION_NAMES['2.0'],
        'goal': 'Собрать калькулятор блюда: dishes, выбор рецепта, граммы по ингредиентам, итог.',
        'milestone': 'Три блюда в консоли: фруктовый салат, борщ, омлет → ккал блюда.',
        'feature': M2_VERSION_NAMES['2.0'],
    },
}


def project_step_for_module_2(num: int) -> dict:
    row = MODULE_2_PROJECT.get(num, {})
    return {
        'project': PROJECT_NAME,
        'version': row.get('version', ''),
        'name': row.get('name', ''),
        'goal': row.get('goal', ''),
        'milestone': row.get('milestone', ''),
        'feature': row.get('feature', ''),
        'continues_from': '1.0',
    }
