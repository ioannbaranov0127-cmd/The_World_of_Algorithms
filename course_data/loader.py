# -*- coding: utf-8 -*-
"""Сборка MODULES / LESSONS / индексов заданий."""

from __future__ import annotations

from course_data.achievements import ACHIEVEMENTS
from course_data.constants import COURSE, MODULE_IDS, XP_PER_LEVEL
from course_data.modules.module_1 import get_all_topics as get_module_1_topics
from course_data.modules.module_2 import get_all_topics as get_module_2_topics
from course_data.registry import flatten_module_tasks


def _module_1() -> dict:
    topics = get_module_1_topics()
    published = sum(1 for t in topics if not t.get('draft'))
    total = len(topics)
    return {
        'id': 1,
        'title': 'Основы программирования на Python',
        'icon': '🍽️',
        'icon_file': 'Иконка_модуль_1.svg',
        'description': (
            f'Курс «{COURSE["title"]}»: проект «{COURSE["project_name"]}» '
            f'растёт от темы к теме. Опубликовано тем: {published} из {total}.'
        ),
        'topics': topics,
    }


def _module_2() -> dict:
    topics = get_module_2_topics()
    return {
        'id': 2,
        'title': 'Решение задач и развитие проекта',
        'icon': '📋',
        'icon_file': 'Иконка_модуль_2_1.svg',
        'description': (
            f'Развитие «{COURSE["project_name"]}» после версии 1.0: for, списки, словари '
            f'и функции для версии 2.0.'
        ),
        'topics': topics,
    }


MODULES: dict[int, dict] = {
    1: _module_1(),
    2: _module_2(),
}

LESSONS: dict[int, dict] = {}
for _mid, _mod in MODULES.items():
    LESSONS[_mid] = {**_mod, 'tasks': flatten_module_tasks(_mod)}

TOTAL_TASKS_COUNT = sum(len(LESSONS[m]['tasks']) for m in LESSONS if not LESSONS[m].get('stub'))

TASK_BY_ID: dict[int, dict] = {}
for _mod in LESSONS.values():
    for _t in _mod['tasks']:
        TASK_BY_ID[_t['id']] = _t
