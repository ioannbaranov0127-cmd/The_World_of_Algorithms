# -*- coding: utf-8 -*-
"""Админ-панель: ученики, прогресс, экспорт."""

from __future__ import annotations

from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from admin_service import (
    build_admin_overview,
    build_student_detail,
    delete_student,
    export_students_csv,
    reset_student_progress,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route('/', strict_slashes=False)
@admin_required
def index():
    data = build_admin_overview()
    return render_template(
        'admin/index.html',
        students=data['students'],
        stats=data['stats'],
        auth_user=current_user,
    )


@admin_bp.route('/students/<int:user_id>')
@admin_required
def student_detail(user_id: int):
    detail = build_student_detail(user_id)
    if detail is None:
        abort(404)
    return render_template(
        'admin/student.html',
        student=detail,
        auth_user=current_user,
    )


@admin_bp.route('/students/<int:user_id>/reset', methods=['POST'])
@admin_required
def student_reset(user_id: int):
    if not reset_student_progress(user_id):
        flash('Не удалось сбросить прогресс.', 'error')
    else:
        flash('Прогресс ученика сброшен.', 'success')
    return redirect(url_for('admin.student_detail', user_id=user_id))


@admin_bp.route('/students/<int:user_id>/delete', methods=['POST'])
@admin_required
def student_delete(user_id: int):
    if not delete_student(user_id):
        flash('Не удалось удалить ученика.', 'error')
        return redirect(url_for('admin.index'))
    flash('Ученик удалён.', 'success')
    return redirect(url_for('admin.index'))


@admin_bp.route('/export.csv')
@admin_required
def export_csv():
    from flask import Response

    payload = export_students_csv()
    return Response(
        '\ufeff' + payload,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=students_progress.csv'},
    )
