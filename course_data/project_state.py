# -*- coding: utf-8 -*-
"""Состояние проекта «Калькулятор калорий» для UI и проверок."""

from __future__ import annotations

from course_data.project import PROJECT_LINE, PROJECT_NAME

_PROJECT_RELEASE_KINDS = frozenset({'project_stage', 'project_step'})

# ВРЕМЕННО: превью «Калькулятор калорий — готов» (золото + все ✓).
# Откат: поставить False или удалить блок _preview_complete_meta ниже.
PREVIEW_PROJECT_COMPLETE = False


def project_line_for_module(module_id: int) -> dict[int, dict]:
    """Проектная дорожная карта для конкретного модуля."""
    if module_id == 2:
        from course_data.modules.module_2.project import MODULE_2_PROJECT

        return MODULE_2_PROJECT
    return PROJECT_LINE


def project_base_version_for_module(module_id: int) -> str:
    return '1.0' if module_id == 2 else '0.0'


def project_stage_task_id(topic: dict) -> int | None:
    """Id проектного шага в теме (если есть)."""
    for t in topic.get('tasks') or []:
        if t.get('kind') in _PROJECT_RELEASE_KINDS:
            return t['id']
    return None


def completed_project_stages(progress, module_id: int = 1) -> list[int]:
    """Номера тем, чей проектный шаг сдан."""
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
        can_focus = (task.get('kind') in _PROJECT_RELEASE_KINDS) or (not focus_only_project_stage)
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
    """Данные для правой панели: проектная линия текущего модуля."""
    project_line = project_line_for_module(module_id)
    base_version = project_base_version_for_module(module_id)
    raw_done = completed_project_stages(progress, module_id)
    stages_done = [n for n in raw_done if n in project_line]
    done_set = set(stages_done)
    checklist: list[dict] = []
    version = base_version
    version_display = base_version
    focus_num = topic_num if topic_num in project_line else None
    current_num: int | None = None

    for num in sorted(project_line.keys()):
        row = project_line[num]
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

    stages_total = len(project_line)
    stages_done_count = len(stages_done)
    is_complete = stages_total > 0 and stages_done_count >= stages_total

    if is_complete:
        panel_suffix = 'готов'
    elif focus_num is not None:
        panel_suffix = project_line[focus_num].get(
            'version_label', project_line[focus_num].get('version', base_version)
        )
    elif current_num is not None:
        panel_suffix = project_line[current_num].get(
            'version_label', project_line[current_num].get('version', base_version)
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
