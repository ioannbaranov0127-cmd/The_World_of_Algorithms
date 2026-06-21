# -*- coding: utf-8 -*-
"""Registration, login, logout."""

from __future__ import annotations

import re

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from db import db
from models import User
from progress_service import ensure_progress_row

auth_bp = Blueprint('auth', __name__)

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _safe_next_url(raw: str | None) -> str:
    if not raw:
        return url_for('learn')
    if raw.startswith('/') and not raw.startswith('//'):
        return raw
    return url_for('learn')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('learn'))

    errors: list[str] = []
    name = ''
    email = ''

    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        password2 = request.form.get('password2') or ''

        if len(name) < 2:
            errors.append('Укажите имя (минимум 2 символа).')
        if not _EMAIL_RE.match(email):
            errors.append('Укажите корректный email.')
        if len(password) < 6:
            errors.append('Пароль — минимум 6 символов.')
        if password != password2:
            errors.append('Пароли не совпадают.')
        if User.query.filter_by(email=email).first():
            errors.append('Пользователь с таким email уже зарегистрирован.')

        if not errors:
            admin_email = (current_app.config.get('ADMIN_EMAIL') or '').strip().lower()
            role = 'admin' if admin_email and email == admin_email else 'student'
            user = User(email=email, name=name, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            ensure_progress_row(user.id)
            login_user(user, remember=True)
            flash('Аккаунт создан. Добро пожаловать!', 'success')
            return redirect(_safe_next_url(request.args.get('next')))

    return render_template('auth_register.html', errors=errors, name=name, email=email)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('learn'))

    errors: list[str] = []
    email = ''

    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            errors.append('Неверный email или пароль.')
        else:
            ensure_progress_row(user.id)
            login_user(user, remember=True)
            user.touch_seen()
            db.session.commit()
            flash('Вы вошли в аккаунт.', 'success')
            return redirect(_safe_next_url(request.form.get('next') or request.args.get('next')))

    return render_template(
        'auth_login.html',
        errors=errors,
        email=email,
        next_url=_safe_next_url(request.args.get('next')),
    )


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'info')
    return redirect(url_for('home'))
