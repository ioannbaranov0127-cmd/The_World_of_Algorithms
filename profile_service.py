# -*- coding: utf-8 -*-
"""Данные для страницы профиля."""

from __future__ import annotations

from course_data import LESSONS, TOTAL_TASKS_COUNT
from course_data.project import PROJECT_NAME
from course_data.project_state import (
    completed_project_stages,
    project_line_for_module,
    project_stage_task_id,
)
from models import User
from progress_service import UserProgress, module_access_lock_message


def _format_dt(dt) -> str | None:
    if dt is None:
        return None
    try:
        return dt.strftime('%d.%m.%Y')
    except AttributeError:
        return str(dt)


def _project_checklist(progress: UserProgress, module_id: int) -> list[dict]:
    line = project_line_for_module(module_id)
    done_set = set(completed_project_stages(progress, module_id))
    rows: list[dict] = []
    for num in sorted(line.keys()):
        row = line[num]
        rows.append({
            'num': num,
            'version_label': row.get('version_label', row.get('version', '')),
            'feature': row.get('feature') or row.get('name') or f'Шаг {num}',
            'done': num in done_set,
        })
    return rows


def _last_project_snapshot(progress: UserProgress) -> dict | None:
    completed = set(progress.completed_tasks)
    best: tuple[int, int, int, str, str] | None = None

    for mid in sorted(LESSONS.keys()):
        mod = LESSONS.get(mid) or {}
        line = project_line_for_module(mid)
        for topic in mod.get('topics') or []:
            num = topic.get('num')
            if num is None or num not in line:
                continue
            pid = project_stage_task_id(topic)
            if pid is None or pid not in completed:
                continue
            ver = str(line[num].get('version_label', line[num].get('version', '')))
            feat = str(line[num].get('feature') or line[num].get('name') or '')
            candidate = (mid, int(num), int(pid), ver, feat)
            if best is None or (candidate[0], candidate[1]) > (best[0], best[1]):
                best = candidate

    if best is None:
        return None

    mid, num, task_id, version_label, feature = best
    code = (progress.project_code.get(mid) or '').strip()
    mod_title = LESSONS.get(mid, {}).get('title', f'Модуль {mid}')
    return {
        'module_id': mid,
        'module_title': mod_title,
        'topic_num': num,
        'task_id': task_id,
        'version_label': version_label,
        'feature': feature,
        'code': code,
        'has_code': bool(code),
    }


def _current_position_label(progress: UserProgress) -> str:
    mid = progress.current_module
    mod = LESSONS.get(mid) or {}
    tasks = mod.get('tasks') or []
    idx = progress.current_task_index
    if not tasks or idx < 0 or idx >= len(tasks):
        return mod.get('title') or f'Модуль {mid}'
    task = tasks[idx]
    topic_title = task.get('topic_title') or mod.get('title') or f'Модуль {mid}'
    return f'{topic_title} · задание #{task.get("id", idx + 1)}'


def build_profile_context(user: User, progress: UserProgress, *, enforce_m1_gate: bool) -> dict:
    from app import (
        achievement_list,
        build_modules_stats,
        course_grade_meta,
        course_started,
        next_task_preview,
    )

    completed_count = len(progress.completed_tasks)
    overall_pct = int(completed_count * 100 / TOTAL_TASKS_COUNT) if TOTAL_TASKS_COUNT else 0
    grade = course_grade_meta(progress)
    modules = build_modules_stats(progress)
    achievements = achievement_list(progress, TOTAL_TASKS_COUNT)
    achievements_unlocked = sum(1 for a in achievements if a.get('unlocked'))

    m1_stages = _project_checklist(progress, 1)
    m2_stages = _project_checklist(progress, 2)
    next_task = next_task_preview(progress)

    module_details = []
    for mod in modules:
        mid = mod['id']
        mod_obj = LESSONS.get(mid) or {}
        tasks = mod_obj.get('tasks') or []
        done = sum(1 for t in tasks if t['id'] in progress.completed_tasks)
        module_details.append({
            **mod,
            'completed_tasks': done,
            'total_tasks': len(tasks),
            'is_locked': bool(module_access_lock_message(progress, mid, enforce=enforce_m1_gate)),
            'project_done': len(completed_project_stages(progress, mid)),
            'project_total': len(project_line_for_module(mid)),
        })

    return {
        'profile_user': user,
        'progress': progress,
        'project_name': PROJECT_NAME,
        'member_since': _format_dt(user.created_at),
        'last_seen': _format_dt(user.last_seen_at),
        'has_progress': course_started(progress),
        'completed_tasks': completed_count,
        'total_tasks': TOTAL_TASKS_COUNT,
        'overall_progress_pct': overall_pct,
        'course_grade': grade,
        'modules_stats': module_details,
        'achievements': achievements,
        'achievements_unlocked': achievements_unlocked,
        'achievements_total': len(achievements),
        'm1_project_stages': m1_stages,
        'm2_project_stages': m2_stages,
        'next_task': next_task,
        'current_position': _current_position_label(progress),
        'current_module': progress.current_module,
    }
