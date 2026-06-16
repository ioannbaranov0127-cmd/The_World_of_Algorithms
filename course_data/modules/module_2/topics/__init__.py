# -*- coding: utf-8 -*-
"""Темы модуля 2."""

from __future__ import annotations

from course_data.modules.module_2.topics.stubs import TOPICS

_ALL = TOPICS


def get_topics() -> list[dict]:
    return list(_ALL)
