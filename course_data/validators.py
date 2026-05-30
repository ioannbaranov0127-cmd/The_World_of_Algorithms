# -*- coding: utf-8 -*-

from __future__ import annotations

from course_data.constants import DEFAULT_CODE_EDITOR_PLACEHOLDER


def topic_by_task_id(module_id: int, task_id: int) -> dict | None:
    from course_data.loader import LESSONS

    mod = LESSONS.get(module_id)
    if not mod:
        return None
    for topic in mod.get('topics') or []:
        for t in topic.get('tasks') or []:
            if t['id'] == task_id:
                return topic
    return None


def task_client_payload(task: dict) -> dict:
    ttype = task.get('type', 'code')
    base: dict = {
        'id': task['id'],
        'type': ttype,
        'text': task['text'],
        'hint': task.get('hint', ''),
        'xp': task.get('xp', 0),
    }
    if ttype == 'code':
        sc = task.get('starter_code')
        if sc is None or not str(sc).strip():
            base['starter_code'] = DEFAULT_CODE_EDITOR_PLACEHOLDER
        else:
            base['starter_code'] = sc
    elif ttype == 'quiz':
        base['options'] = task['options']
    elif ttype == 'ordering':
        base['items'] = list(task['items'])
    elif ttype == 'matching':
        base['left'] = list(task['left'])
        base['right'] = list(task['right'])
    elif ttype == 'fill_gaps':
        base['template'] = task['template']
        base['blank_count'] = len(task.get('answers') or [])
    return base


def validate_interactive_answer(task: dict, answer) -> bool:
    ttype = task.get('type', 'code')
    if ttype == 'code':
        return False
    if ttype == 'quiz':
        return answer == task.get('correct')
    if ttype == 'ordering':
        return answer == task.get('correct_order')
    if ttype == 'matching':
        exp = task.get('correct_pairs')
        if not isinstance(answer, list) or len(answer) != len(exp):
            return False
        return list(answer) == list(exp)
    if ttype == 'fill_gaps':
        exp = task.get('answers')
        if not isinstance(answer, list) or len(answer) != len(exp):
            return False
        return [str(x).strip() for x in answer] == [str(x).strip() for x in exp]
    return False
