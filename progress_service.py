# -*- coding: utf-8 -*-
"""Course progress: in-memory API backed by CourseProgress rows."""

from __future__ import annotations

from flask import session
from flask_login import current_user

from course_data.loader import LESSONS
from course_data.project_state import completed_project_stages, project_line_for_module
from db import db
from models import CourseProgress


class UserProgress:
    """Runtime progress state; persists to DB for authenticated users."""

    def __init__(self, row: CourseProgress | None = None):
        self._row = row
        if row is not None:
            self.completed_tasks = list(row.completed_tasks or [])
            self.total_xp = int(row.total_xp or 0)
            self.current_module = int(row.current_module or 1)
            self.current_task_index = int(row.current_task_index or 0)
            raw_pc = row.project_code or {}
            self.project_code = {int(k): v for k, v in raw_pc.items()}
        else:
            self.completed_tasks = []
            self.total_xp = 0
            self.current_module = 1
            self.current_task_index = 0
            self.project_code = {}

    def save(self) -> None:
        if self._row is None:
            return
        self._row.completed_tasks = list(self.completed_tasks)
        self._row.total_xp = int(self.total_xp)
        self._row.current_module = int(self.current_module)
        self._row.current_task_index = int(self.current_task_index)
        self._row.project_code = {str(k): v for k, v in self.project_code.items()}
        db.session.commit()

    def complete_task(self, task_id, xp) -> bool:
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
            self.total_xp += xp
            mark_course_started()
            self.save()
            return True
        return False

    def get_module_progress(self, module_id):
        if module_id not in LESSONS:
            return 0
        mod = LESSONS[module_id]
        tasks = mod['tasks']
        if mod.get('stub') and not tasks:
            return 0
        if not tasks:
            return 0
        completed = sum(1 for task in tasks if task['id'] in self.completed_tasks)
        return int((completed / len(tasks)) * 100)

    def is_module_completed(self, module_id):
        if module_id not in LESSONS:
            return False
        mod = LESSONS[module_id]
        if mod.get('stub') and not mod['tasks']:
            return True
        tasks = mod['tasks']
        if not tasks:
            return False
        return self.get_module_progress(module_id) == 100

    def get_next_module(self):
        for i in sorted(LESSONS.keys()):
            mod = LESSONS[i]
            if mod.get('stub') and not mod['tasks']:
                continue
            if not self.is_module_completed(i):
                return i
        return None

    def reset(self) -> None:
        self.completed_tasks = []
        self.total_xp = 0
        self.current_module = 1
        self.current_task_index = 0
        self.project_code = {}
        if self._row is not None:
            self._row.reset()
            db.session.commit()


def mark_course_started() -> None:
    session['course_started'] = True


def course_started(progress: UserProgress) -> bool:
    if session.get('course_started'):
        return True
    if progress.completed_tasks or progress.total_xp > 0:
        return True
    if progress.current_module > 1 or progress.current_task_index > 0:
        return True
    if any((code or '').strip() for code in progress.project_code.values()):
        return True
    return False


def get_user_progress() -> UserProgress:
    if not current_user.is_authenticated:
        raise RuntimeError('get_user_progress requires authenticated user')
    row = CourseProgress.query.filter_by(user_id=current_user.id).first()
    if row is None:
        row = CourseProgress(user_id=current_user.id)
        db.session.add(row)
        db.session.commit()
    current_user.touch_seen()
    db.session.commit()
    return UserProgress(row)


def ensure_progress_row(user_id: int) -> CourseProgress:
    row = CourseProgress.query.filter_by(user_id=user_id).first()
    if row is None:
        row = CourseProgress(user_id=user_id)
        db.session.add(row)
        db.session.commit()
    return row


def strict_course_enforcement_enabled(*, user=None) -> bool:
    """False для admin — в курсе все задания и модули открыты."""
    from flask_login import current_user

    subject = user
    if subject is None and current_user.is_authenticated:
        subject = current_user
    if subject is not None and getattr(subject, 'is_admin', False):
        return False
    return True


def module_access_lock_message(progress: UserProgress, module_id: int, *, enforce: bool) -> str | None:
    if not enforce or module_id <= 1:
        return None
    stages_total = len(project_line_for_module(1))
    stages_done = len(completed_project_stages(progress, 1))
    if stages_total > 0 and stages_done >= stages_total:
        return None
    return (
        'Модуль 2 откроется после сдачи всех версий проекта в модуле 1 (до 1.0). '
        'Продолжайте темы первого модуля и сдавайте project_stage каждой темы.'
    )


def module_id_for_task(task_id: int) -> int | None:
    for mid, mod in LESSONS.items():
        if any((t.get('id') == task_id) for t in (mod.get('tasks') or [])):
            return mid
    return None


def task_access_lock_message(progress: UserProgress, task_id: int, *, enforce: bool) -> str | None:
    mid = module_id_for_task(task_id)
    if mid is None:
        return None
    return module_access_lock_message(progress, mid, enforce=enforce)
