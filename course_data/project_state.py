# -*- coding: utf-8 -*-
"""Состояние проекта «Калькулятор калорий» для UI и проверок."""

from __future__ import annotations

from course_data.project import PROJECT_LINE, PROJECT_NAME


def project_stage_task_id(topic: dict) -> int | None:
    """Id задания project_stage в теме (если есть)."""
    for t in topic.get('tasks') or []:
        if t.get('kind') == 'project_stage':
            return t['id']
    return None


def completed_project_stages(progress, module_id: int = 1) -> list[int]:
    """Номера тем, чей этап разработки (project_stage) сдан."""
    from course_data.loader import LESSONS

    mod = LESSONS.get(module_id)
    if not mod:
        return []
    done: list[int] = []
    completed = set(progress.completed_tasks)
    for topic in mod.get('topics') or []:
        num = topic.get('num')
        if num is None:
            continue
        pid = project_stage_task_id(topic)
        if pid is not None and pid in completed:
            done.append(int(num))
    return sorted(done)


def build_project_meta(progress, module_id: int = 1) -> dict:
    """Данные для правой панели: только основные версии 0.1–1.0."""
    raw_done = completed_project_stages(progress, module_id)
    stages_done = [n for n in raw_done if n in PROJECT_LINE]
    done_set = set(stages_done)
    checklist: list[dict] = []
    version = '0.0'
    version_display = '0.0'
    current_num: int | None = None

    for num in sorted(PROJECT_LINE.keys()):
        row = PROJECT_LINE[num]
        label = row.get('feature') or f'Шаг {num}'
        ver = row.get('version_label', row.get('version', ''))
        if num in done_set:
            status = 'done'
            version = row.get('version', version)
            version_display = ver
        elif current_num is None:
            status = 'current'
            current_num = num
        else:
            status = 'pending'

        checklist.append(
            {
                'num': num,
                'feature': label,
                'version_label': ver,
                'status': status,
            }
        )

    stages_total = len(PROJECT_LINE)
    stages_done_count = len(stages_done)

    return {
        'name': PROJECT_NAME,
        'version': version,
        'version_display': version_display,
        'stages_done': stages_done,
        'stages_done_count': stages_done_count,
        'stages_total': stages_total,
        'current_stage': current_num,
        'checklist': checklist,
    }
