# -*- coding: utf-8 -*-
"""
Пакет данных курса «Мир алгоритмов: проектируем на Python».

Публичный API совместим с прежним course_data.py — app.py менять не нужно.
"""

from course_data.achievements import ACHIEVEMENTS
from course_data.constants import COURSE, INCLUDE_DRAFT_TOPICS, MODULE_IDS, XP_PER_LEVEL
from course_data.loader import LESSONS, MODULES, TASK_BY_ID, TOTAL_TASKS_COUNT
from course_data.project import PROJECT_LINE, PROJECT_NAME, project_step_for_topic
from course_data.validators import (
    task_client_payload,
    topic_by_task_id,
    validate_interactive_answer,
    validate_project_tests,
    stdout_matches,
)

__all__ = [
    'ACHIEVEMENTS',
    'COURSE',
    'INCLUDE_DRAFT_TOPICS',
    'LESSONS',
    'MODULE_IDS',
    'MODULES',
    'PROJECT_LINE',
    'PROJECT_NAME',
    'TASK_BY_ID',
    'TOTAL_TASKS_COUNT',
    'XP_PER_LEVEL',
    'project_step_for_topic',
    'task_client_payload',
    'topic_by_task_id',
    'validate_interactive_answer',
]
