# -*- coding: utf-8 -*-
"""
Шаблон файла темы. Скопируйте в topic_XX.py и подключите в __init__.py модуля.

Структура TOPIC:
  id, num, title, summary, theory, project_step, tasks[]
Задание: kind (авторский) + type (для сайта) — см. course_data/task_types.py
"""

from __future__ import annotations

from course_data.constants import DEFAULT_CODE_EDITOR_PLACEHOLDER
from course_data.project import project_step_for_topic

TOPIC: dict = {
    'id': 'm1-t99',
    'num': 99,
    'title': 'Тема 99. Название темы',
    'summary': 'Краткое описание для шапки.',
    'project_step': project_step_for_topic(99),
    'theory': {
        'intro': 'Вводный абзац.',
        'sections': [{'title': 'Блок', 'body': 'Текст.'}],
        'visual_blocks': [],
        'schemes': [],
        'remember': [],
        'mistakes': [],
        'tips': [],
    },
    'tasks': [
        {
            'id': 9001,
            'kind': 'code_input',
            'category': 'practice',
            'text': 'Текст задания.',
            'hint': 'Подсказка.',
            'xp': 10,
            'expected': 'ожидаемый вывод',
            'starter_code': DEFAULT_CODE_EDITOR_PLACEHOLDER,
        },
    ],
}
