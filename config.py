# -*- coding: utf-8 -*-
"""Application configuration."""

from __future__ import annotations

import os


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ('1', 'true', 'yes', 'on')


class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'instance',
            'course.db',
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAIL = (os.environ.get('ADMIN_EMAIL') or '').strip().lower()

    ENFORCE_PROJECT_STAGE_PREREQUISITE = True
    ENFORCE_M1_BEFORE_M2 = True
    COURSE_GRADE_DEMO_PANEL_ENABLED = True

    @staticmethod
    def init_app(app) -> None:
        is_prod = not app.debug and not _env_bool('FLASK_DEBUG')
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['SESSION_COOKIE_SECURE'] = is_prod and _env_bool('SESSION_COOKIE_SECURE', True)

        uri = app.config['SQLALCHEMY_DATABASE_URI']
        if uri.startswith('postgres://'):
            app.config['SQLALCHEMY_DATABASE_URI'] = uri.replace('postgres://', 'postgresql://', 1)

        if is_prod and app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            raise RuntimeError(
                'В production нужен DATABASE_URL (PostgreSQL). '
                'SQLite на Render стирается при каждом перезапуске — аккаунты и прогресс пропадут.'
            )

        if is_prod and not app.config['SECRET_KEY']:
            raise RuntimeError('FLASK_SECRET_KEY is required in production')
