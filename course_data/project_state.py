# -*- coding: utf-8 -*-
"""Состояние проекта «Калькулятор калорий» для UI и проверок."""

from __future__ import annotations

from course_data.project import PROJECT_LINE, PROJECT_NAME

# ВРЕМЕННО: превью «Калькулятор калорий — готов» (золото + все ✓).
# Откат: поставить False или удалить блок _preview_complete_meta ниже.
PREVIEW_PROJECT_COMPLETE = False


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


def project_meta_for_task(
    progress,
    module_id: int,
    task_id: int | None = None,
    *,
    focus_only_project_stage: bool = True,
) -> dict:
    """Панель прогресса с привязкой к теме текущего задания.

    Если focus_only_project_stage=True, подсветка текущей версии включается
    только на project_stage заданиях темы.
    """
    topic_num: int | None = None
    if task_id is not None:
        from course_data.validators import topic_by_task_id
        from course_data import TASK_BY_ID

        topic = topic_by_task_id(module_id, task_id)
        task = TASK_BY_ID.get(task_id) or {}
        can_focus = (task.get('kind') == 'project_stage') or (not focus_only_project_stage)
        if topic and can_focus:
            topic_num = topic.get('num')
    return build_project_meta(progress, module_id, topic_num=topic_num)


def _preview_complete_meta(meta: dict) -> dict:
    """Временная подмена: все этапы сданы, заголовок «готов»."""
    stages_total = meta['stages_total']
    checklist = []
    last_ver = '1.0'
    for item in meta['checklist']:
        row = dict(item)
        row['status'] = 'done'
        checklist.append(row)
        last_ver = row.get('version_label') or last_ver
    return {
        **meta,
        'version': last_ver,
        'version_display': last_ver,
        'panel_suffix': 'готов',
        'is_complete': True,
        'stages_done': list(PROJECT_LINE.keys()),
        'stages_done_count': stages_total,
        'current_stage': None,
        'focused_topic': None,
        'checklist': checklist,
    }


def build_project_meta(
    progress,
    module_id: int = 1,
    *,
    topic_num: int | None = None,
) -> dict:
    """Данные для правой панели: этапы 0.1–1.0 (10 шагов, без отдельного «полностью готов»)."""
    raw_done = completed_project_stages(progress, module_id)
    stages_done = [n for n in raw_done if n in PROJECT_LINE]
    done_set = set(stages_done)
    checklist: list[dict] = []
    version = '0.0'
    version_display = '0.0'
    focus_num = topic_num if topic_num in PROJECT_LINE else None
    current_num: int | None = None

    for num in sorted(PROJECT_LINE.keys()):
        row = PROJECT_LINE[num]
        label = row.get('feature') or f'Шаг {num}'
        ver = row.get('version_label', row.get('version', ''))
        if num in done_set:
            status = 'done'
            version = row.get('version', version)
            version_display = ver
        elif focus_num is not None:
            if num == focus_num:
                status = 'current'
                current_num = num
            else:
                status = 'pending'
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
    is_complete = stages_total > 0 and stages_done_count >= stages_total

    if is_complete:
        panel_suffix = 'готов'
    elif focus_num is not None:
        panel_suffix = PROJECT_LINE[focus_num].get(
            'version_label', PROJECT_LINE[focus_num].get('version', '0.1')
        )
    elif current_num is not None:
        panel_suffix = PROJECT_LINE[current_num].get(
            'version_label', PROJECT_LINE[current_num].get('version', '0.1')
        )
    else:
        panel_suffix = version_display

    result = {
        'name': PROJECT_NAME,
        'version': version,
        'version_display': version_display,
        'panel_suffix': panel_suffix,
        'is_complete': is_complete,
        'stages_done': stages_done,
        'stages_done_count': stages_done_count,
        'stages_total': stages_total,
        'current_stage': current_num,
        'focused_topic': focus_num,
        'checklist': checklist,
    }

    if PREVIEW_PROJECT_COMPLETE:
        return _preview_complete_meta(result)

    return result
