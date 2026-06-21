# -*- coding: utf-8 -*-
"""Стартовая инициализация: админ-аккаунт из переменных окружения."""

from __future__ import annotations

import logging

from flask import current_app

from config import _env_bool
from db import db
from models import User
from progress_service import ensure_progress_row

logger = logging.getLogger(__name__)


def ensure_admin_user() -> None:
    """Создать или обновить преподавателя по ADMIN_EMAIL (+ ADMIN_PASSWORD при необходимости)."""
    email = (current_app.config.get('ADMIN_EMAIL') or '').strip().lower()
    if not email:
        return

    password = (current_app.config.get('ADMIN_PASSWORD') or '').strip()
    name = (current_app.config.get('ADMIN_NAME') or 'Преподаватель').strip() or 'Преподаватель'

    user = User.query.filter_by(email=email).first()
    if user is None:
        if len(password) < 6:
            logger.warning(
                'ADMIN_EMAIL=%s задан, но аккаунта нет. '
                'Укажите ADMIN_PASSWORD (мин. 6 символов) или зарегистрируйтесь на /register.',
                email,
            )
            return
        user = User(email=email, name=name, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        ensure_progress_row(user.id)
        logger.info('Создан админ-аккаунт: %s', email)
        return

    changed = False
    if user.role != 'admin':
        user.role = 'admin'
        changed = True
    if user.name != name:
        user.name = name
        changed = True

    reset_password = _env_bool('ADMIN_RESET_PASSWORD')
    if reset_password and len(password) >= 6:
        user.set_password(password)
        changed = True

    if changed:
        db.session.commit()
        logger.info('Обновлён админ-аккаунт: %s', email)

    ensure_progress_row(user.id)
