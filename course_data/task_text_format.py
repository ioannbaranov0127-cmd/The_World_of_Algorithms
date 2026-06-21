# -*- coding: utf-8 -*-
"""Форматирование текста задания: фрагменты кода с переносами строк, вопрос отдельно."""

from __future__ import annotations

import re

from markupsafe import Markup, escape

_CODE_LINE = re.compile(
    r'^\s*(?:'
    r'#|'
    r'(?:for|while|if|elif|else)\b|'
    r'print\s*\(|'
    r'def\s+|'
    r'return\b|'
    r'import\b|'
    r'from\b|'
    r'break\b|'
    r'continue\b|'
    r'[a-z_][\w]*\s*=|'
    r'[a-z_][\w]*\s*\('
    r')',
    re.IGNORECASE,
)


def _looks_like_code_line(line: str) -> bool:
    if not line.strip():
        return True
    if line.startswith('    ') or line.startswith('\t'):
        return True
    return bool(_CODE_LINE.match(line))


def format_task_text(text: str) -> Markup:
    """
    Рендер текста задания для learn.html.

    Если в начале есть строки кода (for, print, присваивания…) — показываем их в <pre>,
    остальной текст — отдельным абзацем. Иначе сохраняем переносы через pre-line.
    """
    raw = text or ''
    if not raw.strip():
        return Markup('')

    if '\n' not in raw:
        return Markup(f'<strong>{escape(raw)}</strong>')

    lines = raw.split('\n')
    code_end = 0
    for i, line in enumerate(lines):
        if _looks_like_code_line(line):
            code_end = i + 1
        elif code_end > 0:
            break

    while code_end > 0 and not lines[code_end - 1].strip():
        code_end -= 1

    if code_end == 0:
        body = escape(raw)
        return Markup(f'<strong class="task-panel__text-body">{body}</strong>')

    code_part = '\n'.join(lines[:code_end]).rstrip()
    prose_part = '\n'.join(lines[code_end:]).strip()

    chunks: list[str] = []
    if code_part:
        chunks.append(f'<pre class="task-panel__snippet">{escape(code_part)}</pre>')
    if prose_part:
        chunks.append(f'<p class="task-panel__prompt"><strong>{escape(prose_part)}</strong></p>')

    return Markup(''.join(chunks))
