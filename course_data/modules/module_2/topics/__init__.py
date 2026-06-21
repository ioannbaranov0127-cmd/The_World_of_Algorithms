# -*- coding: utf-8 -*-
"""Темы модуля 2."""

from __future__ import annotations

from course_data.modules.module_2.topics.stubs import TOPICS as _STUB_TOPICS
from course_data.modules.module_2.topics.topic_01 import TOPIC as TOPIC_01
from course_data.modules.module_2.topics.topic_02 import TOPIC as TOPIC_02
from course_data.modules.module_2.topics.topic_03 import TOPIC as TOPIC_03
from course_data.modules.module_2.topics.topic_04 import TOPIC as TOPIC_04
from course_data.modules.module_2.topics.topic_05 import TOPIC as TOPIC_05
from course_data.modules.module_2.topics.topic_06 import TOPIC as TOPIC_06
from course_data.modules.module_2.topics.topic_07 import TOPIC as TOPIC_07
from course_data.modules.module_2.topics.topic_08 import TOPIC as TOPIC_08
from course_data.modules.module_2.topics.topic_09 import TOPIC as TOPIC_09
from course_data.modules.module_2.topics.topic_10 import TOPIC as TOPIC_10

_ALL = (TOPIC_01, TOPIC_02, TOPIC_03, TOPIC_04, TOPIC_05, TOPIC_06, TOPIC_07, TOPIC_08, TOPIC_09, TOPIC_10, *_STUB_TOPICS[10:])


def get_topics() -> list[dict]:
    return list(_ALL)
