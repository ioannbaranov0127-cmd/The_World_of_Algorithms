# -*- coding: utf-8 -*-
"""User accounts and persisted course progress."""

from __future__ import annotations

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from db import db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)
    last_seen_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow)

    progress = db.relationship(
        'CourseProgress',
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan',
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'

    def touch_seen(self) -> None:
        self.last_seen_at = _utcnow()


class CourseProgress(db.Model):
    __tablename__ = 'course_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    completed_tasks = db.Column(db.JSON, nullable=False, default=list)
    total_xp = db.Column(db.Integer, nullable=False, default=0)
    current_module = db.Column(db.Integer, nullable=False, default=1)
    current_task_index = db.Column(db.Integer, nullable=False, default=0)
    project_code = db.Column(db.JSON, nullable=False, default=dict)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    user = db.relationship('User', back_populates='progress')

    def reset(self) -> None:
        self.completed_tasks = []
        self.total_xp = 0
        self.current_module = 1
        self.current_task_index = 0
        self.project_code = {}
        self.updated_at = _utcnow()
