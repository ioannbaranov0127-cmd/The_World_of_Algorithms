# -*- coding: utf-8 -*-
"""Заглушки тем модуля 2: развитие калькулятора после версии 1.0."""

from __future__ import annotations

from course_data.modules.module_2.project import M2_VERSION_NAMES, project_step_for_module_2


def _quiz(task_id: int, text: str, correct_label: str, wrong_label: str) -> dict:
    return {
        'id': task_id,
        'kind': 'quiz',
        'category': 'theory',
        'type': 'quiz',
        'text': text,
        'hint': 'Выберите вариант, который соответствует теме.',
        'xp': 10,
        'options': [
            {'key': 'a', 'label': correct_label},
            {'key': 'b', 'label': wrong_label},
        ],
        'correct': 'a',
    }


def _project_task(task_id: int, text: str, starter_code: str = '# Заглушка практики\n') -> dict:
    return {
        'id': task_id,
        'kind': 'project_step',
        'category': 'project_step',
        'type': 'code',
        'text': text,
        'hint': 'Это задание-заглушка: позже здесь появится полноценная проверка версии.',
        'xp': 10,
        'expected': '',
        'starter_code': starter_code,
    }


def _topic_base_id(num: int) -> int:
    return 58 + num * 2


def _topic(num: int, title: str, version_key: str, summary: str, theory: str, practice: str) -> dict:
    version = f'Версия {version_key} — {M2_VERSION_NAMES.get(version_key, "")}'
    base_id = _topic_base_id(num)
    return {
        'id': f'm2-t{num}',
        'num': num,
        'title': f'Тема {num}. {title}',
        'summary': f'{version_key}. {summary}',
        'project_step': project_step_for_module_2(num),
        'theory': {
            'intro': theory,
            'sections': [
                {'title': version, 'body': summary, 'code': ''},
                {'title': 'Практическая работа', 'body': practice, 'code': ''},
            ],
            'visual_blocks': [
                {'title': 'Версия калькулятора', 'body': f'{version}: {practice}'},
            ],
            'schemes': [],
            'remember': [
                'Каждая тема — шаг к калькулятору блюда как в HTML-демо.',
                'Продукты и блюда задаются в project_stage: фрукты → салат, борщ, омлет к версии 2.0.',
            ],
            'mistakes': [
                'Смешивать новую тему с несколькими будущими улучшениями сразу.',
            ],
            'tips': [
                'Откройте HTML-демо на сайте и сравните с main.py после project_stage.',
            ],
        },
        'tasks': [
            _quiz(
                base_id,
                f'Что добавляет версия «{version_key}»?',
                practice,
                'Новый отдельный проект, не связанный с калькулятором.',
            ),
            _project_task(base_id + 1, practice),
        ],
    }


TOPICS: tuple[dict, ...] = (
    _topic(
        1,
        'Повторение ключевых конструкций. Запуск проекта',
        '1.1',
        'Формула ккал × г / 100 в цикле while — как в демо для одной строки.',
        'Восстанавливаем алгоритм на фруктах салата (яблоко 52, банан 89, апельсин 47).',
        'Собрать while с меню фруктов, формулой и итогом total.',
    ),
    _topic(
        2,
        'Списки',
        '1.2',
        'Каталог фруктов в двух списках — база под рецепты.',
        'Списки products и kcal_per_100 — заготовка под products_kcal из демо.',
        'Перенести фрукты (яблоко, банан, апельсин, груша) в списки и показать каталог.',
    ),
    _topic(
        3,
        'Индексы списков',
        '1.3',
        'Выбор продукта по номеру — как строка в таблице демо.',
        'Индекс связывает название и калории: products[i] и kcal_per_100[i].',
        'Брать продукт по номеру меню и считать порцию.',
    ),
    _topic(
        4,
        'Методы списков (append, remove, len)',
        '1.4',
        'Список append — тренировка перед списком ингредиентов блюда.',
        'eaten.append(name) — зачаток списка продуктов в рецепте из демо.',
        'Вести список eaten, append после порции, len() для числа записей.',
    ),
    _topic(
        5,
        'Цикл for',
        '1.5',
        'Меню циклом for — как список продуктов на экране в демо.',
        'for по products — без копипасты print; в 2.0 так же выведете меню блюд.',
        'Показать каталог продуктов через цикл for.',
    ),
    _topic(
        6,
        'Вложенные списки',
        '1.6',
        'Продукт одной строкой [имя, калории] — компактная база.',
        'Вложенный список — шаг к словарю products_kcal.',
        'Хранить продукты как [[имя, кал], …] и брать [0] и [1].',
    ),
    _topic(
        7,
        'Функции',
        '1.7',
        'show_menu и приветствие в def — заготовка под show_dishes().',
        'Функции вывода — репетиция перед финальным меню блюд.',
        'Вынести меню и приветствие в функции def.',
    ),
    _topic(
        8,
        'Функции с параметрами и return',
        '1.8',
        'calc_portion — та же формула, что для каждого ингредиента в демо.',
        'return kcal * grams / 100 — в 2.0 сложите несколько вызовов в итог блюда.',
        'Создать calc_portion с параметрами и return.',
    ),
    _topic(
        9,
        'Словари',
        '1.9',
        'products_kcal — база для салата, борща и омлета, как в HTML-демо.',
        'Словарь «продукт → ккал»; в теме 10 добавите dishes с тремя рецептами.',
        'Перенести базу в products_kcal и меню через for.',
    ),
    _topic(
        10,
        'Методы словарей',
        '2.0',
        'Финал: dishes, выбор блюда, граммы по ингредиентам — как демо.',
        'get() для калорий, dishes.get() для списка ингредиентов, цикл for по рецепту.',
        'Собрать калькулятор блюда: фруктовый салат, борщ или омлет → итог ккал.',
    ),
)
