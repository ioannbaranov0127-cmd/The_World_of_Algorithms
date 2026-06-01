# -*- coding: utf-8 -*-
"""Нормализация тем и заданий перед сборкой LESSONS."""

from __future__ import annotations

from course_data.task_types import normalize_task

_PROJECT_TASK_KINDS = frozenset({'project_stage', 'project_step'})


def _tasks_with_project_last(tasks: list[dict]) -> list[dict]:
    """Проектное задание — всегда последний этап в теме."""
    regular: list[dict] = []
    project: list[dict] = []
    for task in tasks:
        if task.get('kind') in _PROJECT_TASK_KINDS:
            project.append(task)
        else:
            regular.append(task)
    return regular + project


def finalize_topic(topic: dict) -> dict:
    """Копия темы с нормализованными заданиями и полями num / project_step."""
    row = dict(topic)
    tasks = row.get('tasks') or []
    normalized = [normalize_task(t) for t in tasks]
    row['tasks'] = _tasks_with_project_last(normalized)
    return row


def flatten_module_tasks(module: dict) -> list[dict]:
    out: list[dict] = []
    for topic in module.get('topics') or []:
        tid = topic['id']
        ttitle = topic['title']
        tnum = topic.get('num')
        for task in topic.get('tasks') or []:
            row = {**task, 'topic_id': tid, 'topic_title': ttitle}
            if tnum is not None:
                row['topic_num'] = tnum
            if 'type' not in row:
                row['type'] = 'code'
            out.append(row)
    return out
