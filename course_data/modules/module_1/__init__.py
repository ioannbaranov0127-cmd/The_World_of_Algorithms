# -*- coding: utf-8 -*-
"""Сборка тем модуля 1: готовые (1–4, 5–10) + черновые (12–17)."""

from __future__ import annotations

from course_data.constants import INCLUDE_DRAFT_TOPICS
from course_data.modules.module_1.foundation import get_topics as get_foundation_topics
from course_data.modules.module_1.topics import get_topics_5_10
from course_data.modules.module_1.topics_draft import get_draft_topics
from course_data.project import project_step_for_topic
from course_data.registry import finalize_topic


def get_all_topics() -> list[dict]:
    topics = [finalize_topic(t) for t in get_foundation_topics()]
    topics.extend(finalize_topic(t) for t in get_topics_5_10())
    for t in topics:
        num = t.get('num')
        if num is None:
            try:
                num = int(str(t['id']).split('-t')[-1])
                t['num'] = num
            except (ValueError, IndexError):
                pass
        if num and 'project_step' not in t:
            t['project_step'] = project_step_for_topic(num)
    if INCLUDE_DRAFT_TOPICS:
        topics.extend(finalize_topic(t) for t in get_draft_topics())
    return topics
