# -*- coding: utf-8 -*-
"""Опубликованные темы 5–10 модуля 1 (порядок по учебному плану)."""

from __future__ import annotations

from course_data.modules.module_1.topics.topic_06 import TOPIC as TOPIC_06
from course_data.modules.module_1.topics.topic_07 import TOPIC as TOPIC_07
from course_data.modules.module_1.topics.topic_08 import TOPIC as TOPIC_08
from course_data.modules.module_1.topics.topic_09 import TOPIC as TOPIC_09
from course_data.modules.module_1.topics.topic_10 import TOPIC as TOPIC_09_COMPARE
from course_data.modules.module_1.topics.topic_11 import TOPIC as TOPIC_10_WHILE

_PUBLISHED_5_10 = (
    TOPIC_07,
    TOPIC_06,
    TOPIC_08,
    TOPIC_09,
    TOPIC_09_COMPARE,
    TOPIC_10_WHILE,
)


def get_topics_5_10() -> list[dict]:
    return list(_PUBLISHED_5_10)
