# -*- coding: utf-8 -*-
"""
Типы заданий: канонические (для UI) и авторские (для хранения контента).

Канонические type — те, что уже поддерживает сайт:
  code, quiz, ordering, matching, fill_gaps

Авторские kind/category маппятся на канонические без изменения интерфейса.
"""

# kind/category → runtime type для проверки и рендера
_KIND_TO_TYPE: dict[str, str] = {
    'theory': 'quiz',
    'code_input': 'code',
    'code': 'code',
    'quiz': 'quiz',
    'output_prediction': 'quiz',
    'fix_error': 'code',
    'drag_order': 'ordering',
    'ordering': 'ordering',
    'matching': 'matching',
    'fill_gaps': 'fill_gaps',
    'project_step': 'code',
    'project_stage': 'code',
    'practice': 'code',
    'warmup': 'code',
    'trainer': 'quiz',
}


def normalize_task(task: dict) -> dict:
    """Возвращает копию задания с полем type для движка сайта."""
    row = dict(task)
    kind = row.pop('kind', None) or row.pop('category', None)
    if kind and kind in _KIND_TO_TYPE:
        row.setdefault('type', _KIND_TO_TYPE[kind])
        row['kind'] = kind
    elif 'type' not in row:
        row['type'] = 'code'
    else:
        row.setdefault('kind', row['type'])
    return row
