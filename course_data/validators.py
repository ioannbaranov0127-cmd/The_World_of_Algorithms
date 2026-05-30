# -*- coding: utf-8 -*-

from __future__ import annotations

import ast

from course_data.constants import DEFAULT_CODE_EDITOR_PLACEHOLDER


def stdout_matches(output: str, expected: str) -> bool:
    output_lines = [line.strip() for line in output.split('\n') if line.strip()]
    expected_lines = [line.strip() for line in expected.split('\n') if line.strip()]
    return output_lines == expected_lines


def validate_project_tests(code: str, tests: list[dict] | None) -> tuple[bool, list[str]]:
    """Проверки кода этапа разработки (без stdout)."""
    if not tests:
        return True, []
    failures: list[str] = []
    src = code or ''
    for i, rule in enumerate(tests, start=1):
        check = rule.get('check')
        msg = rule.get('message') or f'Тест {i} не пройден'
        if check == 'contains':
            if rule.get('value', '') not in src:
                failures.append(msg)
        elif check == 'not_contains':
            if rule.get('value', '') in src:
                failures.append(msg)
        elif check == 'uses_name':
            try:
                tree = ast.parse(src)
            except SyntaxError:
                failures.append('Сначала исправьте синтаксис программы.')
                break
            names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            if rule.get('name') not in names:
                failures.append(msg)
        elif check == 'uses_call':
            fn = rule.get('name', '')
            found = False
            try:
                tree = ast.parse(src)
            except SyntaxError:
                failures.append('Сначала исправьте синтаксис программы.')
                break
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == fn:
                        found = True
                        break
            if not found:
                failures.append(msg)
    return len(failures) == 0, failures


def topic_by_task_id(module_id: int, task_id: int) -> dict | None:
    from course_data.loader import LESSONS

    mod = LESSONS.get(module_id)
    if not mod:
        return None
    for topic in mod.get('topics') or []:
        for t in topic.get('tasks') or []:
            if t['id'] == task_id:
                return topic
    return None


def task_client_payload(task: dict) -> dict:
    ttype = task.get('type', 'code')
    base: dict = {
        'id': task['id'],
        'type': ttype,
        'text': task['text'],
        'hint': task.get('hint', ''),
        'xp': task.get('xp', 0),
        'kind': task.get('kind', ttype),
    }
    if ttype == 'code':
        sc = task.get('starter_code')
        if sc is None or not str(sc).strip():
            base['starter_code'] = DEFAULT_CODE_EDITOR_PLACEHOLDER
        else:
            base['starter_code'] = sc
    elif ttype == 'quiz':
        base['options'] = task['options']
    elif ttype == 'ordering':
        base['items'] = list(task['items'])
    elif ttype == 'matching':
        base['left'] = list(task['left'])
        base['right'] = list(task['right'])
    elif ttype == 'fill_gaps':
        base['template'] = task['template']
        base['blank_count'] = len(task.get('answers') or [])
    return base


def validate_interactive_answer(task: dict, answer) -> bool:
    ttype = task.get('type', 'code')
    if ttype == 'code':
        return False
    if ttype == 'quiz':
        return answer == task.get('correct')
    if ttype == 'ordering':
        return answer == task.get('correct_order')
    if ttype == 'matching':
        exp = task.get('correct_pairs')
        if not isinstance(answer, list) or len(answer) != len(exp):
            return False
        return list(answer) == list(exp)
    if ttype == 'fill_gaps':
        exp = task.get('answers')
        if not isinstance(answer, list) or len(answer) != len(exp):
            return False
        return [str(x).strip() for x in answer] == [str(x).strip() for x in exp]
    return False
