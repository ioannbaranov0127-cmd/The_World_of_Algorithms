# -*- coding: utf-8 -*-
"""Агрегация данных для админ-панели."""

from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload

from course_data import LESSONS, TOTAL_TASKS_COUNT
from course_data.constants import INCLUDE_DRAFT_TOPICS
from course_data.project_state import completed_project_stages, project_line_for_module
from db import db
from models import CourseProgress, User
from profile_service import _last_project_snapshot, _project_checklist
from progress_service import UserProgress, ensure_progress_row


def _format_dt(dt) -> str:
    if dt is None:
        return '—'
    try:
        return dt.strftime('%d.%m.%Y %H:%M')
    except AttributeError:
        return str(dt)


def _format_date(dt) -> str:
    if dt is None:
        return '—'
    try:
        return dt.strftime('%d.%m.%Y')
    except AttributeError:
        return str(dt)


def progress_from_user(user: User) -> UserProgress:
    row = user.progress
    if row is None:
        row = ensure_progress_row(user.id)
    return UserProgress(row)


def progress_has_activity(progress: UserProgress) -> bool:
    if progress.completed_tasks or progress.total_xp > 0:
        return True
    if progress.current_module > 1 or progress.current_task_index > 0:
        return True
    return any((code or '').strip() for code in progress.project_code.values())


def _student_metrics(user: User, progress: UserProgress) -> dict:
    from app import course_grade_meta

    completed = len(progress.completed_tasks)
    overall_pct = int(completed * 100 / TOTAL_TASKS_COUNT) if TOTAL_TASKS_COUNT else 0
    m1_done = len(completed_project_stages(progress, 1))
    m1_total = len(project_line_for_module(1))
    m2_done = len(completed_project_stages(progress, 2))
    m2_total = len(project_line_for_module(2))
    grade = course_grade_meta(progress)
    last_project = _last_project_snapshot(progress)

    row = user.progress
    return {
        'user_id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'is_admin': user.is_admin,
        'created_at': _format_date(user.created_at),
        'last_seen_at': _format_dt(user.last_seen_at),
        'progress_updated_at': _format_dt(row.updated_at if row else None),
        'started': progress_has_activity(progress),
        'completed_tasks': completed,
        'total_tasks': TOTAL_TASKS_COUNT,
        'overall_pct': overall_pct,
        'm1_project_done': m1_done,
        'm1_project_total': m1_total,
        'm2_project_done': m2_done,
        'm2_project_total': m2_total,
        'last_project_version': last_project['version_label'] if last_project else '—',
        'last_project_module': last_project['module_title'] if last_project else '—',
        'grade_label': grade['label'],
        'grade_percent': grade['percent'],
        'grade_state': grade['state'],
        'current_module': progress.current_module,
        'module1_pct': progress.get_module_progress(1),
        'module2_pct': progress.get_module_progress(2),
    }


def build_admin_overview() -> dict:
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    users = (
        User.query.options(joinedload(User.progress))
        .order_by(User.last_seen_at.desc())
        .all()
    )
    students = [u for u in users if not u.is_admin]
    admins = [u for u in users if u.is_admin]

    rows = [_student_metrics(u, progress_from_user(u)) for u in students]
    active_week = 0
    started_count = 0
    for u in students:
        p = progress_from_user(u)
        if progress_has_activity(p):
            started_count += 1
        seen = u.last_seen_at
        if seen is not None:
            if seen.tzinfo is None:
                seen = seen.replace(tzinfo=timezone.utc)
            if seen >= week_ago:
                active_week += 1

    return {
        'students': rows,
        'stats': {
            'students_total': len(students),
            'admins_total': len(admins),
            'started_count': started_count,
            'active_week': active_week,
            'draft_topics_enabled': INCLUDE_DRAFT_TOPICS,
            'course_tasks_total': TOTAL_TASKS_COUNT,
        },
    }


def build_student_detail(user_id: int) -> dict | None:
    user = User.query.options(joinedload(User.progress)).filter_by(id=user_id).first()
    if user is None or user.is_admin:
        return None

    progress = progress_from_user(user)
    metrics = _student_metrics(user, progress)
    return {
        **metrics,
        'm1_stages': _project_checklist(progress, 1),
        'm2_stages': _project_checklist(progress, 2),
        'last_project': _last_project_snapshot(progress),
        'completed_task_ids': list(progress.completed_tasks),
    }


def reset_student_progress(user_id: int) -> bool:
    user = User.query.options(joinedload(User.progress)).filter_by(id=user_id).first()
    if user is None or user.is_admin:
        return False
    progress = progress_from_user(user)
    progress.reset()
    return True


def delete_student(user_id: int) -> bool:
    user = User.query.filter_by(id=user_id).first()
    if user is None or user.is_admin:
        return False
    db.session.delete(user)
    db.session.commit()
    return True


def export_students_csv() -> str:
    overview = build_admin_overview()
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=';')
    writer.writerow([
        'Имя',
        'Email',
        'Прогресс %',
        'Заданий',
        'M1 версии',
        'M2 версии',
        'Последняя версия',
        'Оценка',
        'Оценка %',
        'Начал',
        'Последний визит',
        'Обновление прогресса',
    ])
    for row in overview['students']:
        writer.writerow([
            row['name'],
            row['email'],
            row['overall_pct'],
            f"{row['completed_tasks']}/{row['total_tasks']}",
            f"{row['m1_project_done']}/{row['m1_project_total']}",
            f"{row['m2_project_done']}/{row['m2_project_total']}",
            row['last_project_version'],
            row['grade_label'],
            row['grade_percent'],
            'да' if row['started'] else 'нет',
            row['last_seen_at'],
            row['progress_updated_at'],
        ])
    return buf.getvalue()
